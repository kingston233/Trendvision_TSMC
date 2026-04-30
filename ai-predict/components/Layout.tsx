import React, { useState } from 'react';
import { LayoutDashboard, TrendingUp, PieChart, Bell, Settings, Search, BrainCircuit, Activity, GitCompare } from 'lucide-react';
import { getStocks } from '../services/mockDataService';

interface LayoutProps {
  children: React.ReactNode;
  onNavigate: (page: string) => void;
  currentPage: string;
  onStockSelect?: (symbol: string) => void;
}

const Layout: React.FC<LayoutProps> = ({ children, onNavigate, currentPage, onStockSelect }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showResults, setShowResults] = useState(false);

  const allStocks = getStocks();
  const filteredStocks = allStocks.filter(s =>
    s.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSelect = (symbol: string) => {
    if (onStockSelect) {
      onStockSelect(symbol);
      setSearchQuery('');
      setShowResults(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 text-slate-900 font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-20 lg:w-64 bg-white border-r border-slate-200 flex-shrink-0 flex flex-col transition-all duration-300 shadow-sm z-20">
        <div className="p-6 flex items-center gap-3 justify-center lg:justify-start">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <BrainCircuit className="text-white w-6 h-6" />
          </div>
          <span className="hidden lg:block font-bold text-xl tracking-tight text-slate-800">NeuroStock</span>
        </div>

        <nav className="flex-1 px-4 py-6 space-y-2">
          <NavItem icon={LayoutDashboard} label="Dashboard" active={currentPage === 'dashboard'} onClick={() => onNavigate('dashboard')} />
          <NavItem icon={GitCompare} label="Compare Stocks" active={currentPage === 'comparison'} onClick={() => onNavigate('comparison')} />
          <NavItem icon={TrendingUp} label="Backtest Strategy" active={currentPage === 'backtest'} onClick={() => onNavigate('backtest')} />
          <NavItem icon={Activity} label="Market Overview" active={false} onClick={() => { }} disabled />
          <NavItem icon={TrendingUp} label="Predictive Models" active={false} onClick={() => { }} disabled />
          <NavItem icon={PieChart} label="Portfolio AI" active={false} onClick={() => { }} disabled />
        </nav>

        <div className="p-4 border-t border-slate-100">
          <NavItem icon={Settings} label="Settings" active={currentPage === 'settings'} onClick={() => onNavigate('settings')} />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative bg-slate-50">
        {/* Header */}
        <header className="h-16 border-b border-slate-200 bg-white/80 backdrop-blur-md flex items-center justify-between px-8 z-10 sticky top-0">
          <div className="relative w-full max-w-xl">
            <div className="flex items-center gap-4 w-full bg-slate-100 rounded-lg px-4 py-2 focus-within:ring-2 focus-within:ring-blue-500/20 transition-all">
              <Search className="w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="搜尋股票代碼 (例如 2330, 2454)..."
                className="bg-transparent border-none outline-none text-sm w-full text-slate-900 placeholder-slate-400"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setShowResults(e.target.value.length > 0);
                }}
                onFocus={() => setShowResults(searchQuery.length > 0)}
              />
            </div>

            {/* Search Results Dropdown */}
            {showResults && searchQuery && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-xl border border-slate-100 max-h-60 overflow-y-auto overflow-x-hidden">
                {filteredStocks.length > 0 ? (
                  filteredStocks.map(stock => (
                    <button
                      key={stock.symbol}
                      onClick={() => handleSelect(stock.symbol)}
                      className="w-full text-left px-4 py-3 hover:bg-slate-50 border-b border-slate-50 last:border-0 flex justify-between items-center group"
                    >
                      <div>
                        <div className="font-bold text-slate-800">{stock.symbol}</div>
                        <div className="text-xs text-slate-500">{stock.name}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium text-slate-700">NT${stock.price.toFixed(2)}</div>
                        <div className={`text-xs ${stock.change >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                          {stock.change > 0 ? '+' : ''}{stock.changePercent}%
                        </div>
                      </div>
                    </button>
                  ))
                ) : (
                  <div className="p-4 text-center text-sm text-slate-500">No stocks found</div>
                )}
              </div>
            )}
            {/* Overlay to close search when clicking outside */}
            {showResults && (
              <div className="fixed inset-0 z-[-1]" onClick={() => setShowResults(false)}></div>
            )}
          </div>

          <div className="flex items-center gap-4">
            <button className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white"></span>
            </button>
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 flex items-center justify-center text-xs font-bold text-white shadow-md shadow-blue-500/20">
              JD
            </div>
          </div>
        </header>

        {/* Scrollable Area */}
        <div className="flex-1 overflow-y-auto p-6 lg:p-8 scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-transparent">
          {children}
        </div>
      </main>
    </div>
  );
};

// Updated NavItem to accept icon component directly
const NavItem = ({ icon: Icon, label, active, onClick, disabled }: any) => (
  <button
    onClick={disabled ? undefined : onClick}
    className={`flex items-center gap-3 w-full p-3 rounded-xl transition-all duration-200 group font-medium
      ${active
        ? 'bg-blue-50 text-blue-600'
        : disabled
          ? 'text-slate-300 cursor-not-allowed'
          : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'}`}
  >
    <div className={`${active ? 'text-blue-600' : disabled ? 'text-slate-300' : 'text-slate-400 group-hover:text-slate-600'}`}>
      <Icon size={20} />
    </div>
    <span className="hidden lg:block text-sm">{label}</span>
    {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-blue-600 hidden lg:block"></div>}
    {disabled && <span className="hidden lg:block ml-auto text-[10px] bg-slate-100 text-slate-400 px-1.5 py-0.5 rounded">SOON</span>}
  </button>
);

export default Layout;