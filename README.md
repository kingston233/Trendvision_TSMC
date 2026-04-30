# 台積電股價預測應用 - 簡化版

專注於兩個核心功能的股價預測應用。

## 功能

1. **預測收盤價** - 使用機器學習模型預測台積電下一個交易日收盤價
2. **CSV 資料展示** - 查看所有收集到的歷史資料和技術指標

## 快速開始

### 首次使用

```bash
# 1. 安裝前端依賴
cd ai-predict
npm install

# 2. 抓取資料
cd ../DataGet
python Get2330.py

# 3. 訓練模型
python ML.py

# 4. 啟動應用
cd ..
start_app.bat
```

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

## 詳細說明

請查看 `walkthrough.md` 獲取完整使用說明。
