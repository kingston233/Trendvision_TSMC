import React, { useState } from 'react';
import PredictPage from './pages/PredictPage';
import DataPage from './pages/DataPage';
import ChartPage from './pages/ChartPage';

function App() {
    const [currentPage, setCurrentPage] = useState<'predict' | 'data' | 'chart'>('predict');

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
            {/* 導航欄 */}
            <nav className="bg-black/30 backdrop-blur-lg border-b border-white/10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        <div className="flex items-center">
                            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                                台積電股價預測
                            </h1>
                        </div>
                        <div className="flex space-x-4">
                            <button
                                onClick={() => setCurrentPage('predict')}
                                className={`px-4 py-2 rounded-lg font-medium transition-all ${currentPage === 'predict'
                                    ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                                    : 'text-gray-300 hover:bg-white/10'
                                    }`}
                            >
                                預測收盤價
                            </button>
                            <button
                                onClick={() => setCurrentPage('chart')}
                                className={`px-4 py-2 rounded-lg font-medium transition-all ${currentPage === 'chart'
                                    ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                                    : 'text-gray-300 hover:bg-white/10'
                                    }`}
                            >
                                圖表展示
                            </button>
                            <button
                                onClick={() => setCurrentPage('data')}
                                className={`px-4 py-2 rounded-lg font-medium transition-all ${currentPage === 'data'
                                    ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                                    : 'text-gray-300 hover:bg-white/10'
                                    }`}
                            >
                                資料展示
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* 主要內容 */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {currentPage === 'predict' && <PredictPage />}
                {currentPage === 'chart' && <ChartPage />}
                {currentPage === 'data' && <DataPage />}
            </main>
        </div>
    );
}

export default App;
