@echo off
echo ========================================
echo 台積電資料更新腳本
echo ========================================
echo.

echo [1/2] 正在抓取最新台積電資料...
python Get2330.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [錯誤] 資料抓取失敗！
    pause
    exit /b 1
)

echo.
echo [2/2] 資料更新完成！
echo.
echo ========================================
echo 下一步：
echo 1. 如果要重新訓練模型，請執行: python ML.py
echo 2. 如果只是更新資料，請重啟後端伺服器
echo ========================================
echo.
pause
