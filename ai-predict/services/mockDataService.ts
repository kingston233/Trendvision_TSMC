import { StockDataPoint, StockInfo, PredictionSummary } from '../types';

const STOCKS: StockInfo[] = [
  { symbol: '2330', name: '台積電 (TSMC)', price: 980.00, change: 12.00, changePercent: 1.24, sector: '半導體', marketCap: '25.4T', peRatio: 24.5, volatility: 'Low' },
];

// Helper to generate random walk data
export const generateHistory = (basePrice: number, days: number): StockDataPoint[] => {
  const data: StockDataPoint[] = [];
  let currentPrice = basePrice * 0.95; // Start a bit lower
  const now = new Date();

  for (let i = days; i > 0; i--) {
    const date = new Date(now);
    date.setDate(date.getDate() - i);

    const volatility = 0.025; // Slightly higher volatility for better demo
    const change = currentPrice * (Math.random() * volatility - (volatility / 2) + 0.0005);

    const open = currentPrice;
    currentPrice += change;
    const high = currentPrice * (1 + Math.random() * 0.015);
    const low = currentPrice * (1 - Math.random() * 0.015);

    data.push({
      date: date.toISOString().split('T')[0],
      price: parseFloat(currentPrice.toFixed(2)),
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      volume: Math.floor(Math.random() * 5000) + 1000, // Adjusted volume for TW lots usually
    });
  }
  return data;
};

// Generate future prediction points
export const generatePredictionPoints = (lastPrice: number, days: number): StockDataPoint[] => {
  const data: StockDataPoint[] = [];
  let currentPrice = lastPrice;
  const now = new Date();

  for (let i = 1; i <= days; i++) {
    const date = new Date(now);
    date.setDate(date.getDate() + i);

    const change = currentPrice * (Math.random() * 0.02 - 0.005);
    currentPrice += change;

    const confidenceGap = (i / days) * (currentPrice * 0.08);

    data.push({
      date: date.toISOString().split('T')[0],
      price: parseFloat(currentPrice.toFixed(2)),
      open: 0, high: 0, low: 0, volume: 0,
      isPrediction: true,
      confidenceUpper: parseFloat((currentPrice + confidenceGap).toFixed(2)),
      confidenceLower: parseFloat((currentPrice - confidenceGap).toFixed(2)),
    });
  }
  return data;
};

export const getStocks = (): StockInfo[] => STOCKS;

export const getStockDetails = (symbol: string): StockInfo | undefined => {
  return STOCKS.find(s => s.symbol === symbol);
};

export const getPredictionSummary = (symbol: string): PredictionSummary => {
  const stock = getStockDetails(symbol);
  const isBullish = Math.random() > 0.45;
  return {
    symbol,
    targetPrice: stock ? stock.price * (isBullish ? 1.12 : 0.92) : 100,
    timeframe: '30 Days',
    confidence: Math.floor(Math.random() * 15) + 80, // 80-95%
    signal: isBullish ? 'BUY' : 'SELL',
  };
};