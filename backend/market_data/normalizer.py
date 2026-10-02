"""
Canonical Instrument Normalizer
Normalizes symbols, markets, exchanges, currencies, and timeframes across diverse data sources.
"""

from typing import Dict, Any, Optional

CANONICAL_INSTRUMENT_MAP: Dict[str, Dict[str, Any]] = {
    # Crypto
    "BTCUSDT": {
        "canonical_id": "CRYPTO_BTCUSDT",
        "symbol": "BTCUSDT",
        "name": "Bitcoin / Tether",
        "market": "crypto",
        "exchange": "BINANCE",
        "currency": "USDT",
        "timezone": "UTC",
        "provider": "binance",
        "price_decimals": 2,
    },
    "ETHUSDT": {
        "canonical_id": "CRYPTO_ETHUSDT",
        "symbol": "ETHUSDT",
        "name": "Ethereum / Tether",
        "market": "crypto",
        "exchange": "BINANCE",
        "currency": "USDT",
        "timezone": "UTC",
        "provider": "binance",
        "price_decimals": 2,
    },
    "SOLUSDT": {
        "canonical_id": "CRYPTO_SOLUSDT",
        "symbol": "SOLUSDT",
        "name": "Solana / Tether",
        "market": "crypto",
        "exchange": "BINANCE",
        "currency": "USDT",
        "timezone": "UTC",
        "provider": "binance",
        "price_decimals": 2,
    },
    # US Equities
    "AAPL": {
        "canonical_id": "US_EQ_AAPL",
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "market": "us_equity",
        "exchange": "NASDAQ",
        "currency": "USD",
        "timezone": "America/New_York",
        "provider": "yfinance",
        "price_decimals": 2,
    },
    "NVDA": {
        "canonical_id": "US_EQ_NVDA",
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "market": "us_equity",
        "exchange": "NASDAQ",
        "currency": "USD",
        "timezone": "America/New_York",
        "provider": "yfinance",
        "price_decimals": 2,
    },
    "MSFT": {
        "canonical_id": "US_EQ_MSFT",
        "symbol": "MSFT",
        "name": "Microsoft Corporation",
        "market": "us_equity",
        "exchange": "NASDAQ",
        "currency": "USD",
        "timezone": "America/New_York",
        "provider": "yfinance",
        "price_decimals": 2,
    },
    # Indices
    "NAS100": {
        "canonical_id": "INDEX_NAS100",
        "symbol": "NAS100",
        "name": "Nasdaq 100 Index (QQQ)",
        "market": "index",
        "exchange": "NASDAQ",
        "currency": "USD",
        "timezone": "America/New_York",
        "provider": "yfinance",
        "price_decimals": 2,
    },
    "US30": {
        "canonical_id": "INDEX_US30",
        "symbol": "US30",
        "name": "Dow Jones Industrial Average (DIA)",
        "market": "index",
        "exchange": "DJI",
        "currency": "USD",
        "timezone": "America/New_York",
        "provider": "yfinance",
        "price_decimals": 2,
    },
    # Indian Equities
    "RELIANCE": {
        "canonical_id": "IN_EQ_RELIANCE",
        "symbol": "RELIANCE",
        "name": "Reliance Industries Limited",
        "market": "in_equity",
        "exchange": "NSE",
        "currency": "INR",
        "timezone": "Asia/Kolkata",
        "provider": "yfinance",
        "price_decimals": 2,
    },
    "TCS": {
        "canonical_id": "IN_EQ_TCS",
        "symbol": "TCS",
        "name": "Tata Consultancy Services Ltd",
        "market": "in_equity",
        "exchange": "NSE",
        "currency": "INR",
        "timezone": "Asia/Kolkata",
        "provider": "yfinance",
        "price_decimals": 2,
    },
    "NIFTY50": {
        "canonical_id": "INDEX_NIFTY50",
        "symbol": "NIFTY50",
        "name": "Nifty 50 Index (^NSEI)",
        "market": "index",
        "exchange": "NSE",
        "currency": "INR",
        "timezone": "Asia/Kolkata",
        "provider": "yfinance",
        "price_decimals": 2,
    },
}

def get_canonical_instrument(raw_symbol: str) -> Dict[str, Any]:
    cleaned = raw_symbol.upper().replace("/", "").replace("-", "").replace(".", "").strip()
    
    # Check if exact match exists
    if cleaned in CANONICAL_INSTRUMENT_MAP:
        return CANONICAL_INSTRUMENT_MAP[cleaned]
    
    # Try with raw_symbol uppercase
    if raw_symbol.upper() in CANONICAL_INSTRUMENT_MAP:
        return CANONICAL_INSTRUMENT_MAP[raw_symbol.upper()]
    
    # Dynamic instrument creation
    if cleaned.endswith("USDT") or cleaned.endswith("BTC") or cleaned.endswith("USD") and len(cleaned) <= 8:
        return {
            "canonical_id": f"CRYPTO_{cleaned}",
            "symbol": cleaned,
            "name": f"{cleaned} Crypto Asset",
            "market": "crypto",
            "exchange": "BINANCE",
            "currency": "USDT" if cleaned.endswith("USDT") else "USD",
            "timezone": "UTC",
            "provider": "binance",
            "price_decimals": 4 if "SHIB" in cleaned or "DOGE" in cleaned else 2,
        }
    elif cleaned.endswith(".NS") or cleaned.endswith(".BO"):
        base_sym = cleaned.replace(".NS", "").replace(".BO", "")
        return {
            "canonical_id": f"IN_EQ_{base_sym}",
            "symbol": base_sym,
            "name": f"{base_sym} Indian Equity",
            "market": "in_equity",
            "exchange": "NSE",
            "currency": "INR",
            "timezone": "Asia/Kolkata",
            "provider": "yfinance",
            "price_decimals": 2,
        }
    else:
        return {
            "canonical_id": f"US_EQ_{cleaned}",
            "symbol": cleaned,
            "name": f"{cleaned} Equity",
            "market": "us_equity",
            "exchange": "NASDAQ",
            "currency": "USD",
            "timezone": "America/New_York",
            "provider": "yfinance",
            "price_decimals": 2,
        }

def get_provider_symbol(canonical_id: str) -> str:
    parts = canonical_id.split("_")
    if canonical_id.startswith("CRYPTO_"):
        return canonical_id.replace("CRYPTO_", "")
    elif canonical_id.startswith("IN_EQ_"):
        sym = canonical_id.replace("IN_EQ_", "")
        return f"{sym}.NS"
    elif canonical_id == "INDEX_NIFTY50":
        return "^NSEI"
    elif canonical_id == "INDEX_NAS100":
        return "QQQ"
    elif canonical_id == "INDEX_US30":
        return "DIA"
    elif canonical_id.startswith("US_EQ_"):
        return canonical_id.replace("US_EQ_", "")
    return canonical_id
