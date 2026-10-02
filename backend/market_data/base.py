from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import pandas as pd

class MarketDataProvider(ABC):
    @abstractmethod
    async def get_historical_bars(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 500,
        start: Optional[str] = None,
        end: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch historical OHLCV data as a validated pandas DataFrame."""
        pass

    @abstractmethod
    async def get_latest_ticker(self, symbol: str) -> Dict[str, Any]:
        """Fetch latest price, timestamp, 24h high/low, volume, and freshness status."""
        pass

    @abstractmethod
    async def search_instruments(self, query: str) -> List[Dict[str, Any]]:
        """Search instruments matching the query string."""
        pass
