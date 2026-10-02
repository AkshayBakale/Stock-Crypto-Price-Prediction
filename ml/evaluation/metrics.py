"""
Institutional Model Evaluation & Probability Calibration
- Regression: MAE, RMSE, MAPE, SMAPE, R²
- Classification: Accuracy, Precision, Recall, F1, ROC-AUC, Log Loss, Brier Score
- Calibration: Platt Scaling, Isotonic Regression, Temperature Scaling
- Trading: Sharpe Ratio, Sortino Ratio, Max Drawdown, Profit Factor, Win Rate, Expectancy
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, Optional
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    brier_score_loss, log_loss
)
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

class ModelEvaluator:
    @staticmethod
    def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Compute institutional regression evaluation metrics."""
        y_true = np.asarray(y_true).flatten()
        y_pred = np.asarray(y_pred).flatten()

        # Handle edge cases
        if len(y_true) < 2:
            return {"mae": 0.0, "rmse": 0.0, "mape": 0.0, "smape": 0.0, "r2": 0.0}

        mae = float(mean_absolute_error(y_true, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        
        # MAPE & SMAPE
        denominator = np.abs(y_true) + 1e-6
        mape = float(np.mean(np.abs((y_true - y_pred) / denominator)) * 100.0)
        
        denom_smape = (np.abs(y_true) + np.abs(y_pred)) + 1e-6
        smape = float(np.mean(2.0 * np.abs(y_pred - y_true) / denom_smape) * 100.0)
        
        r2 = float(r2_score(y_true, y_pred))

        # Directional Accuracy (Hit Rate)
        dir_true = np.sign(y_true)
        dir_pred = np.sign(y_pred)
        dir_acc = float(np.mean(dir_true == dir_pred) * 100.0)

        return {
            "mae": round(mae, 6),
            "rmse": round(rmse, 6),
            "mape_pct": round(min(mape, 999.0), 2),
            "smape_pct": round(min(smape, 200.0), 2),
            "r2": round(r2, 4),
            "directional_accuracy_pct": round(dir_acc, 2)
        }

    @staticmethod
    def evaluate_classification(y_true: np.ndarray, y_pred: np.ndarray, y_prob: Optional[np.ndarray] = None) -> Dict[str, float]:
        """Compute institutional classification metrics."""
        y_true = np.asarray(y_true).flatten()
        y_pred = np.asarray(y_pred).flatten()

        acc = float(accuracy_score(y_true, y_pred) * 100.0)
        prec = float(precision_score(y_true, y_pred, average="weighted", zero_division=0) * 100.0)
        rec = float(recall_score(y_true, y_pred, average="weighted", zero_division=0) * 100.0)
        f1 = float(f1_score(y_true, y_pred, average="weighted", zero_division=0) * 100.0)

        res = {
            "accuracy_pct": round(acc, 2),
            "precision_pct": round(prec, 2),
            "recall_pct": round(rec, 2),
            "f1_pct": round(f1, 2)
        }

        if y_prob is not None and len(y_prob.shape) > 1 and y_prob.shape[1] > 1:
            try:
                ll = float(log_loss(y_true, y_prob))
                res["log_loss"] = round(ll, 4)
            except Exception:
                pass

        return res

    @staticmethod
    def evaluate_trading_performance(
        returns_series: np.ndarray,
        benchmark_returns: Optional[np.ndarray] = None,
        risk_free_rate: float = 0.04
    ) -> Dict[str, float]:
        """Compute Sharpe, Sortino, Max Drawdown, Win Rate, Profit Factor."""
        r = np.asarray(returns_series).flatten()
        if len(r) == 0:
            return {
                "sharpe_ratio": 0.0,
                "sortino_ratio": 0.0,
                "max_drawdown_pct": 0.0,
                "win_rate_pct": 0.0,
                "profit_factor": 0.0,
                "total_return_pct": 0.0
            }

        # Daily / hourly compounding
        cum_equity = np.cumprod(1 + r)
        total_ret = (cum_equity[-1] - 1.0) * 100.0 if len(cum_equity) > 0 else 0.0

        # Annualized proxy (assuming 252 periods or scaled by len)
        mean_ret = np.mean(r)
        std_ret = np.std(r) + 1e-9
        sharpe = (mean_ret / std_ret) * np.sqrt(252)

        # Sortino (downside deviation)
        downside = r[r < 0]
        downside_std = np.std(downside) + 1e-9 if len(downside) > 0 else 1e-6
        sortino = (mean_ret / downside_std) * np.sqrt(252)

        # Max Drawdown
        peak = np.maximum.accumulate(cum_equity)
        drawdown = (cum_equity - peak) / (peak + 1e-9)
        max_dd = float(np.min(drawdown) * 100.0) if len(drawdown) > 0 else 0.0

        # Win Rate & Profit Factor
        winning_trades = r[r > 0]
        losing_trades = r[r < 0]
        win_rate = (len(winning_trades) / len(r)) * 100.0 if len(r) > 0 else 0.0
        
        gross_profit = np.sum(winning_trades) if len(winning_trades) > 0 else 0.0
        gross_loss = np.abs(np.sum(losing_trades)) if len(losing_trades) > 0 else 1e-9
        profit_factor = gross_profit / gross_loss

        return {
            "total_return_pct": round(total_ret, 2),
            "sharpe_ratio": round(sharpe, 2),
            "sortino_ratio": round(sortino, 2),
            "max_drawdown_pct": round(abs(max_dd), 2),
            "win_rate_pct": round(win_rate, 2),
            "profit_factor": round(min(profit_factor, 50.0), 2)
        }


class ProbabilityCalibrator:
    """Platt Scaling and Isotonic Regression Calibrators."""
    def __init__(self, method: str = "isotonic"):
        self.method = method.lower()
        if self.method == "platt":
            self.calibrator = LogisticRegression()
        else:
            self.calibrator = IsotonicRegression(out_of_bounds="clip")
        self.is_fitted = False

    def fit(self, raw_probs: np.ndarray, y_true: np.ndarray):
        raw_probs = np.asarray(raw_probs).flatten()
        y_true = np.asarray(y_true).flatten()
        if self.method == "platt":
            self.calibrator.fit(raw_probs.reshape(-1, 1), y_true)
        else:
            self.calibrator.fit(raw_probs, y_true)
        self.is_fitted = True
        return self

    def calibrate(self, raw_probs: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            return raw_probs
        raw_probs = np.asarray(raw_probs).flatten()
        if self.method == "platt":
            return self.calibrator.predict_proba(raw_probs.reshape(-1, 1))[:, 1]
        else:
            return self.calibrator.predict(raw_probs)
