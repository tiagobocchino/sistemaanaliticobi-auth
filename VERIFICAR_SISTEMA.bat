@echo off
echo ========================================
echo VERIFICANDO SISTEMA - Analytics Platform
echo ========================================
echo.

echo Verificando Backend (porta 8000)...
powershell -Command "try { $r = Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing -TimeoutSec 2; Write-Host '[OK] Backend esta rodando!' -ForegroundColor Green; Write-Host '   Resposta:' $r.Content } catch { Write-Host '[ERRO] Backend NAO esta rodando!' -ForegroundColor Red; Write-Host '   Execute: python main.py' }"

echo.
echo Verificando Frontend (porta 5173)...
powershell -Command "try { $r = Invoke-WebRequest -Uri http://localhost:5173/ -UseBasicParsing -TimeoutSec 2; Write-Host '[OK] Frontend esta rodando!' -ForegroundColor Green; Write-Host '   Status:' $r.StatusCode } catch { Write-Host '[ERRO] Frontend NAO esta rodando!' -ForegroundColor Red; Write-Host '   Execute: cd frontend && npm run dev' }"

echo.
echo Verificando portas...
netstat -ano | findstr ":8000 :5173" | findstr "LISTENING"
if %errorlevel% neq 0 (
    echo [INFO] Nenhuma das portas esta em uso
)

echo.
echo ========================================
echo Pressione qualquer tecla para fechar...
pause >nul
