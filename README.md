# MarketAI — Institutional-Grade AI/ML/DL Quantitative Market Prediction Platform

A quantitative market research, machine learning forecasting, financial information retrieval, and real-time algorithmic execution platform designed for Cryptocurrencies, US Equities & Indices, and Indian Equities.

---

## 📌 Overview

**MarketAI** bridges the gap between institutional-grade quantitative finance and modern deep learning. It provides an end-to-end framework for streaming real-time tick and candle data, engineering leak-free predictive alpha features, training tree-based and deep neural sequence models, explaining decisions with SHAP attributions, executing realistic backtests with transaction costs and slippage, and performing real-time paper trading through a responsive terminal dashboard.

### Target Audience & Use Cases
- **Quantitative Researchers & Algorithmic Traders**: Develop, evaluate, and backtest statistical and deep learning market prediction strategies.
- **Financial Analysts & Portfolio Managers**: Inspect live multi-horizon forecasts, confidence intervals, risk metrics (VaR, Expected Shortfall), and NLP-driven market sentiment.
- **Developers & Data Scientists**: Explore clean, modular architecture with decoupled data providers, reproducible dataset record storage, and model registries.

---

## 🚀 Key Features

- **🌐 Real-Time Multi-Asset Data Ingestion**:
  - **Crypto**: Zero-key public WebSockets and REST feeds via Binance (e.g., `BTCUSDT`, `ETHUSDT`, `SOLUSDT`).
  - **US Equities & Indices**: Live quote streaming and historical data for `AAPL`, `NVDA`, `NAS100`, `US30` via Yahoo Finance, Finnhub, and Alpha Vantage.
  - **Indian Equities**: Live NSE / Indian market feed support (`RELIANCE`, `TCS`, `NIFTY50`).
  - **Canonical Normalization**: Standardized schema across all asset classes with timestamp alignment and automated gap/anomaly validation.

- **🔬 Leak-Free Feature Engineering Engine**:
  - Over 30 technical and statistical indicators: RSI, MACD, Bollinger Bands, ATR, Stochastic Oscillator, OBV, VWAP, ADX, Hurst Exponent, realized volatility, and rolling returns.
  - Strict chronological isolation: Feature scalers (StandardScaler, RobustScaler, MinMaxScaler) are fitted *strictly* on training splits to prevent lookahead data leakage.

- **🧠 Multi-Architecture AI/ML/DL Suite**:
  - **Classical Baselines**: Naive Drift, Moving Average, Momentum, Linear Regression.
  - **Gradient Boosted Trees**: XGBoost, LightGBM, Random Forest with multi-target support.
  - **Deep Neural Networks (PyTorch)**: LSTM, GRU, CNN-LSTM hybrid, and Time-Series Transformer models.
  - **Multi-Task Heads**: Simultaneous forecasting of expected return, 3-class directional probability (UP / SIDEWAYS / DOWN), and quantile confidence bands (10th, 25th, 50th, 75th, 90th percentiles).
  - **Explainability**: Integrated SHAP (SHapley Additive exPlanations) for transparent feature attribution.

- **📊 Realistic Quantitative Backtesting Studio**:
  - Simulates fill execution with configurable commission rates, bid-ask slippage, stop-loss, and take-profit parameters.
  - Generates comprehensive risk and performance metrics: Sharpe Ratio, Sortino Ratio, Maximum Drawdown, Win Rate, Profit Factor, and Buy & Hold benchmark comparisons.

- **📑 Financial Information Retrieval (IR) & NLP Intelligence**:
  - Automated crawling, structured content extraction, and financial document indexing.
  - Custom financial language model with domain tokenization, term-weighting scoring, and semantic trade recommendations.

- **📈 Institutional Trading Terminal UI**:
  - Interactive candlestick charts with TradingView Lightweight Charts.
  - Live order book depth, quantile forecasting cones, real-time training progress monitoring via WebSockets, and interactive paper trading simulator.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, TradingView Lightweight Charts |
| **Backend** | Python 3.13 / 3.11, FastAPI, Pydantic v2, SQLAlchemy (Async), Uvicorn, WebSockets, aiohttp |
| **Machine Learning** | PyTorch, Scikit-learn, XGBoost, LightGBM, SHAP, Joblib, NumPy, Pandas, SciPy |
| **Database & Cache** | PostgreSQL / Async SQLite (`aiosqlite`), Redis (with async in-memory fallback) |
| **DevOps & Containers** | Docker, Docker Compose, Nginx |

---

## 📁 Project Structure

