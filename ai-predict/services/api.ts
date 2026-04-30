import { StockDataPoint, StockInfo, PredictionSummary, AIAnalysisResponse } from '../types';
import * as mockDataService from './mockDataService';
import { generateAIAnalysis } from './geminiService';

// ------------------------------------------------------------------
// CONFIGURATION
// ------------------------------------------------------------------
// Set this to true when your FastAPI backend is running
const USE_REAL_BACKEND = true;
const API_BASE_URL = 'http://localhost:8000/api/v1';

// ------------------------------------------------------------------
// API SERVICE
// ------------------------------------------------------------------

export const api = {
  /**
   * Fetch list of supported stocks
   */
  getStocks: async (): Promise<StockInfo[]> => {
    if (USE_REAL_BACKEND) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

        const res = await fetch(`${API_BASE_URL}/stocks`, {
          signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      } catch (error) {
        console.error('Failed to fetch stocks from backend:', error);
        console.warn('Falling back to mock data');
        return mockDataService.getStocks();
      }
    }
    return mockDataService.getStocks();
  },

  /**
   * Fetch historical OHLCV data + Your Model's Predictions
   */
  getStockData: async (symbol: string): Promise<StockDataPoint[]> => {
    if (USE_REAL_BACKEND) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

        const res = await fetch(`${API_BASE_URL}/stocks/${symbol}/history`, {
          signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      } catch (error) {
        console.error('Failed to fetch stock data from backend:', error);
        console.warn('Falling back to mock data');
        // Fallback to mock data
        const stock = mockDataService.getStockDetails(symbol);
        if (!stock) return [];
        const hist = mockDataService.generateHistory(stock.price, 60);
        const future = mockDataService.generatePredictionPoints(hist[hist.length - 1].price, 15);
        return [...hist, ...future];
      }
    }

    // Fallback Mock Logic
    const stock = mockDataService.getStockDetails(symbol);
    if (!stock) return [];
    const hist = mockDataService.generateHistory(stock.price, 60);
    const future = mockDataService.generatePredictionPoints(hist[hist.length - 1].price, 15);
    return [...hist, ...future];
  },

  /**
   * Get the specific prediction summary (Target price, signal, confidence)
   * This is where your ML model's specific output goes.
   */
  getPrediction: async (symbol: string): Promise<PredictionSummary> => {
    if (USE_REAL_BACKEND) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

        const res = await fetch(`${API_BASE_URL}/predict/${symbol}`, {
          signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      } catch (error) {
        console.error('Failed to fetch prediction from backend:', error);
        console.warn('Falling back to mock prediction');
        return mockDataService.getPredictionSummary(symbol);
      }
    }
    return mockDataService.getPredictionSummary(symbol);
  },

  /**
   * Get Gemini Analysis (Proxy via Backend to hide API Key, or Client-side)
   */
  getAnalysis: async (stock: StockInfo, prediction: PredictionSummary): Promise<AIAnalysisResponse> => {
    // Ideally, move Gemini calls to backend too to protect API_KEY
    if (USE_REAL_BACKEND) {
      const res = await fetch(`${API_BASE_URL}/analyze/${stock.symbol}`, {
        method: 'POST',
        body: JSON.stringify(prediction)
      });
      return res.json();
    }
    return generateAIAnalysis(stock, prediction);
  },

  /**
   * Run Backtest
   */
  runBacktest: async (symbol: string, days: number, threshold: number, initialCapital: number): Promise<any> => {
    if (USE_REAL_BACKEND) {
      const res = await fetch(`${API_BASE_URL}/backtest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          symbol,
          days,
          threshold,
          initialCapital
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Backtest failed');
      }
      return res.json();
    }
    throw new Error("Backtest requires real backend");
  }
};

// Named exports for easier importing
export const getStocks = api.getStocks;
export const getStockData = api.getStockData;
export const getPrediction = api.getPrediction;
export const getAnalysis = api.getAnalysis;