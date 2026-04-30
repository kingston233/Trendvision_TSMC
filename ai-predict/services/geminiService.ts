import { GoogleGenAI, Type } from "@google/genai";
import { StockInfo, PredictionSummary, AIAnalysisResponse } from '../types';

// Initialize Gemini
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY || '' });

export const generateAIAnalysis = async (
  stock: StockInfo,
  prediction: PredictionSummary
): Promise<AIAnalysisResponse> => {
  if (!process.env.API_KEY) {
    return {
      summary: "未設定 API 金鑰。請設定您的 Gemini API 金鑰以查看 AI 分析見解。",
      keyFactors: ["缺少 API Key", "需要系統設定"],
      riskLevel: "Medium"
    };
  }

  try {
    const prompt = `
      你是一位在頂尖避險基金工作的資深台股分析師 AI。
      請根據以下股票數據和機器學習模型的預測信號進行分析。
      請使用**繁體中文 (Traditional Chinese)** 回答。
      
      股票: ${stock.name} (${stock.symbol})
      現價: NT$${stock.price}
      板塊: ${stock.sector}
      本益比 (PE): ${stock.peRatio}
      
      ML 模型預測信號: ${prediction.signal}
      ML 模型信心度: ${prediction.confidence}%
      目標價 (30天): NT$${prediction.targetPrice.toFixed(2)}

      請提供一個 JSON 格式的簡明分析，包含：
      1. "summary": 一段簡短的總結，解釋為何出現此信號（結合技術面或基本面）。
      2. "keyFactors": 3 個導致此走勢的關鍵因素（簡短條列）。
      3. "riskLevel": 風險等級 (Low, Medium, High)。
    `;

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            summary: { type: Type.STRING },
            keyFactors: { 
              type: Type.ARRAY, 
              items: { type: Type.STRING } 
            },
            riskLevel: { type: Type.STRING, enum: ["Low", "Medium", "High"] }
          }
        }
      }
    });

    if (response.text) {
      return JSON.parse(response.text) as AIAnalysisResponse;
    }
    
    throw new Error("No response text");

  } catch (error) {
    console.error("Gemini Analysis Error:", error);
    return {
      summary: "AI 分析目前因需求量大或網絡問題暫時無法使用。但從技術指標來看，建議密切關注成交量變化與法人動向。",
      keyFactors: ["技術支撐位測試", "市場波動", "產業趨勢"],
      riskLevel: "Medium"
    };
  }
};

export const chatWithAI = async (message: string, context: string): Promise<string> => {
    if (!process.env.API_KEY) return "請先設定您的 API 金鑰。";
    
    try {
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: `Context: ${context}\n\nUser Question: ${message}\n\n請作為一位專業的台股分析師，用繁體中文回答用戶的問題。保持簡潔專業。`,
        });
        return response.text || "我無法處理此請求。";
    } catch (e) {
        return "目前無法連接到市場數據伺服器。";
    }
}