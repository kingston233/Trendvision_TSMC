# 台積電股價預測應用 - 使用指南

## ⚠️ 重要提醒

**執行 Python 腳本時,必須使用虛擬環境中的 Python!**

### ❌ 錯誤方式
```powershell
python simple_backend.py  # 這會使用系統 Python,找不到 fastapi
```

### ✅ 正確方式

#### 方法 1: 啟動虛擬環境後執行 (推薦)
```powershell
# 1. 啟動虛擬環境
.\venv\Scripts\Activate.ps1

# 2. 執行腳本 (現在 python 指向虛擬環境)
python simple_backend.py
python DataGet\ML.py

# 3. 完成後退出虛擬環境
deactivate
```

#### 方法 2: 直接使用虛擬環境的 Python
```powershell
# 不需要啟動虛擬環境,直接使用虛擬環境的 Python
.\venv\Scripts\python.exe simple_backend.py
.\venv\Scripts\python.exe DataGet\ML.py
```

#### 方法 3: 使用批次檔 (最簡單)
```powershell
# 啟動後端服務器
.\start_backend_venv.bat

# 或啟動完整應用 (後端 + 前端)
.\start_app.bat
```

## 🚀 快速啟動

### 啟動完整應用 (後端 + 前端)
```powershell
.\start_app.bat
```
這會自動:
- 使用虛擬環境啟動後端 API (http://localhost:8000)
- 啟動前端開發服務器 (http://localhost:5173)

### 只啟動後端 API
```powershell
.\start_backend_venv.bat
```

### 訓練 ML 模型
```powershell
# 啟動虛擬環境
.\venv\Scripts\Activate.ps1

# 執行訓練
python DataGet\ML.py
```

### 獲取股價資料
```powershell
# 啟動虛擬環境
.\venv\Scripts\Activate.ps1

# 執行資料獲取
python DataGet\Get2330.py
```

## 🔍 檢查當前使用的 Python

```powershell
# 檢查當前 Python 路徑
python -c "import sys; print(sys.executable)"

# 應該顯示:
# C:\Users\kings\Desktop\Zip\PythonProject_App\PythonProject_App\venv\Scripts\python.exe

# 如果顯示 C:\Program Files\Python312\python.exe
# 表示您還沒有啟動虛擬環境!
```

## 📦 已安裝的套件

虛擬環境中已安裝:
- ✅ fastapi (0.124.0)
- ✅ uvicorn (0.34.0)
- ✅ pandas (2.2.3)
- ✅ numpy (2.2.3)
- ✅ scikit-learn (1.6.1)
- ✅ matplotlib (3.10.3)
- ✅ yfinance (0.2.61)
- ✅ 其他所有必要套件

## 🛠️ 重新安裝虛擬環境

如果遇到問題,可以重新安裝:
```powershell
.\setup_venv.bat
```

## 📝 常見問題

### Q: 為什麼會出現 "ModuleNotFoundError: No module named 'fastapi'"?
**A:** 因為您使用的是系統 Python,而不是虛擬環境的 Python。請先啟動虛擬環境或使用 `.\venv\Scripts\python.exe`。

### Q: 如何確認我在虛擬環境中?
**A:** 命令提示字元前面會顯示 `(venv)`,例如:
```
(venv) PS C:\Users\kings\Desktop\Zip\PythonProject_App\PythonProject_App>
```

### Q: 可以直接執行 python 嗎?
**A:** 只有在啟動虛擬環境後才可以。否則請使用 `.\venv\Scripts\python.exe`。
