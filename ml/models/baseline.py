"""
Baseline Forecasting Models
Institutional benchmarks:
- Naive Forecast (last price/return)
- Random Walk Benchmark
- Moving Average Forecast
- Linear Regression Baseline
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.linear_model import Ridge

class BaselineModel:
    def __init__(self, model_type: str = "naive"):
        self.model_type = model_type.lower()
        self.lin_reg = Ridge(alpha=1.0)
        self.mean_return = 0.0

    def fit(self, X: np.ndarray, y: np.ndarray):
        if self.model_type == "linear_regression":
            self.lin_reg.fit(X, y)
        elif self.model_type == "moving_average":
            self.mean_return = float(np.mean(y))
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        n_samples = len(X)
        if self.model_type == "naive":
            # Naive expectation of zero future return change
            return np.zeros(n_samples)
        elif self.model_type == "random_walk":
            return np.random.normal(0.0, 0.005, size=n_samples)
        elif self.model_type == "moving_average":
            return np.full(n_samples, self.mean_return)
        elif self.model_type == "linear_regression":
            return self.lin_reg.predict(X)
        return np.zeros(n_samples)
