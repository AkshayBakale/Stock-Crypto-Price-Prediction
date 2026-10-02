import React, { useState } from "react";
import { TickerData } from "../types";
import { 
  Activity, 
  BarChart3, 
  BrainCircuit, 
  Database, 
  Wallet, 
  Search, 
  Server, 
  Zap,
  TrendingUp,
  TrendingDown,
  Sparkles
} from "lucide-react";

interface HeaderProps {
  currentTicker: TickerData | null;
  activeSymbol: string;
  onSelectSymbol: (symbol: string) => void;
  activeTab: string;
  onSelectTab: (tab: string) => void;
  isWsConnected: boolean;
  onOpenHealth: () => void;
}

const QUICK_INSTRUMENTS = [
  { symbol: "BTCUSDT", label: "BTC/USDT", market: "crypto" },
  { symbol: "ETHUSDT", label: "ETH/USDT", market: "crypto" },
  { symbol: "SOLUSDT", label: "SOL/USDT", market: "crypto" },
  { symbol: "AAPL", label: "AAPL", market: "us_equity" },
  { symbol: "NVDA", label: "NVDA", market: "us_equity" },
  { symbol: "NAS100", label: "NAS100", market: "index" },
  { symbol: "US30", label: "US30", market: "index" },
  { symbol: "RELIANCE", label: "RELIANCE", market: "in_equity" },
  { symbol: "TCS", label: "TCS", market: "in_equity" },
  { symbol: "NIFTY50", label: "NIFTY 50", market: "index" },
];

export const Header: React.FC<HeaderProps> = ({
  currentTicker,
  activeSymbol,
  onSelectSymbol,
  activeTab,
  onSelectTab,
  isWsConnected,
  onOpenHealth,
}) => {
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSelectSymbol(searchQuery.trim().toUpperCase());
      setSearchQuery("");
    }
  };

  const isPositive = (currentTicker?.change_24h_pct || 0) >= 0;

  return (
    <header className="bg-[#0B0E14] border-b border-[#1E2430] px-4 py-2.5 select-none">
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Logo & Brand */}
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center shadow-lg shadow-blue-500/20 border border-blue-400/30">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold tracking-tight text-white font-mono text-base">MARKET AI</span>
              <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded">
                PRO v1.0
              </span>
            </div>
            <p className="text-[11px] text-[#8B949E] tracking-wider uppercase font-medium">Stock & Crypto Prediction</p>
          </div>
        </div>

        {/* Quick Tickers */}
        <div className="hidden lg:flex items-center space-x-1.5 overflow-x-auto py-1">
          {QUICK_INSTRUMENTS.map((item) => {
            const active = activeSymbol === item.symbol;
            return (
              <button
                key={item.symbol}
                onClick={() => onSelectSymbol(item.symbol)}
                className={`px-2.5 py-1 text-xs font-mono rounded transition-all flex items-center space-x-1 border ${
                  active
                    ? "bg-blue-600/20 border-blue-500/50 text-blue-300 font-semibold shadow-sm"
                    : "bg-[#151A22] border-[#232936] text-[#8B949E] hover:text-white hover:border-[#374151]"
                }`}
              >
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="relative w-48 sm:w-64">
          <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-[#8B949E]" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search e.g. BTC, AAPL..."
            className="w-full bg-[#151A22] border border-[#232936] rounded-md pl-8 pr-3 py-1.5 text-xs text-white placeholder-[#8B949E] focus:outline-none focus:border-blue-500 font-mono transition-colors"
          />
        </form>

        {/* System Health & Status */}
        <div className="flex items-center space-x-2">
          {/* Connection Status Badge */}
          <div
            className={`flex items-center space-x-1.5 px-2.5 py-1 rounded text-xs font-mono font-medium border ${
              isWsConnected
                ? "bg-emerald-950/40 border-emerald-500/30 text-emerald-400"
                : "bg-red-950/40 border-red-500/30 text-red-400"
            }`}
          >
            <span
              className={`h-2 w-2 rounded-full ${
                isWsConnected ? "bg-emerald-400 pulsing-dot" : "bg-red-500"
              }`}
            />
            <span>{isWsConnected ? "LIVE WS" : "DISCONNECTED"}</span>
          </div>

          <button
            onClick={onOpenHealth}
            className="p-1.5 bg-[#151A22] hover:bg-[#1E2430] border border-[#232936] rounded text-[#8B949E] hover:text-white transition-colors"
            title="System Telemetry & Health"
          >
            <Server className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Secondary Bar: Live Active Ticker & Main Nav */}
      <div className="mt-2.5 pt-2 border-t border-[#1E2430]/70 flex flex-wrap items-center justify-between gap-3">
        {/* Active Instrument Stats */}
        <div className="flex items-center space-x-4">
          <div className="flex items-baseline space-x-2">
            <span className="text-base font-bold font-mono text-white">{activeSymbol}</span>
            <span className="text-[11px] text-[#8B949E] uppercase font-mono">
              {currentTicker?.exchange || "MARKET"} • {currentTicker?.provider || "API"}
            </span>
          </div>

          <div className="flex items-baseline space-x-2">
            <span className="text-lg font-bold font-mono text-white tracking-tight">
              ${currentTicker?.price != null ? currentTicker.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "---"}
            </span>
            <span
              className={`text-xs font-mono font-semibold flex items-center ${
                isPositive ? "text-emerald-400" : "text-rose-400"
              }`}
            >
              {isPositive ? <TrendingUp className="h-3 w-3 mr-0.5 inline" /> : <TrendingDown className="h-3 w-3 mr-0.5 inline" />}
              {isPositive ? "+" : ""}
              {currentTicker?.change_24h_pct != null ? currentTicker.change_24h_pct.toFixed(2) : "0.00"}%
            </span>
          </div>

          <div className="hidden sm:flex items-center space-x-3 text-xs text-[#8B949E] font-mono border-l border-[#232936] pl-4">
            <div>
              <span className="text-[#6E7681]">24h High: </span>
              <span className="text-white">${currentTicker?.high_24h?.toLocaleString() || "---"}</span>
            </div>
            <div>
              <span className="text-[#6E7681]">24h Low: </span>
              <span className="text-white">${currentTicker?.low_24h?.toLocaleString() || "---"}</span>
            </div>
            <div>
              <span className="text-[#6E7681]">Volume: </span>
              <span className="text-white">{currentTicker?.volume_24h?.toLocaleString() || "---"}</span>
            </div>
            <div>
              <span className="text-[#6E7681]">Data Age: </span>
              <span className="text-emerald-400 font-medium">{currentTicker?.data_age_seconds ?? 0}s</span>
            </div>
          </div>
        </div>

        {/* Main Navigation Tabs */}
        <div className="flex items-center space-x-1 bg-[#151A22] p-0.5 rounded-lg border border-[#232936]">
          {[
            { id: "terminal", label: "Terminal", icon: BarChart3 },
            { id: "model_lab", label: "AI Model Lab", icon: BrainCircuit },
            { id: "ir_intelligence", label: "IR Intelligence", icon: Sparkles },
            { id: "backtest", label: "Backtesting", icon: Activity },
            { id: "datasets", label: "Saved Datasets", icon: Database },
            { id: "paper_trading", label: "Paper Trading", icon: Wallet },
          ].map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onSelectTab(tab.id)}
                className={`flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                  active
                    ? "bg-blue-600 text-white shadow-sm font-semibold"
                    : "text-[#8B949E] hover:text-white hover:bg-[#1E2430]"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