```text
Stock and Crypto predication/
├── backend/                        # FastAPI modular backend application
│   ├── api/v1/                     # REST API v1 route controllers
│   │   ├── assets.py               # Asset catalog & instrument metadata
│   │   ├── backtests.py            # Backtest execution & results
│   │   ├── datasets.py             # Dataset record management
│   │   ├── ir.py                   # Financial IR & document crawling
│   │   ├── market.py               # Live & historical market data
│   │   ├── models.py               # Model registry endpoints
│   │   ├── portfolio.py            # Paper trading & portfolio simulation
│   │   ├── predictions.py          # Real-time multi-horizon AI inference
│   │   ├── system.py               # System health & data provider status
│   │   └── training.py             # Model training job orchestration
│   ├── core/                       # Core configuration & async database setup
│   │   ├── config.py               # Pydantic environment settings
│   │   └── database.py             # SQLAlchemy async engine & session maker
│   ├── ir/                         # Information Retrieval & Financial NLP
│   │   ├── crawler.py              # Financial web & filings crawler
│   │   ├── extractor.py            # Content extraction & cleaning
│   │   ├── language_model.py       # Domain tokenizer & scoring engine
│   │   └── recommender.py          # Semantic trade recommendation engine
│   ├── market_data/                # Market data providers & normalizers
│   │   ├── base.py                 # Abstract market provider interface
│   │   ├── crypto.py               # Binance WebSocket & REST provider
│   │   ├── indian_stocks.py        # NSE / Indian market provider
│   │   ├── normalizer.py           # Canonical schema normalizer
│   │   ├── streamer.py             # Async real-time hub & broadcaster
│   │   ├── us_stocks.py            # US equities provider (Yahoo/Finnhub)
│   │   └── validator.py            # Data quality & anomaly validator
│   ├── models/                     # SQLAlchemy ORM database models
│   │   └── schema.py               # DB schema (instruments, candles, ticks, orders)
│   ├── websocket/                  # Real-time WebSocket handlers
│   │   └── routes.py               # Live market & training progress WebSockets
│   └── main.py                     # FastAPI application entrypoint & lifespan
│
├── frontend/                       # React 19 + TypeScript + Vite SPA
│   ├── public/                     # Static public assets
│   ├── src/
│   │   ├── components/             # Reusable UI & terminal modules
│   │   │   ├── BacktestStudio.tsx  # Backtesting configuration & equity charts
│   │   │   ├── DatasetsViewer.tsx  # Saved dataset browser & feature schema
│   │   │   ├── Header.tsx          # Navigation, asset selector & market ticker
│   │   │   ├── IRIntelligence.tsx  # Financial search, crawling & recommendations
│   │   │   ├── ModelLab.tsx        # Model training console & metrics viewer
│   │   │   ├── PaperTrading.tsx    # Order execution & paper portfolio monitor
│   │   │   ├── PredictionPanel.tsx # Live AI forecast, quantiles & SHAP attribution
│   │   │   ├── SystemHealthModal.tsx# Health diagnostic modal
│   │   │   └── TradingChart.tsx    # TradingView Lightweight interactive charts
│   │   ├── services/               # REST & WebSocket API clients
│   │   ├── types/                  # TypeScript interface definitions
│   │   ├── App.tsx                 # Main application layout
│   │   └── main.tsx                # React root bootstrap
│   ├── Dockerfile.frontend         # Multi-stage production container build
│   ├── nginx.conf                  # Nginx reverse proxy configuration
│   ├── package.json                # Frontend dependencies & npm scripts
│   └── vite.config.ts              # Vite bundler configuration
│
├── ml/                             # Quantitative Machine Learning engine
│   ├── backtesting/                # Realistic simulation & execution engine
│   │   └── engine.py               # BacktestEngine with slippage & risk metrics
│   ├── datasets/                   # Dataset generation & isolated disk storage
│   │   ├── generator.py            # Chronological splitting & target construction
│   │   ├── records/                # Dedicated folder storage for dataset matrices
│   │   └── storage.py              # Parquet/CSV matrix & metadata serializer
│   ├── evaluation/                 # Statistical & out-of-sample metrics
│   │   └── metrics.py              # MAE, RMSE, Directional Accuracy, Sharpe
│   ├── features/                   # Leak-free technical indicator feature engine
│   │   ├── market_features.py      # Volatility, momentum & trend indicators
│   │   └── technical.py            # Multi-timeframe indicator computations
│   ├── models/                     # Model architectures
│   │   ├── baseline.py             # Naive & statistical baselines
│   │   ├── pytorch_models.py       # LSTM, GRU, CNN-LSTM, Transformer (PyTorch)
│   │   └── tree_models.py          # XGBoost, LightGBM, Random Forest & SHAP
│   ├── predictions/                # Live inference & quantile cone generation
│   │   └── predictor.py            # RealtimePredictor multi-model inference
│   ├── preprocessing/              # Scalers & transformation pipelines
│   │   └── scaler.py               # DataPreprocessor with fit/transform separation
│   ├── registry/                   # Model registry & versioned artifact manager
│   │   └── registry.py             # ModelRegistryManager (weights, scalers, metadata)
│   ├── risk/                       # Risk management engine
│   │   └── engine.py               # Value at Risk (VaR), Expected Shortfall (CVaR)
│   └── training/                   # Model training orchestrator
│       └── trainer.py              # ModelTrainer with async epoch callbacks
│
├── docs/                           # Comprehensive documentation & architecture specs
│   ├── API_REFERENCE.md            # REST API endpoints & WebSocket specifications
│   └── ARCHITECTURE_AND_PLAN.md    # Detailed system architecture & design specification
├── models/                         # Isolated model artifact storage by symbol/type
│   └── <symbol>/<model_type>/<v>/  # model.pt/joblib, scaler.joblib, metadata.json
├── scripts/                        # Automation & batch utilities
│   └── train_all_assets.py         # Batch trainer for asset universe
├── tests/                          # Automated test suite (pytest)
│   ├── test_backtest.py            # Backtesting engine tests
│   ├── test_data_validation.py     # Market data quality & anomaly tests
│   ├── test_features.py            # Feature engineering tests
│   ├── test_ir.py                  # Financial IR & tokenizer tests
│   ├── test_leakage_prevention.py  # Chronological split & leakage tests
│   └── test_models.py              # Model architecture tests
│
├── .env.example                    # Environment variable template
├── .gitignore                      # Git exclusion rules
├── backtest.py                     # CLI backtesting utility
├── evaluate.py                     # CLI model evaluation utility
├── predict.py                      # CLI live prediction utility
├── train.py                        # CLI model training utility
├── requirements.txt                # Python backend dependencies
├── docker-compose.yml              # Multi-container orchestration
├── Dockerfile.backend              # Backend Dockerfile
├── LICENSE                         # MIT License
└── README.md                       # Repository documentation
```

