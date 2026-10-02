"""
CLI Model Training Command
Usage:
    python train.py --symbol BTCUSDT --model xgboost --timeframe 1h
    python train.py --symbol AAPL --model lstm --timeframe 1h --epochs 20
    python train.py --symbol RELIANCE --model transformer --timeframe 15m
    python train.py --symbol NAS100 --model lightgbm --timeframe 1h
"""

import argparse
import asyncio
import json
from backend.market_data.streamer import market_streamer
from ml.training.trainer import ModelTrainer

async def main():
    parser = argparse.ArgumentParser(description="Train quantitative prediction model on real market data.")
    parser.add_argument("--symbol", type=str, default="BTCUSDT", help="Instrument symbol (e.g. BTCUSDT, AAPL, RELIANCE, NAS100)")
    parser.add_argument("--model", type=str, default="xgboost", choices=["xgboost", "lightgbm", "lstm", "gru", "cnn_lstm", "transformer", "naive", "linear_regression"], help="Model architecture")
    parser.add_argument("--timeframe", type=str, default="1h", help="Timeframe (1m, 5m, 15m, 1h, 1d)")
    parser.add_argument("--epochs", type=int, default=15, help="Epochs for deep learning models")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--version", type=str, default="v1.0", help="Model version tag")
    
    args = parser.parse_args()

    print(f"==================================================")
    print(f"STARTING TRAINING: {args.symbol} | Model: {args.model.upper()} | Timeframe: {args.timeframe}")
    print(f"==================================================")

    # 1. Fetch real historical bars
    print(f"[1/4] Fetching real historical data for {args.symbol}...")
    df_bars = await market_streamer.get_historical_bars(args.symbol, timeframe=args.timeframe, limit=500)
    if df_bars.empty:
        print(f"Error: Could not retrieve market data for {args.symbol}")
        return

    print(f"      Retrieved {len(df_bars)} historical candles.")

    # 2. Train model
    print(f"[2/4] Engineering leak-free features & training {args.model.upper()}...")
    trainer = ModelTrainer(
        symbol=args.symbol,
        model_type=args.model,
        timeframe=args.timeframe,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr
    )

    def on_epoch(log):
        print(f"      Epoch {log['epoch']}/{args.epochs} -> Train Loss: {log['train_loss']:.6f} | Val Loss: {log['val_loss']:.6f}")

    result = await trainer.train(df_bars, progress_callback=on_epoch, version=args.version)

    # 3. Print Results & Storage Locations
    print(f"\n[3/4] Model Training Completed!")
    print(f"      Model ID:        {result['model_id']}")
    print(f"      Dataset Folder:  {result['dataset_folder']}")
    print(f"      Model Artifacts: {result['model_folder']}")
    
    print(f"\n[4/4] Out-Of-Sample Evaluation Metrics:")
    print(json.dumps(result["metrics"], indent=4))
    print(f"==================================================")

if __name__ == "__main__":
    asyncio.run(main())
