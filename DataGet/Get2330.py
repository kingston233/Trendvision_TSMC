"""
修正版 Get2330.py - 台積電(2330) 資料抓取系統 (路徑統一版)
專門負責抓取和處理資料，儲存為CSV檔案供LSTM使用
路徑統一為: Data/YYYYMMDDHHMM (與Predict.py一致)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import os

# 忽略警告
warnings.filterwarnings('ignore')

print("\n" + "="*80)
print(" "*15 + "台積電(2330) 資料抓取")
print("="*80 + "\n")

# ============================================================================
# 0. 建立時間戳記資料夾 (統一路徑結構)
# ============================================================================

def create_timestamp_folder():
    """建立時間戳記資料夾 - 與Predict.py路徑結構一致"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    
    # 統一路徑結構: Data/YYYYMMDDHHMM (與Predict.py搜尋路徑一致)
    folder_path = f"../Data/{timestamp}"
    
    # 確保資料夾存在
    os.makedirs(folder_path, exist_ok=True)
    
    print(f"📁 建立輸出資料夾: {folder_path}")
    print(f"📅 時間戳記: {timestamp}")
    print(f"🔗 路徑結構與 Predict.py 一致")
    
    return folder_path, timestamp

# ============================================================================
# 1. 資料抓取
# ============================================================================

def get_tsmc_data(period="2y"):
    """抓取台積電基本資料 - 改進版"""
    print(f"\n【1】正在抓取台積電資料 ({period})...")
    
    try:
        # 嘗試多個代碼
        tickers_to_try = ["2330.TW", "2330.TWO", "TSM"]
        
        for symbol in tickers_to_try:
            try:
                print(f"  嘗試連接: {symbol}")
                ticker = yf.Ticker(symbol)
                
                # 先測試連接
                test_data = ticker.history(period="5d")
                
                if test_data.empty:
                    print(f"  ⚠ {symbol} 無資料")
                    continue
                
                # 測試成功，獲取完整歷史資料
                print(f"  ✓ 成功連接: {symbol}")
                print(f"  正在下載 {period} 的歷史資料...")
                hist = ticker.history(period=period)
                
                if hist.empty:
                    print(f"  ⚠ 使用日期範圍方法...")
                    from datetime import timedelta
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=730)  # 2年
                    hist = ticker.history(start=start_date, end=end_date)
                
                if not hist.empty:
                    # 修正時區
                    if hasattr(hist.index, 'tz') and hist.index.tz is not None:
                        hist.index = hist.index.tz_localize(None)
                    
                    # 獲取基本面資料
                    print("  抓取基本面資料...")
                    try:
                        info = ticker.info
                    except:
                        info = {}
                    
                    print(f"✓ 成功抓取 {len(hist)} 筆歷史資料")
                    print(f"  期間: {hist.index[0].date()} 至 {hist.index[-1].date()}")
                    
                    return hist, info, ticker
                else:
                    print(f"  ✗ {symbol} 無法獲取歷史資料")
                    continue
                    
            except Exception as e:
                print(f"  ✗ {symbol} 連接失敗: {e}")
                continue
        
        print("✗ 所有代碼都無法連接")
        return None, None, None
        
    except Exception as e:
        print(f"✗ 資料抓取失敗: {e}")
        return None, None, None

# ============================================================================
# 2. 計算技術指標 (與Predict.py完全一致)
# ============================================================================

