@echo off
chcp 65001 >nul 2>&1
echo 啟動後端服務器...
echo.
python simple_backend.py
pause
