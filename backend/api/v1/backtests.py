from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from backend.market_data.streamer import market_streamer
from ml.backtesting.engine import BacktestEngine
from ml.registry.registry import ModelRegistryManager
from ml.features.technical import FeatureEngine

router = APIRouter(prefix="/backtests", tags=["Backtesting"])

class BacktestRequest(BaseModel):
    symbol: str = Field("BTCUSDT", example="BTCUSDT")
    model_type: Optional[str] = Field("xgboost", example="xgboost")
    initial_capital: float = Field(100000.0, ge=100.0)
    commission_pct: float = Field(0.0005, ge=0.0)
    slippage_pct: float = Field(0.0002, ge=0.0)
    stop_loss_pct: float = Field(0.02, ge=0.001, le=0.20)
    take_profit_pct: float = Field(0.04, ge=0.001, le=0.50)
    position_size_pct: float = Field(0.20, ge=0.01, le=1.0)
    timeframe: str = Field("1h")

@router.post("", response_model=Dict[str, Any])
async def execute_backtest(req: BacktestRequest):
    """Run realistic backtest simulation comparing ML strategy vs Buy & Hold."""
    clean_sym = req.symbol.upper().replace("/", "").replace("-", "").strip()
    
    # 1. Fetch historical bars
    df_bars = await market_streamer.get_historical_bars(clean_sym, timeframe=req.timeframe, limit=500)
    if df_bars.empty or len(df_bars) < 30:
        raise HTTPException(status_code=400, detail="Insufficient historical market data for backtest")

    # 2. Check for trained model or generate strategy signals
    all_models = ModelRegistryManager.list_models()
    matching = [m for m in all_models if m["symbol"] == clean_sym]
    if req.model_type:
        matching = [m for m in matching if m["model_type"] == req.model_type.lower()]

    signals = np.zeros(len(df_bars))

    if matching:
        # Use trained model predictions for signals
        meta = matching[0]
        try:
            model_obj, preprocessor, _ = ModelRegistryManager.load_model_bundle(clean_sym, meta["model_type"], meta["version"])
            df_feat = FeatureEngine.compute_all_features(df_bars)
            feature_names = meta.get("hyperparameters", {}).get("feature_names", preprocessor.feature_names)
            
            # Predict
            clean_feat = df_feat.dropna(subset=feature_names)
            if not clean_feat.empty:
                X_scaled = preprocessor.transform(clean_feat)
                preds = model_obj.predict(X_scaled)
                # Align indices
                for row_idx, pred_val in zip(clean_feat.index, preds):
                    if pred_val > 0.0015:
                        signals[row_idx] = 1 # BUY
                    elif pred_val < -0.0015:
                        signals[row_idx] = -1 # SELL
        except Exception as e:
            print(f"[Backtest] Fallback to technical strategy due to model error: {e}")
            signals = _fallback_technical_signals(df_bars)
    else:
        # Technical momentum strategy
        signals = _fallback_technical_signals(df_bars)

    # 3. Execute backtest simulation
    engine = BacktestEngine(
        initial_capital=req.initial_capital,
        commission_rate=req.commission_pct,
        slippage_rate=req.slippage_pct,
        stop_loss_pct=req.stop_loss_pct,
        take_profit_pct=req.take_profit_pct,
        position_size_pct=req.position_size_pct
    )

    result = engine.run_backtest(df_bars, signals, symbol=clean_sym)
    return {
        "symbol": clean_sym,
        "timeframe": req.timeframe,
        "model_used": matching[0]["model_id"] if matching else "Technical Trend Strategy",
        **result
    }

def _fallback_technical_signals(df: pd.DataFrame) -> np.ndarray:
    close = df["close"]
    sma_short = close.rolling(9).mean()
    sma_long = close.rolling(21).mean()
    
    signals = np.zeros(len(df))
    for i in range(1, len(df)):
        if sma_short.iloc[i] > sma_long.iloc[i] and sma_short.iloc[i-1] <= sma_long.iloc[i-1]:
            signals[i] = 1 # Golden cross
        elif sma_short.iloc[i] < sma_long.iloc[i] and sma_short.iloc[i-1] >= sma_long.iloc[i-1]:
            signals[i] = -1 # Death cross
    return signals
