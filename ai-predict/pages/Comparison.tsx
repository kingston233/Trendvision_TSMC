import React, { useState, useEffect } from 'react';
import { Plus, X, GitCompare, Search, TrendingUp, AlertTriangle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { StockInfo, StockDataPoint } from '../types';
import { getStocks, getStockDetails, generateHistory } from '../services/mockDataService';

const CHART_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#f43f5e'];

const Comparison: React.FC = () => {
    const [selectedSymbols, setSelectedSymbols] = useState<string[]>(['2330']);
    const [chartData, setChartData] = useState<any[]>([]);
    const [stockDetails, setStockDetails] = useState<StockInfo[]>([]);
    const [isAdding, setIsAdding] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');

    const allStocks = getStocks();
    const availableStocks = allStocks.filter(s => !selectedSymbols.includes(s.symbol));
    const filteredSearch = availableStocks.filter(s =>
        s.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    useEffect(() => {
        // 1. Fetch details for all selected stocks
        const details = selectedSymbols.map(sym => getStockDetails(sym)).filter((s): s is StockInfo => !!s);
        setStockDetails(details);

        // 2. Generate and normalize chart data
        // We want to show Percentage Return starting from Day 0 = 0%
        if (details.length > 0) {
            const historyLength = 30;
            // Get raw history for each
            const rawHistories = details.map(stock => {
                const hist = generateHistory(stock.price, historyLength);
                // Sort by date ascending just in case
                return { symbol: stock.symbol, data: hist.reverse() };
            });

            // Merge into one array: [{ date: '...', AAPL: 0, MSFT: 0 }, { date: '...', AAPL: 1.2, MSFT: -0.5 }]
            const mergedData: any[] = [];

            // Assume all generated histories have same length/dates for this mock
            const dates = rawHistories[0].data.map(d => d.date);

            dates.forEach((date, dateIdx) => {
                const entry: any = { date: date.slice(5) }; // MM-DD

                rawHistories.forEach(item => {
                    const dayPrice = item.data[dateIdx].price;
                    const startPrice = item.data[0].price;
                    // Calculate percentage return relative to start of period
                    const pctReturn = ((dayPrice - startPrice) / startPrice) * 100;
                    entry[item.symbol] = pctReturn;
                });

                mergedData.push(entry);
            });

            setChartData(mergedData);
        } else {
            setChartData([]);
        }
    }, [selectedSymbols]);

    const addStock = (symbol: string) => {
        if (selectedSymbols.length < 5) {
            setSelectedSymbols([...selectedSymbols, symbol]);
            setIsAdding(false);
            setSearchQuery('');
        }
    };

    const removeStock = (symbol: string) => {
        setSelectedSymbols(selectedSymbols.filter(s => s !== symbol));
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 mb-2">股票比較 (Compare Stocks)</h1>
                    <p className="text-slate-500">並排分析關鍵績效指標與趨勢。</p>
                </div>

                {/* Stock Selector */}
                <div className="relative z-20">
                    {!isAdding ? (
                        <button
                            onClick={() => setIsAdding(true)}
                            disabled={selectedSymbols.length >= 5}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white rounded-lg transition-colors font-medium shadow-sm shadow-blue-500/20"
                        >
                            <Plus className="w-4 h-4" /> 加入股票
                        </button>
                    ) : (
                        <div className="w-64 bg-white border border-slate-200 rounded-lg shadow-xl p-2 animate-in fade-in zoom-in-95 duration-200">
                            <div className="flex items-center gap-2 border-b border-slate-100 pb-2 mb-2 px-2">
                                <Search className="w-4 h-4 text-slate-400" />
                                <input
                                    autoFocus
                                    type="text"
                                    placeholder="輸入代碼 (例如 2330)..."
                                    className="w-full text-sm outline-none text-slate-700"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                />
                                <button onClick={() => setIsAdding(false)}><X className="w-4 h-4 text-slate-400 hover:text-slate-600" /></button>
                            </div>
                            <div className="max-h-48 overflow-y-auto">
                                {filteredSearch.map(s => (
                                    <button
                                        key={s.symbol}
                                        onClick={() => addStock(s.symbol)}
                                        className="w-full text-left px-3 py-2 text-sm hover:bg-slate-50 rounded text-slate-700 flex justify-between"
                                    >
                                        <span className="font-bold">{s.symbol}</span>
                                        <span className="text-slate-400 text-xs">{s.name}</span>
                                    </button>
                                ))}
                                {filteredSearch.length === 0 && <div className="p-2 text-xs text-center text-slate-400">無結果</div>}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Selected Tags */}
            <div className="flex flex-wrap gap-3">
                {stockDetails.map((stock, idx) => (
                    <div key={stock.symbol} className="flex items-center gap-3 pl-3 pr-2 py-1.5 bg-white border border-slate-200 rounded-full shadow-sm">
                        <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: CHART_COLORS[idx % CHART_COLORS.length] }}></div>
                        <div className="flex flex-col leading-none">
                            <span className="font-bold text-sm text-slate-800">{stock.symbol}</span>
                            <span className="text-[10px] text-slate-500">NT${stock.price}</span>
                        </div>
                        <button
                            onClick={() => removeStock(stock.symbol)}
                            className="p-1 hover:bg-slate-100 rounded-full text-slate-400 hover:text-rose-500 transition-colors ml-1"
                        >
                            <X className="w-3 h-3" />
                        </button>
                    </div>
                ))}
            </div>

            {/* Performance Chart */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <h3 className="font-semibold text-lg text-slate-800 mb-6 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-blue-600" /> 績效比較 (30天)
                </h3>
                <div className="h-[400px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                            <XAxis
                                dataKey="date"
                                stroke="#94a3b8"
                                tick={{ fontSize: 12, fill: '#64748b' }}
                                axisLine={false}
                                tickLine={false}
                            />
                            <YAxis
                                stroke="#94a3b8"
                                tick={{ fontSize: 12, fill: '#64748b' }}
                                axisLine={false}
                                tickLine={false}
                                tickFormatter={(val) => `${val > 0 ? '+' : ''}${val}%`}
                            />
                            <Tooltip
                                contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                formatter={(value: number) => [`${value.toFixed(2)}%`, 'Return']}
                            />
                            <Legend />
                            {stockDetails.map((stock, idx) => (
                                <Line
                                    key={stock.symbol}
                                    type="monotone"
                                    dataKey={stock.symbol}
                                    stroke={CHART_COLORS[idx % CHART_COLORS.length]}
                                    strokeWidth={2}
                                    dot={false}
                                    activeDot={{ r: 6 }}
                                />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Metrics Comparison Table */}
            <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                <div className="p-6 border-b border-slate-100 bg-slate-50/50">
                    <h3 className="font-semibold text-lg text-slate-800 flex items-center gap-2">
                        <GitCompare className="w-5 h-5 text-indigo-600" /> 基本面比較
                    </h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead>
                            <tr className="bg-slate-50 border-b border-slate-200">
                                <th className="px-6 py-4 font-medium text-slate-500">指標</th>
                                {stockDetails.map((stock, idx) => (
                                    <th key={stock.symbol} className="px-6 py-4 font-bold text-slate-800" style={{ color: CHART_COLORS[idx % CHART_COLORS.length] }}>
                                        {stock.symbol}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            <MetricRow label="現價 (Price)" stocks={stockDetails} formatter={(val: number) => `NT$${val.toFixed(2)}`} accessor="price" />
                            <MetricRow
                                label="漲跌幅 (Change)"
                                stocks={stockDetails}
                                accessor="changePercent"
                                render={(s: StockInfo) => (
                                    <span className={`${s.change >= 0 ? 'text-emerald-600' : 'text-rose-600'} font-medium`}>
                                        {s.change > 0 ? '+' : ''}{s.changePercent}%
                                    </span>
                                )}
                            />
                            <MetricRow label="市值 (Market Cap)" stocks={stockDetails} accessor="marketCap" />
                            <MetricRow label="本益比 (P/E)" stocks={stockDetails} accessor="peRatio" />
                            <MetricRow
                                label="波動率 (Volatility)"
                                stocks={stockDetails}
                                accessor="volatility"
                                render={(s: StockInfo) => (
                                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${s.volatility === 'High' ? 'bg-rose-100 text-rose-700' :
                                            s.volatility === 'Medium' ? 'bg-amber-100 text-amber-700' :
                                                'bg-emerald-100 text-emerald-700'
                                        }`}>
                                        {s.volatility}
                                    </span>
                                )}
                            />
                            <MetricRow label="產業 (Sector)" stocks={stockDetails} accessor="sector" />
                            <MetricRow
                                label="AI 信號 (AI Signal)"
                                stocks={stockDetails}
                                // Simulate an AI signal for the comparison table
                                render={(s: StockInfo) => {
                                    const signal = Math.random() > 0.5 ? 'BUY' : 'HOLD'; // Mock logic for table
                                    return (
                                        <span className={`font-bold ${signal === 'BUY' ? 'text-emerald-500' : 'text-slate-500'}`}>
                                            {signal}
                                        </span>
                                    )
                                }}
                            />
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

const MetricRow = ({ label, stocks, accessor, formatter, render }: any) => (
    <tr className="hover:bg-slate-50/50 transition-colors">
        <td className="px-6 py-4 font-medium text-slate-500">{label}</td>
        {stocks.map((stock: any) => (
            <td key={stock.symbol} className="px-6 py-4 text-slate-800">
                {render ? render(stock) : (formatter ? formatter(stock[accessor]) : stock[accessor])}
            </td>
        ))}
    </tr>
);

export default Comparison;