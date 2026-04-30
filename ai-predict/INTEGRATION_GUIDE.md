# AI 股價預測系統 - 整合指南

## 系統架構

```
PythonProject_App/
├── DataGet/              # Python ML 模型和資料處理
│   ├── ML.py            # 模型訓練
│   ├── Predict.py       # 預測邏輯
│   └── Get2330.py       # 資料獲取
├── Data/                # 訓練資料和模型檔案
│   └── YYYYMMDDHHMM/   # 時間戳記資料夾
│       ├── best_three_model.joblib
│       └── tsmc_lstm_data.csv
└── ai-predict/          # React 前端 + FastAPI 後端
    ├── backend_server.py    # FastAPI 後端服務
    ├── App.tsx             # React 主應用
    ├── services/api.ts     # API 服務層
    └── pages/              # React 頁面組件
```

## 安裝步驟

### 1. Python 環境設定

確保已安裝所有 Python 依賴：

```bash
cd ai-predict
pip install -r requirements.txt
```

### 2. Node.js 環境設定

安裝前端依賴：

```bash
cd ai-predict
npm install
```

## 啟動方式

### 方式一：使用啟動腳本（推薦）

**啟動完整開發環境（前端 + 後端）：**
```bash
cd ai-predict
start_dev.bat
```

**只啟動後端：**
```bash
cd ai-predict
start_backend.bat
```

### 方式二：手動啟動

**啟動後端：**
```bash
cd ai-predict
python backend_server.py
```
後端將在 `http://localhost:8000` 運行

**啟動前端：**
```bash
cd ai-predict
npm run dev
```
前端將在 `http://localhost:5173` 運行

## API 端點說明

### 健康檢查
- **GET** `/health`
- 檢查系統狀態和模型載入情況

### 股票清單
- **GET** `/api/v1/stocks`
- 返回支援的股票清單（目前僅台積電 2330）

### 歷史資料 + 預測
- **GET** `/api/v1/stocks/{symbol}/history`
- 返回歷史股價資料和未來 15 天預測
- 參數：`symbol` - 股票代碼（例如：2330）

### 預測摘要
- **GET** `/api/v1/predict/{symbol}`
- 返回預測摘要（目標價格、信號、信心度）
- 參數：`symbol` - 股票代碼（例如：2330）

### API 文檔
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 資料流程

1. **模型訓練** (一次性)
   ```
   DataGet/ML.py → 訓練模型 → Data/YYYYMMDDHHMM/best_three_model.joblib
   ```

2. **後端啟動**
   ```
   backend_server.py → 載入模型 → 提供 API 服務
   ```

3. **前端請求**
   ```
   React App → api.ts → FastAPI Backend → Predict.py → 返回預測結果
   ```

## 故障排除

### 問題 1: 模型載入失敗

**錯誤訊息**: `找不到訓練好的模型`

**解決方案**:
1. 確認已執行 `DataGet/ML.py` 訓練模型
2. 檢查 `Data/` 目錄下是否有時間戳記資料夾
3. 確認資料夾內有 `best_three_model.joblib` 檔案

### 問題 2: 無法導入 Predict 模組

**錯誤訊息**: `ModuleNotFoundError: No module named 'Predict'`

**解決方案**:
1. 確認 `DataGet/` 目錄存在於 `PythonProject_App/` 下
2. 檢查 `backend_server.py` 的路徑設定是否正確
3. 查看後端啟動日誌中的路徑資訊

### 問題 3: 前端無法連接後端

**錯誤訊息**: `Failed to fetch` 或 `Network Error`

**解決方案**:
1. 確認後端已啟動且運行在 `http://localhost:8000`
2. 檢查 `services/api.ts` 中 `USE_REAL_BACKEND` 是否為 `true`
3. 檢查 CORS 設定是否正確

### 問題 4: 預測結果不合理

**症狀**: 預測價格過高或過低

**解決方案**:
1. 檢查訓練資料是否完整
2. 重新訓練模型 (`DataGet/ML.py`)
3. 確認即時資料獲取正常

### 問題 5: 依賴套件安裝失敗

**錯誤訊息**: `ERROR: Could not find a version that satisfies the requirement`

**解決方案**:
1. 更新 pip: `python -m pip install --upgrade pip`
2. 使用虛擬環境: `python -m venv venv`
3. 逐個安裝套件以找出問題套件

## 開發建議

### 修改預測邏輯
編輯 `DataGet/Predict.py` 中的相關函數

### 修改 API 端點
編輯 `ai-predict/backend_server.py`

### 修改前端 UI
編輯 `ai-predict/pages/` 下的 React 組件

### 重新訓練模型
```bash
cd DataGet
python ML.py
```

## 效能優化

1. **模型快取**: 後端會快取載入的模型 1 小時
2. **資料快取**: 考慮添加 Redis 快取歷史資料
3. **非同步處理**: 使用 FastAPI 的非同步功能處理耗時操作

## 安全性考量

1. **API Key 保護**: Gemini API Key 應存放在 `.env.local` 中
2. **CORS 設定**: 生產環境應限制允許的來源
3. **輸入驗證**: 所有 API 輸入都應進行驗證
4. **錯誤處理**: 避免在錯誤訊息中洩漏敏感資訊

## 部署建議

### 開發環境
- 使用 `start_dev.bat` 啟動
- 前端: Vite 開發伺服器
- 後端: Uvicorn 開發模式 (reload=True)

### 生產環境
- 前端: `npm run build` → 靜態檔案部署
- 後端: Uvicorn + Gunicorn 或 Docker 容器化
- 資料庫: 考慮使用 PostgreSQL 儲存歷史資料
- 快取: Redis 快取預測結果

## 聯絡資訊

如有問題，請檢查：
1. API 文檔: `http://localhost:8000/docs`
2. 後端日誌輸出
3. 瀏覽器開發者工具的 Network 標籤
