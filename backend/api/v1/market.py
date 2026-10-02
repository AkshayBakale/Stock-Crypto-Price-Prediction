from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any, List, Optional
from backend.market_data.streamer import market_streamer

router = APIRouter(prefix="/market", tags=["Market Data"])

@router.get("/{symbol}", response_model=Dict[str, Any])
async def get_market_ticker(symbol: str):
    """Fetch latest real-time ticker data."""
    ticker = await market_streamer.get_latest_ticker(symbol)
    return ticker

@router.get("/{symbol}/history")
async def get_market_history(
    symbol: str,
    timeframe: str = Query("1h", description="Timeframe: 1m, 5m, 15m, 1h, 1d"),
    limit: int = Query(300, ge=10, le=1000)
):
    """Fetch historical OHLCV bars for charts and indicators."""
    df = await market_streamer.get_historical_bars(symbol, timeframe=timeframe, limit=limit)
    if df.empty:
        return {"symbol": symbol, "timeframe": timeframe, "bars": []}
    
    bars = []
    for _, row in df.iterrows():
        ts = row["timestamp"]
        ts_val = int(ts.timestamp()) if hasattr(ts, "timestamp") else ts
        bars.append({
            "time": ts_val,
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": float(row.get("volume", 0.0))
        })
    return {"symbol": symbol.upper(), "timeframe": timeframe, "bars": bars}
