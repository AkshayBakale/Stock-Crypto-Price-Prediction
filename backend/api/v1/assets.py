from fastapi import APIRouter, Query
from typing import List, Dict, Any
from backend.market_data.streamer import market_streamer
from backend.market_data.normalizer import CANONICAL_INSTRUMENT_MAP

router = APIRouter(prefix="/assets", tags=["Assets"])

@router.get("", response_model=List[Dict[str, Any]])
async def get_all_assets():
    """Return all supported canonical instruments."""
    return list(CANONICAL_INSTRUMENT_MAP.values())

@router.get("/search", response_model=List[Dict[str, Any]])
async def search_assets(q: str = Query(..., min_length=1)):
    """Search instruments dynamically across crypto, US, and Indian markets."""
    return await market_streamer.search_instruments(q)
