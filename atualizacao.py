# -*- coding: utf-8 -*-
"""
Atualizacao automatica.

Toda vez que o programa abre, ele confere no GitHub se tem commit novo
e, se tiver, atualiza sozinho e abre de novo.

Duas situacoes (o app se adapta):

1. **Instalado do repositorio** (tem a pasta `.git` ao lado): ele roda
   `git pull` e atualiza as dependencias. Como o codigo ja esta carregado
   na memoria, so precisa reiniciar.

2. **Instalado do .exe / instalador** (sem `.git`): ele baixa a ultima
   Release do GitHub, troca os arquivos e abre de novo. Como o .exe esta
   rodando (o Windows nao deixa trocar um arquivo em uso), a troca e feita
   por um script auxiliar depois que o app fecha.

Nada aqui trava o programa: se a internet cair, o GitHub estiver fora do
ar ou der qualquer erro, o app abre normalmente.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import zipfile

REPOSITORIO = "guitador123/caminho-da-maestria"
BRANCH = "main"
API = f"https://api.github.com/repos/{REPOSITORIO}"
ARQUIVO_VERSAO = os.path.join("assets", "versao.txt")
TIMEOUT = 10          # segundos de espera pela rede
NOME_ASSET = "Caminho da Maestria"   # prefixo do .zip da Release


# ------------------------------------------------------------- ferramentas
LOG = os.path.join(os.environ.get("LOCALAPPDATA",
                                    os.path.expanduser("~")),
                     "Caminho da Maestria", "log_atualizacao.log")


def _registrar(texto):
    """Deixa um registro do que a atualizacao fez (para depurar)."""
    try:
        from datetime import datetime
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as arquivo:
            arquivo.write(f"{datetime.now():%d/%m %H:%M:%S} | {texto}\n")
    except Exception:
        pass


def _app_dir():
    """A pasta do programa (no .exe, a pasta do executavel)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _caminho_versao():
    """O arquivo com o commit em que esta versao foi montada."""
    candidatos = []
    if getattr(sys, "frozen", False):
        # no .exe, a pasta _internal fica IRMA do executavel
        candidatos.append(os.path.join(os.path.dirname(sys.executable),
                                       "_internal", ARQUIVO_VERSAO))
    candidatos.append(os.path.join(_app_dir(), "_internal", ARQUIVO_VERSAO))
    candidatos.append(os.path.join(_app_dir(), ARQUIVO_VERSAO))
    for caminho in candidatos:
        if os.path.exists(caminho):
            return caminho
    return candidatos[-1]


def versao_local():
    """O commit com que esta versao foi montada.

    - rodando de um clone do git: e o HEAD local (exatamente o que esta
      rodando);
    - rodando do .exe: e o commit gravado em `assets/versao.txt` na hora
      do build.
    """
    if tem_git():
        try:
            return _git("rev-parse", "HEAD").stdout.strip()[:40]
        except Exception:
            return ""
    try:
        with open(_caminho_versao(), "r", encoding="utf-8") as arquivo:
            return arquivo.read().strip().splitlines()[0].strip()[:40]
    except Exception:
        return ""


def _pedir(url, destino=None):
    """GET na API do GitHub (ou baixa o arquivo)."""
    requisicao = urllib.request.Request(
        url, headers={"User-Agent": "Caminho-da-Maestria",
                      "Accept": "application/vnd.github+json"})
    if destino:
        with urllib.request.urlopen(requisicao, timeout=TIMEOUT) as resposta:
            with open(destino, "wb") as arquivo:
                shutil.copyfileobj(resposta, arquivo)
        return True
    with urllib.request.urlopen(requisicao, timeout=TIMEOUT) as resposta:
        return json.loads(resposta.read().decode("utf-8"))


def commit_remoto():
    """(sha, mensagem) do ultimo commit da branch principal."""
    dados = _pedir(f"{API}/commits/{BRANCH}")
    return (dados.get("sha", "")[:40],
            (dados.get("commit", {}).get("message", "") or "").split("\n")[0])


GIT_PADRAO = [
    r"C:\Program Files\Git\cmd\git.exe",
    r"C:\Program Files (x86)\Git\cmd\git.exe",
    os.path.join(os.environ.get("LOCALAPPDATA", ""),
                 "Programs", "Git", "cmd", "git.exe"),
]


