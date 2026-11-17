# Ícones do nível do Chaser

Esta pasta guarda o **ícone de fundo do perfil** (o que aparece à direita do
painel do perfil, no "Caminho da Maestria", com opacidade reduzida).

## Como nomear

O app procura o ícone pelo **nível do Chaser** da conta:

| Nível do Chaser | Arquivo |
|---|---|
| 1 até 99 | `cl1.png` |
| 100 até 199 | `cl100.png` |
| 200 até 299 | `cl200.png` |
| 300 até 399 | `cl300.png` |
| ... | `cl{n}.png`, onde `n` é o primeiro número de 100 do nível |

Exemplos: nível **57** → `cl1.png` · nível **140** → `cl100.png` ·
nível **201** → `cl200.png`.

## Formato

- PNG (`.png`), `.jpg` e `.webp` também funcionam;
- a imagem é **recortada no quadrado central** e redimensionada (150 px);
- se o arquivo não existir, o app simplesmente **não desenha** o ícone
  (sem erro).

## Como colocar

Copie o arquivo nesta pasta (`assets/chaser/`) e reinicie o app.
