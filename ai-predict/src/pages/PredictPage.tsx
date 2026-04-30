import React, { useState, useEffect } from 'react';
import { getPrediction, PredictionResponse } from '../services/apiService';

export default function PredictPage() {
    const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadPrediction = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getPrediction();
            setPrediction(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : '預測失敗');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadPrediction();
    }, []);

    return (
        <div className="space-y-6">
            {/* 標題 */}
            <div className="text-center">
                <h2 className="text-4xl font-bold text-white mb-2">收盤價預測</h2>
                <p className="text-gray-400">使用機器學習模型預測台積電下一個交易日收盤價</p>
            </div>

            {/* 預測結果卡片 */}
            <div className="bg-gradient-to-br from-purple-900/50 to-pink-900/50 backdrop-blur-lg rounded-2xl p-8 border border-white/10 shadow-2xl">
                {loading && (
                    <div className="flex items-center justify-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
                    </div>
                )}

                {error && (
                    <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4 text-red-200">
                        {error}
                    </div>
                )}

                {prediction && !loading && (
                    <div className="space-y-6">
                        {/* 預測價格 */}
                        <div className="text-center">
                            <div className="text-gray-400 text-sm mb-2">預測收盤價</div>
                            <div className="text-6xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                                ${prediction.predicted_price.toFixed(2)}
                            </div>
                            <div className="text-gray-400 text-sm mt-2">TWD</div>
                        </div>

                        {/* 變化百分比 */}
                        {prediction.change_percent !== undefined && (
                            <div className="flex items-center justify-center space-x-2">
                                <span className={`text-2xl font-semibold ${prediction.change_percent >= 0 ? 'text-green-400' : 'text-red-400'
                                    }`}>
                                    {prediction.change_percent >= 0 ? '↑' : '↓'} {Math.abs(prediction.change_percent).toFixed(2)}%
                                </span>
                            </div>
                        )}

                        {/* 詳細資訊 */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
                            {prediction.current_price && (
                                <div className="bg-black/30 rounded-lg p-4">
                                    <div className="text-gray-400 text-sm mb-1">當前價格</div>
                                    <div className="text-2xl font-semibold text-white">
                                        ${prediction.current_price.toFixed(2)}
                                    </div>
                                </div>
                            )}

                            {prediction.confidence !== undefined && (
                                <div className="bg-black/30 rounded-lg p-4">
                                    <div className="text-gray-400 text-sm mb-1">模型信心度</div>
                                    <div className="text-2xl font-semibold text-white">
                                        {prediction.confidence.toFixed(1)}%
                                    </div>
                                </div>
                            )}

                            <div className="bg-black/30 rounded-lg p-4">
                                <div className="text-gray-400 text-sm mb-1">使用模型</div>
                                <div className="text-lg font-semibold text-white">
                                    {prediction.model_name}
                                </div>
                            </div>
                        </div>

                        {/* 預測時間 */}
                        <div className="text-center text-gray-400 text-sm mt-4">
                            預測時間: {prediction.prediction_time}
                        </div>

                        {/* 重新預測按鈕 */}
                        <div className="flex justify-center mt-6">
                            <button
                                onClick={loadPrediction}
                                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg shadow-lg hover:shadow-purple-500/50 transition-all transform hover:scale-105"
                            >
                                重新預測
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* 說明 */}
            <div className="bg-black/30 backdrop-blur-lg rounded-lg p-6 border border-white/10">
                <h3 className="text-xl font-semibold text-white mb-3">預測說明</h3>
                <ul className="space-y-2 text-gray-300">
                    <li>• 使用隨機森林、Ridge 回歸、Lasso 回歸等機器學習模型</li>
                    <li>• 基於歷史股價、技術指標、成交量等多維度特徵</li>
                    <li>• 預測結果僅供參考，投資有風險</li>
                </ul>
            </div>
        </div>
    );
}
