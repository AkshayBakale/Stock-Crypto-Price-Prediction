"""
CLI Real-Time Prediction Command
Usage:
    python predict.py --symbol BTCUSDT
    python predict.py --symbol AAPL --model lstm
"""

import argparse
import asyncio
import json
from ml.predictions.predictor import RealtimePredictor

async def main():
    parser = argparse.ArgumentParser(description="Run real-time inference on latest market data.")
    parser.add_argument("--symbol", type=str, default="BTCUSDT", help="Instrument symbol (e.g. BTCUSDT, AAPL)")
    parser.add_argument("--model", type=str, default=None, help="Optional model architecture")
    
    args = parser.parse_args()

    print(f"Fetching live market data and generating prediction for {args.symbol}...")
    pred = await RealtimePredictor.predict_latest(args.symbol, model_type=args.model)
    
    print("\n==================================================")
    print(f"REAL-TIME QUANTITATIVE PREDICTION: {args.symbol}")
    print("==================================================")
    print(json.dumps(pred, indent=2))
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
