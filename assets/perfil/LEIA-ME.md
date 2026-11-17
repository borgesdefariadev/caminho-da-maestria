# Fotos de perfil (25 personagens)

Esta pasta guarda as **25 fotos de perfil** do app. A foto do usuário **não é
livre**: ele escolhe **um dos 25 personagens** na tela "Minha conta" e usa a
imagem dele.

## Como nomear

O nome do arquivo é o nome do personagem, em **minúsculas**, com o sufixo
`_icon.png`:

```
elesis_icon.png
lire_icon.png
arme_icon.png
lass_icon.png
ryan_icon.png
ronan_icon.png
amy_icon.png
jin_icon.png
sieghart_icon.png
mari_icon.png
dio_icon.png
zero_icon.png
rey_icon.png
lupus_icon.png
lin_icon.png
azin_icon.png
holy_icon.png
edel_icon.png
veigas_icon.png
decane_icon.png
ai_icon.png
kallia_icon.png
uno_icon.png
iris_icon.png
ereb_icon.png
```

## Formato

- PNG (`.png`), quadrado (o app recorta o quadrado central);
- idealmente **96x96** ou maior (o app redimensiona para 128x128 e corta em
  círculo);
- fundo transparente combina melhor com o painel.

## Como colocar

Copie os 25 arquivos nesta pasta (`assets/perfil/`) e reinicie o app. Se um
personagem ainda não tiver a imagem, o botão dele aparece só com as iniciais.

O `.spec` do build já leva esta pasta para o `.exe`.

## Gerar um ícone a partir do retrato do personagem

O script `gerar_icone.py` tira o fundo (`rembg`), recorta a **cabeça**,
clareia (as artes do jogo são escuras) e salva em 128x128:

```
assets\perfil\.venv\Scripts\python.exe assets\perfil\gerar_icone.py rey
```

As caixas de recorte de cada personagem ficam no dicionário `RECORTES`
do próprio script. Use o Python do `.venv` (o `rembg` só existe lá).

## Gerar um ícone a partir de uma arte chibi com moldura

O script `gerar_icone_chibi.py` recebe uma arte **chibi com moldura**
(igual à que o app usa nos 25 ícones):

```
python assets\perfil\gerar_icone_chibi.py assets\perfil\SIEGHART.png sieghart
```

Ele tira a moldura, separa o personagem do painel de fundo (com o
**GrabCut** — o `rembg` apaga o cabelo preto e fica só o colete), recorta
em 128x128 e clareia.

Precisa do OpenCV:

```
python -m pip install opencv-python-headless
```

⚠ **No Windows o nome do arquivo ignora as maiúsculas:** `REY.png` e
`rey.png` são o **mesmo arquivo**. O destino tem que ser sempre o nome
completo (`rey_icon.png`), senão a fonte é sobrescrita.

