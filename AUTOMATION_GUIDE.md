# 自動化批次檔使用指南

## 📦 已建立的自動化腳本

我為您建立了 3 個自動化批次檔,可以一鍵完成「抓取資料 + 訓練模型」的完整流程:

### 1. `auto_update_and_train.bat` (推薦)
**位置**: 專案根目錄  
**特點**: 完整版,包含詳細進度顯示和錯誤處理

```batch
.\auto_update_and_train.bat
```

**功能**:
- ✅ 檢查虛擬環境是否存在
- ✅ 執行 Get2330.py 抓取最新股價資料
- ✅ 執行 ML.py 訓練機器學習模型
- ✅ 顯示詳細進度和結果
- ✅ 錯誤處理和提示
- ✅ 顯示最新資料夾位置

---

### 2. `quick_update.bat` (快速版)
**位置**: 專案根目錄  
**特點**: 簡化版,適合日常快速執行

```batch
.\quick_update.bat
```

**功能**:
- ✅ 快速執行資料抓取和模型訓練
- ✅ 簡潔的輸出訊息
- ✅ 基本錯誤處理

---

### 3. `DataGet\update_data_and_model.bat` (已更新)
**位置**: DataGet 目錄下  
**特點**: 從 DataGet 目錄執行

```batch
cd DataGet
.\update_data_and_model.bat
```

**功能**:
- ✅ 在 DataGet 目錄下執行
- ✅ 使用虛擬環境 Python
- ✅ 完整的錯誤處理

---

## 🚀 使用方法

### 方法 1: 使用完整版 (推薦)
```powershell
# 在專案根目錄執行
.\auto_update_and_train.bat
```

### 方法 2: 使用快速版
```powershell
# 在專案根目錄執行
.\quick_update.bat
```

### 方法 3: 從 DataGet 目錄執行
```powershell
cd DataGet
.\update_data_and_model.bat
```

---

## 📊 執行流程

所有批次檔都會依序執行以下步驟:

```
1️⃣ 檢查虛擬環境
   ↓
2️⃣ 執行 Get2330.py
   - 抓取台積電 2 年歷史資料
   - 計算技術指標
   - 儲存到 Data/YYYYMMDDHHMM/
   ↓
3️⃣ 執行 ML.py
   - 讀取最新資料
   - 訓練 3 個模型 (隨機森林、Ridge、Lasso)
   - 選擇最佳模型
   - 生成視覺化圖表
   - 儲存模型和報告
   ↓
4️⃣ 完成
   - 顯示結果摘要
   - 提示下一步操作
```

---

## ⏱️ 預計執行時間

- **資料抓取** (Get2330.py): 約 30-60 秒
- **模型訓練** (ML.py): 約 10-30 秒
- **總計**: 約 1-2 分鐘

---

## 📁 輸出結果

執行完成後,會在 `Data\YYYYMMDDHHMM\` 資料夾中生成:

### 資料檔案
- `tsmc_lstm_data.csv` - LSTM 訓練資料
- `tsmc_technical_data.csv` - 技術指標資料
- `tsmc_fundamental_data.csv` - 基本面資料

### 模型檔案
- `best_three_model.joblib` - 最佳模型 (Predict.py 會使用)
- `all_three_models.joblib` - 所有模型
- `model_training_report.txt` - 訓練報告

### 視覺化圖表
- `model_performance_comparison.png` - 模型性能比較
- `prediction_vs_actual.png` - 預測 vs 實際
- `accuracy_comparison.png` - 準確率比較
- `feature_importance.png` - 特徵重要性
- `prediction_timeseries.png` - 時間序列預測

---

## ⚠️ 注意事項

1. **執行前確認**:
   - ✅ 虛擬環境已建立 (執行過 `setup_venv.bat`)
   - ✅ 網路連線正常 (需要下載股價資料)

2. **執行頻率建議**:
   - 📅 每日收盤後執行一次
   - 📅 或每週執行一次更新模型

3. **錯誤處理**:
   - 如果資料抓取失敗,檢查網路連線
   - 如果模型訓練失敗,檢查資料是否完整

---

## 🔄 自動化排程 (進階)

如果想要定時自動執行,可以使用 Windows 工作排程器:

1. 開啟「工作排程器」
2. 建立基本工作
3. 設定觸發條件 (例如:每日下午 2:30)
4. 動作選擇「啟動程式」
5. 程式路徑填入批次檔完整路徑

---

## 💡 下一步

執行完自動化更新後:

1. **啟動後端 API**:
   ```batch
   .\start_backend_venv.bat
   ```

2. **啟動完整應用**:
   ```batch
   .\start_app.bat
   ```

3. **查看預測結果**:
   ```batch
   .\venv\Scripts\python.exe DataGet\Predict.py
   ```

---

## 🎯 快速參考

| 批次檔 | 位置 | 特點 | 使用場景 |
|--------|------|------|----------|
| `auto_update_and_train.bat` | 根目錄 | 詳細輸出 | 首次使用、需要詳細資訊 |
| `quick_update.bat` | 根目錄 | 簡潔快速 | 日常更新 |
| `update_data_and_model.bat` | DataGet\ | 從 DataGet 執行 | 在 DataGet 目錄工作時 |
