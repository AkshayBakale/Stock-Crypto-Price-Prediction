"""
Realistic Quantitative Backtesting Engine
Simulates institutional trading execution with:
- Commissions, bid-ask spread, slippage
- Dynamic position sizing & capital allocation
- Stop Loss & Take Profit logic
- Comparison vs Buy & Hold and Naive benchmark
- Full trade execution logs and equity curves
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List, Optional

class BacktestEngine:
    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission_rate: float = 0.0005, # 5 bps
        slippage_rate: float = 0.0002, # 2 bps
        spread_rate: float = 0.0001, # 1 bp
        stop_loss_pct: float = 0.02, # 2%
        take_profit_pct: float = 0.04, # 4%
        position_size_pct: float = 0.20 # 20% of capital per position
    ):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.spread_rate = spread_rate
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.position_size_pct = position_size_pct

    def run_backtest(
        self,
        df: pd.DataFrame,
        signals: np.ndarray, # array of predicted directions (-1: SELL/SHORT, 0: FLAT, 1: BUY/LONG)
        symbol: str = "BTCUSDT"
    ) -> Dict[str, Any]:
        """
        Executes backtest over historical price bars.
        """
        if df.empty or len(df) != len(signals):
            raise ValueError("DataFrame and signals must be non-empty and equal length")

        cash = self.initial_capital
        position_qty = 0.0
        entry_price = 0.0
        trades_log = []
        equity_curve = []
        benchmark_curve = []

        initial_price = float(df["close"].iloc[0])
        total_costs = self.commission_rate + self.slippage_rate + self.spread_rate

        for i in range(len(df)):
            row = df.iloc[i]
            close_p = float(row["close"])
            high_p = float(row.get("high", close_p))
            low_p = float(row.get("low", close_p))
            ts = row.get("timestamp", datetime.utcnow())
            ts_str = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
            
            sig = int(signals[i])

            # 1. Check Stop Loss / Take Profit for active position
            if position_qty > 0: # Long position
                unrealized_return = (close_p - entry_price) / entry_price
                hit_sl = (low_p - entry_price) / entry_price <= -self.stop_loss_pct
                hit_tp = (high_p - entry_price) / entry_price >= self.take_profit_pct

                if hit_sl or hit_tp or sig == -1:
                    # Close Long
                    exit_price = entry_price * (1 - self.stop_loss_pct) if hit_sl else (
                        entry_price * (1 + self.take_profit_pct) if hit_tp else close_p
                    )
                    effective_exit = exit_price * (1 - total_costs)
                    pnl = (effective_exit - entry_price) * position_qty
                    cash += (position_qty * effective_exit)
                    
                    trades_log.append({
                        "trade_id": len(trades_log) + 1,
                        "type": "SELL_CLOSE",
                        "timestamp": ts_str,
                        "price": round(exit_price, 2),
                        "qty": round(position_qty, 4),
                        "pnl": round(pnl, 2),
                        "reason": "STOP_LOSS" if hit_sl else ("TAKE_PROFIT" if hit_tp else "SIGNAL_EXIT")
                    })
                    position_qty = 0.0
                    entry_price = 0.0

            # 2. Enter new position if signal and cash available
            if sig == 1 and position_qty == 0:
                allocated_capital = cash * self.position_size_pct
                if allocated_capital > 10.0:
                    exec_price = close_p * (1 + total_costs)
                    qty = allocated_capital / exec_price
                    cash -= (qty * exec_price)
                    position_qty = qty
                    entry_price = exec_price
                    trades_log.append({
                        "trade_id": len(trades_log) + 1,
                        "type": "BUY_ENTRY",
                        "timestamp": ts_str,
                        "price": round(exec_price, 2),
                        "qty": round(qty, 4),
                        "pnl": 0.0,
                        "reason": "SIGNAL_ENTRY"
                    })

            # 3. Calculate portfolio equity
            current_equity = cash + (position_qty * close_p)
            equity_curve.append({
                "timestamp": ts_str,
                "equity": round(current_equity, 2),
                "cash": round(cash, 2),
                "position_value": round(position_qty * close_p, 2)
            })

            # Benchmark Buy & Hold
            benchmark_equity = self.initial_capital * (close_p / initial_price)
            benchmark_curve.append({
                "timestamp": ts_str,
                "benchmark_equity": round(benchmark_equity, 2)
            })

        # Calculate summary statistics
        final_equity = equity_curve[-1]["equity"] if equity_curve else self.initial_capital
        total_return_pct = ((final_equity - self.initial_capital) / self.initial_capital) * 100.0
        
        final_bench = benchmark_curve[-1]["benchmark_equity"] if benchmark_curve else self.initial_capital
        bench_return_pct = ((final_bench - self.initial_capital) / self.initial_capital) * 100.0

        # Equity array returns
        eq_arr = np.array([e["equity"] for e in equity_curve])
        eq_returns = np.diff(eq_arr) / (eq_arr[:-1] + 1e-9)

        from ml.evaluation.metrics import ModelEvaluator
        perf = ModelEvaluator.evaluate_trading_performance(eq_returns)

        # Winning vs losing trades count
        closed_trades = [t for t in trades_log if t["pnl"] != 0.0]
        wins = [t for t in closed_trades if t["pnl"] > 0]
        losses = [t for t in closed_trades if t["pnl"] < 0]
        win_rate = (len(wins) / len(closed_trades) * 100.0) if closed_trades else 0.0

        return {
            "initial_capital": self.initial_capital,
            "final_equity": round(final_equity, 2),
            "total_return_pct": round(total_return_pct, 2),
            "benchmark_return_pct": round(bench_return_pct, 2),
            "sharpe_ratio": perf["sharpe_ratio"],
            "sortino_ratio": perf["sortino_ratio"],
            "max_drawdown_pct": perf["max_drawdown_pct"],
            "win_rate_pct": round(win_rate, 2),
            "profit_factor": perf["profit_factor"],
            "total_trades": len(closed_trades),
            "trades_log": trades_log[-50:], # return latest 50 for UI
            "equity_curve": equity_curve,
            "benchmark_curve": benchmark_curve
        }
