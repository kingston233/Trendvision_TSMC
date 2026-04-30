"""
修正版 Predict.py - 解決資料期間和市場狀態問題
台積電股價即時預測系統
- 修正資料獲取期間為今年1/1開始
- 修正市場狀態判斷邏輯
- 移除所有 icon
"""

import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime, timedelta
import yfinance as yf
import warnings
import pytz

# 忽略警告訊息，保持輸出清潔
warnings.filterwarnings('ignore')

def load_latest_model():
    """
    載入最新的訓練模型
    
    功能說明:
    - 搜尋 ../Data/ 目錄下的時間戳記資料夾
    - 尋找 'best_three_model.joblib' 檔案 (修正檔名)
    - 選擇最新的模型檔案並載入
    
    Returns:
        dict: 包含模型資料的字典，失敗時返回None
    """
    print("尋找最新的訓練模型...")
    
    try:
        # 修正後的資料目錄路徑
        data_dir = '../Data'
        
        # 檢查資料目錄是否存在
        if not os.path.exists(data_dir):
            print(f"錯誤: 資料目錄不存在: {data_dir}")
            return None
        
        # 搜尋所有時間戳記子資料夾中的模型檔案
        model_files = []
        
        # 遍歷資料目錄中的所有項目
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            
            # 檢查是否為時間戳記格式的資料夾 (12位數字)
            if os.path.isdir(item_path) and len(item) == 12 and item.isdigit():
                print(f"   檢查資料夾: {item}")
                
                # 在時間戳記資料夾中搜尋模型檔案
                try:
                    folder_files = os.listdir(item_path)
                    for file in folder_files:
                        # 修正：尋找 ML.py 實際儲存的檔案名稱
                        if file == 'best_three_model.joblib':
                            full_path = os.path.join(item_path, file)
                            model_files.append(full_path)
                            print(f"   找到模型: {file}")
                        # 備用：也支援舊的命名格式
                        elif file.startswith('best_ml_model_') and file.endswith('.joblib'):
                            full_path = os.path.join(item_path, file)
                            model_files.append(full_path)
                            print(f"   找到模型 (舊格式): {file}")
                        # 新增：支援所有三個模型檔案
                        elif file == 'all_three_models.joblib':
                            full_path = os.path.join(item_path, file)
                            model_files.append(full_path)
                            print(f"   找到所有模型: {file}")
                            
                except Exception as e:
                    print(f"   無法讀取資料夾 {item}: {e}")
                    continue
        
        # 檢查是否找到任何模型檔案
        if not model_files:
            print("錯誤: 找不到訓練好的模型，請先執行 ML.py")
            print("   預期檔案格式:")
            print("   - ../Data/YYYYMMDDHHMM/best_three_model.joblib")
            print("   - ../Data/YYYYMMDDHHMM/all_three_models.joblib")
            print("   - ../Data/YYYYMMDDHHMM/best_ml_model_*.joblib (舊格式)")
            return None
        
        # 優先選擇 best_three_model.joblib，其次是最新的檔案
        best_model_file = None
        for file_path in model_files:
            if 'best_three_model.joblib' in file_path:
                best_model_file = file_path
                break
        
        if best_model_file is None:
            # 如果沒有 best_three_model.joblib，選擇最新的檔案
            best_model_file = max(model_files, key=os.path.getmtime)
        
        print(f"   選擇最新模型: {os.path.basename(best_model_file)}")
        
        # 載入模型資料
        model_data = joblib.load(best_model_file)
        
        # 顯示模型資訊
        print(f"成功載入模型: {os.path.basename(best_model_file)}")
        print(f"   模型類型: {model_data['model_name']}")
        print(f"   特徵數量: {len(model_data['features'])}")
        
        # 檢查模型資料完整性
        required_keys = ['model', 'scaler', 'features', 'model_name']
        missing_keys = [key for key in required_keys if key not in model_data]
        if missing_keys:
            print(f"警告: 模型資料可能不完整，缺少: {missing_keys}")
        
        return model_data
        
    except Exception as e:
        print(f"錯誤: 模型載入失敗: {e}")
        print("   請檢查:")
        print("   1. 模型檔案是否存在")
        print("   2. 檔案是否損壞")
        print("   3. 路徑是否正確")
        print("   4. 是否已執行 ML.py 訓練模型")
        return None

