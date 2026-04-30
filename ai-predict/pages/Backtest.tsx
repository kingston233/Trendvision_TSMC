import React, { useState, useEffect, useRef } from 'react';
import { Play, TrendingUp, DollarSign, Activity, AlertCircle } from 'lucide-react';
import { createChart, ColorType, IChartApi, Time, LineSeries } from 'lightweight-charts';
import { api } from '../services/api';

const Backtest: React.FC = () => {
    const [days, setDays] = useState(90);
    const [threshold, setThreshold] = useState(0.02);
    const [capital, setCapital] = useState(100000);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);

    const runBacktest = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await api.runBacktest('2330', days, threshold, capital);
            setResult(res);
        } catch (err: any) {
            setError(err.message || "Backtest failed");
        } finally {
            setLoading(false);
        }
    };

    // Render Chart when result changes
    useEffect(() => {
        if (!result || !chartContainerRef.current) return;

        if (chartRef.current) {
            chartRef.current.remove();
        }

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: '#ffffff' },
                textColor: '#333',
            },
            width: chartContainerRef.current.clientWidth,
            height: 400,
            grid: {
                vertLines: { color: '#f0f0f0' },
                horzLines: { color: '#f0f0f0' },
            },
        });
        chartRef.current = chart;

        // Equity Curve
        const equitySeries = chart.addSeries(LineSeries, {
            color: '#2563eb',
            lineWidth: 2,
            title: 'Equity',
        });

        const equityData = result.equityCurve.map((d: any) => ({
            time: d.date as Time,
            value: d.equity,
        }));
        equitySeries.setData(equityData);

        // Fit content
        chart.timeScale().fitContent();

        const handleResize = () => {
            chartRef.current?.applyOptions({ width: chartContainerRef.current?.clientWidth });
        };
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, [result]);

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold text-slate-900">Strategy Backtest</h1>

            {/* Controls */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-end">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">Backtest Period (Days)</label>
                        <input
                            type="number"
                            value={days}
                            onChange={(e) => setDays(Number(e.target.value))}
                            className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">Buy/Sell Threshold (%)</label>
                        <input
                            type="number"
                            step="0.01"
                            value={threshold * 100}
                            onChange={(e) => setThreshold(Number(e.target.value) / 100)}
                            className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">Initial Capital (NT$)</label>
                        <input
                            type="number"
                            value={capital}
                            onChange={(e) => setCapital(Number(e.target.value))}
                            className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                        />
                    </div>
                    <button
                        onClick={runBacktest}
                        disabled={loading}
                        className="bg-blue-600 text-white p-2 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                        {loading ? <Activity className="animate-spin w-5 h-5" /> : <Play className="w-5 h-5" />}
                        Run Simulation
                    </button>
                </div>
                {error && (
                    <div className="mt-4 p-3 bg-rose-50 text-rose-600 rounded-lg flex items-center gap-2">
                        <AlertCircle className="w-5 h-5" />
                        {error}
                    </div>
                )}
            </div>

            {/* Results */}
            {result && (
                <div className="space-y-6">
                    {/* Metrics */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <MetricCard
                            label="Total Return"
                            value={`${result.totalReturn.toFixed(2)}%`}
                            icon={TrendingUp}
                            trend={result.totalReturn >= 0 ? 'up' : 'down'}
                        />
                        <MetricCard
                            label="Final Equity"
                            value={`$${result.finalEquity.toLocaleString()}`}
                            icon={DollarSign}
                        />
                        <MetricCard
                            label="Win Rate"
                            value={`${result.winRate.toFixed(1)}%`}
                            icon={Activity}
                        />
                        <MetricCard
                            label="Total Trades"
                            value={result.totalTrades}
                            icon={Activity}
                        />
                    </div>

                    {/* Chart */}
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                        <h3 className="font-bold text-slate-800 mb-4">Equity Curve</h3>
                        <div ref={chartContainerRef} className="w-full h-[400px]" />
                    </div>

                    {/* Trade History */}
                    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                        <div className="p-6 border-b border-slate-100">
                            <h3 className="font-bold text-slate-800">Trade History</h3>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-slate-50 text-slate-500 uppercase">
                                    <tr>
                                        <th className="px-6 py-3">Date</th>
                                        <th className="px-6 py-3">Type</th>
                                        <th className="px-6 py-3">Price</th>
                                        <th className="px-6 py-3">Shares</th>
                                        <th className="px-6 py-3">Reason</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {result.trades.map((trade: any, i: number) => (
                                        <tr key={i} className="hover:bg-slate-50">
                                            <td className="px-6 py-4 font-medium text-slate-900">{trade.date}</td>
                                            <td className="px-6 py-4">
                                                <span className={`px-2 py-1 rounded text-xs font-bold ${trade.type === 'BUY' ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
                                                    }`}>
                                                    {trade.type}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">NT${trade.price.toFixed(2)}</td>
                                            <td className="px-6 py-4">{trade.shares}</td>
                                            <td className="px-6 py-4 text-slate-500">{trade.reason}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

const MetricCard = ({ label, value, icon: Icon, trend }: any) => (
    <div className="bg-white p-5 rounded-xl shadow-sm border border-slate-200 flex items-center justify-between">
        <div>
            <p className="text-sm text-slate-500 mb-1">{label}</p>
            <p className={`text-2xl font-bold ${trend === 'up' ? 'text-emerald-600' :
                    trend === 'down' ? 'text-rose-600' : 'text-slate-900'
                }`}>
                {value}
            </p>
        </div>
        <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center text-slate-500">
            <Icon className="w-5 h-5" />
        </div>
    </div>
);

export default Backtest;
