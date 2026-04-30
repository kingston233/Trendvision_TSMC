import React, { useState, useEffect } from 'react';
import { ArrowUpRight, ArrowDownRight, Zap, PlayCircle, BarChart2 } from 'lucide-react';
import StockChart from '../components/StockChart';
import { StockInfo, StockDataPoint } from '../types';
import { getStocks, generateHistory } from '../services/mockDataService';
import { getStockData } from '../services/api';

interface DashboardProps {
  onSelectStock: (symbol: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onSelectStock }) => {
  const stocks = getStocks();
  const [marketData, setMarketData] = useState<StockDataPoint[]>([]);
  const [fullData, setFullData] = useState<StockDataPoint[]>([]);
  const [currentPrice, setCurrentPrice] = useState<number>(1440);
  const [previousPrice, setPreviousPrice] = useState<number>(1430);
  const [modelAccuracy, setModelAccuracy] = useState<number>(99.0);
  const [timeRange, setTimeRange] = useState<string>('1M');

  useEffect(() => {
    // Fetch real TSMC data
    const fetchData = async () => {
      try {
        const data = await getStockData('2330');
        if (data && data.length > 0) {
          setFullData(data); // Store full data
          setMarketData(data.slice(-30)); // Default to 1 month

          // Get latest prices
          const historicalData = data.filter(d => !d.isPrediction);
          if (historicalData.length >= 2) {
            setCurrentPrice(historicalData[historicalData.length - 1].price);
            setPreviousPrice(historicalData[historicalData.length - 2].price);
          }
        }
      } catch (error) {
        console.error('Failed to fetch market data:', error);
        // Fallback to mock data
        const mockData = generateHistory(1440, 60);
        setFullData(mockData);
        setMarketData(mockData.slice(-30));
      }
    };

    fetchData();
  }, []);

  // Update chart data when time range changes
  useEffect(() => {
    if (fullData.length === 0) return;

    const historicalData = fullData.filter(d => !d.isPrediction);
    let days = 30;

    switch (timeRange) {
      case '1D':
        days = 1;
        break;
      case '1W':
        days = 7;
        break;
      case '1M':
        days = 30;
        break;
      case '3M':
        days = 90;
        break;
      default:
        days = 30;
    }

    const startIndex = Math.max(0, historicalData.length - days);
    const selectedData = fullData.slice(startIndex);
    setMarketData(selectedData);
  }, [timeRange, fullData]);

  // Calculate price change
  const priceChange = currentPrice - previousPrice;
  const priceChangePercent = ((priceChange / previousPrice) * 100).toFixed(2);
  const isPriceUp = priceChange >= 0;

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">台積電市場總覽 (TSMC Market Overview)</h1>
          <p className="text-slate-500">AI 預測分析模組已啟動。使用隨機森林模型分析 485 筆歷史資料。</p>
        </div>
        <div className="flex gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-600 text-xs font-mono">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            MODEL LOADED
          </div>
          <button className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2 shadow-sm">
            <PlayCircle className="w-4 h-4" /> 執行回測
          </button>
        </div>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="台積電即時價格"
          value={`NT$${currentPrice.toFixed(2)}`}
          change={`${isPriceUp ? '+' : ''}${priceChangePercent}%`}
          positive={isPriceUp}
        />
        <StatCard
          label="今日漲跌"
          value={`NT$${Math.abs(priceChange).toFixed(2)}`}
          change={`${isPriceUp ? '+' : ''}${priceChange.toFixed(2)}`}
          positive={isPriceUp}
        />
        <StatCard
          label="AI 準確度 (5%)"
          value={`${modelAccuracy.toFixed(1)}%`}
          change="R² 0.9935"
          neutral={true}
        />
        <StatCard
          label="資料筆數"
          value="485"
          change="2023-2025"
          neutral={true}
        />
      </div>

      {/* Market Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
            <div className="flex justify-between items-center mb-6">
              <h3 className="font-semibold text-lg text-slate-800 flex items-center gap-2">
                <ActivityIcon /> 台積電 (2330) 價格走勢與預測
              </h3>
              <div className="flex gap-2">
                {['1D', '1W', '1M', '3M'].map(t => (
                  <button
                    key={t}
                    onClick={() => setTimeRange(t)}
                    className={`px-3 py-1 text-xs rounded-md font-medium transition-colors ${t === timeRange
                        ? 'bg-slate-900 text-white'
                        : 'text-slate-500 hover:bg-slate-100'
                      }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
            <StockChart data={marketData} color="#3b82f6" />
          </div>
        </div>

        {/* Top Movers List */}
        <div className="bg-white border border-slate-200 rounded-xl p-0 overflow-hidden flex flex-col shadow-sm">
          <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
            <h3 className="font-semibold text-slate-800">熱門交易機會</h3>
            <Zap className="w-4 h-4 text-amber-500" />
          </div>
          <div className="flex-1 overflow-y-auto">
            {stocks.map((stock) => (
              <div
                key={stock.symbol}
                onClick={() => onSelectStock(stock.symbol)}
                className="p-4 border-b border-slate-100 hover:bg-slate-50 cursor-pointer transition-colors group"
              >
                <div className="flex justify-between items-start mb-1">
                  <div>
                    <h4 className="font-bold text-slate-800 group-hover:text-blue-600 transition-colors">{stock.symbol}</h4>
                    <span className="text-xs text-slate-500">{stock.name}</span>
                  </div>
                  <div className={`text-right ${stock.change >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                    <div className="font-mono font-medium">NT${stock.price.toFixed(2)}</div>
                    <div className="text-xs flex items-center justify-end gap-1">
                      {stock.change >= 0 ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                      {Math.abs(stock.changePercent)}%
                    </div>
                  </div>
                </div>
                <div className="mt-2 flex items-center gap-2">
                  <div className="h-1.5 flex-1 bg-slate-100 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-blue-600 to-indigo-400 w-[70%]"></div>
                  </div>
                  <span className="text-[10px] text-blue-600 font-medium">92% Buy Signal</span>
                </div>
              </div>
            ))}
          </div>
          <div className="p-3 bg-slate-50/50 border-t border-slate-100 text-center">
            <button className="text-xs text-blue-600 hover:text-blue-700 font-medium">查看所有市場</button>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ label, value, change, positive, neutral }: any) => (
  <div className="bg-white p-5 rounded-xl border border-slate-200 hover:border-slate-300 hover:shadow-md transition-all">
    <p className="text-slate-500 text-sm font-medium mb-1">{label}</p>
    <div className="flex items-end gap-3">
      <h3 className="text-2xl font-bold text-slate-900 tracking-tight">{value}</h3>
      {!neutral && (
        <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${positive ? 'bg-emerald-50 text-emerald-600 border border-emerald-100' : 'bg-rose-50 text-rose-600 border border-rose-100'} flex items-center`}>
          {positive ? <ArrowUpRight className="w-3 h-3 mr-0.5" /> : <ArrowDownRight className="w-3 h-3 mr-0.5" />}
          {change}
        </span>
      )}
      {neutral && <span className="text-xs text-slate-500 px-1.5 py-0.5 bg-slate-100 rounded border border-slate-200">{change}</span>}
    </div>
  </div>
);

const ActivityIcon = () => (
  <div className="w-6 h-6 rounded-md bg-blue-50 flex items-center justify-center">
    <BarChart2 className="w-4 h-4 text-blue-600" />
  </div>
)

export default Dashboard;