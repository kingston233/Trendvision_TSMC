"""
完整版 ML.py - 包含視覺化功能 (僅使用 matplotlib)
自動偵測最新的時間戳記資料夾並儲存模型與圖表
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings

# 嘗試匯入視覺化套件
try:
    import matplotlib.pyplot as plt
    VISUALIZATION_AVAILABLE = True
    print("視覺化套件載入成功")
except ImportError as e:
    print(f"視覺化套件載入失敗: {e}")
    print("將跳過圖表生成功能")
    print("如需圖表功能，請安裝: pip install matplotlib")
    VISUALIZATION_AVAILABLE = False

warnings.filterwarnings('ignore')

def find_latest_data_folder():
    """尋找最新的時間戳記資料夾"""
    print("尋找最新的資料夾...")
    
    try:
        data_dir = '../Data'
        if not os.path.exists(data_dir):
            print(f"Data 資料夾不存在")
            return None, None
        
        # 尋找所有時間戳記資料夾
        timestamp_folders = []
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            if os.path.isdir(item_path) and len(item) == 12 and item.isdigit():
                timestamp_folders.append((item, item_path))
        
        if not timestamp_folders:
            print("找不到時間戳記資料夾")
            return None, None
        
        # 選擇最新的資料夾
        latest_folder = max(timestamp_folders, key=lambda x: x[0])
        timestamp, folder_path = latest_folder
        
        print(f"找到最新資料夾: {folder_path}")
        print(f"時間戳記: {timestamp}")
        
        return timestamp, folder_path
        
    except Exception as e:
        print(f"搜尋資料夾失敗: {e}")
        return None, None

def load_training_data(folder_path):
    """從指定資料夾載入訓練資料"""
    print("載入訓練資料...")
    
    try:
        # 嘗試載入 tsmc_lstm_data.csv
        data_file = os.path.join(folder_path, 'tsmc_lstm_data.csv')
        
        if not os.path.exists(data_file):
            print(f"資料檔案不存在: {data_file}")
            # 嘗試其他可能的檔案名稱
            alternative_files = [
                'tsmc_technical_data.csv',
                'tsmc_data.csv'
            ]
            
            for alt_file in alternative_files:
                alt_path = os.path.join(folder_path, alt_file)
                if os.path.exists(alt_path):
                    data_file = alt_path
                    print(f"使用替代檔案: {alt_file}")
                    break
            else:
                return None
        
        # 載入資料
        df = pd.read_csv(data_file, index_col=0, parse_dates=True)
        
        print(f"成功載入資料: {len(df)} 筆")
        print(f"檔案路徑: {data_file}")
        print(f"特徵數量: {len(df.columns)}")
        print(f"日期範圍: {df.index[0].date()} ~ {df.index[-1].date()}")
        
        return df
        
    except Exception as e:
        print(f"資料載入失敗: {e}")
        return None

def prepare_features(df):
    """準備機器學習特徵"""
    print("準備機器學習特徵...")
    
    try:
        # 選擇特徵 (排除目標變數)
        feature_columns = [col for col in df.columns if col != 'Close']
        
        # 基本特徵
        features = df[feature_columns].copy()
        
        # 目標變數 (下一日收盤價)
        target = df['Close'].shift(-1)  # 預測下一天的收盤價
        
        # 移除最後一行 (因為沒有下一天的目標值)
        features = features[:-1]
        target = target[:-1]
        
        # 移除缺失值
        mask = ~(features.isnull().any(axis=1) | target.isnull())
        features = features[mask]
        target = target[mask]
        
        print(f"特徵準備完成")
        print(f"特徵數量: {len(features.columns)}")
        print(f"樣本數量: {len(features)}")
        print(f"目標變數範圍: {target.min():.2f} ~ {target.max():.2f}")
        
        return features, target, feature_columns
        
    except Exception as e:
        print(f"特徵準備失敗: {e}")
        return None, None, None

def calculate_accuracy(y_true, y_pred, tolerance=0.05):
    """計算預測準確率 (在容忍範圍內的預測比例)"""
    # 計算相對誤差
    relative_error = np.abs((y_pred - y_true) / y_true)
    # 計算在容忍範圍內的預測比例
    accuracy = np.mean(relative_error <= tolerance) * 100
    return accuracy

def train_models(X_train, X_test, y_train, y_test):
    """訓練多個模型並選擇最佳"""
    print("開始訓練模型...")
    
    models = {
        '隨機森林': RandomForestRegressor(n_estimators=100, random_state=42),
        'Ridge回歸': Ridge(alpha=1.0),
        'Lasso回歸': Lasso(alpha=0.1)
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"訓練 {name}...")
        
        try:
            # 訓練模型
            model.fit(X_train, y_train)
            
            # 預測
            y_pred = model.predict(X_test)
            
            # 評估
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            # 計算預測準確率 (5%容忍範圍)
            accuracy_5 = calculate_accuracy(y_test, y_pred, 0.05)
            accuracy_3 = calculate_accuracy(y_test, y_pred, 0.03)
            accuracy_1 = calculate_accuracy(y_test, y_pred, 0.01)
            
            results[name] = {
                'model': model,
                'mse': mse,
                'mae': mae,
                'r2': r2,
                'rmse': rmse,
                'accuracy_5': accuracy_5,
                'accuracy_3': accuracy_3,
                'accuracy_1': accuracy_1
            }
            
            print(f"      MSE: {mse:.4f}")
            print(f"      MAE: {mae:.4f}")
            print(f"      R²: {r2:.4f}")
            print(f"      準確率(5%): {accuracy_5:.1f}%")
            print(f"      準確率(3%): {accuracy_3:.1f}%")
            print(f"      準確率(1%): {accuracy_1:.1f}%")
            
        except Exception as e:
            print(f"{name} 訓練失敗: {e}")
    
    # 選擇最佳模型 (基於R²分數)
    if results:
        best_model_name = max(results.keys(), key=lambda k: results[k]['r2'])
        best_model_data = results[best_model_name]
        
        print(f"\n最佳模型: {best_model_name}")
        print(f"R² 分數: {best_model_data['r2']:.4f}")
        print(f"RMSE: {best_model_data['rmse']:.4f}")
        print(f"準確率(5%): {best_model_data['accuracy_5']:.1f}%")
        
        return best_model_name, best_model_data, results
    else:
        return None, None, None

def create_visualizations(X_test, y_test, all_results, feature_columns, folder_path):
    """建立視覺化圖表 (僅使用 matplotlib)"""
    if not VISUALIZATION_AVAILABLE:
        print("跳過圖表生成 (視覺化套件未安裝)")
        return []
    
    print("建立視覺化圖表...")
    
    # 設定中文字體
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    chart_files = []
    
    try:
        # 1. 模型性能比較圖 (包含準確率)
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        models = list(all_results.keys())
        r2_scores = [all_results[model]['r2'] for model in models]
        mse_scores = [all_results[model]['mse'] for model in models]
        accuracy_5 = [all_results[model]['accuracy_5'] for model in models]
        accuracy_3 = [all_results[model]['accuracy_3'] for model in models]
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        # R² 分數比較
        bars1 = ax1.bar(models, r2_scores, color=colors)
        ax1.set_title('模型 R² 分數比較', fontsize=14, fontweight='bold')
        ax1.set_ylabel('R² 分數')
        ax1.set_ylim(0, max(r2_scores) * 1.1)
        for i, v in enumerate(r2_scores):
            ax1.text(i, v + max(r2_scores)*0.02, f'{v:.4f}', ha='center', va='bottom')
        
        # MSE 比較
        bars2 = ax2.bar(models, mse_scores, color=colors)
        ax2.set_title('模型 MSE 比較', fontsize=14, fontweight='bold')
        ax2.set_ylabel('均方誤差 (MSE)')
        for i, v in enumerate(mse_scores):
            ax2.text(i, v + max(mse_scores)*0.02, f'{v:.2f}', ha='center', va='bottom')
        
        # 準確率比較 (5%)
        bars3 = ax3.bar(models, accuracy_5, color=colors)
        ax3.set_title('預測準確率比較 (5%容忍)', fontsize=14, fontweight='bold')
        ax3.set_ylabel('準確率 (%)')
        ax3.set_ylim(0, 100)
        for i, v in enumerate(accuracy_5):
            ax3.text(i, v + 2, f'{v:.1f}%', ha='center', va='bottom')
        
        # 準確率比較 (3%)
        bars4 = ax4.bar(models, accuracy_3, color=colors)
        ax4.set_title('預測準確率比較 (3%容忍)', fontsize=14, fontweight='bold')
        ax4.set_ylabel('準確率 (%)')
        ax4.set_ylim(0, 100)
        for i, v in enumerate(accuracy_3):
            ax4.text(i, v + 2, f'{v:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        performance_file = os.path.join(folder_path, 'model_performance_comparison.png')
        plt.savefig(performance_file, dpi=300, bbox_inches='tight')
        chart_files.append(performance_file)
        print(f"性能比較圖已儲存: model_performance_comparison.png")
        plt.close()
        
        # 2. 預測 vs 實際值散點圖
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        
        for idx, (model_name, model_data) in enumerate(all_results.items()):
            model = model_data['model']
            y_pred = model.predict(X_test)
            
            ax = axes[idx]
            ax.scatter(y_test, y_pred, alpha=0.6, color=colors[idx])
            
            # 完美預測線
            min_val = min(y_test.min(), y_pred.min())
            max_val = max(y_test.max(), y_pred.max())
            ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, alpha=0.8)
            
            ax.set_xlabel('實際股價')
            ax.set_ylabel('預測股價')
            ax.set_title(f'{model_name}\nR² = {model_data["r2"]:.4f}\n準確率(5%) = {model_data["accuracy_5"]:.1f}%', 
                        fontweight='bold')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        scatter_file = os.path.join(folder_path, 'prediction_vs_actual.png')
        plt.savefig(scatter_file, dpi=300, bbox_inches='tight')
        chart_files.append(scatter_file)
        print(f"預測散點圖已儲存: prediction_vs_actual.png")
        plt.close()
        
        # 3. 準確率詳細比較圖
        fig, ax = plt.subplots(figsize=(12, 8))
        
        x = np.arange(len(models))
        width = 0.25
        
        accuracy_1_vals = [all_results[model]['accuracy_1'] for model in models]
        accuracy_3_vals = [all_results[model]['accuracy_3'] for model in models]
        accuracy_5_vals = [all_results[model]['accuracy_5'] for model in models]
        
        bars1 = ax.bar(x - width, accuracy_1_vals, width, label='1%容忍', color='#FF6B6B', alpha=0.8)
        bars2 = ax.bar(x, accuracy_3_vals, width, label='3%容忍', color='#4ECDC4', alpha=0.8)
        bars3 = ax.bar(x + width, accuracy_5_vals, width, label='5%容忍', color='#45B7D1', alpha=0.8)
        
        ax.set_xlabel('模型')
        ax.set_ylabel('準確率 (%)')
        ax.set_title('模型預測準確率詳細比較', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(models)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 100)
        
        # 添加數值標籤
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        accuracy_file = os.path.join(folder_path, 'accuracy_comparison.png')
        plt.savefig(accuracy_file, dpi=300, bbox_inches='tight')
        chart_files.append(accuracy_file)
        print(f"準確率比較圖已儲存: accuracy_comparison.png")
        plt.close()
        
        # 4. 特徵重要性圖 (僅隨機森林)
        rf_model = None
        for model_name, model_data in all_results.items():
            if '隨機森林' in model_name:
                rf_model = model_data['model']
                break
        
        if rf_model and hasattr(rf_model, 'feature_importances_'):
            importances = rf_model.feature_importances_
            
            # 取前15個重要特徵
            indices = np.argsort(importances)[::-1][:15]
            
            plt.figure(figsize=(12, 8))
            plt.title('隨機森林 - 特徵重要性排名 (前15名)', fontsize=16, fontweight='bold')
            bars = plt.bar(range(len(indices)), importances[indices], color='#4ECDC4')
            plt.xticks(range(len(indices)), [feature_columns[i] for i in indices], rotation=45, ha='right')
            plt.ylabel('重要性分數')
            plt.grid(True, alpha=0.3)
            
            # 添加數值標籤
            for i, v in enumerate(importances[indices]):
                plt.text(i, v + max(importances)*0.01, f'{v:.3f}', ha='center', va='bottom')
            
            plt.tight_layout()
            importance_file = os.path.join(folder_path, 'feature_importance.png')
            plt.savefig(importance_file, dpi=300, bbox_inches='tight')
            chart_files.append(importance_file)
            print(f"特徵重要性圖已儲存: feature_importance.png")
            plt.close()
        
        # 5. 模型預測時間序列圖
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # 取最後100個測試點進行展示
        n_show = min(100, len(y_test))
        test_indices = range(len(y_test) - n_show, len(y_test))
        
        ax.plot(test_indices, y_test.iloc[-n_show:], 'o-', label='實際值', color='black', alpha=0.8, linewidth=2)
        
        for idx, (model_name, model_data) in enumerate(all_results.items()):
            model = model_data['model']
            y_pred = model.predict(X_test)
            accuracy = model_data['accuracy_5']
            ax.plot(test_indices, y_pred[-n_show:], 's-', 
                   label=f'{model_name} (準確率: {accuracy:.1f}%)', 
                   color=colors[idx], alpha=0.7, linewidth=2)
        
        ax.set_xlabel('測試樣本索引')
        ax.set_ylabel('股價')
        ax.set_title(f'模型預測 vs 實際值 (最後 {n_show} 個測試點)', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        timeseries_file = os.path.join(folder_path, 'prediction_timeseries.png')
        plt.savefig(timeseries_file, dpi=300, bbox_inches='tight')
        chart_files.append(timeseries_file)
        print(f"時間序列預測圖已儲存: prediction_timeseries.png")
        plt.close()
        
    except Exception as e:
        print(f"圖表建立失敗: {e}")
    
    return chart_files

def save_models(best_model_name, best_model_data, all_results, scaler, features, folder_path, timestamp):
    """儲存模型到正確的資料夾"""
    print(f"儲存模型到: {folder_path}")
    
    try:
        # 1. 儲存最佳模型
        best_model_file = os.path.join(folder_path, 'best_three_model.joblib')
        best_model_package = {
            'model': best_model_data['model'],
            'scaler': scaler,
            'features': features,
            'model_name': best_model_name,
            'performance': {
                'mse': best_model_data['mse'],
                'mae': best_model_data['mae'],
                'r2': best_model_data['r2'],
                'rmse': best_model_data['rmse'],
                'accuracy_5': best_model_data['accuracy_5'],
                'accuracy_3': best_model_data['accuracy_3'],
                'accuracy_1': best_model_data['accuracy_1']
            },
            'timestamp': timestamp,
            'save_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        joblib.dump(best_model_package, best_model_file)
        print(f"最佳模型已儲存: best_three_model.joblib")
        
        # 2. 儲存所有模型
        all_models_file = os.path.join(folder_path, 'all_three_models.joblib')
        all_models_package = {
            'models': {name: data['model'] for name, data in all_results.items()},
            'results': all_results,
            'scaler': scaler,
            'features': features,
            'best_model': best_model_name,
            'timestamp': timestamp,
            'save_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        joblib.dump(all_models_package, all_models_file)
        print(f"所有模型已儲存: all_three_models.joblib")
        
        # 3. 儲存模型報告
        report_file = os.path.join(folder_path, 'model_training_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("台積電股價預測 - 模型訓練報告\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"訓練時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"時間戳記: {timestamp}\n")
            f.write(f"儲存路徑: {folder_path}\n")
            f.write(f"特徵數量: {len(features)}\n\n")
            
            f.write("模型性能比較:\n")
            f.write("-" * 30 + "\n")
            for name, data in all_results.items():
                f.write(f"{name}:\n")
                f.write(f"  MSE: {data['mse']:.4f}\n")
                f.write(f"  MAE: {data['mae']:.4f}\n")
                f.write(f"  R²: {data['r2']:.4f}\n")
                f.write(f"  RMSE: {data['rmse']:.4f}\n")
                f.write(f"  準確率(5%): {data['accuracy_5']:.1f}%\n")
                f.write(f"  準確率(3%): {data['accuracy_3']:.1f}%\n")
                f.write(f"  準確率(1%): {data['accuracy_1']:.1f}%\n\n")
            
            f.write(f"最佳模型: {best_model_name}\n")
            f.write(f"最佳R²分數: {best_model_data['r2']:.4f}\n")
            f.write(f"最佳準確率(5%): {best_model_data['accuracy_5']:.1f}%\n")
        
        print(f"訓練報告已儲存: model_training_report.txt")
        
        return best_model_file, all_models_file
        
    except Exception as e:
        print(f"模型儲存失敗: {e}")
        return None, None

def main():
    """主程式"""
    print("\n" + "="*60)
    print(" "*15 + "台積電股價預測 - 模型訓練")
    print("="*60 + "\n")
    
    # 1. 尋找最新資料夾
    timestamp, folder_path = find_latest_data_folder()
    if not folder_path:
        print("找不到資料夾，請先執行 Get2330.py")
        return
    
    # 2. 載入訓練資料
    df = load_training_data(folder_path)
    if df is None:
        print("無法載入訓練資料")
        return
    
    # 3. 準備特徵
    features, target, feature_columns = prepare_features(df)
    if features is None:
        print("特徵準備失敗")
        return
    
    # 4. 分割資料
    print("分割訓練/測試資料...")
    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42
    )
    
    # 5. 特徵標準化
    print("進行特徵標準化...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 6. 訓練模型
    best_model_name, best_model_data, all_results = train_models(
        X_train_scaled, X_test_scaled, y_train, y_test
    )
    
    if not best_model_name:
        print("模型訓練失敗")
        return
    
    # 7. 建立視覺化圖表
    chart_files = create_visualizations(
        X_test_scaled, y_test, all_results, feature_columns, folder_path
    )
    
    # 8. 儲存模型
    best_file, all_file = save_models(
        best_model_name, best_model_data, all_results, 
        scaler, feature_columns, folder_path, timestamp
    )
    
    if best_file:
        print("\n" + "="*60)
        print(" "*18 + "訓練完成！")
        print("="*60)
        print(f"\n模型儲存位置: {folder_path}")
        print(f"時間戳記: {timestamp}")
        print(f"最佳模型: {best_model_name}")
        print(f"R² 分數: {best_model_data['r2']:.4f}")
        print(f"預測準確率(5%): {best_model_data['accuracy_5']:.1f}%")
        print(f"預測準確率(3%): {best_model_data['accuracy_3']:.1f}%")
        print(f"預測準確率(1%): {best_model_data['accuracy_1']:.1f}%")
        
        print(f"\n檔案清單:")
        print(f"   • best_three_model.joblib (Predict.py 會載入此檔)")
        print(f"   • all_three_models.joblib (所有模型)")
        print(f"   • model_training_report.txt (訓練報告)")
        
        if VISUALIZATION_AVAILABLE and chart_files:
            print(f"\n圖表檔案:")
            print(f"   • model_performance_comparison.png (模型性能比較)")
            print(f"   • prediction_vs_actual.png (預測 vs 實際)")
            print(f"   • accuracy_comparison.png (準確率比較)")
            print(f"   • feature_importance.png (特徵重要性)")
            print(f"   • prediction_timeseries.png (時間序列預測)")

if __name__ == "__main__":
    try:
        main()
        input("\n按 Enter 鍵結束...")
    except KeyboardInterrupt:
        print("\n\n程式被使用者中斷")
    except Exception as e:
        print(f"\n程式執行錯誤: {e}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 鍵結束...")
