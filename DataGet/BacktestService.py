import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from Predict import create_prediction_features, make_prediction

logger = logging.getLogger(__name__)

def run_backtest(model_data, df, initial_capital=100000, threshold=0.02, days=90):
    """
    執行回測
    
    Args:
        model_data: 載入的模型資料
        df: 歷史資料 DataFrame
        initial_capital: 初始資金
        threshold: 買賣門檻 (例如 0.02 代表 2%)
        days: 回測天數
        
    Returns:
        dict: 回測結果
    """
    print(f"開始回測: 最近 {days} 天, 門檻 {threshold*100}%")
    
    if len(df) < days + 50: # 需要額外數據計算指標
        return {"error": "資料不足"}
        
    # 截取回測期間
    test_data = df.tail(days).copy()
    
    cash = initial_capital
    position = 0 # 持股數量
    equity_curve = []
    trades = []
    
    wins = 0
    losses = 0
    
    # 模擬交易
    # 注意: 我們需要逐日模擬，確保只使用當日之前的資訊
    
    # 為了效能，我們先預計算所有特徵 (如果特徵不依賴未來數據)
    # 但為了嚴謹，我們應該逐日切片
    
    start_idx = len(df) - days
    
    for i in range(start_idx, len(df)-1):
        # 當前日期 (i)
        current_date = df.index[i]
        current_price = df['Close'].iloc[i]
        
        # 取得截至當日的歷史資料
        # 注意: create_prediction_features 通常需要一定長度的歷史資料
        historical_slice = df.iloc[:i+1]
        
        # 建立特徵
        features = create_prediction_features(historical_slice, model_data['features'])
        
        if features is None:
            continue
            
        # 預測明日 (i+1)
        predicted_price = make_prediction(model_data, features)
        
        if predicted_price is None:
            continue
            
        # 交易邏輯
        action = "HOLD"
        price_change_pct = (predicted_price - current_price) / current_price
        
        # 買入信號
        if price_change_pct > threshold and cash > current_price:
            # 全倉買入 (簡單起見)
            shares_to_buy = int(cash // current_price)
            if shares_to_buy > 0:
                cost = shares_to_buy * current_price
                cash -= cost
                position += shares_to_buy
                action = "BUY"
                trades.append({
                    "date": current_date.strftime('%Y-%m-%d'),
                    "type": "BUY",
                    "price": current_price,
                    "shares": shares_to_buy,
                    "reason": f"預測漲幅 {price_change_pct*100:.2f}%"
                })
        
        # 賣出信號
        elif price_change_pct < -threshold and position > 0:
            # 全倉賣出
            revenue = position * current_price
            cash += revenue
            
            # 計算損益
            last_buy = next((t for t in reversed(trades) if t['type'] == 'BUY'), None)
            if last_buy:
                profit = (current_price - last_buy['price']) * position
                if profit > 0: wins += 1
                else: losses += 1
            
            position = 0
            action = "SELL"
            trades.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "type": "SELL",
                "price": current_price,
                "shares": position, # 賣出後持有0
                "reason": f"預測跌幅 {price_change_pct*100:.2f}%"
            })
            
        # 計算當日總資產
        current_equity = cash + (position * current_price)
        equity_curve.append({
            "date": current_date.strftime('%Y-%m-%d'),
            "equity": current_equity,
            "price": current_price
        })
        
    # 結算
    final_price = df['Close'].iloc[-1]
    final_equity = cash + (position * final_price)
    total_return = (final_equity - initial_capital) / initial_capital
    
    return {
        "initialCapital": initial_capital,
        "finalEquity": final_equity,
        "totalReturn": total_return * 100,
        "totalTrades": len(trades),
        "winRate": (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0,
        "equityCurve": equity_curve,
        "trades": trades
    }
