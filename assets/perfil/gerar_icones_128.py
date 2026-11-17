# -*- coding: utf-8 -*-
"""
gerar_icones_128.py
-------------------
Transforma todas as imagens .png da pasta atual em ícones de 128x128 pixels
com foco no personagem, fundo transparente e nitidez reforçada.

Passos por imagem:
  1. Verifica e instala automaticamente rembg, onnxruntime e Pillow.
  2. Remove o fundo com o rembg (personagem fica com transparência).
  3. Auto-crop (getbbox) ao redor da área visível do personagem.
  4. Redimensiona para caber em 128x128 com margem de 4px (Lanczos).
  5. Centraliza em canvas transparente 128x128 e aplica UnsharpMask leve.
  6. Salva como .png (mesmo nome) na pasta "icones_128".
"""

import importlib
import subprocess
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# Passo 1: verificar e instalar automaticamente as bibliotecas necessárias
# ----------------------------------------------------------------------
# chave = nome do módulo importável | valor = nome do pacote no PyPI
PACOTES = {
    "rembg": "rembg",
    "onnxruntime": "onnxruntime",
    "PIL": "Pillow",
}


def garantir_bibliotecas() -> None:
    """Importa cada módulo; se faltar, instala o pacote correspondente via pip."""
    faltando = []
    for modulo, pacote in PACOTES.items():
        try:
            importlib.import_module(modulo)
        except ImportError:
            faltando.append(pacote)

    if faltando:
        print(f"[SETUP] Instalando bibliotecas: {', '.join(faltando)} ...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *faltando]
        )
        print("[SETUP] Instalação concluída.")
    else:
        print("[SETUP] Todas as bibliotecas já estão instaladas.")


garantir_bibliotecas()

# Imports somente após garantir que tudo está instalado
from PIL import Image, ImageFilter  # noqa: E402
from rembg import new_session, remove  # noqa: E402

# ----------------------------------------------------------------------
# Configurações
# ----------------------------------------------------------------------
PASTA_ATUAL = Path(__file__).resolve().parent
PASTA_SAIDA = PASTA_ATUAL / "icones_128"
TAMANHO_ICONE = 128          # tamanho final do ícone (128x128)
MARGEM = 4                   # margem interna para não cortar as bordas
AREA_UTIL = TAMANHO_ICONE - 2 * MARGEM   # o personagem cabe em 120x120
MODELO_REMBG = "u2net"       # modelo padrão do rembg


def processar_imagem(caminho: Path, sessao) -> None:
    """Executa os passos 2 a 6 em uma única imagem."""
    img = Image.open(caminho).convert("RGBA")

    # Passo 2: remover completamente o fundo, deixando-o transparente
    sem_fundo = remove(img, session=sessao)

    # Passo 3: auto-crop ao redor da área visível do personagem (getbbox)
    bbox = sem_fundo.getbbox()
    if bbox is None:
        print(f"[AVISO] {caminho.name}: nenhuma área visível após remover o fundo; "
              "gerando ícone vazio.")
        vazio = Image.new("RGBA", (TAMANHO_ICONE, TAMANHO_ICONE), (0, 0, 0, 0))
        vazio.save(PASTA_SAIDA / caminho.name, format="PNG")
        return
    recortada = sem_fundo.crop(bbox)

    # Passo 4: redimensionar mantendo a proporção original (Lanczos),
    # cabendo dentro do quadro útil de 120x120 (128 - 2*4 de margem)
    largura, altura = recortada.size
    escala = min(AREA_UTIL / largura, AREA_UTIL / altura)
    nova_largura = max(1, round(largura * escala))
    nova_altura = max(1, round(altura * escala))
    redimensionada = recortada.resize(
        (nova_largura, nova_altura), Image.Resampling.LANCZOS
    )

    # Passo 5: centralizar em canvas transparente exato de 128x128
    icone = Image.new("RGBA", (TAMANHO_ICONE, TAMANHO_ICONE), (0, 0, 0, 0))
    pos_x = (TAMANHO_ICONE - nova_largura) // 2
    pos_y = (TAMANHO_ICONE - nova_altura) // 2
    icone.alpha_composite(redimensionada, (pos_x, pos_y))

    # ...e aplicar um filtro leve de nitidez para definir os detalhes
    icone = icone.filter(
        ImageFilter.UnsharpMask(radius=1, percent=60, threshold=2)
    )

    # Passo 6: salvar em .png (preserva transparência) com o mesmo nome
    destino = PASTA_SAIDA / caminho.name
    icone.save(destino, format="PNG")
    print(f"[OK] {caminho.name} -> icones_128/{destino.name} "
          f"(personagem {nova_largura}x{nova_altura} centralizado em 128x128)")


def main() -> None:
    imagens = sorted(PASTA_ATUAL.glob("*.png"))
    if not imagens:
        print("Nenhuma imagem .png encontrada na pasta atual.")
        return

    PASTA_SAIDA.mkdir(exist_ok=True)

    # Carrega o modelo uma única vez (na 1ª execução o rembg baixa o modelo)
    print(f"[INFO] Carregando modelo '{MODELO_REMBG}' do rembg "
          "(na primeira execução ele será baixado automaticamente)...")
    sessao = new_session(MODELO_REMBG)

    total = len(imagens)
    print(f"[INFO] {total} imagem(ns) .png para processar.\n")
    for indice, caminho in enumerate(imagens, start=1):
        print(f"({indice}/{total}) Processando {caminho.name} ...")
        processar_imagem(caminho, sessao)

    print(f"\nConcluído! {total} ícone(s) 128x128 salvo(s) em: {PASTA_SAIDA}")


if __name__ == "__main__":
    main()
