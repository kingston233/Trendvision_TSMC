@echo off
echo ========================================
echo   AI 股價預測 - 完整開發環境
echo ========================================
echo.
echo 正在啟動後端和前端服務...
echo.

REM 啟動後端服務
start "AI Predict Backend" cmd /k "cd /d %~dp0 && python backend_server.py"

REM 等待後端啟動
echo 等待後端服務啟動...
timeout /t 5 /nobreak >nul

REM 啟動前端服務
start "AI Predict Frontend" cmd /k "cd /d %~dp0 && npm run dev"

echo.
echo ========================================
echo   開發環境啟動完成！
echo ========================================
echo.
echo 後端 API: http://localhost:8000
echo API 文檔: http://localhost:8000/docs
echo 前端應用: http://localhost:5173
echo.
echo 按任意鍵關閉此視窗...
pause >nul