def caminho_git():
    """O executavel do git (no PATH ou nos caminhos padrao)."""
    achado = shutil.which("git")
    if achado:
        return achado
    for caminho in GIT_PADRAO:
        if caminho and os.path.exists(caminho):
            return caminho
    return "git"


def _git(*argumentos):
    """Roda um comando do git na pasta do programa."""
    return subprocess.run([caminho_git()] + list(argumentos), cwd=_app_dir(),
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=60)


def tem_git():
    """O programa esta rodando de dentro de um clone do git?"""
    return os.path.isdir(os.path.join(_app_dir(), ".git"))


# --------------------------------------------------------------- atualizar
def _atualizar_com_git():
    """git pull + dependencias (o app esta num clone)."""
    pasta = _app_dir()
    resultado = subprocess.run([caminho_git(), "pull", "--ff-only"], cwd=pasta,
                               capture_output=True, text=True,
                               encoding="utf-8", errors="replace",
                               timeout=180)
    if resultado.returncode != 0:
        return False
    # atualiza as dependencias (se houver um venv)
    python = os.path.join(pasta, ".venv", "Scripts", "python.exe")
    if os.path.exists(python) and os.path.exists(
            os.path.join(pasta, "requirements.txt")):
        subprocess.run([python, "-m", "pip", "install", "-r",
                        "requirements.txt", "--quiet"], cwd=pasta,
                       capture_output=True, timeout=900)
    return True


def _sha_da_release(tag):
    """O commit de uma release, pelo nome da tag (v2026.11.17-9008aef)."""
    parte = (tag or "").rsplit("-", 1)[-1].strip()
    if parte and all(c in "0123456789abcdefABCDEF" for c in parte) \
            and 7 <= len(parte) <= 40:
        return parte.lower()
    return ""


def _ultima_release():
    """(url_do_zip, sha_do_commit) da release mais recente."""
    dados = _pedir(f"{API}/releases/latest")
    url = ""
    for asset in dados.get("assets", []):
        nome = asset.get("name", "")
        # o GitHub troca espaco por ponto no nome do asset
        # ("Caminho.da.Maestria.zip"), entao comparamos sem pontuacao
        limpo = nome.lower().replace(".", " ").replace("_", " ")
        if nome.lower().endswith(".zip") and "maestria" in limpo:
            url = asset.get("browser_download_url")
            break
    return url, _sha_da_release(dados.get("tag_name", ""))


def _versao_da_release():
    """A versao (sha) da ultima release, ou "" se nao houver."""
    try:
        dados = _pedir(f"{API}/releases/latest")
        return _sha_da_release(dados.get("tag_name", ""))
    except Exception:
        return ""


def _atualizar_com_release():
    """Baixa a ultima Release e troca os arquivos (depois de fechar)."""
    url, _sha = _ultima_release()
    if not url:
        return False
    temporario = tempfile.mkdtemp(prefix="cm_atualizacao_")
    try:
        zip_arquivo = os.path.join(temporario, "programa.zip")
        _pedir(url, zip_arquivo)
        destino = os.path.join(temporario, "programa")
        with zipfile.ZipFile(zip_arquivo) as pacote:
            pacote.extractall(destino)
        # a release pode ter uma pasta dentro do zip
        if not os.path.exists(os.path.join(destino, "Caminho da Maestria.exe")):
            for item in os.listdir(destino):
                sub = os.path.join(destino, item)
                if os.path.isdir(sub) and os.path.exists(
                        os.path.join(sub, "Caminho da Maestria.exe")):
                    destino = sub
                    break
        if not os.path.exists(os.path.join(destino, "Caminho da Maestria.exe")):
            _registrar("o zip da release nao tem o executavel")
            return False
        _registrar(f"release baixada: {url}")
        _agendar_troca(destino)
        _registrar("troca agendada; o programa vai abrir de novo")
        # NAO apaga a pasta temporaria agora: o auxiliar precisa dela
        # para copiar os arquivos (e ele apaga no final)
        return True
    except Exception as erro:
        _registrar(f"ERRO ao baixar a release: {erro!r}")
        shutil.rmtree(temporario, ignore_errors=True)
        return False


