import pytest
import pandas as pd
import numpy as np
from ml.backtesting.engine import BacktestEngine

def test_backtest_execution():
    n = 100
    dates = pd.date_range("2026-01-01", periods=n, freq="1h")
    close = np.linspace(100.0, 150.0, n)
    df = pd.DataFrame({
        "timestamp": dates,
        "open": close,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": 1000.0
    })

    signals = np.zeros(n)
    signals[10] = 1 # BUY
    signals[50] = -1 # SELL

    engine = BacktestEngine(initial_capital=100000.0)
    res = engine.run_backtest(df, signals, symbol="BTCUSDT")

    assert res["initial_capital"] == 100000.0
    assert res["final_equity"] > 100000.0 # Profitable upward trade
    assert res["total_trades"] == 1
    assert "equity_curve" in res
    assert len(res["equity_curve"]) == n
