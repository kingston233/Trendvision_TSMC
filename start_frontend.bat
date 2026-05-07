@echo off
chcp 65001 >nul 2>&1
echo 啟動前端開發服務器...
echo.
cd ai-predict

if not exist "node_modules" (
    echo 找不到 node_modules，正在執行 npm install...
    npm install
    if errorlevel 1 (
        echo 安裝失敗，請確認 Node.js 已安裝
        pause
        exit /b 1
    )
    echo.
)

npm run dev
pause
