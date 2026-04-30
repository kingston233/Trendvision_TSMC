import React, { useState } from 'react';
import { Server, Database, Code, CheckCircle, Copy } from 'lucide-react';

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'general' | 'integration'>('integration');

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">System Settings</h1>
        <p className="text-slate-500 mt-1">Manage platform configuration and backend connections.</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200">
        <button 
            onClick={() => setActiveTab('general')}
            className={`px-6 py-3 text-sm font-medium transition-colors border-b-2 ${activeTab === 'general' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
        >
            General
        </button>
        <button 
            onClick={() => setActiveTab('integration')}
            className={`px-6 py-3 text-sm font-medium transition-colors border-b-2 ${activeTab === 'integration' ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-700'}`}
        >
            Backend Integration
        </button>
      </div>

      {activeTab === 'integration' ? (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* Architecture Overview */}
            <div className="bg-blue-50 border border-blue-100 p-6 rounded-xl">
                <h3 className="font-bold text-blue-900 flex items-center gap-2 mb-4">
                    <Server className="w-5 h-5" /> Integration Architecture
                </h3>
                <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm">
                    <div className="bg-white p-4 rounded-lg shadow-sm border border-blue-100 flex-1 w-full text-center">
                        <strong className="block text-slate-800 mb-1">React Frontend</strong>
                        <span className="text-slate-500">This Interface</span>
                    </div>
                    <div className="hidden md:block text-blue-300">────────►</div>
                    <div className="block md:hidden text-blue-300">▼</div>
                    <div className="bg-white p-4 rounded-lg shadow-sm border-2 border-blue-500 flex-1 w-full text-center relative">
                        <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-600 text-white text-[10px] px-2 py-0.5 rounded-full">YOU ARE HERE</div>
                        <strong className="block text-slate-800 mb-1">FastAPI (Python)</strong>
                        <span className="text-slate-500">Runs your .pkl Model</span>
                    </div>
                    <div className="hidden md:block text-blue-300">────────►</div>
                    <div className="block md:hidden text-blue-300">▼</div>
                    <div className="bg-white p-4 rounded-lg shadow-sm border border-blue-100 flex-1 w-full text-center">
                        <strong className="block text-slate-800 mb-1">PostgreSQL</strong>
                        <span className="text-slate-500">Stores History</span>
                    </div>
                </div>
            </div>

            {/* Step 1: Python Backend */}
            <div className="space-y-4">
                <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                    <Code className="w-5 h-5 text-slate-500" /> 1. Python Backend (FastAPI)
                </h3>
                <p className="text-slate-600 text-sm">
                    Create a file named <code>main.py</code>. This server will load your trained model and serve predictions to the frontend.
                </p>
                <CodeBlock 
                    language="python" 
                    code={`from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()

# Enable CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your trained model (e.g., sklearn, xgboost, pytorch)
# model = joblib.load("my_stock_model.pkl")

@app.get("/api/v1/predict/{symbol}")
def get_prediction(symbol: str):
    # 1. Fetch latest data (from DB or Yahoo Finance)
    # 2. Preprocess data
    # 3. Run inference
    # prediction = model.predict(data)
    
    # Mock response for structure
    return {
        "symbol": symbol,
        "targetPrice": 150.20,
        "confidence": 85.5,
        "signal": "BUY",
        "timeframe": "7 Days"
    }

@app.get("/api/v1/stocks/{symbol}/history")
def get_history(symbol: str):
    # Query your PostgreSQL database here
    return [
        {"date": "2024-03-01", "price": 140.5, "isPrediction": False},
        {"date": "2024-03-02", "price": 142.0, "isPrediction": False},
        # ... append predicted values ...
        {"date": "2024-03-03", "price": 145.0, "isPrediction": True}
    ]`} 
                />
            </div>

            {/* Step 2: Database */}
            <div className="space-y-4">
                <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                    <Database className="w-5 h-5 text-slate-500" /> 2. Database Schema (PostgreSQL)
                </h3>
                <p className="text-slate-600 text-sm">
                    Use this SQL to create the necessary tables for storing historical data and model logs.
                </p>
                <CodeBlock 
                    language="sql" 
                    code={`CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10, 2),
    high DECIMAL(10, 2),
    low DECIMAL(10, 2),
    close DECIMAL(10, 2),
    volume BIGINT,
    UNIQUE(symbol, date)
);

CREATE TABLE model_predictions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    target_date DATE NOT NULL,
    predicted_price DECIMAL(10, 2),
    confidence_score DECIMAL(5, 2),
    signal_type VARCHAR(10), -- 'BUY', 'SELL', 'HOLD'
    model_version VARCHAR(50)
);`} 
                />
            </div>

            {/* Step 3: Connect Frontend */}
            <div className="bg-slate-50 p-6 rounded-xl border border-slate-200">
                <h3 className="font-bold text-slate-900 mb-2">3. Switch to Real Data</h3>
                <p className="text-sm text-slate-600 mb-4">
                    Once your backend is running on <code>localhost:8000</code>, open <code>services/api.ts</code> in this project and update the config:
                </p>
                <div className="bg-white p-3 rounded border border-slate-200 font-mono text-sm text-slate-700">
                    <span className="text-purple-600">const</span> USE_REAL_BACKEND = <span className="text-blue-600">true</span>;
                </div>
            </div>
        </div>
      ) : (
        <div className="text-center py-20 text-slate-400 bg-slate-50 rounded-xl border border-slate-100 border-dashed">
            <SettingsIconLarge />
            <h3 className="text-lg font-medium text-slate-600 mt-4">General Settings</h3>
            <p className="max-w-md mx-auto mt-2">
                Standard preferences like notifications, display currency, and user profile management would go here.
            </p>
        </div>
      )}
    </div>
  );
};

const CodeBlock = ({ language, code }: { language: string, code: string }) => (
    <div className="relative group rounded-xl overflow-hidden border border-slate-200 shadow-sm">
        <div className="flex justify-between items-center bg-slate-50 px-4 py-2 border-b border-slate-200">
            <span className="text-xs font-bold text-slate-500 uppercase">{language}</span>
            <button className="text-slate-400 hover:text-slate-600" title="Copy">
                <Copy className="w-4 h-4" />
            </button>
        </div>
        <div className="bg-slate-900 p-4 overflow-x-auto">
            <pre className="text-sm font-mono text-slate-300">
                {code}
            </pre>
        </div>
    </div>
);

const SettingsIconLarge = () => (
    <svg className="w-16 h-16 mx-auto text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
)

export default Settings;
