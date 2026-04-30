"""
FastAPI 後端伺服器 - 台積電股價預測 API
整合 Python ML 模型與 React 前端
"""

import sys
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加 DataGet 目錄到 Python 路徑 (使用父目錄的 DataGet)
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
dataget_dir = parent_dir / "DataGet"
sys.path.insert(0, str(dataget_dir))

# 記錄路徑資訊
logger.info(f"Current directory: {current_dir}")
logger.info(f"DataGet directory: {dataget_dir}")
logger.info(f"DataGet exists: {dataget_dir.exists()}")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np

# 創建 FastAPI 應用
app = FastAPI(
    title="AI Stock Prediction API",
    description="台積電股價預測 API - 整合機器學習模型",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite 和 React 開發伺服器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# 資料模型定義
# ============================================================================

class StockInfo(BaseModel):
    symbol: str
    name: str
    price: float
    change: float
    changePercent: float
    sector: str
    marketCap: str
    peRatio: float
    volatility: str
    limitUp: Optional[float] = None
    limitDown: Optional[float] = None
    dayHigh: Optional[float] = None
    dayLow: Optional[float] = None
    volume: Optional[int] = None

class StockDataPoint(BaseModel):
    date: str
    price: float
    volume: int
    open: float
    high: float
    low: float
    isPrediction: Optional[bool] = False
    confidenceLower: Optional[float] = None
    confidenceUpper: Optional[float] = None
    rsi: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_middle: Optional[float] = None

class PredictionSummary(BaseModel):
    symbol: str
    targetPrice: float
    timeframe: str
    confidence: float  # 0-100
    signal: str  # 'BUY' | 'SELL' | 'HOLD'
    predictedClosePrice: Optional[float] = None
    predictedNextDayClose: Optional[float] = None
    aiReasoning: Optional[str] = None

class BacktestRequest(BaseModel):
    symbol: str
    days: int = 90
    threshold: float = 0.02
    initialCapital: float = 100000

# ============================================================================
# 模型載入和快取
# ============================================================================

class ModelCache:
    """模型快取管理"""
    def __init__(self):
        self.model_data = None
        self.last_load_time = None
        self.cache_duration = timedelta(hours=1)
    
    def get_model(self):
        """獲取模型,如果需要則重新載入"""
        now = datetime.now()
        
        # 檢查是否需要重新載入
        if (self.model_data is None or 
            self.last_load_time is None or 
            now - self.last_load_time > self.cache_duration):
            
            logger.info("載入機器學習模型...")
            try:
                # 動態導入 Predict.py
                from Predict import load_latest_model
                self.model_data = load_latest_model()
                self.last_load_time = now
                
                if self.model_data:
                    logger.info(f"模型載入成功: {self.model_data.get('model_name', 'Unknown')}")
                else:
                    logger.warning("模型載入失敗")
                    
            except Exception as e:
                logger.error(f"模型載入錯誤: {e}")
                self.model_data = None
        
        return self.model_data

# 全域模型快取
model_cache = ModelCache()

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API 根路徑"""
    return {
        "message": "AI Stock Prediction API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "stocks": "/api/v1/stocks",
            "history": "/api/v1/stocks/{symbol}/history",
            "predict": "/api/v1/predict/{symbol}"
        }
    }

@app.get("/api/v1/stocks", response_model=List[StockInfo])
async def get_stocks():
    """
    取得支援的股票清單
    目前主要支援台積電 (2330)
    """
    try:
        # 目前只支援台積電
        stocks = [
            StockInfo(
                symbol="2330",
                name="台積電 (TSMC)",
                price=0.0,  # 將從即時資料更新
                change=0.0,
                changePercent=0.0,
                sector="半導體",
                marketCap="25.4T",
                peRatio=24.5,
                volatility="Low"
            )
        ]
        
        # 嘗試獲取即時價格
        try:
            from Predict import get_realtime_data
            realtime_data = get_realtime_data()
            if realtime_data:
                stocks[0].price = realtime_data['current_price']
                if realtime_data['previous_close'] > 0:
                    stocks[0].change = realtime_data['current_price'] - realtime_data['previous_close']
                    stocks[0].changePercent = (stocks[0].change / realtime_data['previous_close']) * 100
                
                # Update detailed info
                stocks[0].peRatio = realtime_data.get('pe_ratio', 24.5)
                m_cap = realtime_data.get('market_cap', 0)
                if m_cap > 1000000000000:
                    stocks[0].marketCap = f"{m_cap/1000000000000:.1f}T"
                elif m_cap > 0:
                    stocks[0].marketCap = f"{m_cap/100000000:.1f}B"
                
                stocks[0].limitUp = realtime_data.get('limit_up')
                stocks[0].limitDown = realtime_data.get('limit_down')
                stocks[0].dayHigh = realtime_data.get('high_price')
                stocks[0].dayLow = realtime_data.get('low_price')
                stocks[0].volume = int(realtime_data.get('volume', 0))
        except Exception as e:
            logger.warning(f"無法獲取即時價格: {e}")
        
        return stocks
        
    except Exception as e:
        logger.error(f"獲取股票清單失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stocks/{symbol}/history", response_model=List[StockDataPoint])
async def get_stock_history(symbol: str):
    """
    取得股票歷史資料 + 預測資料
    """
    if symbol != "2330":
        raise HTTPException(status_code=404, detail=f"不支援的股票代碼: {symbol}")
    
    try:
        from Predict import get_latest_data, calculate_technical_indicators, create_prediction_features, make_prediction
        
        # 獲取歷史資料
        logger.info(f"獲取 {symbol} 的歷史資料...")
        df = get_latest_data(start_from_year=True)
        
        if df is None or df.empty:
            raise HTTPException(status_code=500, detail="無法獲取歷史資料")
        
        # 計算技術指標
        df = calculate_technical_indicators(df)
        
        # 轉換為 API 格式
        history_data = []
        for idx, row in df.tail(60).iterrows():  # 只返回最近60天
            history_data.append(StockDataPoint(
                date=idx.strftime('%Y-%m-%d'),
                price=float(row['Close']),
                volume=int(row['Volume']),
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                isPrediction=False,
                rsi=float(row.get('RSI', 0)),
                bb_upper=float(row.get('BB_Upper', 0)),
                bb_lower=float(row.get('BB_Lower', 0)),
                bb_middle=float(row.get('BB_Middle', 0))
            ))
        
        # 生成預測資料
        model_data = model_cache.get_model()
        if model_data:
            try:
                # 建立預測特徵
                features = create_prediction_features(df, model_data['features'])
                
                if features is not None:
                    # 預測未來15天
                    last_price = float(df['Close'].iloc[-1])
                    last_date = df.index[-1]
                    
                    for i in range(1, 16):
                        # 進行預測
                        predicted_price = make_prediction(model_data, features)
                        
                        if predicted_price:
                            future_date = last_date + timedelta(days=i)
                            
                            # 計算信心區間 (基於歷史波動率)
                            volatility = df['Close'].tail(20).std()
                            confidence_gap = volatility * (i / 5)  # 越遠信心區間越大
                            
                            history_data.append(StockDataPoint(
                                date=future_date.strftime('%Y-%m-%d'),
                                price=float(predicted_price),
                                volume=0,
                                open=0.0,
                                high=0.0,
                                low=0.0,
                                isPrediction=True,
                                confidenceUpper=float(predicted_price + confidence_gap),
                                confidenceLower=float(predicted_price - confidence_gap)
                            ))
                            
                            # 更新 last_price 用於下一次預測
                            last_price = predicted_price
                            
            except Exception as e:
                logger.warning(f"預測資料生成失敗: {e}")
        
        return history_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"獲取歷史資料失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/predict/{symbol}", response_model=PredictionSummary)
async def get_prediction(symbol: str):
    """
    取得股票預測摘要
    """
    if symbol != "2330":
        raise HTTPException(status_code=404, detail=f"不支援的股票代碼: {symbol}")
    
    try:
        from Predict import get_latest_data, calculate_technical_indicators, create_prediction_features, make_prediction, predict_closing_price, get_realtime_data
        
        # 獲取模型
        model_data = model_cache.get_model()
        if not model_data:
            raise HTTPException(status_code=500, detail="模型未載入")
        
        # 獲取資料並預測 - 添加重試和降級機制
        df = None
        error_messages = []
        
        # 嘗試 1: 獲取今年年初至今的資料
        try:
            logger.info("嘗試獲取今年年初至今的資料...")
            df = get_latest_data(start_from_year=True)
        except Exception as e:
            error_messages.append(f"年初至今資料獲取失敗: {str(e)}")
            logger.warning(error_messages[-1])
        
        # 嘗試 2: 如果失敗，獲取近期資料
        if df is None or df.empty:
            try:
                logger.info("降級: 嘗試獲取近期資料...")
                df = get_latest_data(start_from_year=False)
            except Exception as e:
                error_messages.append(f"近期資料獲取失敗: {str(e)}")
                logger.warning(error_messages[-1])
        
        # 如果仍然失敗，返回錯誤
        if df is None or df.empty:
            error_detail = "無法獲取股價資料。" + " | ".join(error_messages)
            logger.error(error_detail)
            raise HTTPException(status_code=503, detail=error_detail)
        
        # 計算技術指標
        df = calculate_technical_indicators(df)
        if df is None:
            raise HTTPException(status_code=500, detail="技術指標計算失敗")
        
        # 建立預測特徵
        features = create_prediction_features(df, model_data['features'])
        if features is None:
            raise HTTPException(status_code=500, detail="無法建立預測特徵")
        
        # 執行預測
        predicted_price = make_prediction(model_data, features)
        
        if predicted_price is None:
            raise HTTPException(status_code=500, detail="預測失敗")
        
        # 計算信號和信心度
        current_price = float(df['Close'].iloc[-1])
        price_change_pct = ((predicted_price - current_price) / current_price) * 100
        
        # 判斷買賣信號
        if price_change_pct > 3:
            signal = "BUY"
        elif price_change_pct < -3:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        # 信心度基於模型性能
        confidence = model_data.get('performance', {}).get('accuracy_5', 85.0)
        
        logger.info(f"預測成功: 當前價格={current_price:.2f}, 預測價格={predicted_price:.2f}, 信號={signal}")
        
        # 預測今日收盤價
        predicted_close = None
        try:
            # 需要即時資料
            realtime_data = get_realtime_data()
            if realtime_data:
                predicted_close = predict_closing_price(model_data, df, realtime_data)
        except Exception as e:
            logger.warning(f"今日收盤價預測失敗: {e}")

        return PredictionSummary(
            symbol=symbol,
            targetPrice=float(predicted_price),
            timeframe="30 Days",
            confidence=float(confidence),
            signal=signal,
            predictedClosePrice=float(predicted_close) if predicted_close else None,
            predictedNextDayClose=float(predicted_price),
            aiReasoning=f"基於 {model_data['model_name']} 模型預測,預期價格變化 {price_change_pct:+.2f}%"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"預測失敗: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/backtest")
async def run_backtest_endpoint(request: BacktestRequest):
    """
    執行回測
    """
    if request.symbol != "2330":
        raise HTTPException(status_code=404, detail=f"不支援的股票代碼: {request.symbol}")
        
    try:
        from BacktestService import run_backtest
        from Predict import get_latest_data, calculate_technical_indicators
        
        # 獲取模型
        model_data = model_cache.get_model()
        if not model_data:
            raise HTTPException(status_code=500, detail="模型未載入")
            
        # 獲取資料
        df = get_latest_data(start_from_year=True)
        if df is None or df.empty:
            # 嘗試降級
             df = get_latest_data(start_from_year=False)
             
        if df is None or df.empty:
            raise HTTPException(status_code=500, detail="無法獲取歷史資料")
            
        # 計算指標
        df = calculate_technical_indicators(df)
        
        # 執行回測
        result = run_backtest(
            model_data, 
            df, 
            initial_capital=request.initialCapital,
            threshold=request.threshold,
            days=request.days
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"回測失敗: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康檢查"""
    model_data = model_cache.get_model()
    return {
        "status": "healthy",
        "model_loaded": model_data is not None,
        "model_name": model_data.get('model_name') if model_data else None,
        "timestamp": datetime.now().isoformat()
    }

# ============================================================================
# 主程式
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print(" "*20 + "AI Stock Prediction API")
    print("="*70 + "\n")
    print("🚀 啟動 FastAPI 伺服器...")
    print("📡 API 文件: http://localhost:8000/docs")
    print("🔗 前端連接: http://localhost:5173")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(
        "backend_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
