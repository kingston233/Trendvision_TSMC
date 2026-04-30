import React, { useEffect, useState } from 'react';
import { ArrowLeft, Target, TrendingUp, AlertTriangle, MessageSquare, RefreshCw } from 'lucide-react';
import { StockInfo, StockDataPoint, PredictionSummary, AIAnalysisResponse } from '../types';
import StockChart from '../components/StockChart';
import { api } from '../services/api'; // Updated import
import { chatWithAI } from '../services/geminiService';

interface StockDetailProps {
    stock: StockInfo;
    onBack: () => void;
}

const StockDetail: React.FC<StockDetailProps> = ({ stock, onBack }) => {
    const [historyData, setHistoryData] = useState<StockDataPoint[]>([]);
    const [prediction, setPrediction] = useState<PredictionSummary | null>(null);
    const [aiAnalysis, setAiAnalysis] = useState<AIAnalysisResponse | null>(null);
    const [loading, setLoading] = useState(true);

    // Chat state
    const [chatInput, setChatInput] = useState("");
    const [chatHistory, setChatHistory] = useState<{ role: 'user' | 'ai', text: string }[]>([]);
    const [chatLoading, setChatLoading] = useState(false);

    useEffect(() => {
        const loadData = async () => {
            setLoading(true);

            try {
                // 1. Get History & Predictions from API (or Mock)
                const data = await api.getStockData(stock.symbol);
                setHistoryData(data);

                // 2. Get Prediction Summary
                const pred = await api.getPrediction(stock.symbol);
                setPrediction(pred);

                // 3. Get AI Analysis
                const analysis = await api.getAnalysis(stock, pred);
                setAiAnalysis(analysis);

            } catch (err) {
                console.error("Failed to load stock data", err);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, [stock]);

    const handleSendMessage = async () => {
        if (!chatInput.trim()) return;
        const msg = chatInput;
        setChatInput("");
        setChatHistory(prev => [...prev, { role: 'user', text: msg }]);
        setChatLoading(true);

        const context = `Stock: ${stock.symbol}, Current Price: ${stock.price}, Prediction: ${prediction?.signal} target ${prediction?.targetPrice}`;
        const response = await chatWithAI(msg, context);

        setChatHistory(prev => [...prev, { role: 'ai', text: response }]);
        setChatLoading(false);
    };

    return (
        <div className="space-y-6">
            <button onClick={onBack} className="flex items-center text-slate-500 hover:text-slate-800 transition-colors mb-4 group font-medium">
                <ArrowLeft className="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" /> Back to Dashboard
            </button>

            {/* Header */}
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <h1 className="text-4xl font-bold text-slate-900">{stock.symbol}</h1>
                        <span className="bg-slate-100 border border-slate-200 text-slate-600 text-xs px-2 py-1 rounded font-medium">{stock.sector}</span>
                    </div>
                    <h2 className="text-xl text-slate-500">{stock.name}</h2>
                </div>
                <div className="text-right">
                    <div className="text-3xl font-mono font-bold text-slate-900">NT${stock.price.toFixed(2)}</div>
                    <div className={`text-sm font-medium ${stock.change >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                        {stock.change > 0 ? '+' : ''}{stock.change} ({stock.changePercent}%)
                    </div>
                </div>
            </div>

            {/* Market Stats Bar */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                    <div className="text-xs text-slate-500 mb-1">本益比 (P/E)</div>
                    <div className="font-bold text-slate-800">{stock.peRatio ? stock.peRatio.toFixed(2) : 'N/A'}</div>
                </div>
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                    <div className="text-xs text-slate-500 mb-1">市值 (Market Cap)</div>
                    <div className="font-bold text-slate-800">{stock.marketCap}</div>
                </div>
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                    <div className="text-xs text-slate-500 mb-1">成交量 (Volume)</div>
                    <div className="font-bold text-slate-800">{stock.volume ? stock.volume.toLocaleString() : 'N/A'}</div>
                </div>
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                    <div className="text-xs text-slate-500 mb-1">當日範圍 (Day Range)</div>
                    <div className="font-bold text-slate-800 text-sm">
                        {stock.dayLow ? stock.dayLow.toFixed(1) : '-'} - {stock.dayHigh ? stock.dayHigh.toFixed(1) : '-'}
                    </div>
                </div>
                <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                    <div className="text-xs text-slate-500 mb-1">漲跌停 (Limits)</div>
                    <div className="font-bold text-xs text-slate-800 flex flex-col">
                        <span className="text-rose-600">▲ {stock.limitUp?.toFixed(1) || '-'}</span>
                        <span className="text-emerald-600">▼ {stock.limitDown?.toFixed(1) || '-'}</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-auto">

                {/* Main Chart Section */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Chart Card */}
                    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                                <TrendingUp className="w-4 h-4 text-blue-600" /> 股價走勢與 AI 預測
                            </h3>
                            <div className="flex items-center gap-2 text-xs">
                                <span className="flex items-center gap-1 text-slate-500"><div className="w-2 h-2 bg-emerald-500 rounded-full"></div> 歷史數據</span>
                                <span className="flex items-center gap-1 text-blue-600"><div className="w-2 h-2 bg-blue-500 rounded-full"></div> AI 預測</span>
                            </div>
                        </div>
                        {loading ? (
                            <div className="h-[350px] flex items-center justify-center text-slate-500">
                                <RefreshCw className="w-6 h-6 animate-spin mr-2" /> Loading Neural Model...
                            </div>
                        ) : (
                            <StockChart
                                data={historyData}
                                colors={{
                                    backgroundColor: '#ffffff',
                                    textColor: '#333333',
                                }}
                            />
                        )}
                    </div>

                    {/* AI Analysis Card */}
                    <div className="bg-gradient-to-br from-white to-slate-50 border border-slate-200 rounded-xl p-6 relative overflow-hidden shadow-sm">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none"></div>

                        <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                            <Target className="w-5 h-5 text-indigo-500" /> Gemini 智能分析
                        </h3>

                        {loading || !aiAnalysis ? (
                            <div className="animate-pulse space-y-3">
                                <div className="h-4 bg-slate-100 rounded w-3/4"></div>
                                <div className="h-4 bg-slate-100 rounded w-1/2"></div>
                                <div className="h-4 bg-slate-100 rounded w-5/6"></div>
                            </div>
                        ) : (
                            <div className="space-y-4 relative z-10">
                                <p className="text-slate-600 leading-relaxed text-sm">
                                    {aiAnalysis.summary}
                                </p>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                                    <div>
                                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">關鍵因素</h4>
                                        <ul className="space-y-2">
                                            {aiAnalysis.keyFactors.map((factor, i) => (
                                                <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                                                    <span className="mt-1.5 w-1 h-1 bg-indigo-500 rounded-full flex-shrink-0"></span>
                                                    {factor}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                    <div>
                                        <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">風險評估</h4>
                                        <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg border ${aiAnalysis.riskLevel === 'High' ? 'bg-rose-50 border-rose-200 text-rose-600' :
                                            aiAnalysis.riskLevel === 'Medium' ? 'bg-amber-50 border-amber-200 text-amber-600' :
                                                'bg-emerald-50 border-emerald-200 text-emerald-600'
                                            }`}>
                                            <AlertTriangle className="w-4 h-4" />
                                            <span className="font-bold">{aiAnalysis.riskLevel} Risk</span>
                                        </div>
                                        <p className="text-xs text-slate-500 mt-2">基於波動率與產業逆風判斷。</p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Sidebar - Metrics & Chat */}
                <div className="space-y-6">
                    {/* Prediction Stats */}
                    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                        <h3 className="text-sm font-semibold text-slate-500 mb-4">模型輸出 (MODEL OUTPUT)</h3>
                        {prediction && (
                            <div className="space-y-6">
                                <div className="text-center p-4 rounded-lg bg-slate-50 border border-slate-100">
                                    <span className="text-xs text-slate-500 block mb-1">建議信號 (SIGNAL)</span>
                                    <span className={`text-2xl font-black tracking-wider ${prediction.signal === 'BUY' ? 'text-emerald-500' :
                                        prediction.signal === 'SELL' ? 'text-rose-500' : 'text-slate-500'
                                        }`}>
                                        {prediction.signal}
                                    </span>
                                </div>

                                <div className="flex justify-between items-center border-b border-slate-100 pb-3">
                                    <span className="text-sm text-slate-500">信心度</span>
                                    <div className="text-right">
                                        <span className="text-xl font-bold text-slate-800">{prediction.confidence}%</span>
                                        <div className="w-24 h-1.5 bg-slate-100 rounded-full mt-1 overflow-hidden">
                                            <div className="h-full bg-blue-500" style={{ width: `${prediction.confidence}%` }}></div>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex justify-between items-center border-b border-slate-100 pb-3">
                                    <span className="text-sm text-slate-500">目標價 (30天)</span>
                                    <span className="text-xl font-bold text-blue-600">NT${prediction.targetPrice.toFixed(2)}</span>
                                </div>

                                {prediction.predictedClosePrice && (
                                    <div className="flex justify-between items-center border-b border-slate-100 pb-3">
                                        <span className="text-sm text-slate-500">預測今日收盤</span>
                                        <span className="text-xl font-bold text-indigo-600">NT${prediction.predictedClosePrice.toFixed(2)}</span>
                                    </div>
                                )}

                                {prediction.predictedNextDayClose && (
                                    <div className="flex justify-between items-center border-b border-slate-100 pb-3">
                                        <span className="text-sm text-slate-500">預測隔日收盤</span>
                                        <span className="text-xl font-bold text-purple-600">NT${prediction.predictedNextDayClose.toFixed(2)}</span>
                                    </div>
                                )}

                                <div className="flex justify-between items-center pb-1">
                                    <span className="text-sm text-slate-500">波動率</span>
                                    <span className="text-sm font-medium text-slate-800">{stock.volatility}</span>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* AI Assistant Chat */}
                    <div className="bg-white border border-slate-200 rounded-xl flex flex-col h-[400px] shadow-sm">
                        <div className="p-4 border-b border-slate-100">
                            <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                                <MessageSquare className="w-4 h-4 text-indigo-500" /> 分析師助理
                            </h3>
                        </div>
                        <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin scrollbar-thumb-slate-200">
                            <div className="flex flex-col items-start max-w-[85%]">
                                <div className="bg-slate-100 text-slate-700 p-3 rounded-2xl rounded-tl-none text-sm border border-slate-200">
                                    你好！我正在分析 {stock.symbol} ({stock.name})。你可以問我關於趨勢或具體指標的問題。
                                </div>
                            </div>
                            {chatHistory.map((msg, idx) => (
                                <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                                    <div className={`p-3 rounded-2xl text-sm max-w-[85%] shadow-sm ${msg.role === 'user'
                                        ? 'bg-blue-600 text-white rounded-tr-none'
                                        : 'bg-slate-100 text-slate-700 rounded-tl-none border border-slate-200'
                                        }`}>
                                        {msg.text}
                                    </div>
                                </div>
                            ))}
                            {chatLoading && (
                                <div className="flex items-center gap-1 ml-2">
                                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></div>
                                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce delay-75"></div>
                                    <div className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce delay-150"></div>
                                </div>
                            )}
                        </div>
                        <div className="p-3 border-t border-slate-100">
                            <div className="relative">
                                <input
                                    type="text"
                                    className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-3 pr-10 py-2 text-sm text-slate-900 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                                    placeholder="詢問分析原因..."
                                    value={chatInput}
                                    onChange={(e) => setChatInput(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                                />
                                <button
                                    onClick={handleSendMessage}
                                    className="absolute right-2 top-1.5 text-blue-500 hover:text-blue-600"
                                >
                                    <ArrowLeft className="w-4 h-4 rotate-180" />
                                </button>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
};

export default StockDetail;