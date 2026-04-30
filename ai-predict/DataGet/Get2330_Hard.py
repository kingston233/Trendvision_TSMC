"""
台積電(2330) 機器學習資料抓取系統 - 儲存到Data資料夾
專門為機器學習預測準備的資料集
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import os

# 忽略警告訊息
warnings.filterwarnings('ignore')

# 設定 pandas 顯示選項
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

print("\n" + "="*80)
print(" "*15 + "台積電(2330) 機器學習資料抓取系統")
print(" "*20 + "儲存到 Data 資料夾")
print("="*80 + "\n")

# ============================================================================
# 1. 設定資料夾路徑
# ============================================================================

def setup_data_folder():
    """設定資料夾路徑"""
    # 使用現有的 Data 資料夾
    data_folder = "Data"
    
    try:
        # 確保資料夾存在
        os.makedirs(data_folder, exist_ok=True)
        print(f"✓ 使用資料夾: {os.path.abspath(data_folder)}")
        return data_folder
    except Exception as e:
        print(f"✗ 設定資料夾失敗: {e}")
        return None

# ============================================================================
# 2. 建立台積電股票物件
# ============================================================================

def create_ticker():
    """建立台積電 Ticker 物件"""
    print("正在連接 Yahoo Finance...")
    
    try:
        # 嘗試多個代碼
        tickers_to_try = ["2330.TW", "2330.TWO", "TSM"]
        
        for symbol in tickers_to_try:
            try:
                print(f"嘗試連接: {symbol}")
                ticker = yf.Ticker(symbol)
                
                # 測試連接
                test_data = ticker.history(period="5d")
                
                if not test_data.empty:
                    print(f"✓ 成功連接: {symbol}")
                    return ticker, symbol
                else:
                    print(f"⚠ {symbol} 無資料")
                    
            except Exception as e:
                print(f"✗ {symbol} 連接失敗: {e}")
                continue
        
        print("✗ 所有代碼都無法連接")
        return None, None
        
    except Exception as e:
        print(f"✗ 連接失敗: {e}")
        return None, None

# ============================================================================
# 3. 獲取歷史資料
# ============================================================================

def get_historical_data(ticker, period="2y"):
    """獲取足夠的歷史資料用於機器學習"""
    print(f"\n{'='*80}")
    print("【1】獲取歷史股價資料")
    print(f"{'='*80}")
    
    try:
        print(f"正在下載 {period} 的歷史資料...")
        
        # 基本方法
        hist = ticker.history(period=period)
        
        if hist.empty:
            print("⚠ 使用日期範圍方法...")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)  # 2年
            hist = ticker.history(start=start_date, end=end_date)
        
        if not hist.empty:
            # 修正時區問題
            if hist.index.tz is not None:
                hist.index = hist.index.tz_localize(None)
            
            print(f"✓ 成功獲取 {len(hist)} 筆歷史資料")
            print(f"  期間: {hist.index[0].date()} 至 {hist.index[-1].date()}")
            return hist
        else:
            print("✗ 無法獲取歷史資料")
            return None
            
    except Exception as e:
        print(f"✗ 獲取歷史資料失敗: {e}")
        return None

# ============================================================================
# 4. 計算機器學習特徵
# ============================================================================

def calculate_ml_features(hist):
    """計算機器學習特徵"""
    print(f"\n{'='*80}")
    print("【2】計算機器學習特徵")
    print(f"{'='*80}")
    
    try:
        df = hist.copy()
        
        print("正在計算機器學習特徵...")
        
        # ========== 技術指標特徵 ==========
        
        # 1. 移動平均線
        print("  計算移動平均線...")
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # 2. 指數移動平均線
        print("  計算指數移動平均線...")
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # 3. RSI
        print("  計算RSI...")
        if len(df) >= 14:
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
        
        # 4. MACD
        print("  計算MACD...")
        if len(df) >= 26:
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # 5. 布林通道
        print("  計算布林通道...")
        if len(df) >= 20:
            df['BB_Middle'] = df['Close'].rolling(window=20).mean()
            bb_std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
            df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
            df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # ========== 價格衍生特徵 ==========
        
        # 6. 價格變化
        print("  計算價格變化特徵...")
        df['Price_Change'] = df['Close'].diff()
        df['Price_Change_Pct'] = df['Close'].pct_change()
        df['High_Low_Pct'] = (df['High'] - df['Low']) / df['Low']
        df['Open_Close_Pct'] = (df['Close'] - df['Open']) / df['Open']
        
        # 7. 滯後特徵
        print("  計算滯後特徵...")
        df['Close_Lag_1'] = df['Close'].shift(1)
        df['Close_Lag_2'] = df['Close'].shift(2)
        df['Close_Lag_3'] = df['Close'].shift(3)
        df['Volume_Lag_1'] = df['Volume'].shift(1)
        
        # 8. 滾動統計
        print("  計算滾動統計...")
        df['Close_Std_5'] = df['Close'].rolling(window=5).std()
        df['Close_Std_20'] = df['Close'].rolling(window=20).std()
        df['Volume_MA_5'] = df['Volume'].rolling(window=5).mean()
        df['Volume_MA_20'] = df['Volume'].rolling(window=20).mean()
        
        # ========== 預測目標 ==========
        
        # 9. 預測目標
        print("  設定預測目標...")
        df['Next_Day_Close'] = df['Close'].shift(-1)
        df['Next_Day_High'] = df['High'].shift(-1)
        df['Next_Day_Low'] = df['Low'].shift(-1)
        df['Next_Day_Direction'] = (df['Next_Day_Close'] > df['Close']).astype(int)
        df['Next_Day_Change_Pct'] = (df['Next_Day_Close'] - df['Close']) / df['Close']
        
        # 多天預測目標
        df['Next_3Day_Close'] = df['Close'].shift(-3)
        df['Next_5Day_Close'] = df['Close'].shift(-5)
        df['Next_3Day_Direction'] = (df['Next_3Day_Close'] > df['Close']).astype(int)
        df['Next_5Day_Direction'] = (df['Next_5Day_Close'] > df['Close']).astype(int)
        
        # ========== 清理資料 ==========
        
        # 移除不完整的資料
        df = df.dropna()
        
        print(f"✓ 特徵計算完成！")
        print(f"  最終資料筆數: {len(df)}")
        print(f"  特徵欄位數: {len(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"✗ 計算特徵失敗: {e}")
        import traceback
        traceback.print_exc()
        return hist

# ============================================================================
# 5. 準備不同的資料集
# ============================================================================

def prepare_datasets(df):
    """準備不同用途的資料集"""
    print(f"\n{'='*80}")
    print("【3】準備機器學習資料集")
    print(f"{'='*80}")
    
    try:
        # 基本特徵 (第一優先)
        basic_features = [
            'Open', 'High', 'Low', 'Close', 'Volume',
            'SMA_5', 'SMA_20', 'RSI', 'MACD',
            'Price_Change_Pct', 'Close_Lag_1'
        ]
        
        # 進階特徵
        advanced_features = basic_features + [
            'SMA_10', 'SMA_50', 'EMA_12', 'EMA_26',
            'MACD_Signal', 'MACD_Histogram',
            'BB_Upper', 'BB_Lower', 'BB_Position',
            'High_Low_Pct', 'Open_Close_Pct',
            'Close_Lag_2', 'Close_Lag_3', 'Volume_Lag_1',
            'Close_Std_5', 'Volume_MA_5'
        ]
        
        # 預測目標
        targets_1day = ['Next_Day_Close', 'Next_Day_Direction', 'Next_Day_Change_Pct']
        targets_multi = targets_1day + ['Next_3Day_Direction', 'Next_5Day_Direction']
        
        # 檢查可用特徵
        available_basic = [col for col in basic_features if col in df.columns]
        available_advanced = [col for col in advanced_features if col in df.columns]
        available_targets_1day = [col for col in targets_1day if col in df.columns]
        available_targets_multi = [col for col in targets_multi if col in df.columns]
        
        print(f"可用基本特徵: {len(available_basic)}/{len(basic_features)}")
        print(f"可用進階特徵: {len(available_advanced)}/{len(advanced_features)}")
        print(f"可用1日目標: {len(available_targets_1day)}/{len(targets_1day)}")
        print(f"可用多日目標: {len(available_targets_multi)}/{len(targets_multi)}")
        
        # 建立資料集
        datasets = {}
        
        # 基本資料集
        if available_basic and available_targets_1day:
            X_basic = df[available_basic].copy()
            y_basic = df[available_targets_1day].copy()
            # 移除最後幾行
            X_basic = X_basic[:-5]
            y_basic = y_basic[:-5]
            datasets['basic'] = {
                'X': X_basic,
                'y': y_basic,
                'features': available_basic,
                'targets': available_targets_1day
            }
        
        # 進階資料集
        if available_advanced and available_targets_multi:
            X_advanced = df[available_advanced].copy()
            y_advanced = df[available_targets_multi].copy()
            # 移除最後幾行
            X_advanced = X_advanced[:-5]
            y_advanced = y_advanced[:-5]
            datasets['advanced'] = {
                'X': X_advanced,
                'y': y_advanced,
                'features': available_advanced,
                'targets': available_targets_multi
            }
        
        print(f"\n建立的資料集:")
        for name, data in datasets.items():
            print(f"  {name}: X{data['X'].shape}, y{data['y'].shape}")
        
        return datasets, df
        
    except Exception as e:
        print(f"✗ 準備資料集失敗: {e}")
        return None, df

# ============================================================================
# 6. 儲存資料到Data資料夾
# ============================================================================

def save_to_data_folder(datasets, full_df, data_folder, symbol):
    """儲存資料到Data資料夾"""
    print(f"\n{'='*80}")
    print("【4】儲存資料到 Data 資料夾")
    print(f"{'='*80}")
    
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 儲存完整資料
        full_file = os.path.join(data_folder, f"tsmc_ml_full_data_{timestamp}.csv")
        full_df.to_csv(full_file, encoding='utf-8-sig', index=True)
        print(f"✓ 完整資料: {full_file}")
        
        # 2. 儲存各個資料集
        for dataset_name, dataset in datasets.items():
            X = dataset['X']
            y = dataset['y']
            features = dataset['features']
            targets = dataset['targets']
            
            # 特徵矩陣
            X_file = os.path.join(data_folder, f"tsmc_ml_{dataset_name}_features_{timestamp}.csv")
            X.to_csv(X_file, encoding='utf-8-sig', index=True)
            print(f"✓ {dataset_name}特徵矩陣: {X_file}")
            
            # 目標矩陣
            y_file = os.path.join(data_folder, f"tsmc_ml_{dataset_name}_targets_{timestamp}.csv")
            y.to_csv(y_file, encoding='utf-8-sig', index=True)
            print(f"✓ {dataset_name}目標矩陣: {y_file}")
        
        # 3. 儲存資料說明
        info_file = os.path.join(data_folder, f"tsmc_ml_info_{timestamp}.txt")
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write("台積電(2330) 機器學習資料集說明\n")
            f.write("="*60 + "\n\n")
            f.write(f"資料抓取時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"股票代碼: {symbol}\n")
            f.write(f"資料期間: {full_df.index[0].date()} 至 {full_df.index[-1].date()}\n")
            f.write(f"總筆數: {len(full_df)}\n\n")
            
            for dataset_name, dataset in datasets.items():
                f.write(f"{dataset_name.upper()} 資料集:\n")
                f.write("-" * 40 + "\n")
                f.write(f"特徵數: {len(dataset['features'])}\n")
                f.write(f"目標數: {len(dataset['targets'])}\n")
                f.write(f"樣本數: {len(dataset['X'])}\n")
                f.write(f"特徵列表: {', '.join(dataset['features'])}\n")
                f.write(f"目標列表: {', '.join(dataset['targets'])}\n\n")
            
            f.write("檔案說明:\n")
            f.write("-" * 40 + "\n")
            f.write(f"tsmc_ml_full_data_{timestamp}.csv - 完整資料集\n")
            for dataset_name in datasets.keys():
                f.write(f"tsmc_ml_{dataset_name}_features_{timestamp}.csv - {dataset_name}特徵矩陣\n")
                f.write(f"tsmc_ml_{dataset_name}_targets_{timestamp}.csv - {dataset_name}目標矩陣\n")
        
        print(f"✓ 資料說明: {info_file}")
        
        # 4. 儲存Excel版本 (如果可能)
        try:
            excel_file = os.path.join(data_folder, f"tsmc_ml_dataset_{timestamp}.xlsx")
            
            # 準備Excel資料
            full_df_excel = full_df.copy()
            if full_df_excel.index.tz is not None:
                full_df_excel.index = full_df_excel.index.tz_localize(None)
            
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # 完整資料
                full_df_excel.to_excel(writer, sheet_name='完整資料', index=True)
                
                # 各資料集
                for dataset_name, dataset in datasets.items():
                    X_excel = dataset['X'].copy()
                    y_excel = dataset['y'].copy()
                    
                    if X_excel.index.tz is not None:
                        X_excel.index = X_excel.index.tz_localize(None)
                    if y_excel.index.tz is not None:
                        y_excel.index = y_excel.index.tz_localize(None)
                    
                    X_excel.to_excel(writer, sheet_name=f'{dataset_name}_特徵', index=True)
                    y_excel.to_excel(writer, sheet_name=f'{dataset_name}_目標', index=True)
                
                # 說明頁
                info_data = []
                info_data.append(['資料抓取時間', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                info_data.append(['股票代碼', symbol])
                info_data.append(['資料期間', f"{full_df.index[0].date()} 至 {full_df.index[-1].date()}"])
                info_data.append(['總筆數', len(full_df)])
                
                for dataset_name, dataset in datasets.items():
                    info_data.append([f'{dataset_name}_特徵數', len(dataset['features'])])
                    info_data.append([f'{dataset_name}_樣本數', len(dataset['X'])])
                
                info_df = pd.DataFrame(info_data, columns=['項目', '值'])
                info_df.to_excel(writer, sheet_name='資料說明', index=False)
            
            print(f"✓ Excel檔案: {excel_file}")
            
        except Exception as excel_error:
            print(f"⚠ Excel儲存失敗: {excel_error}")
        
        return True
        
    except Exception as e:
        print(f"✗ 儲存失敗: {e}")
        return False

# ============================================================================
# 7. 主程式
# ============================================================================

def main():
    """主程式"""
    
    # 設定資料夾
    data_folder = setup_data_folder()
    if data_folder is None:
        print("\n✗ 無法設定資料夾，程式結束")
        return
    
    # 建立連接
    ticker, symbol = create_ticker()
    if ticker is None:
        print("\n✗ 無法建立連接，程式結束")
        return
    
    print(f"\n使用股票代碼: {symbol}")
    
    # 獲取歷史資料
    hist = get_historical_data(ticker, period="2y")
    if hist is None or hist.empty:
        print("\n✗ 無法獲取歷史資料，程式結束")
        return
    
    # 計算特徵
    df_with_features = calculate_ml_features(hist)
    
    # 準備資料集
    datasets, full_df = prepare_datasets(df_with_features)
    
    if datasets is None:
        print("\n✗ 無法準備資料集，程式結束")
        return
    
    # 儲存資料
    success = save_to_data_folder(datasets, full_df, data_folder, symbol)
    
    if success:
        print("\n" + "="*80)
        print(" "*25 + "資料抓取完成！")
        print("="*80)
        
        print(f"\n📁 資料儲存位置: {os.path.abspath(data_folder)}")
        print(f"📊 資料集摘要:")
        print(f"   • 股票代碼: {symbol}")
        print(f"   • 資料期間: {full_df.index[0].date()} 至 {full_df.index[-1].date()}")
        print(f"   • 總筆數: {len(full_df)}")
        
        for dataset_name, dataset in datasets.items():
            print(f"   • {dataset_name}資料集: {len(dataset['X'])} 樣本, {len(dataset['features'])} 特徵")
        
        print(f"\n🎯 可以開始機器學習了！")
    else:
        print("\n✗ 資料儲存失敗")

# 執行主程式
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
