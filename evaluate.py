"""
CLI Model Evaluation Command
Usage:
    python evaluate.py --symbol BTCUSDT --model xgboost
"""

import argparse
import json
from ml.registry.registry import ModelRegistryManager

def main():
    parser = argparse.ArgumentParser(description="Evaluate registered model performance.")
    parser.add_argument("--symbol", type=str, default="BTCUSDT", help="Instrument symbol")
    parser.add_argument("--model", type=str, default="xgboost", help="Model architecture")
    parser.add_argument("--version", type=str, default="v1.0", help="Model version")
    
    args = parser.parse_args()
    
    try:
        _, _, meta = ModelRegistryManager.load_model_bundle(args.symbol, args.model, args.version)
        print(f"==================================================")
        print(f"MODEL EVALUATION REPORT: {meta['model_id']}")
        print(f"==================================================")
        print(f"Status:          {meta.get('status')}")
        print(f"Dataset Link:    {meta.get('dataset_folder_path')}")
        print(f"Artifact Folder: {meta.get('folder_path')}")
        print("\nMetrics:")
        print(json.dumps(meta.get("metrics", {}), indent=4))
        print("==================================================")
    except Exception as e:
        print(f"Error evaluating model: {e}")

if __name__ == "__main__":
    main()
