import pytest
import pandas as pd
from datetime import datetime
from backend.market_data.validator import DataQualityValidator

def test_candle_validator():
    # Valid candle
    valid_c = {"open": 100, "high": 105, "low": 98, "close": 102, "volume": 500}
    ok, msg = DataQualityValidator.validate_candle(valid_c)
    assert ok

    # Invalid high < low
    bad_c1 = {"open": 100, "high": 90, "low": 98, "close": 102, "volume": 500}
    ok, msg = DataQualityValidator.validate_candle(bad_c1)
    assert not ok

    # Negative price
    bad_c2 = {"open": -10, "high": 105, "low": 98, "close": 102, "volume": 500}
    ok, msg = DataQualityValidator.validate_candle(bad_c2)
    assert not ok

def test_dataframe_validator():
    df = pd.DataFrame([
        {"timestamp": "2026-01-01 00:00:00", "open": 100, "high": 105, "low": 95, "close": 102, "volume": 10},
        {"timestamp": "2026-01-01 01:00:00", "open": 102, "high": 108, "low": 101, "close": 107, "volume": 15},
        {"timestamp": "2026-01-01 01:00:00", "open": 102, "high": 108, "low": 101, "close": 107, "volume": 15}, # Duplicate
        {"timestamp": "2026-01-01 02:00:00", "open": 107, "high": 110, "low": 105, "close": 109, "volume": 20},
        {"timestamp": "2026-01-01 03:00:00", "open": 109, "high": 112, "low": 108, "close": 111, "volume": 25},
        {"timestamp": "2026-01-01 04:00:00", "open": 111, "high": 115, "low": 110, "close": 114, "volume": 30},
    ])
    
    is_valid, issues, cleaned = DataQualityValidator.validate_dataframe(df)
    assert is_valid
    assert len(cleaned) == 5 # Duplicate removed
