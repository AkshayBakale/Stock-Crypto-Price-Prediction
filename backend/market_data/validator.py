"""
Data Quality Validator
Validates incoming ticks, historical candles, OHLC integrity, volume, and anomaly detection.
"""

from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone
import pandas as pd
import numpy as np

class DataQualityValidator:
    @staticmethod
    def validate_candle(candle: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate individual candle dictionary."""
        open_p = candle.get("open")
        high_p = candle.get("high")
        low_p = candle.get("low")
        close_p = candle.get("close")
        volume = candle.get("volume", 0.0)
        ts = candle.get("timestamp")

        if any(p is None for p in [open_p, high_p, low_p, close_p]):
            return False, "Missing OHLC values"

        if open_p <= 0 or high_p <= 0 or low_p <= 0 or close_p <= 0:
            return False, "Non-positive price detected"

        if volume < 0:
            return False, "Negative volume detected"

        if high_p < low_p:
            return False, f"High price ({high_p}) is lower than low price ({low_p})"

        if high_p < open_p or high_p < close_p:
            return False, f"High price ({high_p}) is less than open ({open_p}) or close ({close_p})"

        if low_p > open_p or low_p > close_p:
            return False, f"Low price ({low_p}) is greater than open ({open_p}) or close ({close_p})"

        # Check timestamp
        if isinstance(ts, datetime):
            now_utc = datetime.now(timezone.utc)
            if ts.tzinfo is not None and ts > now_utc:
                return False, f"Future timestamp detected: {ts}"

        return True, "OK"

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str], pd.DataFrame]:
        """
        Validate and clean an entire OHLCV DataFrame.
        Returns (is_valid, list of issues detected, cleaned_dataframe).
        """
        issues = []
        if df.empty:
            return False, ["DataFrame is completely empty"], df

        required_cols = ["timestamp", "open", "high", "low", "close"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            return False, [f"Missing required columns: {missing_cols}"], df

        cleaned = df.copy()

        # 1. Parse timestamps and sort
        if not pd.api.types.is_datetime64_any_dtype(cleaned["timestamp"]):
            cleaned["timestamp"] = pd.to_datetime(cleaned["timestamp"])
        
        # 2. Check duplicates
        dup_count = cleaned["timestamp"].duplicated().sum()
        if dup_count > 0:
            issues.append(f"Found and removed {dup_count} duplicate timestamps")
            cleaned = cleaned.drop_duplicates(subset=["timestamp"], keep="last")

        cleaned = cleaned.sort_values("timestamp").reset_index(drop=True)

        # 3. Numeric conversion & clean NaNs
        for col in ["open", "high", "low", "close"]:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")
        if "volume" in cleaned.columns:
            cleaned["volume"] = pd.to_numeric(cleaned["volume"], errors="coerce").fillna(0.0)
        else:
            cleaned["volume"] = 0.0

        nan_rows = cleaned[["open", "high", "low", "close"]].isna().any(axis=1).sum()
        if nan_rows > 0:
            issues.append(f"Found and dropped {nan_rows} rows with NaN price data")
            cleaned = cleaned.dropna(subset=["open", "high", "low", "close"]).reset_index(drop=True)

        if cleaned.empty:
            return False, ["No valid rows remaining after NaN filtering"], cleaned

        # 4. Check Non-positive prices
        invalid_prices = (cleaned["open"] <= 0) | (cleaned["high"] <= 0) | (cleaned["low"] <= 0) | (cleaned["close"] <= 0)
        if invalid_prices.any():
            count = invalid_prices.sum()
            issues.append(f"Dropped {count} rows with non-positive prices")
            cleaned = cleaned[~invalid_prices].reset_index(drop=True)

        # 5. Fix/verify OHLC inequalities
        bad_high = (cleaned["high"] < cleaned["open"]) | (cleaned["high"] < cleaned["close"]) | (cleaned["high"] < cleaned["low"])
        bad_low = (cleaned["low"] > cleaned["open"]) | (cleaned["low"] > cleaned["close"])
        if bad_high.any() or bad_low.any():
            issues.append("Repaired anomalous High/Low bounds to encompass Open and Close")
            cleaned["high"] = cleaned[["open", "high", "low", "close"]].max(axis=1)
            cleaned["low"] = cleaned[["open", "high", "low", "close"]].min(axis=1)

        # 6. Check for extreme single-bar price outliers (> 80% change in 1 bar)
        returns = cleaned["close"].pct_change().abs()
        extreme_outliers = returns > 0.80
        if extreme_outliers.any():
            issues.append(f"Detected {extreme_outliers.sum()} extreme single-period return outliers")

        is_valid = len(cleaned) >= 5
        if not is_valid:
            issues.append("DataFrame has fewer than 5 rows after validation")

        return is_valid, issues, cleaned
