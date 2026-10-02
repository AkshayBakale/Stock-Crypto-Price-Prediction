import React, { useState } from "react";
import { BacktestResult, ModelMetadata } from "../types";
import { api } from "../services/api";
import { 
  Activity, 
  Play, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Percent, 
  ShieldCheck, 
  ListOrdered 
} from "lucide-react";

interface BacktestStudioProps {
  activeSymbol: string;
  models: ModelMetadata[];
}

export const BacktestStudio: React.FC<BacktestStudioProps> = ({ activeSymbol, models }) => {
  const [symbol, setSymbol] = useState(activeSymbol || "BTCUSDT");
  const [initialCapital, setInitialCapital] = useState(100000);
  const [stopLossPct, setStopLossPct] = useState(0.02);
  const [takeProfitPct, setTakeProfitPct] = useState(0.04);
  const [timeframe, setTimeframe] = useState("1h");
  const [selectedModelType, setSelectedModelType] = useState("xgboost");

  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunBacktest = async () => {
    setIsRunning(true);
    setError(null);
    try {
      const res = await api.runBacktest({
        symbol,
        model_type: selectedModelType,
        initial_capital: initialCapital,
        stop_loss_pct: stopLossPct,
        take_profit_pct: takeProfitPct,
        timeframe,
      });
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Failed to run backtest");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Config & Launch Card */}
      <div className="bg-[#0D1117] border border-[#232936] rounded-xl p-5 shadow-lg">
        <div className="flex items-center space-x-2 pb-4 border-b border-[#232936] mb-4">
          <Activity className="h-5 w-5 text-blue-400" />
          <h2 className="text-sm font-mono font-bold text-white uppercase tracking-wider">
            Quantitative Backtesting Engine
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 text-xs font-mono">
          <div>
            <label className="block text-[#8B949E] mb-1">Symbol</label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              className="w-full bg-[#151A22] border border-[#232936] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-[#8B949E] mb-1">Strategy / Model</label>
            <select
              value={selectedModelType}
              onChange={(e) => setSelectedModelType(e.target.value)}
              className="w-full bg-[#151A22] border border-[#232936] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-blue-500"
            >
              <option value="xgboost">XGBoost Strategy</option>
              <option value="lightgbm">LightGBM Strategy</option>
              <option value="lstm">PyTorch LSTM Strategy</option>
              <option value="transformer">Transformer Strategy</option>
            </select>
          </div>

          <div>
            <label className="block text-[#8B949E] mb-1">Initial Capital ($)</label>
            <input
              type="number"
              value={initialCapital}
              onChange={(e) => setInitialCapital(Number(e.target.value))}
              className="w-full bg-[#151A22] border border-[#232936] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-[#8B949E] mb-1">Stop Loss ({(stopLossPct * 100).toFixed(1)}%)</label>
            <input
              type="range"
              min="0.005"
              max="0.10"
              step="0.005"
              value={stopLossPct}
              onChange={(e) => setStopLossPct(Number(e.target.value))}
              className="w-full accent-blue-500 mt-2"
            />
          </div>

          <div>
            <label className="block text-[#8B949E] mb-1">Take Profit ({(takeProfitPct * 100).toFixed(1)}%)</label>
            <input
              type="range"
              min="0.01"
              max="0.20"
              step="0.01"
              value={takeProfitPct}
              onChange={(e) => setTakeProfitPct(Number(e.target.value))}
              className="w-full accent-emerald-500 mt-2"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={handleRunBacktest}
              disabled={isRunning}
              className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-mono font-bold text-xs flex items-center justify-center space-x-2 transition-all shadow-md shadow-blue-600/20"
            >
              {isRunning ? (
                <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
              ) : (
                <>
                  <Play className="h-4 w-4 fill-current" />
                  <span>Run Simulation</span>
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-950/40 border border-red-500/30 rounded-lg text-xs font-mono text-red-400">
            {error}
          </div>
        )}
      </div>

      {/* Results View */}
      {result && (
        <div className="space-y-6">
          {/* Metrics Overview Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 font-mono">
            <div className="bg-[#0D1117] border border-[#232936] p-4 rounded-xl">
              <div className="text-[10px] text-[#8B949E] uppercase mb-1">Final Strategy Equity</div>
              <div className="text-lg font-bold text-white">${result.final_equity.toLocaleString()}</div>
              <div
                className={`text-xs font-bold mt-1 ${
                  result.total_return_pct >= 0 ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {result.total_return_pct >= 0 ? "+" : ""}
                {result.total_return_pct}%
              </div>
            </div>

            <div className="bg-[#0D1117] border border-[#232936] p-4 rounded-xl">
              <div className="text-[10px] text-[#8B949E] uppercase mb-1">Buy & Hold Benchmark</div>
              <div className="text-lg font-bold text-[#8B949E]">
                ${Math.round(result.initial_capital * (1 + result.benchmark_return_pct / 100)).toLocaleString()}
              </div>
              <div
                className={`text-xs font-bold mt-1 ${
                  result.benchmark_return_pct >= 0 ? "text-emerald-400" : "text-rose-400"
                }`}
              >
                {result.benchmark_return_pct >= 0 ? "+" : ""}
                {result.benchmark_return_pct}%
              </div>
            </div>

            <div className="bg-[#0D1117] border border-[#232936] p-4 rounded-xl">
              <div className="text-[10px] text-[#8B949E] uppercase mb-1">Sharpe Ratio</div>
              <div className="text-lg font-bold text-blue-400">{result.sharpe_ratio}</div>
              <div className="text-[10px] text-[#8B949E] mt-1">Sortino: {result.sortino_ratio}</div>
            </div>

            <div className="bg-[#0D1117] border border-[#232936] p-4 rounded-xl">
              <div className="text-[10px] text-[#8B949E] uppercase mb-1">Max Drawdown</div>
              <div className="text-lg font-bold text-rose-400">-{result.max_drawdown_pct}%</div>
              <div className="text-[10px] text-[#8B949E] mt-1">Downside risk</div>
            </div>

            <div className="bg-[#0D1117] border border-[#232936] p-4 rounded-xl">
              <div className="text-[10px] text-[#8B949E] uppercase mb-1">Win Rate</div>
              <div className="text-lg font-bold text-emerald-400">{result.win_rate_pct}%</div>
              <div className="text-[10px] text-[#8B949E] mt-1">{result.total_trades} Closed Trades</div>
            </div>

            <div className="bg-[#0D1117] border border-[#232936] p-4 rounded-xl">
              <div className="text-[10px] text-[#8B949E] uppercase mb-1">Profit Factor</div>
              <div className="text-lg font-bold text-amber-400">{result.profit_factor}</div>
              <div className="text-[10px] text-[#8B949E] mt-1">Gross Win / Loss</div>
            </div>
          </div>

          {/* Trade Executions Table */}
          <div className="bg-[#0D1117] border border-[#232936] rounded-xl p-5 shadow-lg">
            <div className="flex items-center space-x-2 pb-4 border-b border-[#232936] mb-4">
              <ListOrdered className="h-4 w-4 text-blue-400" />
              <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider">
                Simulated Execution Log (Recent Trades)
              </h3>
            </div>

            <div className="overflow-x-auto max-h-72">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-[#151A22] text-[#8B949E] border-b border-[#232936]">
                  <tr>
                    <th className="py-2 px-3">#</th>
                    <th className="py-2 px-3">Order Type</th>
                    <th className="py-2 px-3">Timestamp</th>
                    <th className="py-2 px-3">Exec Price</th>
                    <th className="py-2 px-3">Quantity</th>
                    <th className="py-2 px-3">Net PnL</th>
                    <th className="py-2 px-3">Exit Trigger</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#232936]/60">
                  {result.trades_log.map((t) => (
                    <tr key={t.trade_id} className="hover:bg-[#151A22]/50">
                      <td className="py-2 px-3 text-[#8B949E]">{t.trade_id}</td>
                      <td className="py-2 px-3 font-bold">
                        <span
                          className={`px-1.5 py-0.5 rounded text-[10px] ${
                            t.type.includes("BUY")
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                          }`}
                        >
                          {t.type}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-[#8B949E]">{t.timestamp}</td>
                      <td className="py-2 px-3 text-white">${t.price.toLocaleString()}</td>
                      <td className="py-2 px-3 text-white">{t.qty}</td>
                      <td
                        className={`py-2 px-3 font-bold ${
                          t.pnl > 0 ? "text-emerald-400" : t.pnl < 0 ? "text-rose-400" : "text-[#8B949E]"
                        }`}
                      >
                        {t.pnl !== 0 ? `$${t.pnl.toLocaleString()}` : "---"}
                      </td>
                      <td className="py-2 px-3 text-[#8B949E] text-[10px]">{t.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
