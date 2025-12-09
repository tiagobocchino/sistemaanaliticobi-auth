@echo off
echo ================================================================================
echo LIMPEZA COMPLETA DO SISTEMA - ANALYTICS PLATFORM
echo ================================================================================
echo.

REM 1. Parar processos
echo [1/5] Parando processos Python e Node...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
echo      OK - Processos parados

REM 2. Limpar cache Python
echo.
echo [2/5] Limpando cache Python...
if exist __pycache__ (
    rmdir /S /Q __pycache__
)
if exist src\__pycache__ (
    rmdir /S /Q src\__pycache__
)
if exist src\auth\__pycache__ (
    rmdir /S /Q src\auth\__pycache__
)
if exist src\analyses\__pycache__ (
    rmdir /S /Q src\analyses\__pycache__
)
if exist src\users\__pycache__ (
    rmdir /S /Q src\users\__pycache__
)
if exist tests\__pycache__ (
    rmdir /S /Q tests\__pycache__
)
echo      OK - Cache Python limpo

REM 3. Limpar cache Node/Vite
echo.
echo [3/5] Limpando cache Node/Vite...
cd frontend
if exist node_modules\.vite (
    rmdir /S /Q node_modules\.vite
)
if exist dist (
    rmdir /S /Q dist
)
if exist .cache (
    rmdir /S /Q .cache
)
cd ..
echo      OK - Cache Node/Vite limpo

REM 4. Limpar logs
echo.
echo [4/5] Limpando arquivos temporarios...
if exist temp_login.json (
    del /F /Q temp_login.json
)
if exist test_reports (
    rmdir /S /Q test_reports
    mkdir test_reports
    echo. > test_reports\.gitignore
)
echo      OK - Arquivos temporarios limpos

REM 5. Resumo
echo.
echo [5/5] Limpeza concluida!
echo.
echo ================================================================================
echo CACHE LIMPO COM SUCESSO!
echo ================================================================================
echo.
echo PROXIMOS PASSOS:
echo   1. Feche TODOS os navegadores abertos
echo   2. Feche o Cursor/VS Code
echo   3. Reabra o Cursor
echo   4. Execute: INICIAR_SISTEMA_LIMPO.bat
echo.
echo ================================================================================
pause
