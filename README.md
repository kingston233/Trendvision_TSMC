# 台積電股價預測應用 - 簡化版

專注於兩個核心功能的股價預測應用。

## 功能

1. **預測收盤價** - 使用機器學習模型預測台積電下一個交易日收盤價
2. **CSV 資料展示** - 查看所有收集到的歷史資料和技術指標

## 快速開始

### 首次使用
# 快速啟動指南
.\setup_venv.bat

## 🚀 推薦啟動方式

### 方式一：分別啟動（最穩定）

1. **啟動後端**
   ```
   雙擊 start_backend.bat
   ```
   等待看到 "Application startup complete" 訊息

2. **啟動前端**
   ```
   雙擊 start_frontend.bat
   ```
   等待瀏覽器自動打開

### 方式二：一鍵啟動

```
雙擊 start_app.bat
```

會自動打開兩個視窗（後端 + 前端）

---

## 📋 首次使用檢查清單

- [ ] 已安裝 Python 3.8+
- [ ] 已安裝 Node.js 16+
- [ ] 已安裝前端依賴 (`cd ai-predict && npm install`)
- [ ] 已安裝後端依賴 (`pip install fastapi uvicorn pandas numpy joblib yfinance scikit-learn`)
- [ ] 已執行 `Get2330.py` 抓取資料
- [ ] 已執行 `ML.py` 訓練模型

---

## 🔗 訪問地址

- **前端應用：** http://localhost:5173
- **後端 API：** http://localhost:8000
- **API 文檔：** http://localhost:8000/docs

---

## ❓ 常見問題

**Q: 啟動腳本執行失敗？**
A: 使用分別啟動方式（start_backend.bat + start_frontend.bat）

**Q: 找不到模型？**
A: 執行 `cd DataGet && python ML.py`

**Q: 找不到資料？**
A: 執行 `cd DataGet && python Get2330.py`

**Q: 前端無法連接後端？**
A: 確認後端已啟動（訪問 http://localhost:8000/docs）

---

## 📁 啟動腳本說明

| 腳本 | 用途 |
|------|------|
| `start_app.bat` | 同時啟動前後端 |
| `start_backend.bat` | 只啟動後端 |
| `start_frontend.bat` | 只啟動前端 |

---

詳細說明請查看 `walkthrough.md`

### 日常使用

```bash
# 直接啟動
start_app.bat
```

## 訪問應用

- **前端應用：** http://localhost:5173
- **後端 API：** http://localhost:8000
- **API 文檔：** http://localhost:8000/docs

## 技術棧

**後端：** FastAPI + scikit-learn + pandas  
**前端：** React + TypeScript + Tailwind CSS

