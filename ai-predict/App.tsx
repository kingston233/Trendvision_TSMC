import React, { useState } from 'react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import StockDetail from './pages/StockDetail';
import Comparison from './pages/Comparison';
import Settings from './pages/Settings';
import Backtest from './pages/Backtest';
import { getStockDetails } from './services/mockDataService';
import { StockInfo } from './types';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedStockSymbol, setSelectedStockSymbol] = useState<string | null>(null);
  const [selectedStock, setSelectedStock] = useState<StockInfo | null>(null);

  const handleNavigate = (page: string) => {
    setCurrentPage(page);
    if (page === 'dashboard' || page === 'settings' || page === 'comparison') {
      setSelectedStock(null);
      setSelectedStockSymbol(null);
    }
  };

  const handleSelectStock = (symbol: string) => {
    const stock = getStockDetails(symbol);
    if (stock) {
      setSelectedStock(stock);
      setSelectedStockSymbol(symbol);
      setCurrentPage('detail');
    }
  };

  return (
    <Layout onNavigate={handleNavigate} currentPage={currentPage} onStockSelect={handleSelectStock}>
      {currentPage === 'dashboard' && (
        <Dashboard onSelectStock={handleSelectStock} />
      )}
      {currentPage === 'detail' && selectedStock && (
        <StockDetail stock={selectedStock} onBack={() => handleNavigate('dashboard')} />
      )}
      {currentPage === 'comparison' && (
        <Comparison />
      )}
      {currentPage === 'settings' && (
        <Settings />
      )}
      {currentPage === 'backtest' && (
        <Backtest />
      )}
    </Layout>
  );
}

export default App;