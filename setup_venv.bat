@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo 虛擬環境設定腳本
echo ========================================
echo.

REM 檢查 Python
echo [1/5] 檢查 Python 安裝...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 錯誤: 找不到 Python
    echo 請確認已安裝 Python 並加入 PATH
    pause
    exit /b 1
)

python --version
echo ✓ Python 已安裝
echo.

REM 刪除舊的虛擬環境
echo [2/5] 清理舊的虛擬環境...
if exist "venv" (
    echo 正在刪除舊的 venv 資料夾...
    rmdir /s /q venv
    echo ✓ 舊環境已刪除
) else (
    echo ✓ 無需清理
)
echo.

REM 建立新的虛擬環境
echo [3/5] 建立新的虛擬環境...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ 虛擬環境建立失敗
    pause
    exit /b 1
)
echo ✓ 虛擬環境建立成功
echo.

REM 啟動虛擬環境並升級 pip
echo [4/5] 升級 pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠ pip 升級失敗，但繼續安裝套件...
)
echo ✓ pip 已升級
echo.

REM 安裝必要套件
echo [5/5] 安裝必要套件...
if exist "ai-predict\requirements.txt" (
    echo 從 requirements.txt 安裝套件...
    pip install -r ai-predict\requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 套件安裝失敗
        pause
        exit /b 1
    )
    echo ✓ 所有套件安裝完成
) else (
    echo ⚠ 找不到 requirements.txt，手動安裝核心套件...
    pip install pandas numpy scikit-learn joblib yfinance matplotlib openpyxl fastapi uvicorn python-multipart pydantic python-dotenv
)
echo.

REM 驗證安裝
echo ========================================
echo 驗證安裝結果
echo ========================================
echo.
echo 已安裝的套件:
pip list
echo.

echo ========================================
echo ✓ 設定完成！
echo ========================================
echo.
echo 使用方法:
echo 1. 啟動虛擬環境: venv\Scripts\activate
echo 2. 執行 Python 腳本: python DataGet\ML.py
echo 3. 退出虛擬環境: deactivate
echo.
pause
