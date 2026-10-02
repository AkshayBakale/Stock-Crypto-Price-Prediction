"""
Auto-Train Ready-Made Quantitative Models for All Supported Assets
Fetches real market data, engineers features, trains models, and saves datasets & artifacts into separate folders.
"""

import asyncio
from backend.market_data.streamer import market_streamer
from ml.training.trainer import ModelTrainer

ASSET_JOBS = [
    {"symbol": "ETHUSDT", "model": "xgboost", "timeframe": "1h"},
    {"symbol": "SOLUSDT", "model": "xgboost", "timeframe": "1h"},
    {"symbol": "AAPL", "model": "xgboost", "timeframe": "1h"},
    {"symbol": "AAPL", "model": "lstm", "timeframe": "1h", "epochs": 5},
    {"symbol": "NVDA", "model": "xgboost", "timeframe": "1h"},
    {"symbol": "RELIANCE", "model": "xgboost", "timeframe": "1h"},
    {"symbol": "TCS", "model": "xgboost", "timeframe": "1h"},
    {"symbol": "NAS100", "model": "xgboost", "timeframe": "1h"},
    {"symbol": "US30", "model": "xgboost", "timeframe": "1h"},
    {"symbol": "NIFTY50", "model": "xgboost", "timeframe": "1h"},
]

async def train_all():
    print("==================================================")
    print("STARTING AUTO-TRAINING FOR ALL PLATFORM ASSETS")
    print("==================================================")

    for idx, job in enumerate(ASSET_JOBS, 1):
        sym = job["symbol"]
        mtype = job["model"]
        tf = job.get("timeframe", "1h")
        epochs = job.get("epochs", 15)

        print(f"\n[{idx}/{len(ASSET_JOBS)}] Training {sym} ({mtype.upper()})...")
        try:
            df_bars = await market_streamer.get_historical_bars(sym, timeframe=tf, limit=300)
            if df_bars.empty or len(df_bars) < 30:
                print(f"      Warning: Insufficient bars ({len(df_bars)}) for {sym}, skipping.")
                continue

            trainer = ModelTrainer(
                symbol=sym,
                model_type=mtype,
                timeframe=tf,
                epochs=epochs,
                batch_size=32,
                learning_rate=0.001
            )

            res = await trainer.train(df_bars, version="v1.0")
            print(f"      -> Completed: {res['model_id']}")
            print(f"      -> Dataset:   {res['dataset_folder']}")
            print(f"      -> Artifacts: {res['model_folder']}")
        except Exception as e:
            print(f"      -> Error training {sym}: {e}")

    print("\n==================================================")
    print("ALL READY-MADE MODELS SUCCESSFULLY TRAINED & PERSISTED!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(train_all())
