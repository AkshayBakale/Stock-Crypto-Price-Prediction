"""
Crypto Market Data Provider
Integrates with Binance public REST API and WebSockets for real-time and historical cryptocurrency data.
Requires zero external API keys.
"""

import asyncio
import aiohttp
import websockets
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
import pandas as pd

from backend.market_data.base import MarketDataProvider
from backend.market_data.validator import DataQualityValidator
from backend.market_data.normalizer import get_canonical_instrument

class CryptoProvider(MarketDataProvider):
    BASE_REST_URL = "https://api.binance.com/api/v3"
    BASE_WS_URL = "wss://stream.binance.com:9443/ws"

    TIMEFRAME_MAP = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "30m": "30m",
        "1h": "1h",
        "4h": "4h",
        "1d": "1d",
        "1w": "1w"
    }

    def __init__(self):
        self._ws_tasks = {}
        self._subscribers = set()
        self._latest_cache = {}

    async def get_historical_bars(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 500,
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> pd.DataFrame:
        clean_symbol = symbol.upper().replace("/", "").replace("-", "")
        interval = self.TIMEFRAME_MAP.get(timeframe.lower(), "1h")
        
        params = {
            "symbol": clean_symbol,
            "interval": interval,
            "limit": min(limit, 1000)
        }
        
        url = f"{self.BASE_REST_URL}/klines"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        raise ValueError(f"Binance API returned status {resp.status}")
                    data = await resp.json()
            
            # Binance kline format:
            # [ [Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base, Taker buy quote, Ignore] ]
            rows = []
            for item in data:
                rows.append({
                    "timestamp": pd.to_datetime(item[0], unit="ms", utc=True),
                    "open": float(item[1]),
                    "high": float(item[2]),
                    "low": float(item[3]),
                    "close": float(item[4]),
                    "volume": float(item[5])
                })
            
            df = pd.DataFrame(rows)
            is_valid, issues, cleaned_df = DataQualityValidator.validate_dataframe(df)
            if not is_valid:
                print(f"[CryptoProvider] Validation warning for {symbol}: {issues}")
            return cleaned_df
        except Exception as e:
            print(f"[CryptoProvider] Error fetching {symbol} historical bars: {e}")
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

    async def get_latest_ticker(self, symbol: str) -> Dict[str, Any]:
        clean_symbol = symbol.upper().replace("/", "").replace("-", "")
        url = f"{self.BASE_REST_URL}/ticker/24hr"
        params = {"symbol": clean_symbol}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        price = float(data.get("lastPrice", 0.0))
                        high_24h = float(data.get("highPrice", 0.0))
                        low_24h = float(data.get("lowPrice", 0.0))
                        change_24h = float(data.get("priceChangePercent", 0.0))
                        volume_24h = float(data.get("volume", 0.0))
                        ts = datetime.fromtimestamp(data.get("closeTime", 0) / 1000.0, tz=timezone.utc)
                        
                        now_utc = datetime.now(timezone.utc)
                        age_sec = (now_utc - ts).total_seconds()
                        status = "LIVE" if age_sec < 60 else "STALE"
                        
                        canonical = get_canonical_instrument(clean_symbol)
                        result = {
                            "symbol": clean_symbol,
                            "canonical_id": canonical["canonical_id"],
                            "market": "crypto",
                            "exchange": "BINANCE",
                            "provider": "binance",
                            "price": price,
                            "change_24h_pct": change_24h,
                            "high_24h": high_24h,
                            "low_24h": low_24h,
                            "volume_24h": volume_24h,
                            "timestamp": ts.isoformat(),
                            "data_age_seconds": max(0.0, round(age_sec, 2)),
                            "status": status,
                            "is_configured": True
                        }
                        self._latest_cache[clean_symbol] = result
                        return result
        except Exception as e:
            print(f"[CryptoProvider] Ticker error for {symbol}: {e}")
        
        if clean_symbol in self._latest_cache:
            res = self._latest_cache[clean_symbol].copy()
            res["status"] = "STALE"
            return res

        canonical = get_canonical_instrument(clean_symbol)
        return {
            "symbol": clean_symbol,
            "canonical_id": canonical["canonical_id"],
            "market": "crypto",
            "exchange": "BINANCE",
            "provider": "binance",
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
        crypto_list = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT"]
        matches = [c for c in crypto_list if query in c]
        return [get_canonical_instrument(m) for m in matches]

    async def start_websocket_stream(self, symbol: str, callback: Callable[[Dict[str, Any]], Any]):
        """Connect to Binance live trade WebSocket and dispatch normalized ticks."""
        clean_symbol = symbol.lower().replace("/", "").replace("-", "")
        ws_url = f"{self.BASE_WS_URL}/{clean_symbol}@trade"
        
        while True:
            try:
                async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10) as ws:
                    print(f"[CryptoProvider] Connected to Binance trade WebSocket for {symbol}")
                    async for message in ws:
                        data = json.loads(message)
                        # Binance trade event: { "e": "trade", "s": "BTCUSDT", "p": "65432.10", "q": "0.12", "T": 167... }
                        price = float(data.get("p", 0.0))
                        vol = float(data.get("q", 0.0))
                        ts_ms = data.get("T", 0)
                        ts = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc)
                        
                        tick = {
                            "symbol": data.get("s", symbol.upper()),
                            "canonical_id": f"CRYPTO_{data.get('s', symbol.upper())}",
                            "market": "crypto",
                            "exchange": "BINANCE",
                            "provider": "binance",
                            "price": price,
                            "volume": vol,
                            "timestamp": ts.isoformat(),
                            "status": "LIVE",
                            "data_age_seconds": 0.01
                        }
                        self._latest_cache[symbol.upper()] = tick
                        if callback:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(tick)
                            else:
                                callback(tick)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[CryptoProvider] WS connection dropped for {symbol}: {e}. Retrying in 3s...")
                await asyncio.sleep(3)
