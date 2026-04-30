export interface StockDataPoint {
  date: string;
  price: number;
  volume: number;
  open: number;
  high: number;
  low: number;
  isPrediction?: boolean;
  confidenceLower?: number;
  confidenceUpper?: number;
  rsi?: number;
  bb_upper?: number;
  bb_lower?: number;
  bb_middle?: number;
}

export interface StockInfo {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  sector: string;
  marketCap: string;
  peRatio: number;
  volatility: string;
  limitUp?: number;
  limitDown?: number;
  dayHigh?: number;
  dayLow?: number;
  volume?: number;
}

export interface PredictionSummary {
  symbol: string;
  targetPrice: number;
  timeframe: string;
  confidence: number; // 0-100
  signal: 'BUY' | 'SELL' | 'HOLD';
  predictedClosePrice?: number;
  predictedNextDayClose?: number;
  aiReasoning?: string;
}

export type TimeRange = '1D' | '1W' | '1M' | '3M' | '1Y';

export interface AIAnalysisResponse {
  summary: string;
  keyFactors: string[];
  riskLevel: 'Low' | 'Medium' | 'High';
}
