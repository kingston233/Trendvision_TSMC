"""
簡化版 FastAPI 後端 - 台積電股價預測應用
專注於兩個核心功能：
1. 預測收盤價
2. 展示 CSV 資料
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
import joblib
from datetime import datetime
from typing import List, Dict, Any, Optional
import subprocess
import sys

app = FastAPI(title="台積電股價預測 API")

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# 資料模型
# ============================================================================

class PredictionResponse(BaseModel):
    predicted_price: float
    prediction_time: str
    model_name: str
    confidence: Optional[float] = None
    current_price: Optional[float] = None
    change_percent: Optional[float] = None

class CsvFileInfo(BaseModel):
    folder: str
    filename: str
    size: int
    modified_time: str

class DataSummary(BaseModel):
    latest_close: float
    latest_date: str
    data_points: int
    date_range: str

# ============================================================================
# 輔助函數
# ============================================================================

def find_latest_data_folder():
    """尋找最新的時間戳記資料夾"""
    data_dir = 'Data'
    if not os.path.exists(data_dir):
        return None, None
    
    timestamp_folders = []
    for item in os.listdir(data_dir):
        item_path = os.path.join(data_dir, item)
        if os.path.isdir(item_path) and len(item) == 12 and item.isdigit():
            timestamp_folders.append((item, item_path))
    
    if not timestamp_folders:
        return None, None
    
    latest_folder = max(timestamp_folders, key=lambda x: x[0])
    return latest_folder

def load_latest_model():
    """載入最新的訓練模型"""
    timestamp, folder_path = find_latest_data_folder()
    if not folder_path:
        return None
    
    model_file = os.path.join(folder_path, 'best_three_model.joblib')
    if not os.path.exists(model_file):
        return None
    
    try:
        model_data = joblib.load(model_file)
        return model_data
    except Exception as e:
        print(f"模型載入失敗: {e}")
        return None

def load_latest_csv_data():
    """載入最新的 CSV 資料"""
    timestamp, folder_path = find_latest_data_folder()
    if not folder_path:
        return None
    
    csv_file = os.path.join(folder_path, 'tsmc_technical_data.csv')
    if not os.path.exists(csv_file):
        csv_file = os.path.join(folder_path, 'tsmc_lstm_data.csv')
    
    if not os.path.exists(csv_file):
        return None
    
    try:
        df = pd.read_csv(csv_file, index_col=0, parse_dates=True)
        return df
    except Exception as e:
        print(f"CSV 載入失敗: {e}")
        return None

# ============================================================================
# API 端點
# ============================================================================

@app.get("/")
async def root():
    """API 根端點"""
    return {
        "message": "台積電股價預測 API",
        "version": "1.0.0",
        "endpoints": [
            "/api/predict",
            "/api/csv-files",
            "/api/csv-data/{folder}/{filename}",
            "/api/chart-data",
            "/api/latest-data",
            "/api/fetch-data",
            "/api/train-model"
        ]
    }

@app.get("/api/predict", response_model=PredictionResponse)
async def predict_closing_price():
    """
    預測下一個交易日的收盤價
    """
    try:
        # 載入模型
        model_data = load_latest_model()
        if model_data is None:
            raise HTTPException(status_code=404, detail="找不到訓練好的模型，請先執行 ML.py")
        
        # 載入最新資料
        df = load_latest_csv_data()
        if df is None:
            raise HTTPException(status_code=404, detail="找不到歷史資料，請先執行 Get2330.py")
        
        # 準備預測特徵
        model = model_data['model']
        scaler = model_data['scaler']
        features = model_data['features']
        
        # 使用最新資料進行預測
        latest_data = df[features].iloc[-1:].values
        
        # 標準化
        latest_data_scaled = scaler.transform(latest_data)
        
        # 預測
        prediction = model.predict(latest_data_scaled)[0]
        
        # 獲取當前價格
        current_price = float(df['Close'].iloc[-1])
        
        # 計算變化百分比
        change_percent = ((prediction - current_price) / current_price) * 100
        
        # 獲取模型性能指標作為信心度
        confidence = None
        if 'performance' in model_data:
            r2_score = model_data['performance'].get('r2', 0)
            confidence = float(r2_score * 100)  # 轉換為百分比
        
        return PredictionResponse(
            predicted_price=float(prediction),
            prediction_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            model_name=model_data['model_name'],
            confidence=confidence,
            current_price=current_price,
            change_percent=float(change_percent)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"預測失敗: {str(e)}")

@app.get("/api/csv-files", response_model=List[CsvFileInfo])
async def get_csv_files():
    """
    獲取所有可用的 CSV 檔案列表（只包含 lstm_data 和 technical_data）
    """
    try:
        data_dir = 'Data'
        if not os.path.exists(data_dir):
            return []
        
        csv_files = []
        
        # 遍歷所有時間戳記資料夾
        for folder in os.listdir(data_dir):
            folder_path = os.path.join(data_dir, folder)
            if os.path.isdir(folder_path) and len(folder) == 12 and folder.isdigit():
                # 遍歷資料夾中的 CSV 檔案
                for file in os.listdir(folder_path):
                    # 只包含 lstm_data 和 technical_data
                    if file.endswith('.csv') and ('lstm_data' in file or 'technical_data' in file):
                        file_path = os.path.join(folder_path, file)
                        file_stat = os.stat(file_path)
                        
                        csv_files.append(CsvFileInfo(
                            folder=folder,
                            filename=file,
                            size=file_stat.st_size,
                            modified_time=datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                        ))
        
        # 按資料夾時間戳記降序排序（最新的在前）
        csv_files.sort(key=lambda x: x.folder, reverse=True)
        
        return csv_files
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取檔案列表失敗: {str(e)}")

@app.get("/api/csv-data/{folder}/{filename}")
async def get_csv_data(folder: str, filename: str):
    """
    讀取特定 CSV 檔案的內容
    """
    try:
        file_path = os.path.join('Data', folder, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="檔案不存在")
        
        # 讀取 CSV
        df = pd.read_csv(file_path)
        
        # 轉換為 JSON 格式
        data = df.to_dict(orient='records')
        
        # 獲取欄位資訊
        columns = list(df.columns)
        
        return {
            "folder": folder,
            "filename": filename,
            "columns": columns,
            "row_count": len(df),
            "data": data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"讀取檔案失敗: {str(e)}")

@app.get("/api/chart-data")
async def get_chart_data():
    """
    獲取圖表資料（本益比、價格、MACD）
    """
    try:
        df = load_latest_csv_data()
        if df is None:
            raise HTTPException(status_code=404, detail="找不到資料")
        
        # 確保索引是日期格式
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # 準備圖表資料
        chart_data = []
        
        for idx, row in df.iterrows():
            data_point = {
                "date": idx.strftime('%Y-%m-%d'),
                "close": float(row['Close']) if 'Close' in row else None,
                "open": float(row['Open']) if 'Open' in row else None,
                "high": float(row['High']) if 'High' in row else None,
                "low": float(row['Low']) if 'Low' in row else None,
            }
            
            # MACD 資料
            if 'MACD' in row:
                data_point['macd'] = float(row['MACD'])
            if 'MACD_Signal' in row:
                data_point['macd_signal'] = float(row['MACD_Signal'])
            if 'MACD_Histogram' in row:
                data_point['macd_histogram'] = float(row['MACD_Histogram'])
            
            chart_data.append(data_point)
        
        # 獲取本益比資料（從基本面資料）
        timestamp, folder_path = find_latest_data_folder()
        pe_ratio = None
        
        if folder_path:
            fundamental_file = os.path.join(folder_path, 'tsmc_fundamental_data.csv')
            if os.path.exists(fundamental_file):
                try:
                    fund_df = pd.read_csv(fundamental_file)
                    if 'PE_Ratio' in fund_df.columns and len(fund_df) > 0:
                        pe_value = fund_df['PE_Ratio'].iloc[0]
                        if pe_value != 'N/A' and pd.notna(pe_value):
                            pe_ratio = float(pe_value)
                except Exception as e:
                    print(f"讀取本益比失敗: {e}")
        
        return {
            "chart_data": chart_data,
            "pe_ratio": pe_ratio,
            "data_points": len(chart_data),
            "date_range": {
                "start": chart_data[0]["date"] if chart_data else None,
                "end": chart_data[-1]["date"] if chart_data else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取圖表資料失敗: {str(e)}")

@app.get("/api/latest-data", response_model=DataSummary)
async def get_latest_data():
    """
    獲取最新的股價資料摘要
    """
    try:
        df = load_latest_csv_data()
        if df is None:
            raise HTTPException(status_code=404, detail="找不到資料")
        
        latest_close = float(df['Close'].iloc[-1])
        latest_date = df.index[-1].strftime('%Y-%m-%d')
        data_points = len(df)
        date_range = f"{df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}"
        
        return DataSummary(
            latest_close=latest_close,
            latest_date=latest_date,
            data_points=data_points,
            date_range=date_range
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取資料摘要失敗: {str(e)}")

@app.post("/api/fetch-data")
async def fetch_data():
    """
    觸發資料抓取（執行 Get2330.py）
    """
    try:
        script_path = os.path.join('DataGet', 'Get2330.py')
        if not os.path.exists(script_path):
            raise HTTPException(status_code=404, detail="找不到 Get2330.py")
        
        # 執行腳本
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5分鐘超時
        )
        
        if result.returncode == 0:
            return {"status": "success", "message": "資料抓取完成"}
        else:
            return {"status": "error", "message": result.stderr}
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="資料抓取超時")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"資料抓取失敗: {str(e)}")

@app.post("/api/train-model")
async def train_model():
    """
    觸發模型訓練（執行 ML.py）
    """
    try:
        script_path = os.path.join('DataGet', 'ML.py')
        if not os.path.exists(script_path):
            raise HTTPException(status_code=404, detail="找不到 ML.py")
        
        # 執行腳本
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=600  # 10分鐘超時
        )
        
        if result.returncode == 0:
            return {"status": "success", "message": "模型訓練完成"}
        else:
            return {"status": "error", "message": result.stderr}
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="模型訓練超時")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型訓練失敗: {str(e)}")

# ============================================================================
# 啟動服務器
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print(" "*15 + "台積電股價預測 API")
    print("="*60)
    print("\n啟動服務器...")
    print("API 文檔: http://localhost:8000/docs")
    print("API 端點: http://localhost:8000")
    print("\n按 Ctrl+C 停止服務器\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
