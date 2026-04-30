@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo 台積電股價預測 - 自動化資料更新與訓練
echo ========================================
echo.

REM 檢查虛擬環境
if not exist "venv\Scripts\python.exe" (
    echo ❌ 錯誤: 找不到虛擬環境
    echo 請先執行 setup_venv.bat 建立虛擬環境
    pause
    exit /b 1
)

echo ✓ 虛擬環境已就緒
echo.

REM 檢查必要檔案
if not exist "DataGet\Get2330.py" (
    echo ❌ 錯誤: 找不到 Get2330.py
    pause
    exit /b 1
)

if not exist "DataGet\ML.py" (
    echo ❌ 錯誤: 找不到 ML.py
    pause
    exit /b 1
)

echo ✓ 所有必要檔案已找到
echo.

echo ========================================
echo 開始自動化流程
echo ========================================
echo.

REM ============================================
REM 步驟 1: 抓取最新股價資料
REM ============================================
echo [步驟 1/2] 抓取台積電最新股價資料...
echo ----------------------------------------
echo.

venv\Scripts\python.exe DataGet\Get2330.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 資料抓取失敗 (錯誤代碼: %errorlevel%)
    echo 請檢查網路連線或稍後再試
    pause
    exit /b 1
)

echo.
echo ✓ 資料抓取完成
echo.

REM 等待一下讓使用者看到結果
timeout /t 2 /nobreak >nul

REM ============================================
REM 步驟 2: 訓練機器學習模型
REM ============================================
echo ========================================
echo [步驟 2/2] 訓練機器學習模型...
echo ----------------------------------------
echo.

venv\Scripts\python.exe DataGet\ML.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 模型訓練失敗 (錯誤代碼: %errorlevel%)
    pause
    exit /b 1
)

echo.
echo ✓ 模型訓練完成
echo.

REM ============================================
REM 完成
REM ============================================
echo ========================================
echo ✓ 自動化流程完成！
echo ========================================
echo.

REM 顯示最新資料夾
echo 📁 最新資料位置:
for /f "delims=" %%i in ('dir /b /ad /o-n Data 2^>nul ^| findstr /r "^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$" ^| findstr /n "^" ^| findstr "^1:"') do (
    set "latest=%%i"
)
if defined latest (
    set "latest=%latest:*:=%"
    echo    Data\%latest%\
    echo.
    echo 📊 包含檔案:
    echo    • tsmc_lstm_data.csv (訓練資料)
    echo    • best_three_model.joblib (最佳模型)
    echo    • 5 個視覺化圖表 (PNG)
)
echo.

echo 💡 下一步:
echo    1. 啟動後端 API: start_backend_venv.bat
echo    2. 啟動完整應用: start_app.bat
echo    3. 查看預測結果: venv\Scripts\python.exe DataGet\Predict.py
echo.

pause
