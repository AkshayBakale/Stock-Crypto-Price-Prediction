import React, { useState, useEffect } from "react";
import { PaperPortfolio, TickerData } from "../types";
import { api } from "../services/api";
import { Wallet, ArrowUpRight, ArrowDownRight, DollarSign, Layers, CheckCircle2 } from "lucide-react";

interface PaperTradingProps {
  currentTicker: TickerData | null;
  activeSymbol: string;
}

export const PaperTrading: React.FC<PaperTradingProps> = ({ currentTicker, activeSymbol }) => {
  const [portfolio, setPortfolio] = useState<PaperPortfolio | null>(null);
  const [tradeSymbol, setTradeSymbol] = useState(activeSymbol || "BTCUSDT");
  const [quantity, setQuantity] = useState(0.1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [orderMsg, setOrderMsg] = useState<string | null>(null);

  const fetchPortfolio = async () => {
    try {
      const data = await api.getPortfolio();
      setPortfolio(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchPortfolio();
    const interval = setInterval(fetchPortfolio, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    setTradeSymbol(activeSymbol);
  }, [activeSymbol]);

  const handleOrder = async (side: "BUY" | "SELL") => {
    setIsSubmitting(true);
    setOrderMsg(null);
    try {
      const res = await api.submitPaperOrder({
        symbol: tradeSymbol,
        side,
        quantity,
      });
      setOrderMsg(`Executed ${side} ${quantity} ${tradeSymbol} @ $${res.price}`);
      await fetchPortfolio();
    } catch (err: any) {
      setOrderMsg(err.message || "Order execution failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 font-mono">
      {/* Balance Summary Header */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-[#0D1117] border border-[#232936] p-4 rounded-xl shadow-lg">
          <div className="text-[10px] text-[#8B949E] uppercase mb-1">Virtual Cash Balance</div>
          <div className="text-xl font-bold text-white">
            ${portfolio?.cash.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? "100,000.00"}
          </div>
        </div>

        <div className="bg-[#0D1117] border border-[#232936] p-4 rounded-xl shadow-lg">
          <div className="text-[10px] text-[#8B949E] uppercase mb-1">Total Portfolio Equity</div>
          <div className="text-xl font-bold text-blue-400">
            ${portfolio?.total_equity.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? "100,000.00"}
          </div>
        </div>

        <div className="bg-[#0D1117] border border-[#232936] p-4 rounded-xl shadow-lg">
          <div className="text-[10px] text-[#8B949E] uppercase mb-1">Unrealized P&L</div>
          <div
            className={`text-xl font-bold ${
              (portfolio?.total_pnl ?? 0) >= 0 ? "text-emerald-400" : "text-rose-400"
            }`}
          >
            {(portfolio?.total_pnl ?? 0) >= 0 ? "+" : ""}
            ${portfolio?.total_pnl.toFixed(2) ?? "0.00"} ({portfolio?.total_pnl_pct.toFixed(2) ?? "0.00"}%)
          </div>
        </div>

        <div className="bg-[#0D1117] border border-[#232936] p-4 rounded-xl shadow-lg flex items-center justify-between">
          <div>
            <div className="text-[10px] text-[#8B949E] uppercase mb-1">Execution Mode</div>
            <div className="text-sm font-bold text-amber-400">PAPER TRADING</div>
          </div>
          <span className="px-2 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 text-[10px] rounded font-bold">
            ZERO RISK
          </span>
        </div>
      </div>

      {/* Main Trading Execution Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Order Ticket */}
        <div className="bg-[#0D1117] border border-[#232936] rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 pb-4 border-b border-[#232936] mb-4">
              <Wallet className="h-5 w-5 text-blue-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Instant Order Execution</h3>
            </div>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block text-[#8B949E] mb-1">Instrument</label>
                <input
                  type="text"
                  value={tradeSymbol}
                  onChange={(e) => setTradeSymbol(e.target.value.toUpperCase())}
                  className="w-full bg-[#151A22] border border-[#232936] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-[#8B949E] mb-1">Quantity</label>
                <input
                  type="number"
                  step="0.01"
                  value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                  className="w-full bg-[#151A22] border border-[#232936] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="bg-[#151A22] p-3 rounded-lg border border-[#232936] space-y-1 text-[11px]">
                <div className="flex justify-between text-[#8B949E]">
                  <span>Live Market Price:</span>
                  <span className="text-white font-bold">${currentTicker?.price ?? "---"}</span>
                </div>
                <div className="flex justify-between text-[#8B949E]">
                  <span>Est. Order Value:</span>
                  <span className="text-white font-bold">
                    ${((currentTicker?.price || 0) * quantity).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                </div>
                <div className="flex justify-between text-[#8B949E]">
                  <span>Commission (0.05%):</span>
                  <span className="text-amber-400 font-bold">
                    ${(((currentTicker?.price || 0) * quantity) * 0.0005).toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-6 space-y-2">
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleOrder("BUY")}
                disabled={isSubmitting}
                className="py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold text-xs flex items-center justify-center space-x-1 transition-all shadow-md shadow-emerald-600/20"
              >
                <ArrowUpRight className="h-4 w-4" />
                <span>BUY / LONG</span>
              </button>
              <button
                onClick={() => handleOrder("SELL")}
                disabled={isSubmitting}
                className="py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg font-bold text-xs flex items-center justify-center space-x-1 transition-all shadow-md shadow-rose-600/20"
              >
                <ArrowDownRight className="h-4 w-4" />
                <span>SELL / CLOSE</span>
              </button>
            </div>

            {orderMsg && (
              <div className="p-2.5 bg-[#151A22] border border-blue-500/30 rounded text-[11px] text-blue-300">
                {orderMsg}
              </div>
            )}
          </div>
        </div>

        {/* Positions & Orders Tabs */}
        <div className="lg:col-span-2 bg-[#0D1117] border border-[#232936] rounded-xl p-5 shadow-lg">
          <div className="flex items-center space-x-2 pb-4 border-b border-[#232936] mb-4">
            <Layers className="h-5 w-5 text-blue-400" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Open Positions</h3>
          </div>

          {!portfolio?.positions || portfolio.positions.length === 0 ? (
            <div className="py-12 text-center text-xs text-[#8B949E]">
              No active paper positions. Submit a BUY order to open a position.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#151A22] text-[#8B949E] border-b border-[#232936]">
                  <tr>
                    <th className="py-2.5 px-3">Symbol</th>
                    <th className="py-2.5 px-3">Quantity</th>
                    <th className="py-2.5 px-3">Avg Entry</th>
                    <th className="py-2.5 px-3">Current Price</th>
                    <th className="py-2.5 px-3">Market Value</th>
                    <th className="py-2.5 px-3">Unrealized P&L</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#232936]/60">
                  {portfolio.positions.map((p) => (
                    <tr key={p.symbol} className="hover:bg-[#151A22]/50">
                      <td className="py-3 px-3 font-bold text-blue-400">{p.symbol}</td>
                      <td className="py-3 px-3 text-white">{p.quantity}</td>
                      <td className="py-3 px-3 text-[#8B949E]">${p.avg_entry_price.toLocaleString()}</td>
                      <td className="py-3 px-3 text-white font-bold">${p.current_price.toLocaleString()}</td>
                      <td className="py-3 px-3 text-white">${p.position_value.toLocaleString()}</td>
                      <td
                        className={`py-3 px-3 font-bold ${
                          p.unrealized_pnl >= 0 ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {p.unrealized_pnl >= 0 ? "+" : ""}${p.unrealized_pnl.toFixed(2)} ({p.unrealized_pnl_pct.toFixed(2)}%)
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