def _agendar_troca(novos):
    """Cria o script que troca os arquivos (depois que o app fechar)."""
    destino = _app_dir()
    auxiliar = os.path.join(tempfile.gettempdir(), "cm_trocar_arquivos.cmd")
    with open(auxiliar, "w", encoding="utf-8", newline="\r\n") as arquivo:
        arquivo.write(
            "@echo off\r\n"
            "rem troca os arquivos do programa e abre de novo\r\n"
            "ping 127.0.0.1 -n 4 >nul\r\n"
            f'robocopy "{novos}" "{destino}" /MIR /XF login_prefs.json '
            "/NFL /NDL /NJH /NJS /NP >nul\r\n"
            f'start "" "{os.path.join(destino, "Caminho da Maestria.exe")}"\r\n'
            f'rmdir /s /q "{novos}" >nul 2>&1\r\n'
            f'del /q "{auxiliar}" >nul 2>&1\r\n')
    subprocess.Popen(["cmd", "/c", auxiliar], creationflags=0x08000000)


def aplicar_atualizacao():
    """Aplica a atualizacao. Devolve True se deu certo."""
    if tem_git():
        return _atualizar_com_git()
    return _atualizar_com_release()


def reiniciar():
    """Abre o programa de novo e fecha este."""
    if getattr(sys, "frozen", False):
        comando = [sys.executable]
    else:
        comando = [sys.executable,
                   os.path.join(_app_dir(), "app_grandchase.py")]
    try:
        subprocess.Popen(comando, cwd=_app_dir(),
                         creationflags=0x08000000 if os.name == "nt" else 0)
    except Exception:
        pass
    os._exit(0)


# ------------------------------------------------------------------ splash
def _splash(texto):
    """Uma janelinha mostrando o que esta acontecendo (some depois)."""
    try:
        import tkinter as tk
        janela = tk.Tk()
        janela.title("Caminho da Maestria")
        janela.configure(bg="#16112b")
        janela.resizable(False, False)
        tk.Label(janela, text=texto, bg="#16112b", fg="#f2f0fa",
                 font=("Segoe UI", 11)).pack(padx=26, pady=18)
        janela.update()
        janela.attributes("-topmost", True)
        return janela
    except Exception:
        return None


def verificar_e_atualizar(mostrar=True):
    """Confere o GitHub e atualiza se precisar. Devolve True se atualizou."""
    splash = _splash("Verificando atualizacoes...") if mostrar else None
    try:
        sha_local = versao_local()
        if tem_git():
            # num clone: compara com o commit do GitHub
            sha_remoto, mensagem = commit_remoto()
            if not sha_remoto:
                return False
            if sha_local and sha_local[:40] == sha_remoto[:40]:
                return False   # ja esta na ultima
        else:
            # no .exe: compara com a ULTIMA RELEASE (assim o app nao fica
            # tentando atualizar sem ter release nova)
            sha_release = _versao_da_release()
            if not sha_release:
                return False
            if sha_local and sha_local.lower().startswith(sha_release):
                return False   # ja esta na ultima release
            mensagem = "versao nova disponivel"
    except Exception:
        return False      # sem internet/GitHub: segue normal
    finally:
        if splash is not None:
            try:
                splash.destroy()
            except Exception:
                pass

    # tem coisa nova: atualiza
    if splash is not None:
        try:
            splash.configure(bg="#16112b")
            splash.children[0].configure(
                text=f"Nova versao disponivel!\n{mensagem}\nAtualizando...")
            splash.update()
        except Exception:
            pass

    try:
        deu_certo = aplicar_atualizacao()
    except Exception:
        deu_certo = False

    if deu_certo:
        if splash is not None:
            try:
                splash.destroy()
            except Exception:
                pass
        if tem_git():
            reiniciar()          # a troca ja foi feita (git pull)
        else:
            reiniciar()          # o auxiliar troca e abre de novo
    return deu_certo


def checar_em_segundo_plano(callback):
    """Roda a verificacao numa thread (para nao travar a abertura)."""
    def alvo():
        try:
            verificar_e_atualizar(mostrar=False)
        except Exception:
            pass
        try:
            callback()
        except Exception:
            pass

    thread = threading.Thread(target=alvo, daemon=True)
    thread.start()
    return thread
