"""
診斷程式 - 檢查資料狀況
"""
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

def diagnose_data():
    print("🔍 診斷台積電資料狀況...")
    
    # 1. 檢查原始資料
    print("\n1️⃣ 檢查原始資料:")
    ticker = yf.Ticker("2330.TW")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    df = ticker.history(start=start_date, end=end_date)
    print(f"   原始資料筆數: {len(df)}")
    print(f"   日期範圍: {df.index[0].date()} 到 {df.index[-1].date()}")
    print(f"   最新收盤價: {df['Close'].iloc[-1]:.2f}")
    
    # 2. 檢查技術指標計算過程
    print("\n2️⃣ 檢查技術指標計算:")
    
    # 移動平均線
    df['MA_5'] = df['Close'].rolling(window=5).mean()
    df['MA_10'] = df['Close'].rolling(window=10).mean()
    df['MA_20'] = df['Close'].rolling(window=20).mean()
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    print(f"   計算移動平均線後: {len(df.dropna())} 筆")
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    print(f"   計算RSI後: {len(df.dropna())} 筆")
    
    # MACD
    exp1 = df['Close'].ewm(span=12).mean()
    exp2 = df['Close'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
    print(f"   計算MACD後: {len(df.dropna())} 筆")
    
    # 布林通道
    bb_period = 20
    bb_std = 2
    df['BB_Middle'] = df['Close'].rolling(window=bb_period).mean()
    bb_std_dev = df['Close'].rolling(window=bb_period).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std_dev * bb_std)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std_dev * bb_std)
    df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
    df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
    print(f"   計算布林通道後: {len(df.dropna())} 筆")
    
    # 成交量指標
    df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_MA']
    print(f"   計算成交量指標後: {len(df.dropna())} 筆")
    
    # 價格變化
    df['Price_Change'] = df['Close'].pct_change()
    print(f"   計算價格變化後: {len(df.dropna())} 筆")
    
    # 波動率
    df['Volatility_10'] = df['Close'].rolling(window=10).std()
    df['Volatility_20'] = df['Close'].rolling(window=20).std()
    print(f"   計算波動率後: {len(df.dropna())} 筆")
    
    # 最終清理
    df_clean = df.dropna()
    print(f"\n✅ 最終可用資料: {len(df_clean)} 筆")
    
    # 3. 檢查缺失值
    print("\n3️⃣ 檢查缺失值:")
    missing_info = df.isnull().sum()
    print(missing_info[missing_info > 0])
    
    return df_clean

if __name__ == "__main__":
    diagnose_data()
