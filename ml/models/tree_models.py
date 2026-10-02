"""
Tree-Based Models: XGBoost & LightGBM
Implements gradient boosted decision trees for quantitative return prediction and direction classification,
along with SHAP (SHapley Additive exPlanations) feature attributions.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
try:
    import xgboost as xgb
except ImportError:
    xgb = None

try:
    import lightgbm as lgb
except ImportError:
    lgb = None

try:
    import shap
except ImportError:
    shap = None

from sklearn.ensemble import RandomForestRegressor
import joblib
import os

class QuantitativeTreeModel:
    def __init__(
        self,
        model_type: str = "xgboost",
        task: str = "regression",
        params: Optional[Dict[str, Any]] = None
    ):
        self.model_type = model_type.lower()
        self.task = task.lower()
        self.params = params or {}
        self.model = None
        self.explainer = None
        self._init_model()

    def _init_model(self):
        default_n_estimators = self.params.get("n_estimators", 150)
        default_lr = self.params.get("learning_rate", 0.03)
        default_max_depth = self.params.get("max_depth", 5)

        if self.model_type == "xgboost":
            if xgb is None:
                raise ImportError("xgboost is not installed. Please install it using 'pip install xgboost'.")
            if self.task == "regression":
                self.model = xgb.XGBRegressor(
                    n_estimators=default_n_estimators,
                    learning_rate=default_lr,
                    max_depth=default_max_depth,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    n_jobs=-1
                )
            else:
                self.model = xgb.XGBClassifier(
                    n_estimators=default_n_estimators,
                    learning_rate=default_lr,
                    max_depth=default_max_depth,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    n_jobs=-1
                )
        elif self.model_type == "lightgbm":
            if lgb is None:
                raise ImportError("lightgbm is not installed. Please install it using 'pip install lightgbm'.")
            if self.task == "regression":
                self.model = lgb.LGBMRegressor(
                    n_estimators=default_n_estimators,
                    learning_rate=default_lr,
                    max_depth=default_max_depth,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    verbose=-1,
                    n_jobs=-1
                )
            else:
                self.model = lgb.LGBMClassifier(
                    n_estimators=default_n_estimators,
                    learning_rate=default_lr,
                    max_depth=default_max_depth,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                    verbose=-1,
                    n_jobs=-1
                )
        else:
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=default_max_depth,
                random_state=42,
                n_jobs=-1
            )

    def fit(self, X_train: np.ndarray, y_train: np.ndarray, X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None):
        self.model.fit(X_train, y_train)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X)
        return np.zeros((len(X), 3))

    def compute_shap_importance(self, X: np.ndarray, feature_names: List[str], max_display: int = 8) -> Dict[str, float]:
        """Compute top SHAP feature contributions for explainability."""
        try:
            # Use TreeExplainer
            sample_X = X[-min(len(X), 50):] # Last 50 rows for fast real-time explanation
            explainer = shap.TreeExplainer(self.model)
            shap_vals = explainer.shap_values(sample_X)
            
            if isinstance(shap_vals, list):
                shap_vals = shap_vals[0]
            if len(shap_vals.shape) == 3:
                shap_vals = shap_vals[:, :, 0]
                
            mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)
            
            # Map to feature names
            importance_dict = {}
            for idx, feat in enumerate(feature_names):
                if idx < len(mean_abs_shap):
                    importance_dict[feat] = float(mean_abs_shap[idx])
            
            # Sort top features
            sorted_feats = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:max_display]
            total_sum = sum([v for _, v in sorted_feats]) + 1e-9
            return {k: round(v / total_sum, 4) for k, v in sorted_feats}
        except Exception as e:
            # Fallback to feature_importances_ if shap encounters issue
            if hasattr(self.model, "feature_importances_"):
                fi = self.model.feature_importances_
                importance_dict = {feat: float(fi[idx]) for idx, feat in enumerate(feature_names) if idx < len(fi)}
                sorted_feats = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:max_display]
                total_sum = sum([v for _, v in sorted_feats]) + 1e-9
                return {k: round(v / total_sum, 4) for k, v in sorted_feats}
            return {}

    def save(self, file_path: str):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        joblib.dump({
            "model": self.model,
            "model_type": self.model_type,
            "task": self.task,
            "params": self.params
        }, file_path)

    @classmethod
    def load(cls, file_path: str) -> "QuantitativeTreeModel":
        data = joblib.load(file_path)
        inst = cls(model_type=data["model_type"], task=data["task"], params=data.get("params"))
        inst.model = data["model"]
        return inst
