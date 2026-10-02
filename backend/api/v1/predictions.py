from fastapi import APIRouter, Query
from typing import Dict, Any, Optional
from ml.predictions.predictor import RealtimePredictor

router = APIRouter(prefix="/predictions", tags=["Predictions"])

@router.get("", response_model=Dict[str, Any])
async def get_live_prediction(
    symbol: str = Query(..., description="Symbol e.g. BTCUSDT, AAPL, RELIANCE"),
    model_type: Optional[str] = Query(None, description="Optional model type e.g. lstm, xgboost")
):
    """Generate or retrieve live prediction, quantile cones, and SHAP explanations."""
    return await RealtimePredictor.predict_latest(symbol, model_type=model_type)
