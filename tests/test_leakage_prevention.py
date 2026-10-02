import pytest
import pandas as pd
import numpy as np
from ml.datasets.generator import DatasetGenerator
from ml.preprocessing.scaler import DataPreprocessor

def test_no_leakage_in_splits():
    n = 200
    dates = pd.date_range("2026-01-01", periods=n, freq="1h")
    close = 100.0 + np.cumsum(np.random.normal(0, 1, n))
    df = pd.DataFrame({
        "timestamp": dates,
        "open": close + 0.1,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": 1000.0
    })

    gen = DatasetGenerator(forecast_horizon=1)
    df_clean, split_info, dataset_id = gen.create_dataset(df, symbol="BTCUSDT", timeframe="1h", save_to_disk=False)

    train_idx = split_info["train_indices"]
    val_idx = split_info["val_indices"]
    test_idx = split_info["test_indices"]

    # Verify chronological separation
    assert train_idx[1] == val_idx[0]
    assert val_idx[1] == test_idx[0]

    # Verify timestamps are strictly increasing across splits
    t_train_max = df_clean.iloc[train_idx[0]:train_idx[1]]["timestamp"].max()
    t_val_min = df_clean.iloc[val_idx[0]:val_idx[1]]["timestamp"].min()
    t_val_max = df_clean.iloc[val_idx[0]:val_idx[1]]["timestamp"].max()
    t_test_min = df_clean.iloc[test_idx[0]:test_idx[1]]["timestamp"].min()

    assert t_train_max < t_val_min
    assert t_val_max < t_test_min

def test_scaler_leak_prevention():
    train_df = pd.DataFrame({"f1": [10.0, 20.0, 30.0], "f2": [1.0, 2.0, 3.0]})
    test_df = pd.DataFrame({"f1": [100.0, 200.0, 300.0], "f2": [10.0, 20.0, 30.0]})

    preproc = DataPreprocessor(feature_names=["f1", "f2"], scaler_type="standard")
    
    # Preprocessor must not be allowed to transform before fit
    with pytest.raises(RuntimeError):
        preproc.transform(test_df)

    X_train_scaled = preproc.fit_transform_train(train_df)
    assert preproc.is_fitted

    # Scaler mean must match train mean (20.0, 2.0), not test mean!
    assert np.isclose(preproc.scaler.mean_[0], 20.0)
    assert np.isclose(preproc.scaler.mean_[1], 2.0)
