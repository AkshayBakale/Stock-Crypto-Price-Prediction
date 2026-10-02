"""
Market Data Streamer & Manager
Orchestrates multi-market providers, live WebSocket streaming, and price caching.
"""

import asyncio
from typing import Dict, Any, List, Optional, Set
import pandas as pd

from backend.market_data.crypto import CryptoProvider
from backend.market_data.us_stocks import USStocksProvider
from backend.market_data.indian_stocks import IndianStocksProvider
from backend.market_data.normalizer import get_canonical_instrument

class MarketDataStreamer:
    def __init__(self):
        self.crypto_provider = CryptoProvider()
        self.us_provider = USStocksProvider()
        self.in_provider = IndianStocksProvider()
        
        self._active_ws_symbols: Set[str] = set()
        self._ws_tasks: Dict[str, asyncio.Task] = {}
        self._price_subscribers: List[Any] = [] # WebSocket connection handlers
        self._latest_ticks: Dict[str, Dict[str, Any]] = {}
        self._running = False
        self._bg_polling_task: Optional[asyncio.Task] = None

    def get_provider_for_symbol(self, symbol: str):
        canonical = get_canonical_instrument(symbol)
        market = canonical.get("market")
        if market == "crypto":
            return self.crypto_provider
        elif market == "in_equity":
            return self.in_provider
        else:
            return self.us_provider

    async def get_historical_bars(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 500,
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> pd.DataFrame:
        provider = self.get_provider_for_symbol(symbol)
        return await provider.get_historical_bars(symbol, timeframe, limit, start, end)

    async def get_latest_ticker(self, symbol: str) -> Dict[str, Any]:
        clean_sym = symbol.upper().strip()
        if clean_sym in self._latest_ticks:
            return self._latest_ticks[clean_sym]
        
        provider = self.get_provider_for_symbol(clean_sym)
        ticker = await provider.get_latest_ticker(clean_sym)
        self._latest_ticks[clean_sym] = ticker
        return ticker

    async def search_instruments(self, query: str) -> List[Dict[str, Any]]:
        crypto_results = await self.crypto_provider.search_instruments(query)
        us_results = await self.us_provider.search_instruments(query)
        in_results = await self.in_provider.search_instruments(query)
        
        # Deduplicate by canonical_id
        seen = set()
        combined = []
        for r in crypto_results + us_results + in_results:
            cid = r.get("canonical_id")
            if cid not in seen:
                seen.add(cid)
                combined.append(r)
        return combined

    async def _on_live_tick(self, tick: Dict[str, Any]):
        sym = tick.get("symbol", "").upper()
        self._latest_ticks[sym] = tick
        # Broadcast to all connected WebSockets
        await self.broadcast_tick(tick)

    async def broadcast_tick(self, tick: Dict[str, Any]):
        for queue in list(self._price_subscribers):
            try:
                await queue.put(tick)
            except Exception:
                pass

    def subscribe_ticks(self) -> asyncio.Queue:
        q = asyncio.Queue(maxsize=100)
        self._price_subscribers.append(q)
        return q

    def unsubscribe_ticks(self, q: asyncio.Queue):
        if q in self._price_subscribers:
            self._price_subscribers.remove(q)

    async def start(self):
        """Start background streamers and polling tasks."""
        if self._running:
            return
        self._running = True
        
        # Start crypto streaming for core liquid pairs
        tracked_crypto = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        for sym in tracked_crypto:
            if sym not in self._ws_tasks:
                task = asyncio.create_task(
                    self.crypto_provider.start_websocket_stream(sym, self._on_live_tick)
                )
                self._ws_tasks[sym] = task

        # Start periodic polling for equities and indices
        self._bg_polling_task = asyncio.create_task(self._poll_equities_loop())
        print("[MarketDataStreamer] Real-time market streaming started successfully.")

    async def _poll_equities_loop(self):
        equities = ["AAPL", "NVDA", "MSFT", "NAS100", "US30", "RELIANCE", "TCS", "NIFTY50"]
        while self._running:
            try:
                for sym in equities:
                    provider = self.get_provider_for_symbol(sym)
                    ticker = await provider.get_latest_ticker(sym)
                    self._latest_ticks[sym.upper()] = ticker
                    await self.broadcast_tick(ticker)
                    await asyncio.sleep(0.5) # stagger requests
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[MarketDataStreamer] Equities poll error: {e}")
                await asyncio.sleep(5)

    async def stop(self):
        self._running = False
        for sym, task in self._ws_tasks.items():
            task.cancel()
        self._ws_tasks.clear()
        if self._bg_polling_task:
            self._bg_polling_task.cancel()

market_streamer = MarketDataStreamer()