def get_latest_data(start_from_year=True):
    """
    獲取最新的台積電股價資料 - 修正版
    
    功能說明:
    - 修正：從今年1月1日開始獲取資料
    - 使用 yfinance 從 Yahoo Finance 獲取台積電 (2330.TW) 的歷史資料
    - 確保有足夠的資料進行技術指標計算
    - 包含開盤價、最高價、最低價、收盤價、成交量等資訊
    
    Args:
        start_from_year (bool): 是否從今年1月1日開始，預設True
    
    Returns:
        pandas.DataFrame: 包含股價資料的DataFrame，失敗時返回None
    """
    print("獲取最新台積電資料...")
    
    try:
        # 建立台積電股票物件 (2330.TW = 台積電在台股的代碼)
        ticker = yf.Ticker("2330.TW")
        
        # 計算日期範圍 - 修正為從今年1月1日開始
        end_date = datetime.now()
        
        if start_from_year:
            # 從今年1月1日開始
            start_date = datetime(end_date.year, 1, 1)
            print(f"   獲取期間: {start_date.date()} 到 {end_date.date()}")
            print(f"   資料範圍: 今年年初至今")
        else:
            # 備用方案：往前推120天
            start_date = end_date - timedelta(days=120)
            print(f"   獲取期間: {start_date.date()} 到 {end_date.date()}")
            print(f"   資料範圍: 近120天")
        
        # 從 Yahoo Finance 下載歷史資料
        print("   正在下載資料...")
        df = ticker.history(
            start=start_date,    # 開始日期
            end=end_date         # 結束日期
        )
        
        # 檢查是否成功獲取資料
        if df.empty:
            print("錯誤: 無法獲取最新資料")
            print("   可能原因:")
            print("   1. 網路連線問題")
            print("   2. Yahoo Finance API 暫時不可用")
            print("   3. 股票代碼錯誤")
            
            # 如果從年初開始失敗，嘗試近期資料
            if start_from_year:
                print("   嘗試獲取近期資料...")
                return get_latest_data(start_from_year=False)
            
            return None
        
        # 顯示獲取結果
        actual_days = len(df)
        expected_days = (end_date - start_date).days
        
        print(f"成功獲取 {actual_days} 天的資料")
        print(f"   實際日期範圍: {df.index[0].date()} 到 {df.index[-1].date()}")
        print(f"   最新收盤價: {df['Close'].iloc[-1]:.2f} TWD")
        print(f"   資料完整度: {actual_days}/{expected_days} 天 ({actual_days/expected_days*100:.1f}%)")
        
        # 檢查資料品質
        missing_data = df.isnull().sum().sum()
        if missing_data > 0:
            print(f"警告: 發現 {missing_data} 個缺失值，將自動處理")
            # 處理缺失值
            df = df.fillna(method='ffill').fillna(method='bfill')
        
        # 檢查資料是否足夠
        if len(df) < 50:
            print(f"警告: 資料量較少 ({len(df)} 天)，可能影響預測準確度")
        
        return df
        
    except Exception as e:
        print(f"錯誤: 資料獲取失敗: {e}")
        print("   建議解決方案:")
        print("   1. 檢查網路連線")
        print("   2. 稍後再試")
        print("   3. 確認 yfinance 套件已正確安裝")
        
        # 如果從年初開始失敗，嘗試近期資料
        if start_from_year:
            print("   嘗試獲取近期資料...")
            return get_latest_data(start_from_year=False)
        
        return None

