"""
台積電(2330) 資料抓取 - 使用台灣證券交易所官方 API
更穩定、更可靠的資料來源
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import warnings
import urllib3

warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("\n" + "="*80)
print(" "*15 + "台積電(2330) 資料抓取 - TWSE 官方 API")
print("="*80 + "\n")

# ============================================================================
# 1. 台灣證券交易所 API 函數
# ============================================================================

def fetch_twse_daily_data(date_str):
    """
    從台灣證券交易所抓取單日資料
    date_str: YYYYMMDD 格式
    """
    url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date={date_str}&type=ALLBUT0999"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return None
    except Exception as e:
        # 靜默失敗，避免太多錯誤訊息
        return None

def parse_tsmc_data(data, target_date):
    """解析台積電資料"""
    if not data or 'data9' not in data:
        return None
    
    # 尋找台積電 (2330)
    for row in data['data9']:
        if len(row) > 0 and '2330' in row[0]:
            try:
                # 資料格式: [股票代號, 股票名稱, 成交股數, 成交筆數, 成交金額, 開盤價, 最高價, 最低價, 收盤價, ...]
                stock_data = {
                    'Date': pd.to_datetime(target_date),
                    'Open': float(row[5].replace(',', '')) if row[5] != '--' else None,
                    'High': float(row[6].replace(',', '')) if row[6] != '--' else None,
                    'Low': float(row[7].replace(',', '')) if row[7] != '--' else None,
                    'Close': float(row[8].replace(',', '')) if row[8] != '--' else None,
                    'Volume': int(row[2].replace(',', '')) if row[2] != '--' else 0
                }
                return stock_data
            except Exception as e:
                print(f"  ⚠ 解析資料失敗: {e}")
                return None
    
    return None

def get_twse_historical_data(start_date, end_date):
    """
    獲取歷史資料
    start_date, end_date: datetime 物件
    """
    print(f"\n【1】從台灣證券交易所抓取資料...")
    print(f"  期間: {start_date.date()} 至 {end_date.date()}")
    
    all_data = []
    current_date = start_date
    total_days = (end_date - start_date).days
    success_count = 0
    
    while current_date <= end_date:
        # 只抓取工作日
        if current_date.weekday() < 5:  # 0-4 是週一到週五
            date_str = current_date.strftime("%Y%m%d")
            
            # 顯示進度
            progress = ((current_date - start_date).days / total_days) * 100
            print(f"\r  進度: {progress:.1f}% - {date_str}", end='', flush=True)
            
            # 抓取資料
            data = fetch_twse_daily_data(date_str)
            if data:
                stock_data = parse_tsmc_data(data, current_date)
                if stock_data and stock_data['Close'] is not None:
                    all_data.append(stock_data)
                    success_count += 1
            
            # 避免請求太頻繁
            time.sleep(3)  # TWSE API 建議間隔 3 秒
        
        current_date += timedelta(days=1)
    
    print(f"\n✓ 成功抓取 {success_count} 個交易日的資料")
    
    if all_data:
        df = pd.DataFrame(all_data)
        df.set_index('Date', inplace=True)
        df.sort_index(inplace=True)
        return df
    else:
        return None

# ============================================================================
# 2. 計算技術指標 (與原版一致)
# ============================================================================

def calculate_technical_indicators(df):
    """計算技術指標"""
    print(f"\n【2】計算技術指標...")
    
    try:
        data = df.copy()
        
        # 移動平均線
        print("  計算移動平均線...")
        data['MA_5'] = data['Close'].rolling(window=5, min_periods=1).mean()
        data['MA_10'] = data['Close'].rolling(window=10, min_periods=1).mean()
        data['MA_20'] = data['Close'].rolling(window=20, min_periods=1).mean()
        data['MA_50'] = data['Close'].rolling(window=50, min_periods=1).mean()
        
        # MACD
        print("  計算MACD...")
        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
        data['MACD'] = exp1 - exp2
        data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
        data['MACD_Hist'] = data['MACD'] - data['MACD_Signal']
        
        # RSI
        print("  計算RSI...")
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # 布林通道
        print("  計算布林通道...")
        data['BB_Middle'] = data['Close'].rolling(window=20, min_periods=1).mean()
        bb_std = data['Close'].rolling(window=20, min_periods=1).std()
        data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
        data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
        
        # KD指標
        print("  計算KD...")
        low_min = data['Low'].rolling(window=9, min_periods=1).min()
        high_max = data['High'].rolling(window=9, min_periods=1).max()
        data['RSV'] = (data['Close'] - low_min) / (high_max - low_min) * 100
        data['K'] = data['RSV'].ewm(com=2, adjust=False).mean()
        data['D'] = data['K'].ewm(com=2, adjust=False).mean()
        
        # 成交量指標
        print("  計算成交量指標...")
        data['Volume_MA_5'] = data['Volume'].rolling(window=5, min_periods=1).mean()
        data['Volume_MA_20'] = data['Volume'].rolling(window=20, min_periods=1).mean()
        
        # 價格變化
        data['Price_Change'] = data['Close'].diff()
        data['Price_Change_Pct'] = data['Close'].pct_change()
        
        print(f"✓ 技術指標計算完成")
        print(f"  最終資料筆數: {len(data)}")
        print(f"  特徵欄位數: {len(data.columns)}")
        
        return data
        
    except Exception as e:
        print(f"✗ 計算失敗: {e}")
        import traceback
        traceback.print_exc()
        return df

# ============================================================================
# 3. 儲存資料
# ============================================================================

def save_data(df, folder_path):
    """儲存資料到指定資料夾"""
    print(f"\n【3】儲存資料...")
    
    try:
        # 儲存為 LSTM 格式
        lstm_file = os.path.join(folder_path, "tsmc_lstm_data.csv")
        df.to_csv(lstm_file, encoding='utf-8-sig')
        print(f"✓ LSTM資料: {lstm_file}")
        
        # 儲存技術指標資料
        tech_file = os.path.join(folder_path, "tsmc_technical_data.csv")
        df.to_csv(tech_file, encoding='utf-8-sig')
        print(f"✓ 技術指標資料: {tech_file}")
        
        # 儲存資料說明
        info_file = os.path.join(folder_path, "data_info.txt")
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write("台積電(2330) 股價資料\n")
            f.write("="*60 + "\n\n")
            f.write(f"資料來源: 台灣證券交易所 (TWSE)\n")
            f.write(f"抓取時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"資料期間: {df.index[0].date()} 至 {df.index[-1].date()}\n")
            f.write(f"交易日數: {len(df)}\n")
            f.write(f"欄位數量: {len(df.columns)}\n\n")
            f.write("欄位說明:\n")
            f.write("-" * 40 + "\n")
            for col in df.columns:
                f.write(f"  • {col}\n")
        
        print(f"✓ 資料說明: {info_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ 儲存失敗: {e}")
        return False

# ============================================================================
# 4. 主程式
# ============================================================================

def main():
    """主程式"""
    
    # 建立時間戳記資料夾
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    folder_path = f"../Data/{timestamp}"
    os.makedirs(folder_path, exist_ok=True)
    
    print(f"📁 建立輸出資料夾: {folder_path}")
    print(f"📅 時間戳記: {timestamp}")
    
    # 設定日期範圍 (最近2年)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    
    # 抓取資料
    df = get_twse_historical_data(start_date, end_date)
    
    if df is None or df.empty:
        print("\n✗ 無法抓取資料，程式結束")
        return
    
    print(f"\n資料摘要:")
    print(f"  期間: {df.index[0].date()} 至 {df.index[-1].date()}")
    print(f"  交易日數: {len(df)}")
    print(f"  最新收盤價: {df['Close'].iloc[-1]:.2f}")
    
    # 計算技術指標
    df_with_indicators = calculate_technical_indicators(df)
    
    # 儲存資料
    success = save_data(df_with_indicators, folder_path)
    
    if success:
        print("\n" + "="*80)
        print(" "*25 + "資料抓取完成！")
        print("="*80)
        print(f"\n📁 資料儲存位置: {os.path.abspath(folder_path)}")
        print(f"📊 資料摘要:")
        print(f"   • 資料來源: 台灣證券交易所 (TWSE)")
        print(f"   • 交易日數: {len(df_with_indicators)}")
        print(f"   • 期間: {df_with_indicators.index[0].date()} 至 {df_with_indicators.index[-1].date()}")
        print(f"   • 最新收盤價: NT${df_with_indicators['Close'].iloc[-1]:.2f}")
        print(f"\n✅ 可以開始訓練模型了！")
    else:
        print("\n✗ 資料儲存失敗")

if __name__ == "__main__":
    try:
        main()
        input("\n按 Enter 鍵結束...")
    except KeyboardInterrupt:
        print("\n\n程式被使用者中斷")
    except Exception as e:
        print(f"\n✗ 程式執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 鍵結束...")
