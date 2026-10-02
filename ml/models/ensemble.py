"""
Ensemble Quantitative Forecasting
Combines Tree Models (XGBoost, LightGBM) and Deep Learning Models (PyTorch LSTM/Transformer)
using performance-weighted averaging, stacking, and probability calibration.
"""

import numpy as np
from typing import List, Dict, Any, Tuple

class QuantitativeEnsemble:
    def __init__(self, models: List[Any], weights: List[float] = None):
        self.models = models
        if weights is None:
            # Equal weighting initially
            self.weights = np.ones(len(models)) / len(models)
        else:
            self.weights = np.array(weights) / (np.sum(weights) + 1e-9)

    def set_weights_from_val_losses(self, val_losses: List[float]):
        """Derive weights strictly from validation loss performance (inverse variance weighting)."""
        losses = np.array(val_losses)
        inv_losses = 1.0 / (losses + 1e-6)
        self.weights = inv_losses / np.sum(inv_losses)

    def predict_return(self, model_predictions: List[np.ndarray]) -> np.ndarray:
        """Combine return predictions via weighted average."""
        stacked = np.column_stack(model_predictions)
        return np.dot(stacked, self.weights)

    def predict_probabilities(self, model_prob_arrays: List[np.ndarray]) -> np.ndarray:
        """Combine direction probabilities."""
        combined = np.zeros_like(model_prob_arrays[0])
        for p, w in zip(model_prob_arrays, self.weights):
            combined += p * w
        # Normalize
        combined = combined / (np.sum(combined, axis=-1, keepdims=True) + 1e-9)
        return combined
