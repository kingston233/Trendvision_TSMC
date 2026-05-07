# TrendVision TSMC — 台積電股價預測系統

以機器學習預測台積電（2330）下一個交易日收盤價，並提供歷史資料視覺化與技術指標分析。

---

## 系統功能

| 功能 | 說明 |
|------|------|
| 收盤價預測 | 使用訓練好的 ML 模型預測下一交易日收盤價 |
| 技術指標圖表 | 顯示收盤價走勢、MACD 等技術指標 |
| 歷史資料瀏覽 | 查看所有 CSV 格式的歷史股價與技術指標資料 |
| 本益比顯示 | 讀取基本面資料並顯示當前本益比 |
| 資料抓取 | 透過 API 觸發 `Get2330.py` 重新抓取最新股價 |
| 模型重訓 | 透過 API 觸發 `ML.py` 使用最新資料重新訓練模型 |

---

## 系統技術

**後端**
- Python / FastAPI — REST API 框架
- scikit-learn / joblib — 機器學習模型訓練與載入
- pandas / numpy — 資料處理
- yfinance — Yahoo Finance 股價資料抓取
- uvicorn — ASGI 伺服器

**前端**
- React 19 + TypeScript — UI 框架
- Vite — 開發與打包工具
- Tailwind CSS — 樣式框架
- Recharts / lightweight-charts — 圖表元件
- @google/genai — Gemini AI 整合

---

## 首次使用（環境建立）

### 前置需求
- Python 3.8 以上
- Node.js 16 以上

### 步驟 1 — 建立 Python 虛擬環境並安裝套件
```
雙擊 setup_venv.bat
```
這會自動建立 `venv/`、升級 pip、並安裝所有後端套件。

### 步驟 2 — 抓取股價資料
```
venv\Scripts\python.exe DataGet\Get2330.py
```

### 步驟 3 — 訓練預測模型
```
venv\Scripts\python.exe DataGet\ML.py
```

### 步驟 4 — 安裝前端套件
```
cd ai-predict
npm install
```

---

## 啟動系統

### 方式一：一鍵啟動（前後端同時）
```
雙擊 start_app.bat
```
會自動開啟兩個視窗，分別執行後端與前端。

### 方式二：分開啟動（建議，較穩定）

1. 先啟動後端，等待看到 `Application startup complete`
```
雙擊 start_backend.bat
```

2. 再啟動前端
```
雙擊 start_frontend.bat
```

> 首次啟動前端時，`start_frontend.bat` 會自動偵測是否已安裝 `node_modules`，沒有的話會先執行 `npm install`。

---

## 啟動腳本說明

| 腳本 | 用途 |
|------|------|
| `setup_venv.bat` | 建立虛擬環境並安裝所有 Python 套件 |
| `start_app.bat` | 同時啟動後端與前端 |
| `start_backend.bat` | 只啟動後端 API |
| `start_frontend.bat` | 只啟動前端（自動檢查 npm install） |

---

## 訪問地址

| 服務 | 網址 |
|------|------|
| 前端應用 | http://localhost:3000 |
| 後端 API | http://localhost:8000 |
| API 文件 | http://localhost:8000/docs |

---

## 常見問題

**Q: 執行 ML.py 出現 `ModuleNotFoundError`？**
A: 確認使用虛擬環境執行：`venv\Scripts\python.exe DataGet\ML.py`，不要直接用系統的 `python`。

**Q: API 回傳 500 錯誤？**
A: `Data/` 資料夾不存在，請先執行 `Get2330.py` 抓取資料，再執行 `ML.py` 訓練模型。

**Q: 前端無法連線後端？**
A: 確認後端已啟動，可開啟 http://localhost:8000/docs 確認。

**Q: 前端啟動失敗，`vite` 不是可執行命令？**
A: 尚未安裝前端套件，在 `ai-predict/` 目錄下執行 `npm install`。
