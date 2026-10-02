"""
Market-Specific Feature Engineering
Calculates macroeconomic, index, and market-structure context features.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class MarketFeatureEngine:
    @staticmethod
    def enrich_with_market_context(
        df: pd.DataFrame,
        market: str,
        benchmark_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Enrich feature set with regime & benchmark context when available.
        """
        out = df.copy()
        
        if benchmark_df is not None and not benchmark_df.empty:
            bench_ret = benchmark_df["close"].pct_change(1)
            # Reindex / merge by timestamp
            bench_aligned = pd.merge_asof(
                out[["timestamp"]],
                pd.DataFrame({"timestamp": benchmark_df["timestamp"], "bench_return": bench_ret}),
                on="timestamp",
                direction="backward"
            )
            out["benchmark_return_1"] = bench_aligned["bench_return"].fillna(0.0)
            
            # Beta proxy (20-period rolling covariance / variance)
            if "return_1" in out.columns:
                cov = out["return_1"].rolling(20).cov(out["benchmark_return_1"])
                var = out["benchmark_return_1"].rolling(20).var()
                out["beta_20"] = (cov / (var + 1e-9)).fillna(1.0)
        else:
            out["benchmark_return_1"] = 0.0
            out["beta_20"] = 1.0

        return out
