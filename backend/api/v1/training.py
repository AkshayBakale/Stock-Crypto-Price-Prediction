from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime

from backend.market_data.streamer import market_streamer
from ml.training.trainer import ModelTrainer

router = APIRouter(prefix="/training", tags=["AI Training"])

# Active training jobs tracker
active_training_jobs: Dict[str, Dict[str, Any]] = {}
training_ws_subscribers: List[asyncio.Queue] = []

class TrainingRequest(BaseModel):
    symbol: str = Field(..., example="BTCUSDT")
    model_type: str = Field("xgboost", example="lstm")
    timeframe: str = Field("1h", example="1h")
    epochs: int = Field(15, ge=1, le=100)
    batch_size: int = Field(32, ge=8, le=256)
    learning_rate: float = Field(0.001, ge=0.00001, le=0.1)
    hidden_dim: int = Field(64, ge=16, le=512)
    seq_len: int = Field(20, ge=5, le=100)
    forecast_horizon: int = Field(1, ge=1, le=10)
    version: str = Field("v1.0")

async def broadcast_training_update(data: Dict[str, Any]):
    for q in list(training_ws_subscribers):
        try:
            await q.put(data)
        except Exception:
            pass

async def run_training_task(run_id: str, req: TrainingRequest):
    try:
        active_training_jobs[run_id]["status"] = "FETCHING_DATA"
        await broadcast_training_update({"run_id": run_id, "status": "FETCHING_DATA", "epoch": 0, "message": "Fetching historical market data..."})

        # 1. Fetch real historical bars
        df_bars = await market_streamer.get_historical_bars(req.symbol, timeframe=req.timeframe, limit=500)
        if df_bars.empty or len(df_bars) < 30:
            raise ValueError(f"Insufficient market data returned ({len(df_bars)} bars) for symbol {req.symbol}")

        active_training_jobs[run_id]["status"] = "TRAINING"
        
        async def on_epoch_progress(epoch_log: Dict[str, Any]):
            active_training_jobs[run_id]["current_epoch"] = epoch_log["epoch"]
            active_training_jobs[run_id]["train_loss"] = epoch_log["train_loss"]
            active_training_jobs[run_id]["val_loss"] = epoch_log["val_loss"]
            active_training_jobs[run_id]["epoch_logs"].append(epoch_log)
            await broadcast_training_update({
                "run_id": run_id,
                "status": "TRAINING",
                "symbol": req.symbol,
                "model_type": req.model_type,
                **epoch_log
            })

        trainer = ModelTrainer(
            symbol=req.symbol,
            model_type=req.model_type,
            timeframe=req.timeframe,
            epochs=req.epochs,
            batch_size=req.batch_size,
            learning_rate=req.learning_rate,
            hidden_dim=req.hidden_dim,
            seq_len=req.seq_len,
            forecast_horizon=req.forecast_horizon
        )

        result = await trainer.train(
            df_raw=df_bars,
            progress_callback=on_epoch_progress,
            version=req.version
        )

        active_training_jobs[run_id]["status"] = "COMPLETED"
        active_training_jobs[run_id]["result"] = result
        active_training_jobs[run_id]["completed_at"] = datetime.utcnow().isoformat()

        await broadcast_training_update({
            "run_id": run_id,
            "status": "COMPLETED",
            "symbol": req.symbol,
            "model_type": req.model_type,
            "result": result
        })
    except Exception as e:
        active_training_jobs[run_id]["status"] = "FAILED"
        active_training_jobs[run_id]["error"] = str(e)
        active_training_jobs[run_id]["completed_at"] = datetime.utcnow().isoformat()
        await broadcast_training_update({
            "run_id": run_id,
            "status": "FAILED",
            "error": str(e)
        })

@router.post("", response_model=Dict[str, Any])
async def trigger_training(req: TrainingRequest, bg: BackgroundTasks):
    """Start model training on real market data in the background."""
    clean_sym = req.symbol.upper().replace("/", "").replace("-", "").strip()
    run_id = f"RUN_{clean_sym}_{req.model_type.upper()}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    active_training_jobs[run_id] = {
        "run_id": run_id,
        "symbol": clean_sym,
        "model_type": req.model_type,
        "timeframe": req.timeframe,
        "status": "QUEUED",
        "current_epoch": 0,
        "total_epochs": req.epochs,
        "train_loss": 0.0,
        "val_loss": 0.0,
        "epoch_logs": [],
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "error": None
    }

    bg.add_task(run_training_task, run_id, req)
    return {
        "run_id": run_id,
        "status": "QUEUED",
        "message": f"Training started for {clean_sym} ({req.model_type})"
    }

@router.get("/runs", response_model=List[Dict[str, Any]])
async def list_training_runs():
    """List all recent training runs and their real metrics."""
    return list(reversed(list(active_training_jobs.values())))

@router.get("/runs/{run_id}")
async def get_training_run(run_id: str):
    if run_id not in active_training_jobs:
        raise HTTPException(status_code=404, detail="Training run not found")
    return active_training_jobs[run_id]