def get_realtime_data():
    """
    獲取即時股價資料 - 修正市場狀態判斷
    
    功能說明:
    - 獲取當天的即時股價資料
    - 修正市場狀態判斷邏輯
    - 包含開盤價、當前價格、最高價、最低價等
    - 用於收盤價預測
    
    Returns:
        dict: 包含即時資料的字典，失敗時返回None
    """
    print("獲取即時股價資料...")
    
    try:
        ticker = yf.Ticker("2330.TW")
        
        # 獲取即時資訊
        info = ticker.info
        
        # 獲取今日資料 - 嘗試多種方式
        today_data = None
        
        # 方法1: 嘗試獲取分鐘資料
        try:
            today_data = ticker.history(period="1d", interval="1m")
            if not today_data.empty:
                print("   使用分鐘級資料")
        except:
            pass
        
        # 方法2: 如果沒有分鐘資料，獲取日資料
        if today_data is None or today_data.empty:
            try:
                today_data = ticker.history(period="2d")
                if not today_data.empty:
                    today_data = today_data.tail(1)
                    print("   使用日級資料")
            except:
                pass
        
        # 方法3: 使用最近5天資料的最後一天
        if today_data is None or today_data.empty:
            try:
                recent_data = ticker.history(period="5d")
                if not recent_data.empty:
                    today_data = recent_data.tail(1)
                    print("   使用最近資料")
            except:
                pass
        
        if today_data is None or today_data.empty:
            print("錯誤: 無法獲取今日資料")
            return None
        
        # 判斷市場狀態 - 修正邏輯
        current_time = datetime.now()
        taiwan_tz = pytz.timezone('Asia/Taipei')
        
        # 轉換為台灣時間
        if current_time.tzinfo is None:
            current_time = taiwan_tz.localize(current_time)
        else:
            current_time = current_time.astimezone(taiwan_tz)
        
        # 台股交易時間: 週一到週五 09:00-13:30
        weekday = current_time.weekday()  # 0=週一, 6=週日
        hour = current_time.hour
        minute = current_time.minute
        
        # 判斷是否為交易日 (週一到週五)
        is_trading_day = weekday < 5
        
        # 判斷是否在交易時間內
        if is_trading_day:
            # 上午盤: 09:00-12:00, 下午盤: 13:30-13:30 (實際到13:30)
            morning_session = (hour == 9 and minute >= 0) or (hour >= 10 and hour < 12)
            afternoon_session = (hour == 13 and minute >= 30) or (hour == 13 and minute <= 30)
            is_market_open = morning_session or afternoon_session
        else:
            is_market_open = False
        
        # 從info或today_data獲取市場狀態
        market_state = info.get('marketState', 'UNKNOWN')
        
        # 綜合判斷市場狀態
        if market_state in ['OPEN', 'REGULAR']:
            is_market_open = True
        elif market_state in ['CLOSED', 'PRE', 'POST']:
            is_market_open = False
        # 如果API沒有提供狀態，使用時間判斷
        
        # 整理即時資料
        current_data = {
            'current_price': info.get('currentPrice', today_data['Close'].iloc[-1]),
            'open_price': today_data['Open'].iloc[0] if len(today_data) > 0 else info.get('open', 0),
            'high_price': today_data['High'].max(),
            'low_price': today_data['Low'].min(),
            'volume': today_data['Volume'].sum(),
            'previous_close': info.get('previousClose', info.get('regularMarketPreviousClose', 0)),
            'market_time': current_time,
            'is_market_open': is_market_open,
            'market_state': market_state,
            'trading_day': is_trading_day
        }
        
        # 如果沒有previous_close，嘗試從歷史資料獲取
        if current_data['previous_close'] == 0:
            try:
                recent_history = ticker.history(period="5d")
                if len(recent_history) >= 2:
                    current_data['previous_close'] = recent_history['Close'].iloc[-2]
            except:
                pass
        
        print(f"即時資料獲取成功")
        print(f"   當前價格: {current_data['current_price']:.2f} TWD")
        print(f"   今日開盤: {current_data['open_price']:.2f} TWD")
        print(f"   今日最高: {current_data['high_price']:.2f} TWD")
        print(f"   今日最低: {current_data['low_price']:.2f} TWD")
        print(f"   昨日收盤: {current_data['previous_close']:.2f} TWD")
        
        # 顯示市場狀態
        if is_trading_day:
            if is_market_open:
                market_status = "開盤中"
            else:
                market_status = "交易日休市"
        else:
            market_status = "非交易日"
        
        print(f"   市場狀態: {market_status}")
        print(f"   當前時間: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (台北時間)")
        
        return current_data
        
    except Exception as e:
        print(f"錯誤: 即時資料獲取失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def calculate_technical_indicators(df):
    """
    計算技術指標 - 改進版
    
    功能說明:
    - 計算各種技術分析指標，包括移動平均線、MACD、成交量等
    - 動態調整指標計算週期，適應不同的資料長度
    - 處理資料不足和除零錯誤的情況
    - 確保與 ML.py 中的特徵計算一致
    
    Args:
        df (pandas.DataFrame): 包含OHLCV資料的DataFrame
    
    Returns:
        pandas.DataFrame: 包含所有技術指標的DataFrame，失敗時返回None
    """
    print("計算技術指標...")
    
    try:
        data_length = len(df)
        print(f"   開始計算，原始資料: {data_length} 筆")
        
        # === 移動平均線 (與ML.py保持一致) ===
        print("   計算移動平均線...")
        df['MA_5'] = df['Close'].rolling(window=5, min_periods=1).mean()
        df['MA_10'] = df['Close'].rolling(window=10, min_periods=1).mean()
        df['MA_20'] = df['Close'].rolling(window=20, min_periods=1).mean()
        df['MA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()
        
        # === MACD (與ML.py保持一致) ===
        print("   計算MACD...")
        exp1 = df['Close'].ewm(span=12, min_periods=1).mean()
        exp2 = df['Close'].ewm(span=26, min_periods=1).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9, min_periods=1).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']  # 新增：MACD柱狀圖
        
        # === 成交量指標 (與ML.py保持一致) ===
        print("   計算成交量指標...")
        vol_period = min(20, data_length // 2)
        vol_period = max(vol_period, 5)
        
        df['Volume_MA'] = df['Volume'].rolling(window=vol_period, min_periods=1).mean()
        df['Volume_Ratio'] = df['Volume'] / (df['Volume_MA'] + 1e-8)
        
        # === 價格變化指標 (與ML.py保持一致) ===
        print("   計算價格變化指標...")
        df['Price_Change'] = df['Close'].pct_change().fillna(0)
        df['Price_Change_5'] = df['Close'].pct_change(periods=5).fillna(0)  # 5日變化率
        
        # === 波動率指標 (與ML.py保持一致) ===
        print("   計算波動率指標...")
        df['Volatility_10'] = df['Close'].rolling(window=min(10, data_length//2), min_periods=1).std()
        df['Volatility_20'] = df['Close'].rolling(window=min(20, data_length//2), min_periods=1).std()
        
        # === 高低價百分比 (與ML.py保持一致) ===
        print("   計算高低價指標...")
        df['High_Low_Pct'] = (df['High'] - df['Low']) / df['Close']
        
        # === 資料清理 ===
        print("   清理和驗證資料...")
        df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
        df = df.replace([np.inf, -np.inf], 0)
        
        print(f"技術指標計算完成，最終資料: {len(df)} 筆")
        print(f"   新增指標欄位: {len(df.columns) - 5} 個")
        
        return df
        
    except Exception as e:
        print(f"錯誤: 技術指標計算失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_prediction_features(df, model_features, look_back=10):
    """
    建立預測特徵 - 與ML.py保持一致
    
    功能說明:
    - 模擬ML.py中的時間序列特徵建立方式
    - 確保特徵計算邏輯完全一致
    - 處理特徵缺失問題
    
    Args:
        df (pandas.DataFrame): 包含技術指標的DataFrame
        model_features (list): 模型訓練時使用的特徵列表
        look_back (int): 時間窗口大小，預設10天
    
    Returns:
        numpy.ndarray: 預測特徵矩陣 (1, n_features)，失敗時返回None
    """
    print("建立預測特徵...")
    
    try:
        available_data = len(df)
        print(f"   可用資料: {available_data} 筆")
        
        if available_data < look_back + 1:
            print(f"錯誤: 資料不足，需要至少 {look_back + 1} 筆資料")
            return None
        
        print(f"   使用 {look_back} 天的歷史資料")
        
        # === 檢查並補充缺失特徵 ===
        print("   檢查特徵完整性...")
        missing_features = []
        for feature in model_features:
            if feature not in df.columns:
                missing_features.append(feature)
        
        if missing_features:
            print(f"警告: 缺少特徵: {missing_features}")
            for feature in missing_features:
                if 'MA' in feature:
                    df[feature] = df['Close']
                elif 'Volume' in feature:
                    df[feature] = df['Volume'].mean()
                elif 'MACD' in feature:
                    df[feature] = 0
                else:
                    df[feature] = 0
                print(f"      {feature} -> 已補充")
        
        # === 模擬ML.py的特徵建立邏輯 ===
        print("   建立時間序列特徵...")
        
        # 使用最後 look_back+1 天的資料
        recent_data = df[model_features].tail(look_back + 1)
        
        # 1. 當前特徵 (最新一天)
        current_features = recent_data.iloc[-1].values
        features = list(current_features)
        
        # 2. 歷史統計特徵 (過去 look_back 天)
        historical_data = recent_data.iloc[:-1]
        
        # 統計特徵
        hist_mean = historical_data.mean().values
        hist_std = historical_data.std().fillna(0).values
        hist_min = historical_data.min().values
        hist_max = historical_data.max().values
        
        # 趨勢特徵
        hist_last = historical_data.iloc[-1].values
        hist_first = historical_data.iloc[0].values
        hist_trend = np.where(hist_first != 0, 
                             (hist_last - hist_first) / hist_first, 
                             0)
        
        # 3. 變化率特徵 (與前一天比較)
        if len(recent_data) >= 2:
            prev_features = recent_data.iloc[-2].values
            feature_changes = np.where(prev_features != 0,
                                     (current_features - prev_features) / prev_features,
                                     0)
        else:
            feature_changes = np.zeros_like(current_features)
        
        # === 組合所有特徵 (與ML.py順序一致) ===
        features.extend(hist_mean)
        features.extend(hist_std)
        features.extend(hist_min)
        features.extend(hist_max)
        features.extend(hist_trend)
        features.extend(feature_changes)
        
        # === 清理特徵 ===
        features = np.array(features)
        features = np.where(np.isfinite(features), features, 0)
        
        print(f"預測特徵建立完成")
        print(f"   特徵總數: {len(features)}")
        print(f"   基礎特徵: {len(current_features)}")
        print(f"   統計特徵: {len(hist_mean) * 4}")
        print(f"   趨勢特徵: {len(hist_trend)}")
        print(f"   變化特徵: {len(feature_changes)}")
        
        return features.reshape(1, -1)
        
    except Exception as e:
        print(f"錯誤: 預測特徵建立失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_closing_prediction_features(df, realtime_data, model_features, look_back=10):
    """
    建立收盤價預測特徵 (新增功能)
    
    功能說明:
    - 結合歷史資料和即時資料建立特徵
    - 用於預測當天的收盤價
    - 考慮當天的開盤價、最高價、最低價、當前價格等
    
    Args:
        df (pandas.DataFrame): 歷史股價資料
        realtime_data (dict): 即時股價資料
        model_features (list): 模型特徵列表
        look_back (int): 時間窗口大小
    
    Returns:
        numpy.ndarray: 收盤價預測特徵矩陣，失敗時返回None
    """
    print("建立收盤價預測特徵...")
    
    try:
        # 建立今日資料點
        today_data = {
            'Open': realtime_data['open_price'],
            'High': realtime_data['high_price'],
            'Low': realtime_data['low_price'],
            'Close': realtime_data['current_price'],  # 使用當前價格作為臨時收盤價
            'Volume': realtime_data['volume']
        }
        
        print(f"   今日資料:")
        print(f"     開盤: {today_data['Open']:.2f}")
        print(f"     最高: {today_data['High']:.2f}")
        print(f"     最低: {today_data['Low']:.2f}")
        print(f"     當前: {today_data['Close']:.2f}")
        
        # 將今日資料添加到歷史資料
        today_df = pd.DataFrame([today_data], index=[datetime.now().date()])
        extended_df = pd.concat([df, today_df])
        
        # 重新計算技術指標 (包含今日資料)
        extended_df = calculate_technical_indicators(extended_df)
        
        if extended_df is None:
            print("錯誤: 無法計算包含今日資料的技術指標")
            return None
        
        # 建立預測特徵
        features = create_prediction_features(extended_df, model_features, look_back)
        
        if features is not None:
            print("收盤價預測特徵建立完成")
            
            # 添加當日特殊特徵
            intraday_features = []
            
            # 當日價格範圍特徵
            price_range = (today_data['High'] - today_data['Low']) / today_data['Close']
            intraday_features.append(price_range)
            
            # 當日價格位置 (當前價格在今日高低價間的位置)
            if today_data['High'] != today_data['Low']:
                price_position = (today_data['Close'] - today_data['Low']) / (today_data['High'] - today_data['Low'])
            else:
                price_position = 0.5
            intraday_features.append(price_position)
            
            # 開盤價差 (相對於昨日收盤)
            if realtime_data['previous_close'] > 0:
                open_gap = (today_data['Open'] - realtime_data['previous_close']) / realtime_data['previous_close']
            else:
                open_gap = 0
            intraday_features.append(open_gap)
            
            # 當前漲跌幅
            if today_data['Open'] > 0:
                current_change = (today_data['Close'] - today_data['Open']) / today_data['Open']
            else:
                current_change = 0
            intraday_features.append(current_change)
            
            # 成交量比較 (與歷史平均比較)
            if len(df) > 0:
                avg_volume = df['Volume'].tail(20).mean()
                volume_ratio = today_data['Volume'] / avg_volume if avg_volume > 0 else 1
            else:
                volume_ratio = 1
            intraday_features.append(volume_ratio)
            
            # 將當日特徵添加到原有特徵 - 修正：不添加額外特徵，避免維度不匹配
            # intraday_features = np.array(intraday_features).reshape(1, -1)
            # features = np.concatenate([features, intraday_features], axis=1)
            
            print(f"   當日特殊特徵已計算但不添加到模型輸入")
            print(f"   最終特徵數: {features.shape[1]} 個")
        
        return features
        
    except Exception as e:
        print(f"錯誤: 收盤價預測特徵建立失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def make_prediction(model_data, features):
    """
    進行股價預測
    
    功能說明:
    - 載入訓練好的機器學習模型和標準化器
    - 處理特徵維度不匹配問題
    - 進行特徵標準化，確保與訓練時一致
    - 執行預測並返回結果
    
    Args:
        model_data (dict): 包含模型、scaler等資訊的字典
        features (numpy.ndarray): 預測特徵矩陣
    
    Returns:
        float: 預測的股價，失敗時返回None
    """
    print("進行股價預測...")
    
    try:
        model = model_data['model']
        scaler = model_data['scaler']
        model_name = model_data['model_name']
        
        print(f"   使用模型: {model_name}")
        
        # 特徵維度檢查和調整
        expected_features = scaler.n_features_in_
        actual_features = features.shape[1]
        
        print(f"   期望特徵數: {expected_features}")
        print(f"   實際特徵數: {actual_features}")
        
        if actual_features != expected_features:
            print(f"警告: 特徵數不匹配，進行調整...")
            if actual_features > expected_features:
                features = features[:, :expected_features]
                print(f"      截取前 {expected_features} 個特徵")
            else:
                padding_size = expected_features - actual_features
                padding = np.zeros((1, padding_size))
                features = np.concatenate([features, padding], axis=1)
                print(f"      補零 {padding_size} 個特徵")
        
        # 特徵標準化
        print("   進行特徵標準化...")
        try:
            features_scaled = scaler.transform(features)
            print("      標準化成功")
        except Exception as scale_error:
            print(f"警告: 標準化失敗: {scale_error}")
            features_scaled = features
        
        # 執行預測
        print("   執行模型預測...")
        prediction = model.predict(features_scaled)[0]
        
        # 驗證預測結果
        if not np.isfinite(prediction):
            print(f"警告: 預測結果包含無效值: {prediction}")
            return None
        
        if prediction < 50 or prediction > 5000:
            print(f"警告: 預測結果超出合理範圍: {prediction:.2f}")
        
        print(f"預測完成")
        print(f"   使用模型: {model_name}")
        print(f"   預測價格: {prediction:.2f} TWD")
        
        return prediction
        
    except Exception as e:
        print(f"錯誤: 預測失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

def predict_closing_price(model_data, df, realtime_data):
    """
    預測今日收盤價 (新增功能)
    
    功能說明:
    - 結合歷史資料和即時資料預測今日收盤價
    - 考慮當日的交易情況和技術指標
    - 提供盤中預測參考
    
    Args:
        model_data (dict): 模型資料
        df (pandas.DataFrame): 歷史資料
        realtime_data (dict): 即時資料
    
    Returns:
        float: 預測的收盤價，失敗時返回None
    """
    print("\n預測今日收盤價...")
    
    try:
        # 建立收盤價預測特徵
        features = create_closing_prediction_features(df, realtime_data, model_data['features'])
        
        if features is None:
            print("錯誤: 無法建立收盤價預測特徵")
            return None
        
        # 執行預測
        closing_prediction = make_prediction(model_data, features)
        
        if closing_prediction is not None:
            print(f"今日收盤價預測完成: {closing_prediction:.2f} TWD")
        
        return closing_prediction
        
    except Exception as e:
        print(f"錯誤: 收盤價預測失敗: {e}")
        return None

def main():
    """
    主程式 - 台積電股價預測系統 (包含收盤價預測)
    """
    print("\n" + "="*70)
    print(" "*15 + "台積電股價即時預測系統")
    print(" "*10 + "明日股價預測 + 今日收盤價預測")
    print("="*70 + "\n")
    
    # 載入訓練模型
    print("【第1步】載入訓練模型")
    print("-" * 30)
    model_data = load_latest_model()
    if model_data is None:
        print("\n錯誤: 無法載入模型，程式結束")
        return
    
    # 獲取歷史股價資料 - 修正為從今年1月1日開始
    print("\n【第2步】獲取歷史股價資料 (今年年初至今)")
    print("-" * 30)
    df = get_latest_data(start_from_year=True)
    if df is None:
        print("\n錯誤: 無法獲取股價資料，程式結束")
        return
    
    # 獲取即時資料
    print("\n【第3步】獲取即時股價資料")
    print("-" * 30)
    realtime_data = get_realtime_data()
    if realtime_data is None:
        print("警告: 無法獲取即時資料，將只進行明日預測")
        realtime_data = None
    
    # 計算技術指標
    print("\n【第4步】計算技術指標")
    print("-" * 30)
    df = calculate_technical_indicators(df)
    if df is None:
        print("\n錯誤: 技術指標計算失敗，程式結束")
        return
    
    # === 明日股價預測 (原有功能) ===
    print("\n【第5步】明日股價預測")
    print("-" * 30)
    
    # 建立明日預測特徵
    tomorrow_features = create_prediction_features(df, model_data['features'])
    if tomorrow_features is None:
        print("錯誤: 明日預測特徵建立失敗")
        tomorrow_prediction = None
    else:
        # 執行明日預測
        tomorrow_prediction = make_prediction(model_data, tomorrow_features)
    
    # === 今日收盤價預測 (新增功能) ===
    closing_prediction = None
    if realtime_data is not None:
        print("\n【第6步】今日收盤價預測")
        print("-" * 30)
        closing_prediction = predict_closing_price(model_data, df, realtime_data)
    
    # === 顯示結果 ===
    print("\n【第7步】結果分析")
    print("-" * 30)
    
    current_price = df['Close'].iloc[-1]
    
    print("\n" + "="*70)
    print(" "*20 + "預測結果總覽")
    print("="*70)
    
    print(f"預測時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"股票代號: 台積電 (2330.TW)")
    print(f"使用模型: {model_data['model_name']}")
    
    print(f"\n價格資訊:")
    print(f"昨日收盤: {current_price:.2f} TWD")
    
    if realtime_data:
        print(f"當前價格: {realtime_data['current_price']:.2f} TWD")
        if realtime_data['previous_close'] > 0:
            current_change = realtime_data['current_price'] - realtime_data['previous_close']
            current_change_pct = (current_change / realtime_data['previous_close']) * 100
            print(f"今日變化: {current_change:+.2f} TWD ({current_change_pct:+.2f}%)")
    
    # === 今日收盤價預測結果 ===
    if closing_prediction is not None and realtime_data is not None:
        print(f"\n今日收盤價預測:")
        print(f"預測收盤: {closing_prediction:.2f} TWD")
        
        closing_change = closing_prediction - realtime_data['current_price']
        closing_change_pct = (closing_change / realtime_data['current_price']) * 100
        print(f"預期變化: {closing_change:+.2f} TWD ({closing_change_pct:+.2f}%)")
        
        # 收盤價預測趨勢分析
        if closing_change_pct > 1:
            closing_trend = "預測強勢收高"
            closing_suggestion = "可能尾盤拉升"
        elif closing_change_pct > 0:
            closing_trend = "預測小幅收高"
            closing_suggestion = "預期正面收盤"
        elif closing_change_pct > -1:
            closing_trend = "預測小幅收低"
            closing_suggestion = "預期震盪收盤"
        else:
            closing_trend = "預測明顯收低"
            closing_suggestion = "可能尾盤走弱"
        
        print(f"收盤趨勢: {closing_trend}")
        print(f"盤中參考: {closing_suggestion}")
    
    # === 明日股價預測結果 ===
    if tomorrow_prediction is not None:
        print(f"\n明日股價預測:")
        print(f"預測價格: {tomorrow_prediction:.2f} TWD")
        
        tomorrow_change = tomorrow_prediction - current_price
        tomorrow_change_pct = (tomorrow_change / current_price) * 100
        print(f"預期變化: {tomorrow_change:+.2f} TWD ({tomorrow_change_pct:+.2f}%)")
        
        # 明日預測趨勢分析
        if tomorrow_change_pct > 2:
            tomorrow_trend = "強烈上漲"
            tomorrow_suggestion = "建議關注，但注意風險控制"
        elif tomorrow_change_pct > 0:
            tomorrow_trend = "預測上漲"
            tomorrow_suggestion = "可考慮適量買入"
        elif tomorrow_change_pct > -2:
            tomorrow_trend = "預測下跌"
            tomorrow_suggestion = "建議觀望或分批買入"
        else:
            tomorrow_trend = "明顯下跌"
            tomorrow_suggestion = "建議等待更好的進場時機"
        
        print(f"明日趨勢: {tomorrow_trend}")
        print(f"操作建議: {tomorrow_suggestion}")
    
    # === 綜合分析 ===
    if closing_prediction is not None and tomorrow_prediction is not None and realtime_data is not None:
        print(f"\n綜合分析:")
        
        # 短期動能分析
        if closing_prediction > realtime_data['current_price'] and tomorrow_prediction > closing_prediction:
            momentum = "連續上漲動能"
        elif closing_prediction < realtime_data['current_price'] and tomorrow_prediction < closing_prediction:
            momentum = "連續下跌壓力"
        else:
            momentum = "震盪整理格局"
        
        print(f"   動能分析: {momentum}")
        
        # 價格區間預測
        price_range_low = min(closing_prediction, tomorrow_prediction) * 0.99
        price_range_high = max(closing_prediction, tomorrow_prediction) * 1.01
        print(f"   預測區間: {price_range_low:.2f} - {price_range_high:.2f} TWD")
    
    # === 技術指標快照 ===
    print(f"\n技術指標快照:")
    if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
        current_macd = df['MACD'].iloc[-1]
        current_signal = df['MACD_Signal'].iloc[-1]
        macd_trend = "多頭" if current_macd > current_signal else "空頭"
        print(f"   MACD: {current_macd:.3f} (趨勢: {macd_trend})")
    
    if 'MA_5' in df.columns and 'MA_20' in df.columns:
        ma5 = df['MA_5'].iloc[-1]
        ma20 = df['MA_20'].iloc[-1]
        ma_trend = "多頭排列" if ma5 > ma20 else "空頭排列"
        print(f"   均線: MA5({ma5:.2f}) vs MA20({ma20:.2f}) - {ma_trend}")
    
    # === 市場狀態 ===
    if realtime_data:
        print(f"\n市場狀態:")
        
        # 顯示詳細的市場狀態
        if realtime_data['trading_day']:
            if realtime_data['is_market_open']:
                market_status = "開盤中"
            else:
                market_status = "交易日休市"
        else:
            market_status = "非交易日"
        
        print(f"   交易狀態: {market_status}")
        print(f"   今日成交: {realtime_data['volume']:,} 股")
        
        # 價格位置分析
        if realtime_data['high_price'] != realtime_data['low_price']:
            price_position = (realtime_data['current_price'] - realtime_data['low_price']) / (realtime_data['high_price'] - realtime_data['low_price'])
            if price_position > 0.8:
                position_desc = "接近今日高點"
            elif price_position < 0.2:
                position_desc = "接近今日低點"
            else:
                position_desc = "位於中間區域"
            print(f"   價格位置: {position_desc} ({price_position:.1%})")
    
    print(f"\n資料統計:")
    print(f"   使用資料天數: {len(df)} 天")
    print(f"   資料日期範圍: {df.index[0].date()} ~ {df.index[-1].date()}")
    print(f"   模型特徵數量: {len(model_data['features'])} 個")
    
    print(f"\n風險提醒:")
    print("   此預測僅供參考，不構成投資建議")
    print("   收盤價預測適用於盤中參考，實際收盤可能受突發事件影響")
    print("   股市有風險，投資需謹慎")
    print("   請結合基本面分析和市場消息")
    print("   建議分散投資，控制風險")

if __name__ == "__main__":
    try:
        main()
        input("\n按 Enter 鍵結束程式...")
    except KeyboardInterrupt:
        print("\n\n警告: 程式被使用者中斷 (Ctrl+C)")
    except Exception as e:
        print(f"\n錯誤: 程式執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 鍵結束程式...")
