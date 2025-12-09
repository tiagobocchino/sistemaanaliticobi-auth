@echo off
echo ================================================================================
echo INICIAR SISTEMA LIMPO - ANALYTICS PLATFORM
echo ================================================================================
echo.

REM Verificar se Python esta disponivel
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo      ERRO: Python nao encontrado!
    pause
    exit /b 1
)
echo      OK - Python instalado

REM Verificar se Node esta disponivel
echo.
echo [2/4] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo      ERRO: Node.js nao encontrado!
    pause
    exit /b 1
)
echo      OK - Node.js instalado

REM Verificar arquivo .env
echo.
echo [3/4] Verificando configuracoes...
if not exist .env (
    echo      AVISO: Arquivo .env nao encontrado!
    echo      Copie .env.example para .env e configure
    pause
    exit /b 1
)
echo      OK - Arquivo .env encontrado

echo.
echo [4/4] Iniciando sistema...
echo.
echo ================================================================================
echo CREDENCIAIS PARA LOGIN:
echo ================================================================================
echo   Email:  tiago.bocchino@4pcapital.com.br
echo   Senha:  Admin123!@#
echo ================================================================================
echo.
echo ABRINDO 2 TERMINAIS:
echo   Terminal 1: Backend (Python)
echo   Terminal 2: Frontend (React)
echo.
echo Aguarde os servidores iniciarem...
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo ================================================================================
echo.

REM Abrir terminal 1 - Backend
start "Backend - Analytics Platform" cmd /k "python main.py"

REM Aguardar 3 segundos
timeout /t 3 /nobreak >nul

REM Abrir terminal 2 - Frontend
start "Frontend - Analytics Platform" cmd /k "cd frontend && npm run dev"

echo.
echo ================================================================================
echo SISTEMA INICIADO!
echo ================================================================================
echo.
echo   Backend API:    http://localhost:8000
echo   Frontend App:   http://localhost:5173
echo   Documentacao:   http://localhost:8000/docs
echo.
echo ACESSE: http://localhost:5173/login
echo.
echo ================================================================================
