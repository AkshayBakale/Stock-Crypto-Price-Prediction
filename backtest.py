"""
CLI Quantitative Backtesting Command
Usage:
    python backtest.py --symbol BTCUSDT --model xgboost --timeframe 1h
    python backtest.py --symbol AAPL --model lstm --timeframe 1h --capital 50000
"""

import argparse
import asyncio
import json
import numpy as np
from backend.market_data.streamer import market_streamer
from ml.backtesting.engine import BacktestEngine
from ml.registry.registry import ModelRegistryManager
from ml.features.technical import FeatureEngine

async def main():
    parser = argparse.ArgumentParser(description="Run realistic backtest on real market data.")
    parser.add_argument("--symbol", type=str, default="BTCUSDT", help="Instrument symbol")
    parser.add_argument("--model", type=str, default="xgboost", help="Model type")
    parser.add_argument("--timeframe", type=str, default="1h", help="Timeframe")
    parser.add_argument("--capital", type=float, default=100000.0, help="Initial capital in USD")
    parser.add_argument("--stop_loss", type=float, default=0.02, help="Stop loss %")
    parser.add_argument("--take_profit", type=float, default=0.04, help="Take profit %")

    args = parser.parse_args()

    print(f"==================================================")
    print(f"RUNNING BACKTEST: {args.symbol} | Strategy: {args.model.upper()} | Initial Capital: ${args.capital:,.2f}")
    print(f"==================================================")

    # 1. Fetch historical bars
    df_bars = await market_streamer.get_historical_bars(args.symbol, timeframe=args.timeframe, limit=500)
    if df_bars.empty:
        print(f"Error: Could not retrieve market data for {args.symbol}")
        return

    # 2. Get signals
    signals = np.zeros(len(df_bars))
    try:
        model_obj, preprocessor, meta = ModelRegistryManager.load_model_bundle(args.symbol, args.model)
        df_feat = FeatureEngine.compute_all_features(df_bars)
        feature_names = meta.get("hyperparameters", {}).get("feature_names", preprocessor.feature_names)
        clean_feat = df_feat.dropna(subset=feature_names)
        if not clean_feat.empty:
            X_scaled = preprocessor.transform(clean_feat)
            preds = model_obj.predict(X_scaled)
            for row_idx, pred_val in zip(clean_feat.index, preds):
                if pred_val > 0.0015:
                    signals[row_idx] = 1
                elif pred_val < -0.0015:
                    signals[row_idx] = -1
    except Exception as e:
        print(f"Notice: Model {args.model} not found or error loading ({e}). Using Technical Momentum Strategy.")
        close = df_bars["close"]
        sma9 = close.rolling(9).mean()
        sma21 = close.rolling(21).mean()
        for i in range(1, len(df_bars)):
            if sma9.iloc[i] > sma21.iloc[i]:
                signals[i] = 1
            elif sma9.iloc[i] < sma21.iloc[i]:
                signals[i] = -1

    # 3. Execute
    engine = BacktestEngine(
        initial_capital=args.capital,
        stop_loss_pct=args.stop_loss,
        take_profit_pct=args.take_profit
    )
    res = engine.run_backtest(df_bars, signals, symbol=args.symbol)

    print(f"\nBACKTEST PERFORMANCE SUMMARY:")
    print(f"  Final Strategy Equity:   ${res['final_equity']:,.2f}")
    print(f"  Strategy Total Return:   {res['total_return_pct']}%")
    print(f"  Buy & Hold Return:       {res['benchmark_return_pct']}%")
    print(f"  Sharpe Ratio:            {res['sharpe_ratio']}")
    print(f"  Sortino Ratio:           {res['sortino_ratio']}")
    print(f"  Max Drawdown:            {res['max_drawdown_pct']}%")
    print(f"  Win Rate:                {res['win_rate_pct']}%")
    print(f"  Profit Factor:           {res['profit_factor']}")
    print(f"  Total Closed Trades:     {res['total_trades']}")
    print(f"==================================================")

if __name__ == "__main__":
    asyncio.run(main())
