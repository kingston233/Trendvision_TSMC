@echo off
echo ========================================
echo   AI 股價預測後端服務
echo ========================================
echo.
echo 正在啟動 FastAPI 後端伺服器...
echo.
cd /d %~dp0
python backend_server.py
pause
