# 使用 ngrok 遠程訪問應用

## 配置完成

✅ Vite 配置已更新，現在支援 ngrok 訪問

## 使用步驟

### 1. 啟動應用

確保前後端都在運行：
```bash
# 後端
python simple_backend.py

# 前端（在另一個終端）
cd ai-predict
npm run dev
```

### 2. 使用 ngrok 暴露前端

前端運行在端口 3000：
```bash
ngrok http 3000
```

您會看到類似的輸出：
```
Forwarding  https://angeline-unvivid-moanfully.ngrok-free.dev -> http://localhost:3000
```

### 3. 使用 ngrok 暴露後端（可選）

如果需要遠程訪問後端 API：
```bash
ngrok http 8000
```

### 4. 更新 API 地址（如果暴露後端）

如果您暴露了後端，需要更新前端的 API 地址：

編輯 `ai-predict/src/services/apiService.ts`：
```typescript
// 將這行
const API_BASE_URL = 'http://localhost:8000';

// 改為您的 ngrok 後端地址
const API_BASE_URL = 'https://your-backend-ngrok-url.ngrok-free.dev';
```

## 注意事項

1. **免費版限制**：ngrok 免費版有連接數和流量限制
2. **URL 變化**：每次重啟 ngrok，URL 會改變（除非使用付費版）
3. **安全性**：不要在生產環境使用 ngrok，僅用於開發和測試
4. **CORS**：後端已配置允許所有來源，支援 ngrok 訪問

## 常見問題

**Q: 前端可以訪問，但無法連接後端？**
A: 確保：
1. 後端正在運行（http://localhost:8000）
2. 如果後端也用 ngrok 暴露，更新前端的 API_BASE_URL
3. 檢查瀏覽器控制台的錯誤訊息

**Q: ngrok 顯示 "ERR_NGROK_108"？**
A: 這是 ngrok 的速率限制，稍等片刻後重試

**Q: 需要固定的 ngrok URL？**
A: 升級到 ngrok 付費版可以獲得固定域名

## 完整範例

### 只暴露前端（推薦）
```bash
# 終端 1: 啟動後端
python simple_backend.py

# 終端 2: 啟動前端
cd ai-predict
npm run dev

# 終端 3: ngrok 暴露前端
ngrok http 3000
```

訪問 ngrok 提供的 URL 即可！

### 暴露前後端
```bash
# 終端 1: 啟動後端
python simple_backend.py

# 終端 2: ngrok 暴露後端
ngrok http 8000
# 記下後端 URL，例如: https://abc123.ngrok-free.dev

# 終端 3: 更新前端 API 地址
# 編輯 ai-predict/src/services/apiService.ts
# 將 API_BASE_URL 改為後端 ngrok URL

# 終端 4: 啟動前端
cd ai-predict
npm run dev

# 終端 5: ngrok 暴露前端
ngrok http 3000
```

訪問前端 ngrok URL 即可！
