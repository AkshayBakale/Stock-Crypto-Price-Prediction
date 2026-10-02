"""
Technical Feature Engineering
Pure NumPy & Pandas implementation of institutional quantitative features:
- Price: Simple/log returns, momentum, acceleration, gap
- Trend: SMA, EMA, WMA, VWAP, trend slope
- Momentum: RSI, MACD, Stochastic %K/%D, CCI, ROC, Williams %R
- Volatility: ATR, Historical Volatility, Parkinson, Garman-Klass
- Volume: Volume changes, Relative Volume, OBV, MFI
"""

import pandas as pd
import numpy as np
from typing import List, Optional

class FeatureEngine:
    @staticmethod
    def compute_all_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute full suite of technical features from OHLCV DataFrame.
        Guarantees strictly backward-looking calculations to prevent lookahead leakage.
        """
        if df.empty or len(df) < 15:
            return df

        out = df.copy()
        
        # Ensure correct column types
        for col in ["open", "high", "low", "close", "volume"]:
            if col in out.columns:
                out[col] = pd.to_numeric(out[col], errors="coerce")

        close = out["close"]
        high = out["high"]
        low = out["low"]
        open_p = out["open"]
        volume = out["volume"].fillna(0.0)

        # -------------------------------------------------------------
        # 1. Price & Return Features
        # -------------------------------------------------------------
        out["return_1"] = close.pct_change(1)
        out["return_3"] = close.pct_change(3)
        out["return_5"] = close.pct_change(5)
        out["return_10"] = close.pct_change(10)
        out["return_20"] = close.pct_change(20)
        out["log_return"] = np.log(close / close.shift(1))
        
        out["momentum_5"] = close - close.shift(5)
        out["momentum_10"] = close - close.shift(10)
        out["acceleration_5"] = out["momentum_5"] - out["momentum_5"].shift(1)
        
        # Gap: open vs previous close
        out["gap"] = (open_p - close.shift(1)) / (close.shift(1) + 1e-9)

        # -------------------------------------------------------------
        # 2. Trend Indicators
        # -------------------------------------------------------------
        for period in [7, 14, 21, 50]:
            out[f"sma_{period}"] = close.rolling(period).mean()
            out[f"close_to_sma_{period}"] = (close - out[f"sma_{period}"]) / (out[f"sma_{period}"] + 1e-9)
            
        for period in [9, 21, 50]:
            out[f"ema_{period}"] = close.ewm(span=period, adjust=False).mean()
            out[f"close_to_ema_{period}"] = (close - out[f"ema_{period}"]) / (out[f"ema_{period}"] + 1e-9)

        # WMA (Weighted Moving Average) 14
        weights = np.arange(1, 15)
        out["wma_14"] = close.rolling(14).apply(lambda prices: np.dot(prices, weights) / weights.sum(), raw=True)

        # VWAP (Volume Weighted Average Price) rolling 20
        typical_price = (high + low + close) / 3.0
        pv = typical_price * volume
        cum_pv = pv.rolling(20).sum()
        cum_vol = volume.rolling(20).sum()
        out["vwap_20"] = cum_pv / (cum_vol + 1e-9)
        out["close_to_vwap"] = (close - out["vwap_20"]) / (out["vwap_20"] + 1e-9)

        # Trend Slope (10 period linear regression slope of close)
        def _calc_slope(series):
            x = np.arange(len(series))
            if len(series) < 2:
                return 0.0
            cov = np.cov(x, series)[0, 1]
            var = np.var(x)
            return cov / (var + 1e-9)

        out["trend_slope_10"] = close.rolling(10).apply(_calc_slope, raw=True)

        # -------------------------------------------------------------
        # 3. Momentum Indicators
        # -------------------------------------------------------------
        # RSI 14
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / (avg_loss + 1e-9)
        out["rsi_14"] = 100 - (100 / (1 + rs))

        # MACD (12, 26, 9)
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        out["macd"] = ema_12 - ema_26
        out["macd_signal"] = out["macd"].ewm(span=9, adjust=False).mean()
        out["macd_hist"] = out["macd"] - out["macd_signal"]

        # Stochastic Oscillator (%K, %D) 14
        low_14 = low.rolling(14).min()
        high_14 = high.rolling(14).max()
        out["stoch_k"] = 100 * ((close - low_14) / ((high_14 - low_14) + 1e-9))
        out["stoch_d"] = out["stoch_k"].rolling(3).mean()

        # CCI (Commodity Channel Index) 20
        tp_mean = typical_price.rolling(20).mean()
        tp_mad = typical_price.rolling(20).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
        out["cci_20"] = (typical_price - tp_mean) / (0.015 * (tp_mad + 1e-9))

        # Rate of Change (ROC) 12
        out["roc_12"] = ((close - close.shift(12)) / (close.shift(12) + 1e-9)) * 100

        # Williams %R 14
        out["williams_r_14"] = -100 * ((high_14 - close) / ((high_14 - low_14) + 1e-9))

        # -------------------------------------------------------------
        # 4. Volatility Indicators
        # -------------------------------------------------------------
        # True Range & ATR 14
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        out["atr_14"] = tr.rolling(14).mean()
        out["atr_pct"] = out["atr_14"] / (close + 1e-9)

        # Historical & Rolling Volatility (annualized proxy)
        out["hist_vol_20"] = out["return_1"].rolling(20).std() * np.sqrt(252)

        # Parkinson Volatility (based on High/Low)
        hl_ratio = np.log(high / (low + 1e-9)) ** 2
        out["parkinson_vol_20"] = np.sqrt((1.0 / (4.0 * np.log(2))) * hl_ratio.rolling(20).mean()) * np.sqrt(252)

        # Garman-Klass Volatility (incorporating Open/High/Low/Close)
        gk_term1 = 0.5 * (np.log(high / (low + 1e-9)) ** 2)
        gk_term2 = (2 * np.log(2) - 1) * (np.log(close / (open_p + 1e-9)) ** 2)
        out["garman_klass_vol_20"] = np.sqrt((gk_term1 - gk_term2).rolling(20).mean()) * np.sqrt(252)

        # -------------------------------------------------------------
        # 5. Volume Indicators
        # -------------------------------------------------------------
        out["vol_change_1"] = volume.pct_change(1)
        out["vol_ma_20"] = volume.rolling(20).mean()
        out["rel_volume_20"] = volume / (out["vol_ma_20"] + 1e-9)

        # On-Balance Volume (OBV)
        obv_dir = np.sign(close.diff()).fillna(0)
        out["obv"] = (obv_dir * volume).cumsum()
        out["obv_ema_20"] = out["obv"].ewm(span=20, adjust=False).mean()

        # Money Flow Index (MFI) 14
        raw_mf = typical_price * volume
        pos_mf = raw_mf.where(typical_price > typical_price.shift(1), 0.0)
        neg_mf = raw_mf.where(typical_price < typical_price.shift(1), 0.0)
        mfr = pos_mf.rolling(14).sum() / (neg_mf.rolling(14).sum() + 1e-9)
        out["mfi_14"] = 100 - (100 / (1 + mfr))

        return out

    @staticmethod
    def get_feature_column_names() -> List[str]:
        """Returns the canonical list of computed technical feature names."""
        return [
            "return_1", "return_3", "return_5", "return_10", "return_20", "log_return",
            "momentum_5", "momentum_10", "acceleration_5", "gap",
            "close_to_sma_7", "close_to_sma_14", "close_to_sma_21", "close_to_sma_50",
            "close_to_ema_9", "close_to_ema_21", "close_to_ema_50",
            "close_to_vwap", "trend_slope_10",
            "rsi_14", "macd", "macd_signal", "macd_hist",
            "stoch_k", "stoch_d", "cci_20", "roc_12", "williams_r_14",
            "atr_pct", "hist_vol_20", "parkinson_vol_20", "garman_klass_vol_20",
            "vol_change_1", "rel_volume_20", "mfi_14"
        ]