def calculate_technical_indicators(hist):
    """計算技術指標 - 與Predict.py保持完全一致"""
    print("\n【2】計算技術指標 (與Predict.py一致)...")
    
    try:
        df = hist.copy()
        data_length = len(df)
        print(f"  開始計算，原始資料: {data_length} 筆")
        
        # === 移動平均線 (與Predict.py一致) ===
        print("  計算移動平均線...")
        df['MA_5'] = df['Close'].rolling(window=5, min_periods=1).mean()
        df['MA_10'] = df['Close'].rolling(window=10, min_periods=1).mean()
        df['MA_20'] = df['Close'].rolling(window=20, min_periods=1).mean()
        df['MA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()
        
        # === MACD (與Predict.py一致) ===
        print("  計算MACD...")
        exp1 = df['Close'].ewm(span=12, min_periods=1).mean()
        exp2 = df['Close'].ewm(span=26, min_periods=1).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9, min_periods=1).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']  # 與Predict.py一致
        
        # === 成交量指標 (與Predict.py一致) ===
        print("  計算成交量指標...")
        vol_period = min(20, data_length // 2)
        vol_period = max(vol_period, 5)
        
        df['Volume_MA'] = df['Volume'].rolling(window=vol_period, min_periods=1).mean()
        df['Volume_Ratio'] = df['Volume'] / (df['Volume_MA'] + 1e-8)
        
        # === 價格變化指標 (與Predict.py一致) ===
        print("  計算價格變化指標...")
        df['Price_Change'] = df['Close'].pct_change().fillna(0)
        df['Price_Change_5'] = df['Close'].pct_change(periods=5).fillna(0)  # 與Predict.py一致
        
        # === 波動率指標 (與Predict.py一致) ===
        print("  計算波動率指標...")
        df['Volatility_10'] = df['Close'].rolling(window=min(10, data_length//2), min_periods=1).std()
        df['Volatility_20'] = df['Close'].rolling(window=min(20, data_length//2), min_periods=1).std()
        
        # === 高低價百分比 (與Predict.py一致) ===
        print("  計算高低價指標...")
        df['High_Low_Pct'] = (df['High'] - df['Low']) / df['Close']
        
        # === RSI指標 (額外技術指標) ===
        print("  計算RSI...")
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
            rs = gain / (loss + 1e-8)  # 避免除零
            df['RSI'] = 100 - (100 / (1 + rs))
        else:
            df['RSI'] = 50  # 預設中性值
        
        # === 布林通道 (額外技術指標) ===
        print("  計算布林通道...")
        if len(df) >= 20:
            bb_period = 20
            bb_std = 2
            df['BB_Middle'] = df['Close'].rolling(window=bb_period, min_periods=1).mean()
            bb_std_dev = df['Close'].rolling(window=bb_period, min_periods=1).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std_dev * bb_std)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std_dev * bb_std)
            df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'] + 1e-8)
            df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / (df['BB_Middle'] + 1e-8)
        else:
            df['BB_Middle'] = df['Close']
            df['BB_Upper'] = df['Close'] * 1.02
            df['BB_Lower'] = df['Close'] * 0.98
            df['BB_Position'] = 0.5
            df['BB_Width'] = 0.04
        
        # === 成交量移動平均 (額外指標) ===
        print("  計算額外成交量指標...")
        df['Volume_MA_5'] = df['Volume'].rolling(window=5, min_periods=1).mean()
        df['Volume_MA_20'] = df['Volume'].rolling(window=20, min_periods=1).mean()
        
        # === 資料清理 (與Predict.py一致) ===
        print("  清理和驗證資料...")
        df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
        df = df.replace([np.inf, -np.inf], 0)
        
        print(f"✓ 技術指標計算完成，最終資料: {len(df)} 筆")
        print(f"  總共 {len(df.columns)} 個特徵")
        
        return df
        
    except Exception as e:
        print(f"✗ 技術指標計算失敗: {e}")
        import traceback
        traceback.print_exc()
        return hist

# ============================================================================
# 3. 整理基本面資料
# ============================================================================

def get_fundamental_data(info):
    """整理基本面資料"""
    print("\n【3】整理基本面資料...")
    
    try:
        fundamental = {}
        
        # 基本資訊
        fundamental['Company_Name'] = info.get('longName', 'Taiwan Semiconductor Manufacturing Company Limited')
        fundamental['Sector'] = info.get('sector', 'Technology')
        fundamental['Industry'] = info.get('industry', 'Semiconductors')
        
        # 估值指標
        fundamental['PE_Ratio'] = info.get('trailingPE', 'N/A')
        fundamental['Forward_PE'] = info.get('forwardPE', 'N/A')
        fundamental['PEG_Ratio'] = info.get('pegRatio', 'N/A')
        fundamental['Price_to_Book'] = info.get('priceToBook', 'N/A')
        fundamental['Price_to_Sales'] = info.get('priceToSalesTrailing12Months', 'N/A')
        
        # 獲利能力
        fundamental['EPS'] = info.get('trailingEps', 'N/A')
        fundamental['Revenue'] = info.get('totalRevenue', 'N/A')
        fundamental['Profit_Margin'] = info.get('profitMargins', 'N/A')
        fundamental['Operating_Margin'] = info.get('operatingMargins', 'N/A')
        fundamental['ROE'] = info.get('returnOnEquity', 'N/A')
        fundamental['ROA'] = info.get('returnOnAssets', 'N/A')
        
        # 市值和規模
        fundamental['Market_Cap'] = info.get('marketCap', 'N/A')
        fundamental['Enterprise_Value'] = info.get('enterpriseValue', 'N/A')
        fundamental['Shares_Outstanding'] = info.get('sharesOutstanding', 'N/A')
        
        # 股息
        fundamental['Dividend_Yield'] = info.get('dividendYield', 'N/A')
        fundamental['Dividend_Rate'] = info.get('dividendRate', 'N/A')
        fundamental['Payout_Ratio'] = info.get('payoutRatio', 'N/A')
        
        # 財務健康
        fundamental['Book_Value'] = info.get('bookValue', 'N/A')
        fundamental['Debt_to_Equity'] = info.get('debtToEquity', 'N/A')
        fundamental['Current_Ratio'] = info.get('currentRatio', 'N/A')
        
        # 成長率
        fundamental['Revenue_Growth'] = info.get('revenueGrowth', 'N/A')
        fundamental['Earnings_Growth'] = info.get('earningsGrowth', 'N/A')
        
        print("✓ 基本面資料整理完成")
        
        return fundamental
        
    except Exception as e:
        print(f"✗ 基本面資料整理失敗: {e}")
        return {}

# ============================================================================
# 4. 儲存資料 (統一路徑結構)
# ============================================================================

def save_data_for_lstm(df, fundamental, output_folder, timestamp):
    """儲存資料供LSTM使用 - 統一路徑結構"""
    print(f"\n【4】儲存資料 (統一路徑結構)...")
    
    try:
        # === 1. 儲存LSTM訓練資料 (主要檔案) ===
        lstm_data_file = f"{output_folder}/tsmc_lstm_data.csv"
        df.to_csv(lstm_data_file, encoding='utf-8-sig')
        print(f"✓ LSTM訓練資料: {lstm_data_file}")
        
        # === 2. 儲存技術指標資料 ===
        technical_file = f"{output_folder}/tsmc_technical_data.csv"
        df.to_csv(technical_file, encoding='utf-8-sig')
        print(f"✓ 技術指標資料: {technical_file}")
        
        # === 3. 儲存基本面資料 ===
        fund_file = f"{output_folder}/tsmc_fundamental_data.csv"
        fund_df = pd.DataFrame([fundamental])
        fund_df.to_csv(fund_file, encoding='utf-8-sig', index=False)
        print(f"✓ 基本面資料: {fund_file}")
        
        # === 4. 儲存特徵說明 (與Predict.py相容) ===
        features_file = f"{output_folder}/features_description.txt"
        with open(features_file, 'w', encoding='utf-8') as f:
            f.write("台積電股價預測 - 特徵說明\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"資料更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"時間戳記: {timestamp}\n")
            f.write(f"資料筆數: {len(df)}\n")
            f.write(f"特徵數量: {len(df.columns)}\n")
            f.write(f"路徑結構: Data/{timestamp}/ (與Predict.py一致)\n\n")
            
            f.write("技術指標特徵列表 (與Predict.py相容):\n")
            f.write("-" * 40 + "\n")
            
            # 核心特徵 (與Predict.py完全一致)
            core_features = [
                'Open', 'High', 'Low', 'Close', 'Volume',
                'MA_5', 'MA_10', 'MA_20', 'MA_50',
                'MACD', 'MACD_Signal', 'MACD_Histogram',
                'Volume_MA', 'Volume_Ratio',
                'Price_Change', 'Price_Change_5',
                'Volatility_10', 'Volatility_20',
                'High_Low_Pct'
            ]
            
            f.write("核心特徵 (與Predict.py一致):\n")
            for i, feature in enumerate(core_features, 1):
                if feature in df.columns:
                    f.write(f"  {i:2d}. {feature} ✓\n")
                else:
                    f.write(f"  {i:2d}. {feature} ✗ (缺失)\n")
            
            f.write(f"\n額外特徵:\n")
            extra_features = [col for col in df.columns if col not in core_features]
            for i, col in enumerate(extra_features, len(core_features)+1):
                f.write(f"  {i:2d}. {col}\n")
            
            f.write(f"\n基本面資料:\n")
            f.write("-" * 30 + "\n")
            for key, value in fundamental.items():
                f.write(f"{key}: {value}\n")
        
        print(f"✓ 特徵說明: {features_file}")
        
        # === 5. 儲存Excel版本 ===
        try:
            excel_file = f"{output_folder}/tsmc_complete_data.xlsx"
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='技術指標', index=True)
                fund_df.to_excel(writer, sheet_name='基本面', index=False)
                
                # 資料摘要
                summary_data = {
                    '項目': ['資料筆數', '特徵數量', '開始日期', '結束日期', '最新收盤價', 
                            '時間戳記', '路徑結構', 'Predict.py相容性'],
                    '數值': [len(df), len(df.columns), str(df.index[0].date()), 
                            str(df.index[-1].date()), f"{df['Close'].iloc[-1]:.2f}", 
                            timestamp, f"Data/{timestamp}/", " 完全相容"]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='資料摘要', index=False)
            
            print(f"✓ Excel完整資料: {excel_file}")
            
        except Exception as excel_error:
            print(f"⚠ Excel儲存失敗: {excel_error}")
        
        # === 6. 建立路徑相容性檔案 ===
        compatibility_file = f"{output_folder}/path_compatibility.txt"
        with open(compatibility_file, 'w', encoding='utf-8') as f:
            f.write("路徑相容性說明\n")
            f.write("=" * 30 + "\n\n")
            f.write(f"建立時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"時間戳記: {timestamp}\n")
            f.write(f"資料夾路徑: {output_folder}\n\n")
            f.write("與其他程式的相容性:\n")
            f.write(f" Predict.py: 完全相容 (搜尋路徑: Data/{timestamp}/)\n")
            f.write(f" ML.py: 相容 (可讀取 tsmc_lstm_data.csv)\n")
            f.write(f" 路徑結構: 統一使用 Data/YYYYMMDDHHMM/ 格式\n")
        
        print(f"✓ 路徑相容性檔案: {compatibility_file}")
        
        # === 顯示資料統計 ===
        print(f"\n📊 資料統計:")
        print(f"   • 總資料筆數: {len(df)}")
        print(f"   • 特徵數量: {len(df.columns)}")
        print(f"   • 資料期間: {df.index[0].date()} 至 {df.index[-1].date()}")
        print(f"   • 最新收盤價: {df['Close'].iloc[-1]:.2f} TWD")
        print(f"   • 平均成交量: {df['Volume'].mean():,.0f}")
        print(f"   • 路徑結構: {output_folder}")
        
        # === 與Predict.py相容性檢查 ===
        print(f"\n Predict.py 相容性檢查:")
        predict_required_features = [
            'Close', 'Volume', 'MA_5', 'MA_10', 'MA_20', 'MA_50',
            'MACD', 'MACD_Signal', 'MACD_Histogram',
            'Volume_MA', 'Volume_Ratio',
            'Price_Change', 'Price_Change_5',
            'Volatility_10', 'Volatility_20',
            'High_Low_Pct'
        ]
        
        missing_features = [f for f in predict_required_features if f not in df.columns]
        if missing_features:
            print(f"     缺少特徵: {missing_features}")
        else:
            print(f"    所有必要特徵都已包含")
        
        print(f"    路徑結構: Data/{timestamp}/ (Predict.py可搜尋)")
        print(f"    檔案格式: CSV (Predict.py可讀取)")
        
        return lstm_data_file
        
    except Exception as e:
        print(f"✗ 資料儲存失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# 5. 主程式
# ============================================================================

def main():
    """主程式 - 資料抓取和處理 (統一路徑版)"""
    
    print("開始執行台積電資料抓取 (路徑統一版)...")
    
    # 0. 建立時間戳記資料夾 (統一路徑結構)
    output_folder, timestamp = create_timestamp_folder()
    
    # 1. 抓取資料
    hist, info, ticker = get_tsmc_data(period="2y")  # 抓取2年資料
    if hist is None:
        print("\n✗ 無法抓取資料，程式結束")
        return None
    
    # 2. 計算技術指標 (與Predict.py一致)
    df = calculate_technical_indicators(hist)
    
    # 3. 整理基本面資料
    fundamental = get_fundamental_data(info)
    
    # 4. 儲存資料 (統一路徑結構)
    lstm_file = save_data_for_lstm(df, fundamental, output_folder, timestamp)
    
    if lstm_file:
        print("\n" + "="*80)
        print(" "*15 + "資料抓取完成！(路徑統一版)")
        print("="*80)
        print(f"\n📁 輸出資料夾: {output_folder}")
        print(f"時間戳記: {timestamp}")
        print(f"路徑結構: Data/{timestamp}/ (與Predict.py一致)")
        
        
        print(f"\n 所有檔案已儲存到: {output_folder}")
        
        return output_folder, timestamp
    else:
        print("\n 資料處理失敗")
        return None, None

# 執行主程式
if __name__ == "__main__":
    try:
        result = main()

        input("\n按 Enter 鍵結束...")
    except KeyboardInterrupt:
        print("\n\n程式被使用者中斷")
    except Exception as e:
        print(f"\n✗ 程式執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 鍵結束...")