---

## 📦 Model & Dataset Storage Protocol

Training datasets and model artifacts are stored in isolated, reproducible directories:

1. **Datasets Folder**: `ml/datasets/records/<dataset_id>/`
   - `dataset.parquet`: High-performance columnar dataset matrix.
   - `dataset.csv`: Raw comma-separated values.
   - `metadata.json`: Chronological train/val/test split indices, timestamps, row counts.
   - `features.json`: Feature column names and metadata.

2. **Models Folder**: `models/<symbol>/<model_type>/<version>/`
   - `model.pt` (PyTorch) or `model.joblib` (Tree models).
   - `scaler.joblib`: Preprocessing scaler fitted strictly on train split.
   - `features.json`: Feature schema required for inference.
   - `metrics.json`: Out-of-sample evaluation metrics (MAE, RMSE, Directional Accuracy, Sharpe Ratio).
   - `dataset_link.json`: Pointer to the exact dataset directory used for training.
   - `metadata.json`: Hyperparameters, model architecture, and versioning info.

---

## ⚙️ Installation & Setup

### Prerequisites
- **Python**: Version 3.10+ (tested on Python 3.13)
- **Node.js**: Version 20+ & **npm** Version 10+
- **Git**

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/AkshayBakale/Stock-Crypto-Price-Prediction.git
cd "Stock and Crypto predication"
```

---

### Step 2: Configure Environment Variables
Copy the `.env.example` template to `.env`:

```bash
# On Linux / macOS / Git Bash
cp .env.example .env

