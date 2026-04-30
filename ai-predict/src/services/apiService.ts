/**
 * API 服務層 - 封裝所有後端 API 調用
 */

const API_BASE_URL = 'http://localhost:8000';

export interface PredictionResponse {
    predicted_price: number;
    prediction_time: string;
    model_name: string;
    confidence?: number;
    current_price?: number;
    change_percent?: number;
}

export interface CsvFileInfo {
    folder: string;
    filename: string;
    size: number;
    modified_time: string;
}

export interface CsvData {
    folder: string;
    filename: string;
    columns: string[];
    row_count: number;
    data: any[];
}

export interface DataSummary {
    latest_close: number;
    latest_date: string;
    data_points: number;
    date_range: string;
}

/**
 * 獲取預測結果
 */
export async function getPrediction(): Promise<PredictionResponse> {
    const response = await fetch(`${API_BASE_URL}/api/predict`);
    if (!response.ok) {
        throw new Error('預測失敗');
    }
    return response.json();
}

/**
 * 獲取 CSV 檔案列表
 */
export async function getCsvFiles(): Promise<CsvFileInfo[]> {
    const response = await fetch(`${API_BASE_URL}/api/csv-files`);
    if (!response.ok) {
        throw new Error('獲取檔案列表失敗');
    }
    return response.json();
}

/**
 * 獲取 CSV 資料
 */
export async function getCsvData(folder: string, filename: string): Promise<CsvData> {
    const response = await fetch(`${API_BASE_URL}/api/csv-data/${folder}/${filename}`);
    if (!response.ok) {
        throw new Error('讀取檔案失敗');
    }
    return response.json();
}

/**
 * 獲取最新資料摘要
 */
export async function getLatestData(): Promise<DataSummary> {
    const response = await fetch(`${API_BASE_URL}/api/latest-data`);
    if (!response.ok) {
        throw new Error('獲取資料摘要失敗');
    }
    return response.json();
}

/**
 * 觸發資料抓取
 */
export async function fetchData(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/fetch-data`, {
        method: 'POST',
    });
    if (!response.ok) {
        throw new Error('資料抓取失敗');
    }
    return response.json();
}

/**
 * 觸發模型訓練
 */
export async function trainModel(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE_URL}/api/train-model`, {
        method: 'POST',
    });
    if (!response.ok) {
        throw new Error('模型訓練失敗');
    }
    return response.json();
}

export interface ChartDataPoint {
    date: string;
    close: number | null;
    open: number | null;
    high: number | null;
    low: number | null;
    macd?: number;
    macd_signal?: number;
    macd_histogram?: number;
}

export interface ChartDataResponse {
    chart_data: ChartDataPoint[];
    pe_ratio: number | null;
    data_points: number;
    date_range: {
        start: string | null;
        end: string | null;
    };
}

/**
 * 獲取圖表資料（本益比、價格、MACD）
 */
export async function getChartData(): Promise<ChartDataResponse> {
    const response = await fetch(`${API_BASE_URL}/api/chart-data`);
    if (!response.ok) {
        throw new Error('獲取圖表資料失敗');
    }
    return response.json();
}
