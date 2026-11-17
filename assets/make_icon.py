"""
Gera o icone do aplicativo (assets/app.ico) a partir de um PNG.

O `assets/app.ico` atual foi feito a mao (pelo usuario) e NAO precisa
deste script. Use o script so para gerar um .ico a partir de um PNG
novo:

    python assets/make_icon.py [fonte.png]

Ex.:  python assets/make_icon.py assets/login.png
"""
import os
import sys

from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = (sys.argv[1] if len(sys.argv) > 1
         else os.path.join(RAIZ, "assets", "app.png"))
DESTINO = os.path.join(RAIZ, "assets", "app.ico")

if not os.path.exists(FONTE):
    raise SystemExit(f"a fonte nao existe: {FONTE}")

TAMANHOS = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64),
             (128, 128), (256, 256)]

img = Image.open(FONTE).convert("RGBA")
# recorta a parte visivel (a arte vem com borda transparente)
bbox = img.getbbox()
if bbox:
    img = img.crop(bbox)
# quadrado, centralizado
m = max(img.size)
quadrado = Image.new("RGBA", (m, m), (0, 0, 0, 0))
quadrado.alpha_composite(img, ((m - img.width) // 2, (m - img.height) // 2))

quadrado.save(DESTINO, format="ICO", sizes=TAMANHOS)
print(f"[OK] {DESTINO} ({os.path.getsize(DESTINO)} bytes) "
      f"tamanhos: {TAMANHOS}")