# On Windows PowerShell
Copy-Item .env.example .env
```

*(Crypto data feeds connect out of the box via Binance public WebSockets without requiring any API keys).*

---

### Step 3: Install Backend Dependencies
```bash
# Install Python packages globally or in your active environment
pip install -r requirements.txt
```

---

### Step 4: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 🚦 How to Run

### Option A: Local Development (Recommended)

#### Terminal 1 — Start the FastAPI Backend:
```bash
# From the project root directory:
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- **Backend REST API**: [http://localhost:8000](http://localhost:8000)
- **Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Market Data WebSocket**: `ws://localhost:8000/ws/market`
- **Training Progress WebSocket**: `ws://localhost:8000/ws/training`

#### Terminal 2 — Start the React Frontend:
```bash
cd frontend
npm run dev
```
- **Trading Terminal**: [http://localhost:5173](http://localhost:5173)

---

### Option B: Docker Compose (Full Container Stack)

To run the complete platform (Backend, Frontend, PostgreSQL, Redis) in isolated containers:

```bash
docker compose up --build
```
- Frontend UI: [http://localhost:5173](http://localhost:5173)
- Backend API: [http://localhost:8000](http://localhost:8000)

To shut down the containers:
```bash
docker compose down
```

---

## 💻 CLI Commands

The platform provides command-line utilities for training, inference, backtesting, and evaluation:

### 1. Model Training
```bash
# Train XGBoost on BTCUSDT 1-hour candles
python train.py --symbol BTCUSDT --model xgboost --timeframe 1h

# Train PyTorch LSTM Neural Network for 15 epochs
python train.py --symbol BTCUSDT --model lstm --timeframe 1h --epochs 15

# Train Time-Series Transformer on AAPL stock
python train.py --symbol AAPL --model transformer --timeframe 1h --epochs 20

# Train LightGBM on Reliance Industries
python train.py --symbol RELIANCE --model lightgbm --timeframe 15m
```

### 2. Real-Time Inference
```bash
# Generate real-time forecast and quantile confidence cones
python predict.py --symbol BTCUSDT
python predict.py --symbol AAPL
```

### 3. Quantitative Backtesting
```bash
# Run backtest with $100,000 initial capital
python backtest.py --symbol BTCUSDT --model xgboost --capital 100000

# Run backtest with custom stop-loss and take-profit
python backtest.py --symbol AAPL --model naive --capital 50000 --stop_loss 0.02 --take_profit 0.05
```

### 4. Model Evaluation
```bash
# Inspect out-of-sample metrics for a registered model
python evaluate.py --symbol BTCUSDT --model xgboost
```

---

## 🧪 Automated Testing

The project includes unit and integration tests covering data validation, feature computation, leakage prevention, backtesting, and model architectures.

Run the test suite with `pytest`:

```bash
# Run all tests
python -m pytest tests/

# Run tests with verbose output
python -m pytest tests/ -v
```

---

## 🔑 Environment Variables Reference

| Variable | Default Value | Description |
|---|---|---|
| `ENV` | `development` | Application environment (`development`, `production`) |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `SECRET_KEY` | `change-this-...` | Secret key for session security and token signing |
| `DATABASE_URL` | `sqlite+aiosqlite:///./market_ai.db` | SQLAlchemy async connection string (SQLite or PostgreSQL) |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis cache connection string |
| `USE_REDIS` | `false` | Enable Redis for real-time pub/sub caching |
| `CRYPTO_ENABLED` | `true` | Enable real-time cryptocurrency data streaming |
| `CRYPTO_EXCHANGE` | `binance` | Primary crypto data provider |
| `US_MARKET_API_KEY` | `""` | Optional API key for US equity data providers |
| `FINNHUB_API_KEY` | `""` | Optional Finnhub API key |
| `ALPHA_VANTAGE_API_KEY` | `""` | Optional Alpha Vantage API key |
| `INDIA_MARKET_API_KEY` | `""` | Optional Indian market API key |
| `NEWS_API_KEY` | `""` | Optional financial news API key |
| `HOST` | `0.0.0.0` | Backend server host bind address |
| `PORT` | `8000` | Backend server port |
| `FRONTEND_PORT` | `5173` | Frontend Vite development server port |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed CORS origins for browser security |

---

## 👥 Team Members

- **Atharva Raut**
- **Akshay Bakale**
- **Piyush Yadav**
- **Ritesh Patil**

---

## 🔮 Future Improvements & Roadmap

- [ ] **Multi-Asset Portfolio Optimization**: Mean-variance, Black-Litterman, and Hierarchical Risk Parity (HRP) portfolio rebalancing.
- [ ] **Reinforcement Learning Agents**: Deep Q-Learning (DQN) and PPO policy agents for dynamic order execution.
- [ ] **Live Broker Integrations**: Pluggable connectors for Interactive Brokers, Zerodha Kite, and Binance Futures.
- [ ] **On-Chain Crypto Analytics**: Whale wallet monitoring, mempool transactions, and funding rate anomalies.

---

## 📄 License & Disclaimer

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

> **Disclaimer**: *This software is built for research, educational, and simulation purposes only. Quantitative predictions and backtest results do not constitute financial advice. Always perform independent due diligence before trading live capital.*
