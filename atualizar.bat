@echo off
setlocal
chcp 65001 >nul 2>&1
title Caminho da Maestria - atualizar

REM ============================================================
REM  ATUALIZA O PROGRAMA E ABRE.
REM
REM  E o que o PC da guilda usa: depois de clonar o repositorio
REM  uma vez, e so dar dois cliques neste arquivo que ele
REM  baixa a versao nova e abre.
REM ============================================================

cd /d "%~dp0"

echo.
echo  =====================================================
echo   Caminho da Maestria - atualizar
echo  =====================================================
echo.

where git >nul 2>&1
if errorlevel 1 (
    echo  ERRO: nao achei o Git.
    echo  Instale em https://git-scm.com/download/win
    echo  (deixe a opcao "Git from the command line" marcada).
    echo.
    pause
    exit /b 1
)

echo  [1/3] Baixando as novidades...
git pull --ff-only
if errorlevel 1 (
    echo.
    echo  Nao consegui atualizar (se for a primeira vez, rode o
    echo  "clonar" uma vez; se der conflito, faca um backup
    echo  da pasta .venv e apague-a para recriar).
    echo.
    pause
    exit /b 1
)

echo  [2/3] Conferindo as dependencias...
if not exist ".venv\Scripts\python.exe" (
    echo       ambiente novo, instalando...
    python -m venv .venv
    call ".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
) else (
    call ".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
)

echo  [3/3] Abrindo o programa...
echo.
call ".venv\Scripts\python.exe" app_grandchase.py %*
