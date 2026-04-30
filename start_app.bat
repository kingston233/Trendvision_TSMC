@echo off
chcp 65001 >nul 2>&1
cls
echo ========================================
echo 台積電股價預測應用 - 完整啟動腳本
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

REM 檢查前端目錄
if not exist "ai-predict" (
    echo ⚠ 警告: 找不到 ai-predict 目錄
    echo 只啟動後端服務器
    echo.
    
    echo 啟動後端服務器...
    echo.
    echo ========================================
    echo API 端點: http://localhost:8000
    echo API 文檔: http://localhost:8000/docs
    echo ========================================
    echo.
    
    REM 使用虛擬環境的 Python 執行後端
    venv\Scripts\python.exe simple_backend.py
    pause
    exit /b 0
)

echo [1/2] 啟動後端服務器...
start "TSMC後端API" cmd /k "venv\Scripts\python.exe simple_backend.py"

echo 等待後端啟動...
timeout /t 3 /nobreak >nul

echo [2/2] 啟動前端開發服務器...
cd ai-predict
start "TSMC前端" cmd /k "npm run dev"
cd ..

echo.
echo ========================================
echo 啟動完成！
echo ========================================
echo.
echo 後端 API: http://localhost:8000
echo 前端應用: http://localhost:5173
echo API 文檔: http://localhost:8000/docs
echo.
echo 提示: 
echo - 兩個命令視窗會保持打開狀態
echo - 關閉視窗即可停止服務器
echo - 前端啟動需要幾秒鐘時間
echo.
pause
