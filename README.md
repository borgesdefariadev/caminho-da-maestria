# Caminho da Maestria

Gerenciador de personagens, equipamentos e progresso semanal do **Grand
Chase**. Roda no Windows (desktop), com login no Supabase.

![Caminho da Maestria](assets/background.jpg)

---

## Instalar no PC (uma vez)

### Opção 1 - pelo instalador (pronto, sem Python)

Baixe o `Caminho da Maestria - Instalador.zip`, descompacte **inteiro** e
clique em **`Instalar.cmd`**.

- instala em `%LOCALAPPDATA%\Caminho da Maestria` (não pede senha de admin);
- cria os atalhos (Área de Trabalho e Menu Iniciar);
- **não precisa de Python**: o instalador já traz tudo;
- para desinstalar: Menu Iniciar > Caminho da Maestria > Desinstalar.

### Opção 2 - a partir do código (para atualizar sem instalador)

1. instale o [Python 3.11+](https://www.python.org/downloads/) (marque
   **"Add python.exe to PATH"**) e o [Git](https://git-scm.com/download/win);
2. clone este repositório:

   ```bat
   git clone https://github.com/guitador123/caminho-da-maestria.git
   cd caminho-da-maestria
   ```

3. clique duas vezes em **`iniciar.bat`**.

O `iniciar.bat` cria o ambiente `.venv`, instala as dependências e abre o
programa. Nas próximas vezes, use o **`atualizar.bat`**: ele baixa a
versão nova (`git pull`), atualiza as dependências e abre o programa.

> É esse o jeito **sem gerar instalador toda hora**: você so faz
> `git push` no seu PC e, no PC da guilda, dois cliques no
> `atualizar.bat`.

---

## Como publicar uma versão nova (para você, no seu PC)

```bash
git add .
git commit -m "o que mudou"
git push
```

Pronto: os PCs da guilda pegam a versão nova no próximo `atualizar.bat`.

> É o jeito **sem instalador**: você publica no GitHub e, lá na guilda,
> é só dar dois cliques no `atualizar.bat` (ele faz o `git pull` e abre
> o programa).

---

## Rodar os testes

A suíte completa (precisa de uma conta de teste no Supabase):

```bash
python teste_perfil.py
python teste_doacao.py
python teste_integracao.py
python teste_zerar_semanais.py
...
```

A conta de teste é `teste@teste.com` / `testeteste` (definida no padrão
de cada teste; pode passar e-mail e senha como argumento).

---

## Estrutura

| Arquivo | O que é |
|---|---|
| `app_grandchase.py` | tela principal (cards, filtros, perfil, hero) |
| `card_personagem.py` | o card de cada personagem (com as regras de cor) |
| `janela_personagem.py` | tela de edição |
| `janela_perfil.py` | janela "Minha conta" |
| `janela_doacao.py` | painel lateral de doação (Pix/QR) |
| `janela_nivel.py` | edição do Nível do Chaser |
| `janela_missao_rapida.py` | painel de Missão Rápida |
| `tema_visual.py` / `tema_login.py` | cores, layout e cenário (PIL) |
| `supabase_db.py` | acesso ao banco (tabelas, upsert, RLS) |
| `auth.py` | login no Supabase |
| `pix_pagamento.py` | chave Pix, payload e QR Code |
| `opcoes.py` | as opções do Excel (listas de itens) |
| `sql/` | scripts de banco (rodar no SQL Editor do Supabase) |
| `assets/` | imagens (fundo, retratos, ícones de perfil, de Chaser, QR do Pix) |
| `gerar_instalador.py` | monta o instalador (revisando o bundle por segredos) |
| `auditoria_instalador.py` | revisa o `.zip` do instalador antes de distribuir |
| `HANDOFF.md` | o histórico completo do projeto (leia antes de mexer) |

---

## Segurança

- O repositório **não** tem nenhuma chave de serviço do banco: a única
  chave no código é a **publishable key** do Supabase (chave pública,
  feita para ficar dentro do aplicativo).
- A `service_role key` (necessária só para a limpeza semanal local) fica
  **fora** do repositório, em `%LOCALAPPDATA%\Caminho da Maestria\service_role.txt`
  (veja `LEIA-ME-zerar-semanal.txt`).
- `gerar_instalador.py` e `auditoria_instalador.py` **abortam** se
  encontrarem `service_role`, `sb_secret_`, um JWT de serviço, uma chave
  privada, uma senha ou um e-mail pessoal dentro do pacote.

---

## Limpeza semanal das missões (no servidor)

Todo **quarta-feira às 03h (Brasília)** o `pg_cron` do Supabase zera as
missões semanais de **todas** as contas. O script SQL é o
`sql/zerar_semanais_pg_cron.sql` (rode no SQL Editor do Supabase). Ver
`LEIA-ME-zerar-semanal.txt`.
