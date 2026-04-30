@echo off
chcp 65001 >nul 2>&1
echo 啟動前端開發服務器...
echo.
cd ai-predict
npm run dev
pause
