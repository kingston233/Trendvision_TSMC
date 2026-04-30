@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo 快速更新 - 台積電股價預測
echo ========================================
echo.

REM 使用虛擬環境執行
echo [1/2] 抓取資料...
venv\Scripts\python.exe DataGet\Get2330.py
if %errorlevel% neq 0 exit /b 1

echo.
echo [2/2] 訓練模型...
venv\Scripts\python.exe DataGet\ML.py
if %errorlevel% neq 0 exit /b 1

echo.
echo ✓ 更新完成！
pause
