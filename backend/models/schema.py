from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean, Text, JSON, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Instrument(Base):
    __tablename__ = "instruments"
    
    canonical_id = Column(String(64), primary_key=True, index=True) # e.g. CRYPTO_BTCUSDT, US_EQ_AAPL, IN_EQ_RELIANCE
    symbol = Column(String(32), index=True, nullable=False) # BTCUSDT, AAPL, RELIANCE
    name = Column(String(128), nullable=False)
    market = Column(String(32), nullable=False, index=True) # crypto, us_equity, in_equity, index
    exchange = Column(String(32), nullable=False) # BINANCE, NASDAQ, NSE, NYSE
    currency = Column(String(16), default="USD")
    timezone = Column(String(32), default="UTC")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Candle(Base):
    __tablename__ = "candles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    canonical_id = Column(String(64), ForeignKey("instruments.canonical_id"), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    timeframe = Column(String(16), default="1h", index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, default=0.0)
    provider = Column(String(32), default="binance")

    __table_args__ = (
        Index("idx_candle_lookup", "canonical_id", "timeframe", "timestamp", unique=True),
    )

class Tick(Base):
    __tablename__ = "ticks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    canonical_id = Column(String(64), ForeignKey("instruments.canonical_id"), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    price = Column(Float, nullable=False)
    volume = Column(Float, default=0.0)
    provider = Column(String(32), default="live")

class DatasetRecord(Base):
    __tablename__ = "dataset_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(String(64), unique=True, index=True, nullable=False)
    symbol = Column(String(32), index=True, nullable=False)
    canonical_id = Column(String(64), nullable=False)
    timeframe = Column(String(16), nullable=False)
    date_range_start = Column(DateTime, nullable=False)
    date_range_end = Column(DateTime, nullable=False)
    row_count = Column(Integer, default=0)
    feature_count = Column(Integer, default=0)
    feature_names = Column(JSON, default=list)
    target_column = Column(String(64), default="target_return_1d")
    folder_path = Column(String(256), nullable=False) # e.g. ml/datasets/records/DATASET_BTCUSDT_1h_20260907_120000
    created_at = Column(DateTime, default=datetime.utcnow)

class ModelRegistry(Base):
    __tablename__ = "model_registry"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(String(64), unique=True, index=True, nullable=False) # e.g. MODEL_BTCUSDT_XGB_v1
    name = Column(String(128), nullable=False)
    symbol = Column(String(32), index=True, nullable=False)
    canonical_id = Column(String(64), nullable=False)
    model_type = Column(String(32), nullable=False) # baseline, xgboost, lightgbm, lstm, gru, cnn_lstm, transformer, ensemble
    version = Column(String(32), default="v1.0")
    status = Column(String(32), default="DEVELOPMENT") # DEVELOPMENT, STAGING, PRODUCTION, ARCHIVED
    hyperparameters = Column(JSON, default=dict)
    metrics = Column(JSON, default=dict) # MAE, RMSE, R2, Accuracy, F1, Sharpe, WinRate
    folder_path = Column(String(256), nullable=False) # models/BTCUSDT/xgboost/v1.0/
    dataset_id = Column(String(64), nullable=True) # Linked dataset record folder
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TrainingRun(Base):
    __tablename__ = "training_runs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(64), unique=True, index=True, nullable=False)
    symbol = Column(String(32), nullable=False)
    canonical_id = Column(String(64), nullable=False)
    model_type = Column(String(32), nullable=False)
    status = Column(String(32), default="RUNNING") # RUNNING, COMPLETED, FAILED
    current_epoch = Column(Integer, default=0)
    total_epochs = Column(Integer, default=10)
    train_loss = Column(Float, default=0.0)
    val_loss = Column(Float, default=0.0)
    best_epoch = Column(Integer, default=0)
    epoch_logs = Column(JSON, default=list) # List of {epoch, train_loss, val_loss, timestamp}
    metrics = Column(JSON, default=dict)
    dataset_id = Column(String(64), nullable=True)
    folder_path = Column(String(256), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class BacktestRecord(Base):
    __tablename__ = "backtest_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    backtest_id = Column(String(64), unique=True, index=True, nullable=False)
    symbol = Column(String(32), index=True, nullable=False)
    canonical_id = Column(String(64), nullable=False)
    model_id = Column(String(64), nullable=False)
    timeframe = Column(String(16), default="1h")
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, default=100000.0)
    final_equity = Column(Float, default=100000.0)
    total_return_pct = Column(Float, default=0.0)
    benchmark_return_pct = Column(Float, default=0.0) # Buy & Hold return
    sharpe_ratio = Column(Float, default=0.0)
    sortino_ratio = Column(Float, default=0.0)
    max_drawdown_pct = Column(Float, default=0.0)
    win_rate_pct = Column(Float, default=0.0)
    profit_factor = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    trades_log = Column(JSON, default=list)
    equity_curve = Column(JSON, default=list)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

class PredictionRecord(Base):
    __tablename__ = "prediction_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(32), index=True, nullable=False)
    canonical_id = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    model_id = Column(String(64), nullable=False)
    model_version = Column(String(32), default="v1.0")
    current_price = Column(Float, nullable=False)
    predicted_price = Column(Float, nullable=False)
    expected_return_pct = Column(Float, default=0.0)
    direction = Column(String(16), default="SIDEWAYS") # UP, DOWN, SIDEWAYS
    confidence = Column(Float, default=0.0)
    calibrated_probability = Column(Float, default=0.0)
    quantiles = Column(JSON, default=dict) # {p10, p25, p50, p75, p90}
    shap_values = Column(JSON, default=dict)
    market_regime = Column(String(32), default="NORMAL") # BULL, BEAR, HIGH_VOLATILITY, LOW_VOLATILITY, SIDEWAYS
    risk_metrics = Column(JSON, default=dict) # VaR_95, VaR_99, Expected_Shortfall, Volatility
    status = Column(String(32), default="VALID") # VALID, STALE, DATA_ERROR

class PaperOrder(Base):
    __tablename__ = "paper_orders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(64), unique=True, index=True, nullable=False)
    symbol = Column(String(32), index=True, nullable=False)
    side = Column(String(8), nullable=False) # BUY, SELL
    order_type = Column(String(16), default="MARKET")
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String(16), default="FILLED")
    filled_price = Column(Float, nullable=False)
    fee = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class PaperPosition(Base):
    __tablename__ = "paper_positions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(32), unique=True, index=True, nullable=False)
    quantity = Column(Float, default=0.0)
    avg_entry_price = Column(Float, default=0.0)
    current_price = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow)

class SystemEvent(Base):
    __tablename__ = "system_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String(64), index=True, nullable=False)
    component = Column(String(64), nullable=False)
    level = Column(String(16), default="INFO")
    message = Column(Text, nullable=False)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)
