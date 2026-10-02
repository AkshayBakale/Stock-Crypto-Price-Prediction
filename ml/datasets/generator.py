"""
ML/DL Dataset Generator
Computes technical features, forms multi-horizon targets, performs chronological train/val/test splits,
and persists the training data in dedicated folders.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List, Optional
from ml.features.technical import FeatureEngine
from ml.datasets.storage import DatasetStorage

class DatasetGenerator:
    def __init__(self, forecast_horizon: int = 1):
        self.forecast_horizon = forecast_horizon

    def create_dataset(
        self,
        df_raw: pd.DataFrame,
        symbol: str,
        timeframe: str = "1h",
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        save_to_disk: bool = True
    ) -> Tuple[pd.DataFrame, Dict[str, Any], str]:
        """
        Processes raw OHLCV DataFrame into full feature matrix and targets.
        Saves dataset into isolated folder and returns (full_df, split_info, dataset_id).
        """
        if df_raw.empty or len(df_raw) < 30:
            raise ValueError(f"Insufficient historical data: {len(df_raw)} rows (need >= 30)")

        # 1. Compute features
        df = FeatureEngine.compute_all_features(df_raw)
        
        # 2. Compute Forward Targets
        h = self.forecast_horizon
        close = df["close"]
        
        # Target 1: Future return over horizon h
        df[f"target_return_{h}"] = (close.shift(-h) - close) / close
        
        # Target 2: Future price over horizon h
        df[f"target_price_{h}"] = close.shift(-h)
        
        # Target 3: Direction (0: DOWN, 1: SIDEWAYS, 2: UP)
        # Threshold: 0.15% return band
        threshold = 0.0015
        future_ret = df[f"target_return_{h}"]
        df["target_direction"] = np.where(
            future_ret > threshold, 2, # UP
            np.where(future_ret < -threshold, 0, 1) # DOWN or SIDEWAYS
        )

        # Target 4: Forward Volatility (future 5-period standard deviation of returns)
        df["target_volatility"] = df["return_1"].shift(-5).rolling(5).std()

        # 3. Clean NaNs caused by indicators warmup and forward shifts
        feature_names = [f for f in FeatureEngine.get_feature_column_names() if f in df.columns]
        
        # Check required columns
        valid_mask = df[feature_names].notna().all(axis=1) & df[f"target_return_{h}"].notna()
        df_clean = df[valid_mask].reset_index(drop=True)

        if len(df_clean) < 20:
            raise ValueError("Insufficient rows remaining after NaN cleaning")

        # 4. Strict Chronological Time Split (Zero Shuffling!)
        n = len(df_clean)
        train_end = int(n * train_ratio)
        val_end = int(n * (train_ratio + val_ratio))

        split_info = {
            "total_rows": n,
            "train_indices": [0, train_end],
            "val_indices": [train_end, val_end],
            "test_indices": [val_end, n],
            "train_rows": train_end,
            "val_rows": val_end - train_end,
            "test_rows": n - val_end,
            "forecast_horizon": h,
            "target_return_col": f"target_return_{h}",
            "target_price_col": f"target_price_{h}",
            "target_direction_col": "target_direction"
        }

        # 5. Save to dedicated storage folder
        dataset_id = ""
        if save_to_disk:
            dataset_id = DatasetStorage.save_dataset(
                symbol=symbol,
                timeframe=timeframe,
                df=df_clean,
                feature_names=feature_names,
                target_column=f"target_return_{h}",
                split_info=split_info
            )

        return df_clean, split_info, dataset_id
