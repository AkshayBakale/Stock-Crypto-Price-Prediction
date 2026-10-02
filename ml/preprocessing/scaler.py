"""
Preprocessing & Scaler Pipeline
Ensures strict leak-free feature scaling (fitted on train set only) and artifact serialization.
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Optional
from sklearn.preprocessing import RobustScaler, StandardScaler
import joblib
import os

class DataPreprocessor:
    def __init__(self, feature_names: List[str], scaler_type: str = "robust"):
        self.feature_names = feature_names
        self.scaler_type = scaler_type
        if scaler_type == "robust":
            self.scaler = RobustScaler()
        else:
            self.scaler = StandardScaler()
        self.is_fitted = False

    def fit_transform_train(self, train_df: pd.DataFrame) -> np.ndarray:
        """Fit scaler exclusively on training features to prevent data leakage."""
        X_train = train_df[self.feature_names].values
        # Replace any infs or remaining NaNs
        X_train = np.nan_to_num(X_train, nan=0.0, posinf=1e5, neginf=-1e5)
        X_scaled = self.scaler.fit_transform(X_train)
        self.is_fitted = True
        return X_scaled

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """Transform test/validation/live features using pre-fitted scaler."""
        if not self.is_fitted:
            raise RuntimeError("DataPreprocessor must be fitted on training data before transforming")
        X = df[self.feature_names].values
        X = np.nan_to_num(X, nan=0.0, posinf=1e5, neginf=-1e5)
        return self.scaler.transform(X)

    def save(self, file_path: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        joblib.dump({
            "scaler": self.scaler,
            "feature_names": self.feature_names,
            "scaler_type": self.scaler_type,
            "is_fitted": self.is_fitted
        }, file_path)

    @classmethod
    def load(cls, file_path: str) -> "DataPreprocessor":
        data = joblib.load(file_path)
        inst = cls(feature_names=data["feature_names"], scaler_type=data.get("scaler_type", "robust"))
        inst.scaler = data["scaler"]
        inst.is_fitted = data["is_fitted"]
        return inst
