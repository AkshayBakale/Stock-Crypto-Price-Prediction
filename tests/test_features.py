import pytest
import pandas as pd
import numpy as np
from ml.features.technical import FeatureEngine

def test_feature_computation():
    # Create synthetic OHLCV dataframe
    n = 100
    dates = pd.date_range("2026-01-01", periods=n, freq="1h")
    close = 100.0 + np.cumsum(np.random.normal(0, 1, n))
    high = close + np.random.uniform(0.5, 2.0, n)
    low = close - np.random.uniform(0.5, 2.0, n)
    open_p = close + np.random.normal(0, 0.5, n)
    volume = np.random.uniform(1000, 5000, n)

    df = pd.DataFrame({
        "timestamp": dates,
        "open": open_p,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume
    })

    feat_df = FeatureEngine.compute_all_features(df)
    
    # Check essential columns exist
    assert "return_1" in feat_df.columns
    assert "rsi_14" in feat_df.columns
    assert "macd" in feat_df.columns
    assert "atr_14" in feat_df.columns
    assert "vwap_20" in feat_df.columns
    assert "parkinson_vol_20" in feat_df.columns
    assert "rel_volume_20" in feat_df.columns
    
    # Check RSI range
    valid_rsi = feat_df["rsi_14"].dropna()
    assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all()
