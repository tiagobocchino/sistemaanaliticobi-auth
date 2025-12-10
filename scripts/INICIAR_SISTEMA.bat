@echo off
echo ========================================
echo INICIANDO SISTEMA - Analytics Platform
echo ========================================
echo.

echo [1/2] Iniciando Backend...
start "Backend - Analytics Platform" cmd /k "cd /d %~dp0.. && python main.py"
timeout /t 3 /nobreak >nul

echo [2/2] Iniciando Frontend...
start "Frontend - Analytics Platform" cmd /k "cd /d %~dp0..\\frontend && npm run dev"

echo.
echo ========================================
echo SERVIDORES INICIADOS!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo Teste: http://localhost:5173/test.html
echo.
echo Pressione qualquer tecla para fechar este terminal...
pause >nul
