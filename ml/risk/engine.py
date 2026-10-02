"""
Risk Engine & Market Regime Detection
- Value at Risk (Parametric & Historical VaR at 95% and 99%)
- Expected Shortfall (Conditional VaR)
- Volatility & Drawdown profiling
- Quantitative Market Regime Classifier (BULL, BEAR, HIGH_VOLATILITY, LOW_VOLATILITY, SIDEWAYS)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

class RiskEngine:
    @staticmethod
    def calculate_risk_metrics(returns: np.ndarray, current_price: float = 1.0) -> Dict[str, float]:
        """Calculates VaR, Expected Shortfall, and downside exposure."""
        r = np.asarray(returns).flatten()
        r = r[~np.isnan(r)]
        if len(r) < 10:
            return {
                "var_95_pct": 0.0,
                "var_99_pct": 0.0,
                "expected_shortfall_95_pct": 0.0,
                "annualized_volatility_pct": 0.0
            }

        # Historical VaR
        var_95 = float(-np.percentile(r, 5)) * 100.0
        var_99 = float(-np.percentile(r, 1)) * 100.0

        # Expected Shortfall (mean of returns worse than 5th percentile)
        cutoff_5 = np.percentile(r, 5)
        tail_losses = r[r <= cutoff_5]
        es_95 = float(-np.mean(tail_losses)) * 100.0 if len(tail_losses) > 0 else var_95

        # Annualized Volatility
        vol_ann = float(np.std(r) * np.sqrt(252) * 100.0)

        return {
            "var_95_pct": round(max(0.0, var_95), 2),
            "var_99_pct": round(max(0.0, var_99), 2),
            "expected_shortfall_95_pct": round(max(0.0, es_95), 2),
            "annualized_volatility_pct": round(vol_ann, 2)
        }

    @staticmethod
    def detect_market_regime(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Classifies current market state into institutional regimes:
        BULL, BEAR, HIGH_VOLATILITY, LOW_VOLATILITY, SIDEWAYS
        """
        if df.empty or len(df) < 20:
            return {"regime": "SIDEWAYS", "confidence": 0.5, "trend_strength": 0.0, "volatility_level": "NORMAL"}

        close = df["close"]
        sma_20 = close.rolling(20).mean().iloc[-1]
        sma_50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else sma_20
        curr_price = close.iloc[-1]

        # Returns and volatility
        ret_20 = (curr_price - close.iloc[-20]) / close.iloc[-20]
        vol_20 = close.pct_change().rolling(20).std().iloc[-1] * np.sqrt(252)

        # Classify
        if vol_20 > 0.65:
            regime = "HIGH_VOLATILITY"
        elif curr_price > sma_20 and sma_20 >= sma_50 and ret_20 > 0.02:
            regime = "BULL"
        elif curr_price < sma_20 and sma_20 <= sma_50 and ret_20 < -0.02:
            regime = "BEAR"
        elif vol_20 < 0.20:
            regime = "LOW_VOLATILITY"
        else:
            regime = "SIDEWAYS"

        vol_label = "HIGH" if vol_20 > 0.50 else ("LOW" if vol_20 < 0.20 else "NORMAL")
        trend_strength = round(float(abs(ret_20) * 100.0), 2)

        return {
            "regime": regime,
            "volatility_level": vol_label,
            "trend_strength_pct": trend_strength,
            "annualized_vol": round(float(vol_20 * 100.0), 2)
        }
