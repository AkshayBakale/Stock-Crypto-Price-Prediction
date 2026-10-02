"""
US Equities & Indices Market Data Provider
Integrates with yfinance and market APIs for historical and live US stock and index feeds.
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
import yfinance as yf

from backend.market_data.base import MarketDataProvider
from backend.market_data.validator import DataQualityValidator
from backend.market_data.normalizer import get_canonical_instrument, get_provider_symbol

class USStocksProvider(MarketDataProvider):
    TIMEFRAME_MAP = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "1d": "1d",
        "1w": "1wk"
    }

    PERIOD_MAP = {
        "1m": "7d",
        "5m": "60d",
        "15m": "60d",
        "30m": "60d",
        "1h": "730d",
        "1d": "5y",
        "1w": "10y"
    }

    def __init__(self):
        self._latest_cache = {}

    def _fetch_yf_sync(self, ticker_symbol: str, interval: str, period: str) -> pd.DataFrame:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period, interval=interval)
        return df

    async def get_historical_bars(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 500,
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> pd.DataFrame:
        clean_symbol = symbol.upper().replace("/", "").replace("-", "").strip()
        canonical = get_canonical_instrument(clean_symbol)
        yf_symbol = get_provider_symbol(canonical["canonical_id"])
        
        interval = self.TIMEFRAME_MAP.get(timeframe.lower(), "1h")
        period = self.PERIOD_MAP.get(timeframe.lower(), "1y")

        try:
            loop = asyncio.get_event_loop()
            raw_df = await loop.run_in_executor(None, self._fetch_yf_sync, yf_symbol, interval, period)
            
            if raw_df.empty:
                return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

            raw_df = raw_df.reset_index()
            # Normalize column names
            col_map = {}
            for col in raw_df.columns:
                c_lower = str(col).lower()
                if "date" in c_lower or "time" in c_lower:
                    col_map[col] = "timestamp"
                elif c_lower == "open":
                    col_map[col] = "open"
                elif c_lower == "high":
                    col_map[col] = "high"
                elif c_lower == "low":
                    col_map[col] = "low"
                elif c_lower == "close":
                    col_map[col] = "close"
                elif c_lower == "volume":
                    col_map[col] = "volume"
            
            raw_df = raw_df.rename(columns=col_map)
            if "timestamp" in raw_df.columns and raw_df["timestamp"].dt.tz is not None:
                raw_df["timestamp"] = raw_df["timestamp"].dt.tz_convert("UTC")
            
            # Keep latest 'limit' rows
            raw_df = raw_df.tail(limit).reset_index(drop=True)
            
            is_valid, issues, cleaned_df = DataQualityValidator.validate_dataframe(raw_df)
            if not is_valid:
                print(f"[USStocksProvider] Validation warning for {symbol}: {issues}")
            return cleaned_df
        except Exception as e:
            print(f"[USStocksProvider] Error fetching {symbol} historical bars: {e}")
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

    async def get_latest_ticker(self, symbol: str) -> Dict[str, Any]:
        clean_symbol = symbol.upper().strip()
        canonical = get_canonical_instrument(clean_symbol)
        yf_symbol = get_provider_symbol(canonical["canonical_id"])

        try:
            def _get_fast_info():
                t = yf.Ticker(yf_symbol)
                info = t.fast_info
                return {
                    "last_price": getattr(info, "last_price", None),
                    "previous_close": getattr(info, "previous_close", None),
                    "day_high": getattr(info, "day_high", None),
                    "day_low": getattr(info, "day_low", None),
                    "last_volume": getattr(info, "last_volume", 0),
                }

            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, _get_fast_info)
            
            price = info.get("last_price")
            prev_close = info.get("previous_close") or price
            high_24h = info.get("day_high") or price
            low_24h = info.get("day_low") or price
            vol = info.get("last_volume") or 0

            if price is not None and price > 0:
                change_pct = ((price - prev_close) / prev_close) * 100 if prev_close else 0.0
                now_utc = datetime.now(timezone.utc)
                
                result = {
                    "symbol": clean_symbol,
                    "canonical_id": canonical["canonical_id"],
                    "market": canonical["market"],
                    "exchange": canonical["exchange"],
                    "provider": "yfinance",
                    "price": round(float(price), 2),
                    "change_24h_pct": round(float(change_pct), 2),
                    "high_24h": round(float(high_24h), 2),
                    "low_24h": round(float(low_24h), 2),
                    "volume_24h": float(vol),
                    "timestamp": now_utc.isoformat(),
                    "data_age_seconds": 15.0,
                    "status": "LIVE",
                    "is_configured": True
                }
                self._latest_cache[clean_symbol] = result
                return result
        except Exception as e:
            print(f"[USStocksProvider] Ticker error for {symbol}: {e}")

        if clean_symbol in self._latest_cache:
            res = self._latest_cache[clean_symbol].copy()
            res["status"] = "STALE"
            return res

        return {
            "symbol": clean_symbol,
            "canonical_id": canonical["canonical_id"],
            "market": canonical["market"],
            "exchange": canonical["exchange"],
            "provider": "yfinance",
            "price": 0.0,
            "change_24h_pct": 0.0,
            "high_24h": 0.0,
            "low_24h": 0.0,
            "volume_24h": 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data_age_seconds": -1,
            "status": "UNAVAILABLE",
            "is_configured": True
        }

    async def search_instruments(self, query: str) -> List[Dict[str, Any]]:
        query = query.upper().strip()
        common = ["AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NAS100", "US30"]
        matches = [s for s in common if query in s]
        return [get_canonical_instrument(m) for m in matches]
