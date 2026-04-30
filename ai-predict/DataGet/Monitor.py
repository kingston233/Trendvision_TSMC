"""
Monitor.py - 股價監控和警報系統
"""

import time
import pandas as pd
import yfinance as yf
from datetime import datetime
import joblib
import os
import sys
import threading
import select

class TSMCMonitor:
    def __init__(self):
        self.running = True
        self.model_data = None
        self.load_model()
    
    def load_model(self):
        """載入最新的機器學習模型"""
        try:
            # 尋找最新的模型檔案
            data_folder = "Data"
            if not os.path.exists(data_folder):
                print("⚠ Data資料夾不存在，無法載入模型")
                return
            
            model_files = [f for f in os.listdir(data_folder) if f.startswith('best_ml_model_') and f.endswith('.joblib')]
            
            if not model_files:
                print("⚠ 找不到訓練好的模型，僅顯示即時價格")
                return
            
            # 選擇最新的模型
            latest_model = max(model_files, key=lambda x: os.path.getctime(os.path.join(data_folder, x)))
            model_path = os.path.join(data_folder, latest_model)
            
            self.model_data = joblib.load(model_path)
            print(f"✅ 成功載入模型: {latest_model}")
            print(f"   模型類型: {self.model_data['model_name']}")
            
        except Exception as e:
            print(f"⚠ 模型載入失敗: {e}")
            self.model_data = None
    
    def get_current_price(self):
        """獲取當前股價"""
        try:
            ticker = yf.Ticker("2330.TW")
            
            # 嘗試獲取即時價格
            try:
                hist = ticker.history(period="1d", interval="1m")
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    volume = hist['Volume'].iloc[-1]
                    return current_price, volume, True
            except:
                pass
            
            # 備用方法：使用info
            info = ticker.info
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            volume = info.get('volume', 0)
            
            if current_price > 0:
                return current_price, volume, False
            
            # 最後備用：使用歷史資料
            hist = ticker.history(period="1d")
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                volume = hist['Volume'].iloc[-1]
                return current_price, volume, False
            
            return None, None, False
            
        except Exception as e:
            print(f"❌ 價格獲取錯誤: {e}")
            return None, None, False
    
    def predict_price(self, current_price):
        """使用模型預測價格"""
        if not self.model_data:
            return None, None
        
        try:
            # 這裡需要根據實際的特徵工程來準備輸入資料
            # 簡化版本：僅作為示例
            # 實際使用時需要獲取完整的技術指標
            
            print("   📊 預測功能需要完整的技術指標資料")
            return None, None
            
        except Exception as e:
            print(f"   ⚠ 預測失敗: {e}")
            return None, None
    
    def check_for_enter(self):
        """檢查是否按下Enter鍵"""
        if os.name == 'nt':  # Windows
            import msvcrt
            while self.running:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'\r':  # Enter鍵
                        self.running = False
                        break
                time.sleep(0.1)
        else:  # Unix/Linux/Mac
            import termios, tty
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setraw(sys.stdin.fileno())
                while self.running:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1)
                        if key == '\r' or key == '\n':
                            self.running = False
                            break
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    
    def display_price_info(self, current_price, volume, is_realtime, change_pct=None, prev_price=None):
        """顯示價格資訊"""
        current_time = datetime.now().strftime('%H:%M:%S')
        
        # 清除螢幕（可選）
        # os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"\n{'='*60}")
        print(f"🔍 台積電 (2330.TW) 即時監控")
        print(f"{'='*60}")
        print(f"⏰ 更新時間: {current_time}")
        
        if current_price:
            price_status = "📡 即時" if is_realtime else "📊 延遲"
            print(f"💰 當前價格: {current_price:.2f} TWD {price_status}")
            
            if volume:
                print(f"📈 成交量: {volume:,.0f}")
            
            # 顯示價格變化
            if prev_price and change_pct is not None:
                change_symbol = "📈" if change_pct >= 0 else "📉"
                change_color = "+" if change_pct >= 0 else ""
                print(f"📊 價格變化: {change_color}{change_pct:.2f}% {change_symbol}")
            
            # 預測價格（如果有模型）
            predicted_price, confidence = self.predict_price(current_price)
            if predicted_price:
                print(f"🔮 預測價格: {predicted_price:.2f} TWD")
                if confidence:
                    print(f"🎯 信心度: {confidence:.1f}%")
        else:
            print("❌ 無法獲取當前價格")
        
        print(f"{'='*60}")
        print("💡 按 Enter 鍵停止監控...")
        print(f"{'='*60}")
    
    def monitor_tsmc(self):
        """監控台積電股價"""
        print("\n" + "="*60)
        print("🚀 台積電股價監控系統啟動")
        print("="*60)
        print("⚙️  更新頻率: 每10秒")
        print("🛑 停止方式: 按 Enter 鍵")
        print("="*60)
        
        # 啟動按鍵監聽線程
        key_thread = threading.Thread(target=self.check_for_enter)
        key_thread.daemon = True
        key_thread.start()
        
        prev_price = None
        update_count = 0
        
        while self.running:
            try:
                update_count += 1
                current_price, volume, is_realtime = self.get_current_price()
                
                # 計算價格變化
                change_pct = None
                if prev_price and current_price:
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                
                # 顯示資訊
                self.display_price_info(current_price, volume, is_realtime, change_pct, prev_price)
                
                # 更新前一次價格
                if current_price:
                    prev_price = current_price
                
                # 每10次更新顯示統計
                if update_count % 10 == 0:
                    print(f"📊 已更新 {update_count} 次")
                
                # 等待10秒或直到停止
                for i in range(100):  # 10秒 = 100 * 0.1秒
                    if not self.running:
                        break
                    time.sleep(0.1)
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"❌ 監控錯誤: {e}")
                print("🔄 10秒後重試...")
                
                # 錯誤等待
                for i in range(100):
                    if not self.running:
                        break
                    time.sleep(0.1)
        
        print("\n" + "="*60)
        print("🛑 監控已停止")
        print("="*60)
        print(f"📊 總共更新了 {update_count} 次")
        print("👋 感謝使用台積電股價監控系統！")

def main():
    """主程式"""
    try:
        monitor = TSMCMonitor()
        monitor.monitor_tsmc()
    except KeyboardInterrupt:
        print("\n\n🛑 程式被使用者中斷")
    except Exception as e:
        print(f"\n❌ 程式執行錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    input("\n按 Enter 鍵結束...")

if __name__ == "__main__":
    main()
