"""
Dataset Storage Manager
Persists generated training datasets, features, and metadata into dedicated folders.
Every dataset is isolated in its own folder: ml/datasets/records/<dataset_id>/
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

BASE_DATASET_DIR = os.path.abspath("ml/datasets/records")

class DatasetStorage:
    @staticmethod
    def save_dataset(
        symbol: str,
        timeframe: str,
        df: pd.DataFrame,
        feature_names: list,
        target_column: str,
        split_info: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save the dataset to a dedicated timestamped folder.
        Returns the unique dataset_id.
        """
        os.makedirs(BASE_DATASET_DIR, exist_ok=True)
        ts_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        clean_sym = symbol.upper().replace("/", "").replace("-", "")
        dataset_id = f"DATASET_{clean_sym}_{timeframe}_{ts_str}"
        
        target_dir = os.path.join(BASE_DATASET_DIR, dataset_id)
        os.makedirs(target_dir, exist_ok=True)

        # 1. Save data as CSV and Parquet
        csv_path = os.path.join(target_dir, "dataset.csv")
        parquet_path = os.path.join(target_dir, "dataset.parquet")
        
        df.to_csv(csv_path, index=False)
        try:
            df.to_parquet(parquet_path, index=False)
        except Exception:
            pass # CSV is always saved

        # 2. Extract date range
        start_date = str(df["timestamp"].iloc[0]) if "timestamp" in df.columns and len(df) > 0 else ""
        end_date = str(df["timestamp"].iloc[-1]) if "timestamp" in df.columns and len(df) > 0 else ""

        # 3. Save metadata JSON
        meta = {
            "dataset_id": dataset_id,
            "symbol": clean_sym,
            "timeframe": timeframe,
            "row_count": len(df),
            "feature_count": len(feature_names),
            "feature_names": feature_names,
            "target_column": target_column,
            "date_range_start": start_date,
            "date_range_end": end_date,
            "split_info": split_info,
            "folder_path": target_dir,
            "created_at": datetime.utcnow().isoformat(),
            **(metadata or {})
        }

        meta_path = os.path.join(target_dir, "metadata.json")
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)

        # 4. Save feature definitions
        features_meta = {
            "features": feature_names,
            "dtypes": {col: str(df[col].dtype) for col in feature_names if col in df.columns}
        }
        with open(os.path.join(target_dir, "features.json"), "w") as f:
            json.dump(features_meta, f, indent=2)

        print(f"[DatasetStorage] Dataset saved to folder: {target_dir}")
        return dataset_id

    @staticmethod
    def load_dataset(dataset_id: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Load dataset DataFrame and metadata from dedicated folder."""
        target_dir = os.path.join(BASE_DATASET_DIR, dataset_id)
        if not os.path.exists(target_dir):
            raise FileNotFoundError(f"Dataset folder not found: {target_dir}")

        meta_path = os.path.join(target_dir, "metadata.json")
        with open(meta_path, "r") as f:
            meta = json.load(f)

        csv_path = os.path.join(target_dir, "dataset.csv")
        parquet_path = os.path.join(target_dir, "dataset.parquet")

        if os.path.exists(parquet_path):
            try:
                df = pd.read_parquet(parquet_path)
            except Exception:
                df = pd.read_csv(csv_path)
        else:
            df = pd.read_csv(csv_path)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        return df, meta

    @staticmethod
    def list_saved_datasets() -> list:
        """List all saved dataset folders and their metadata."""
        if not os.path.exists(BASE_DATASET_DIR):
            return []
        
        datasets = []
        for folder in os.listdir(BASE_DATASET_DIR):
            folder_path = os.path.join(BASE_DATASET_DIR, folder)
            meta_path = os.path.join(folder_path, "metadata.json")
            if os.path.isdir(folder_path) and os.path.exists(meta_path):
                try:
                    with open(meta_path, "r") as f:
                        meta = json.load(f)
                    datasets.append(meta)
                except Exception:
                    pass
        
        datasets.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return datasets
