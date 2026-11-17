@echo off
setlocal
chcp 65001 >nul 2>&1
title Caminho da Maestria - instalar

REM ============================================================
REM  Instala o que o programa precisa (uma vez so) e roda.
REM  Nao precisa de Python instalado? Este script usa o Python
REM  que estiver no PATH. Se nao tiver, baixe em python.org
REM  (marque "Add python.exe to PATH").
REM ============================================================

cd /d "%~dp0"

echo.
echo  =====================================================
echo   Caminho da Maestria - preparar o PC
echo  =====================================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo  ERRO: nao achei o Python.
    echo.
    echo  Baixe em https://www.python.org/downloads/ e marque
    echo  a opcao "Add python.exe to PATH" na instalacao.
    echo.
    pause
    exit /b 1
)

echo  [1/3] Criando o ambiente (.venv)...
if not exist ".venv" (
    python -m venv .venv
) else (
    echo       ja existe, reaproveitando.
)

echo  [2/3] Instalando as dependencias...
call ".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
call ".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo  ERRO ao instalar as dependencias.
    pause
    exit /b 1
)

echo  [3/3] Abrindo o programa...
echo.
call ".venv\Scripts\python.exe" app_grandchase.py %*
