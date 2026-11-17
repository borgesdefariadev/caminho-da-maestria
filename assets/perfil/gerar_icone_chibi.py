# -*- coding: utf-8 -*-
"""
Gera o icone de perfil (128x128) a partir de uma arte **chibi com moldura**
(estilo dos 25 icones do app).

Exemplo:
    python assets/perfil/gerar_icone_chibi.py assets/perfil/SIEGHART.png sieghart

O que ele faz:
  1. tira a moldura (a borda clara em volta do desenho);
  2. separa o personagem do painel de fundo (GrabCut) \u2014 o `rembg` nao
     funciona nesse tipo de arte (ele apaga o cabelo preto e fica so o
     colete);
  3. recorta o personagem, encaixa em 128x128 com margem;
  4. **clareia** (o cabelo preto ficava "apagado") e da nitidez.

Precisa do `opencv-python-headless`:
    python -m pip install opencv-python-headless
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

RAIZ = Path(__file__).resolve().parent.parent.parent
DESTINO = Path(__file__).resolve().parent

TAMANHO = 128
MARGEM = 6
AREA_UTIL = TAMANHO - 2 * MARGEM

# clareamento (gamma): < 1 levanta as sombras (o cabelo preto)
GAMMA = 0.62
CONTRASTE = 1.06


def tirar_moldura(imagem):
    """Recorta a moldura clara em volta do desenho.

    A moldura e um conjunto de linhas claras (branco/prata) separadas por
    falhas escuras. Varremos a linha do meio de cada lado, de fora para
    dentro, e paramos na ultima linha clara antes de uma falha grande.
    """
    px = imagem.convert("RGB").load()
    largura, altura = imagem.size

    def claro(x, y):
        r, g, b = px[x, y]
        return (r + g + b) / 3 > 128 and max(r, g, b) - min(r, g, b) < 26

    y_meio = altura // 2
    x_meio = largura // 2

    def varre(pixels):
        """pixels: lista de (indice, x, y) de fora para dentro."""
        ultimo = None
        falha = 0
        for indice, x, y in pixels:
            if claro(x, y):
                ultimo = indice
                falha = 0
            else:
                falha += 1
                if falha >= 4 and ultimo is not None:
                    break
        return ultimo

    esq = varre([(i, i, y_meio) for i in range(min(26, largura // 2))])
    dir_ = varre([(i, largura - 1 - i, y_meio)
                  for i in range(min(26, largura // 2))])
    topo = varre([(i, x_meio, i) for i in range(min(26, altura // 2))])
    base = varre([(i, x_meio, altura - 1 - i)
                  for i in range(min(26, altura // 2))])

    if None in (esq, dir_, topo, base):
        return imagem  # nao ha moldura
    print(f"[INFO] moldura: esq={esq} dir={dir_} topo={topo} base={base}")
    recorte = imagem.crop((esq + 1, topo + 1,
                           largura - 1 - dir_, altura - 1 - base))
    # a faixa de painel que sobra embaixo do personagem (a borda dele fica
    # como uma linha fina feia no icone)
    if recorte.height > 20:
        recorte = recorte.crop((0, 0, recorte.width, int(recorte.height * 0.85)))
    return recorte


def separar_personagem(recorte):
    """Mascara do personagem (GrabCut) sobre o painel de fundo."""
    largura, altura = recorte.size
    fator = 6
    grande = recorte.resize((largura * fator, altura * fator), Image.LANCZOS)
    arr = np.array(grande)[:, :, ::-1].copy()          # RGB -> BGR
    alt, larg = arr.shape[:2]

    mascara = np.full((alt, larg), cv2.GC_PR_BGD, np.uint8)
    # fundo COM CERTEZA: as faixas cinzas do painel (ficam nas bordas)
    mascara[:, :int(larg * 0.03)] = cv2.GC_BGD
    mascara[:, int(larg * 0.93):] = cv2.GC_BGD
    mascara[int(alt * 0.85):, :] = cv2.GC_BGD
    # personagem PROVAVEL: a maior parte da arte
    mascara[:, int(larg * 0.03):int(larg * 0.93)] = cv2.GC_PR_FGD
    mascara[:int(alt * 0.90), int(larg * 0.03):int(larg * 0.93)] = cv2.GC_PR_FGD
    # personagem COM CERTEZA: o rosto (pele) e o colete
    mascara[int(alt * 0.38):int(alt * 0.68),
            int(larg * 0.28):int(larg * 0.62)] = cv2.GC_FGD
    mascara[int(alt * 0.70):int(alt * 0.86),
            int(larg * 0.15):int(larg * 0.80)] = cv2.GC_FGD

    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    cv2.grabCut(arr, mascara, None, bgd, fgd, 10, cv2.GC_INIT_WITH_MASK)

    final = np.where((mascara == cv2.GC_FGD) | (mascara == cv2.GC_PR_FGD),
                     255, 0).astype("uint8")

    # abre a mascara (tira as faixas finas do painel que sobraram)
    nucleo = np.ones((9, 9), np.uint8)
    final = cv2.morphologyEx(final, cv2.MORPH_OPEN, nucleo)
    final = cv2.dilate(final, nucleo, iterations=1)

    # so o maior objeto + fecha os furos
    n, rotulos, estatisticas, _ = cv2.connectedComponentsWithStats(final, 8)
    if n > 1:
        maior = 1 + int(np.argmax(estatisticas[1:, cv2.CC_STAT_AREA]))
        final = np.where(rotulos == maior, 255, 0).astype("uint8")
    contornos, _ = cv2.findContours(final, cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_SIMPLE)
    preenchido = np.zeros_like(final)
    cv2.drawContours(preenchido, contornos, -1, 255, cv2.FILLED)

    alfa = Image.fromarray(preenchido).resize(recorte.size, Image.LANCZOS)
    personagem = recorte.convert("RGBA")
    personagem.putalpha(alfa)
    return personagem


def clarear(imagem):
    """Levanta as sombras (gamma) sem estourar as partes claras.

    O alpha e preservado (a tabela do alpha fica intacta) — se nao, o
    fundo transparente viraria preto.
    """
    tabela = [min(255, int(255 * ((i / 255) ** GAMMA))) for i in range(256)]
    tabela = tabela * 3 + list(range(256))   # R, G, B e alpha
    imagem = imagem.point(tabela)
    rgb = ImageEnhance.Contrast(imagem.convert("RGB")).enhance(CONTRASTE)
    rgb.putalpha(imagem.getchannel("A"))
    return rgb


def gerar(origem, nome_destino):
    arte = Image.open(origem).convert("RGB")
    print(f"[INFO] {Path(origem).name} {arte.size}")

    sem_moldura = tirar_moldura(arte)
    print(f"[INFO] sem a moldura: {sem_moldura.size}")

    personagem = separar_personagem(sem_moldura)

    bbox = personagem.getbbox()
    if bbox is None:
        raise SystemExit("[ERRO] nao achou o personagem")
    personagem = personagem.crop(bbox)

    escala = min(AREA_UTIL / personagem.width, AREA_UTIL / personagem.height)
    nova_l = max(1, round(personagem.width * escala))
    nova_a = max(1, round(personagem.height * escala))
    personagem = personagem.resize((nova_l, nova_a), Image.LANCZOS)

    personagem = clarear(personagem)
    personagem = personagem.filter(
        ImageFilter.UnsharpMask(radius=1.1, percent=60, threshold=2))

    icone = Image.new("RGBA", (TAMANHO, TAMANHO), (0, 0, 0, 0))
    icone.alpha_composite(personagem,
                          ((TAMANHO - nova_l) // 2, (TAMANHO - nova_a) // 2))

    destino = DESTINO / f"{nome_destino}_icon.png"
    icone.save(destino, format="PNG")
    print(f"[OK] {destino} ({nova_l}x{nova_a} em {TAMANHO}x{TAMANHO})")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit("uso: python gerar_icone_chibi.py <origem.png> <nome>")
    gerar(sys.argv[1], sys.argv[2])
