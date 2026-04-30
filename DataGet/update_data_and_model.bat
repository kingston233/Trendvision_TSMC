@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo 台積電資料更新 + 模型重新訓練
echo ========================================
echo.

REM 檢查虛擬環境 (從 DataGet 目錄執行)
if not exist "..\venv\Scripts\python.exe" (
    echo ❌ 錯誤: 找不到虛擬環境
    echo 請先執行 ..\setup_venv.bat 建立虛擬環境
    pause
    exit /b 1
)

echo [1/3] 正在抓取最新台積電資料...
..\venv\Scripts\python.exe Get2330.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ [錯誤] 資料抓取失敗！
    pause
    exit /b 1
)

echo.
echo [2/3] 正在重新訓練模型...
..\venv\Scripts\python.exe ML.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ [錯誤] 模型訓練失敗！
    pause
    exit /b 1
)

echo.
echo [3/3] 完成！
echo.
echo ========================================
echo ✓ 資料和模型已更新！
echo 請重啟後端伺服器以使用新模型
echo ========================================
echo.
pause
