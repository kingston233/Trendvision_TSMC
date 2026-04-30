@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo 台積電股價預測 - 後端服務器
echo ========================================
echo.

REM 檢查虛擬環境
if not exist "venv\Scripts\python.exe" (
    echo ❌ 錯誤: 找不到虛擬環境
    echo 請先執行 setup_venv.bat 建立虛擬環境
    pause
    exit /b 1
)

REM 檢查後端文件
if not exist "simple_backend.py" (
    echo ❌ 錯誤: 找不到 simple_backend.py
    pause
    exit /b 1
)

echo ✓ 虛擬環境已就緒
echo ✓ 後端文件已找到
echo.
echo 啟動後端服務器...
echo.
echo ========================================
echo API 端點: http://localhost:8000
echo API 文檔: http://localhost:8000/docs
echo ========================================
echo.
echo 按 Ctrl+C 停止服務器
echo.

REM 使用虛擬環境的 Python 執行後端
venv\Scripts\python.exe simple_backend.py
