# -*- coding: utf-8 -*-
"""
Gera o icone de perfil (128x128) de um personagem a partir do retrato
grande em `assets/personagens/<nome>.png`.

O processo e o mesmo dos 25 icones do app:
    recorte da CABECA -> rembg (tira o fundo) -> auto-crop -> 128x128
    -> clareamento automatico (as artes escuras do jogo ficavam "apagadas")
    -> nitidez.

    assets\\perfil\\.venv\\Scripts\\python.exe assets\\perfil\\gerar_icone.py rey

Obs: rode com o Python do venv (o `rembg` so existe la).
"""
import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from rembg import new_session, remove

RAIZ = Path(__file__).resolve().parent.parent.parent
ORIGEM = RAIZ / "assets" / "personagens"
DESTINO = Path(__file__).resolve().parent

TAMANHO = 128
MARGEM = 6
AREA_UTIL = TAMANHO - 2 * MARGEM
MODELO = "u2net"

# (x1, y1, x2, y2) em porcentagem do retrato: a CABECA de cada personagem.
# As artes temen posicoes diferentes (o retrato e a arte inteira do jogo),
# entao a caixa precisa ser ajustada personagem por personagem.
RECORTES = {
    "rey":      (0.29, 0.00, 0.60, 0.30),
    "sieghart": (0.20, 0.02, 0.47, 0.33),
    "ryan":     (0.52, 0.05, 0.80, 0.40),
    "lupus":    (0.28, 0.00, 0.48, 0.28),
}

# clareamento extra por personagem (a arte e muito escura)
BRILHO = {
    "sieghart": 1.55,
}


def clarear(imagem, fator=1.0, alvo=132):
    """Levanta as sombras (gamma) e devolve o brilho medio para `alvo`."""
    rgb = imagem.convert("RGB")
    alfa = imagem.getchannel("A")

    # 1) gamma: levanta as partes escuras sem estourar as claras
    rgb = ImageOps.autocontrast(rgb, cutoff=1)
    gamma = 0.72
    tabela = [min(255, int(255 * ((i / 255) ** gamma))) for i in range(256)]
    rgb = rgb.point(tabela * 3)

    # 2) brilho: mede a luminancia media do que esta visivel
    pixels = list(rgb.getdata())
    visiveis = [pixels[i] for i in range(len(pixels))
                if alfa.getpixel((i % imagem.width, i // imagem.width)) > 32]
    if visiveis:
        media = sum(sum(p) / 3 for p in visiveis) / len(visiveis)
        if media < alvo:
            rgb = ImageEnhance.Brightness(rgb).enhance(
                min(2.2, (alvo / max(media, 1)) ** 0.85))

    rgb = ImageEnhance.Contrast(rgb).enhance(1.08)
    if fator != 1.0:
        rgb = ImageEnhance.Brightness(rgb).enhance(fator)
    return rgb.convert("RGBA")


def gerar(nome, sessao=None):
    if sessao is None:
        print("[INFO] Carregando o modelo do rembg...")
        sessao = new_session(MODELO)

    retrato = Image.open(ORIGEM / f"{nome}.png").convert("RGBA")
    largura, altura = retrato.size
    x1, y1, x2, y2 = RECORTES.get(nome, (0.25, 0.00, 0.75, 0.45))
    caixa = (int(largura * x1), int(altura * y1),
             int(largura * x2), int(altura * y2))
    cabeca = retrato.crop(caixa)

    sem_fundo = remove(cabeca, session=sessao)
    bbox = sem_fundo.getbbox()
    if bbox is None:
        raise SystemExit(f"[ERRO] {nome}: nada visivel depois do rembg")
    recortada = sem_fundo.crop(bbox)

    escala = min(AREA_UTIL / recortada.width, AREA_UTIL / recortada.height)
    nova_l = max(1, round(recortada.width * escala))
    nova_a = max(1, round(recortada.height * escala))
    corpo = recortada.resize((nova_l, nova_a), Image.Resampling.LANCZOS)

    corpo = clarear(corpo, fator=BRILHO.get(nome, 1.0))

    icone = Image.new("RGBA", (TAMANHO, TAMANHO), (0, 0, 0, 0))
    icone.alpha_composite(corpo, ((TAMANHO - nova_l) // 2, (TAMANHO - nova_a) // 2))
    icone = icone.filter(ImageFilter.UnsharpMask(radius=1.2, percent=70,
                                                  threshold=2))

    destino = DESTINO / f"{nome}_icon.png"
    icone.save(destino, format="PNG")
    print(f"[OK] {destino.name} ({nova_l}x{nova_a} em {TAMANHO}x{TAMANHO})")


if __name__ == "__main__":
    alvos = sys.argv[1:] or list(RECORTES)
    sessao = new_session(MODELO)
    for nome in alvos:
        gerar(nome, sessao)
