import React, { useState, useEffect } from 'react';
import { getChartData, ChartDataResponse } from '../services/apiService';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ChartPage() {
    const [chartData, setChartData] = useState<ChartDataResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [timeRange, setTimeRange] = useState<'1m' | '3m' | '6m' | 'all'>('3m');

    useEffect(() => {
        loadChartData();
    }, []);

    const loadChartData = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await getChartData();
            setChartData(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : '載入圖表資料失敗');
        } finally {
            setLoading(false);
        }
    };

    // 根據時間範圍過濾資料
    const getFilteredData = () => {
        if (!chartData) return [];

        const data = chartData.chart_data;
        const now = new Date();
        let startDate = new Date();

        switch (timeRange) {
            case '1m':
                startDate.setMonth(now.getMonth() - 1);
                break;
            case '3m':
                startDate.setMonth(now.getMonth() - 3);
                break;
            case '6m':
                startDate.setMonth(now.getMonth() - 6);
                break;
            case 'all':
                return data;
        }

        return data.filter(d => new Date(d.date) >= startDate);
    };

    const filteredData = getFilteredData();

    return (
        <div className="space-y-6">
            {/* 標題 */}
            <div className="text-center">
                <h2 className="text-4xl font-bold text-white mb-2">圖表展示</h2>
                <p className="text-gray-400">本益比、價格走勢和 MACD 技術指標</p>
            </div>

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

            {chartData && !loading && (
                <div className="space-y-6">
                    {/* 本益比卡片 */}
                    {chartData.pe_ratio && (
                        <div className="bg-gradient-to-br from-purple-900/50 to-pink-900/50 backdrop-blur-lg rounded-2xl p-6 border border-white/10">
                            <h3 className="text-xl font-semibold text-white mb-4">本益比 (P/E Ratio)</h3>
                            <div className="text-center">
                                <div className="text-5xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                                    {chartData.pe_ratio.toFixed(2)}
                                </div>
                                <div className="text-gray-400 text-sm mt-2">倍</div>
                            </div>
                        </div>
                    )}

                    {/* 時間範圍選擇 */}
                    <div className="flex justify-center space-x-2">
                        {(['1m', '3m', '6m', 'all'] as const).map((range) => (
                            <button
                                key={range}
                                onClick={() => setTimeRange(range)}
                                className={`px-4 py-2 rounded-lg font-medium transition-all ${timeRange === range
                                        ? 'bg-purple-600 text-white'
                                        : 'bg-white/10 text-gray-300 hover:bg-white/20'
                                    }`}
                            >
                                {range === '1m' ? '1個月' : range === '3m' ? '3個月' : range === '6m' ? '6個月' : '全部'}
                            </button>
                        ))}
                    </div>

                    {/* 價格走勢圖 */}
                    <div className="bg-black/30 backdrop-blur-lg rounded-lg p-6 border border-white/10">
                        <h3 className="text-xl font-semibold text-white mb-4">價格走勢</h3>
                        <ResponsiveContainer width="100%" height={400}>
                            <LineChart data={filteredData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis
                                    dataKey="date"
                                    stroke="#888"
                                    tick={{ fill: '#888' }}
                                    tickFormatter={(value) => {
                                        const date = new Date(value);
                                        return `${date.getMonth() + 1}/${date.getDate()}`;
                                    }}
                                />
                                <YAxis
                                    stroke="#888"
                                    tick={{ fill: '#888' }}
                                    domain={['auto', 'auto']}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1a1a2e',
                                        border: '1px solid #444',
                                        borderRadius: '8px',
                                        color: '#fff'
                                    }}
                                    formatter={(value: any) => [`$${value?.toFixed(2)}`, '']}
                                />
                                <Legend wrapperStyle={{ color: '#888' }} />
                                <Line
                                    type="monotone"
                                    dataKey="close"
                                    stroke="#a855f7"
                                    strokeWidth={2}
                                    name="收盤價"
                                    dot={false}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="high"
                                    stroke="#ec4899"
                                    strokeWidth={1}
                                    strokeDasharray="5 5"
                                    name="最高價"
                                    dot={false}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="low"
                                    stroke="#3b82f6"
                                    strokeWidth={1}
                                    strokeDasharray="5 5"
                                    name="最低價"
                                    dot={false}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* MACD 指標圖 */}
                    <div className="bg-black/30 backdrop-blur-lg rounded-lg p-6 border border-white/10">
                        <h3 className="text-xl font-semibold text-white mb-4">MACD 指標</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={filteredData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis
                                    dataKey="date"
                                    stroke="#888"
                                    tick={{ fill: '#888' }}
                                    tickFormatter={(value) => {
                                        const date = new Date(value);
                                        return `${date.getMonth() + 1}/${date.getDate()}`;
                                    }}
                                />
                                <YAxis stroke="#888" tick={{ fill: '#888' }} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1a1a2e',
                                        border: '1px solid #444',
                                        borderRadius: '8px',
                                        color: '#fff'
                                    }}
                                    formatter={(value: any) => [value?.toFixed(4), '']}
                                />
                                <Legend wrapperStyle={{ color: '#888' }} />
                                <Line
                                    type="monotone"
                                    dataKey="macd"
                                    stroke="#10b981"
                                    strokeWidth={2}
                                    name="MACD"
                                    dot={false}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="macd_signal"
                                    stroke="#f59e0b"
                                    strokeWidth={2}
                                    name="信號線"
                                    dot={false}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* MACD 柱狀圖 */}
                    <div className="bg-black/30 backdrop-blur-lg rounded-lg p-6 border border-white/10">
                        <h3 className="text-xl font-semibold text-white mb-4">MACD 柱狀圖</h3>
                        <ResponsiveContainer width="100%" height={200}>
                            <BarChart data={filteredData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                                <XAxis
                                    dataKey="date"
                                    stroke="#888"
                                    tick={{ fill: '#888' }}
                                    tickFormatter={(value) => {
                                        const date = new Date(value);
                                        return `${date.getMonth() + 1}/${date.getDate()}`;
                                    }}
                                />
                                <YAxis stroke="#888" tick={{ fill: '#888' }} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: '#1a1a2e',
                                        border: '1px solid #444',
                                        borderRadius: '8px',
                                        color: '#fff'
                                    }}
                                    formatter={(value: any) => [value?.toFixed(4), 'MACD Histogram']}
                                />
                                <Bar
                                    dataKey="macd_histogram"
                                    fill="#6366f1"
                                    name="MACD 柱狀圖"
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* 資料資訊 */}
                    <div className="bg-black/30 backdrop-blur-lg rounded-lg p-4 border border-white/10">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                            <div>
                                <div className="text-gray-400 text-sm">資料點數</div>
                                <div className="text-white text-lg font-semibold">{filteredData.length}</div>
                            </div>
                            <div>
                                <div className="text-gray-400 text-sm">開始日期</div>
                                <div className="text-white text-lg font-semibold">
                                    {filteredData[0]?.date || '-'}
                                </div>
                            </div>
                            <div>
                                <div className="text-gray-400 text-sm">結束日期</div>
                                <div className="text-white text-lg font-semibold">
                                    {filteredData[filteredData.length - 1]?.date || '-'}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
