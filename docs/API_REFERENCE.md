# MarketAI — REST API & WebSocket Reference

This document outlines all backend REST endpoints and WebSocket streams available on the MarketAI platform.

Interactive Swagger UI documentation is available at `http://localhost:8000/docs` when the backend server is running.

---

## Base URLs
- **REST API Base**: `http://localhost:8000/api/v1`
- **WebSockets Base**: `ws://localhost:8000/ws`

---

## 1. Market Data Endpoints (`/api/v1/market`)

| Method | Endpoint | Description | Parameters |
|---|---|---|---|
| `GET` | `/candles` | Fetch historical OHLCV candles | `symbol` (e.g. `BTCUSDT`), `timeframe` (default `1h`), `limit` (default `200`) |
| `GET` | `/ticker` | Fetch latest real-time quote/price | `symbol` |
| `GET` | `/orderbook` | Get live L2 orderbook snapshot | `symbol`, `depth` (default `20`) |

---

## 2. Asset Catalog (`/api/v1/assets`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | List all tracked instruments across Crypto, US Equities, and Indian Equities |
| `GET` | `/{symbol}` | Get metadata for a specific instrument |

---

## 3. Real-Time Predictions (`/api/v1/predictions`)

| Method | Endpoint | Description | Parameters |
|---|---|---|---|
| `GET` | `/latest` | Compute real-time AI prediction, directional probabilities, and quantile intervals | `symbol`, `model_type` (optional) |

---

## 4. AI Model Lab & Training (`/api/v1/models` & `/api/v1/training`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/models` | List all registered models across symbols and versions |
| `GET` | `/models/{symbol}/{model_type}/{version}` | Fetch model metadata, hyperparameters, metrics, and dataset link |
| `POST` | `/training/start` | Trigger training job for an architecture (`xgboost`, `lightgbm`, `lstm`, `gru`, `cnn_lstm`, `transformer`) |
| `GET` | `/training/status/{run_id}` | Check training job progress and live epoch metrics |

---

## 5. Datasets (`/api/v1/datasets`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | List all saved training dataset matrices in `ml/datasets/records/` |
| `GET` | `/{dataset_id}` | Inspect dataset schema, chronological split dates, and feature list |

---

## 6. Backtesting Studio (`/api/v1/backtests`)

| Method | Endpoint | Description | Request Body |
|---|---|---|---|
| `POST` | `/run` | Execute realistic backtest with slippage & commission | `{ "symbol": "BTCUSDT", "model_type": "xgboost", "initial_capital": 100000, "stop_loss_pct": 0.02, "take_profit_pct": 0.04 }` |

---

## 7. Paper Trading (`/api/v1/portfolio`)

| Method | Endpoint | Description | Request Body |
|---|---|---|---|
| `GET` | `/` | Get simulated portfolio summary, open positions, and balance | — |
| `POST` | `/order` | Place simulated market/limit order | `{ "symbol": "BTCUSDT", "side": "BUY", "quantity": 0.5, "order_type": "MARKET" }` |
| `POST` | `/reset` | Reset paper trading portfolio to initial balance | — |

---

## 8. Financial Information Retrieval (`/api/v1/ir`)

| Method | Endpoint | Description | Parameters |
|---|---|---|---|
| `GET` | `/search` | Search indexed financial documents and filings | `query`, `top_k` |
| `POST` | `/crawl` | Trigger web crawler for financial filings or news | `{ "url": "https://...", "depth": 1 }` |
| `GET` | `/recommendations` | Get domain NLP sentiment analysis & trade signals | `symbol` |

---

## 9. System Health (`/api/v1/system`)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Diagnostic status of all data providers, database, and cache |

---

## 10. Real-Time WebSockets (`/ws`)

### 1. Market Stream: `ws://localhost:8000/ws/market`
- **Subscribe**: Send `{"action": "subscribe", "symbol": "BTCUSDT"}`
- **Payload**: Streams live ticker ticks, bid/ask spread, and real-time candle updates.

### 2. Training Progress: `ws://localhost:8000/ws/training`
- **Payload**: Streams epoch-by-epoch loss updates (`train_loss`, `val_loss`, `epoch`) during active neural network or tree model training.
