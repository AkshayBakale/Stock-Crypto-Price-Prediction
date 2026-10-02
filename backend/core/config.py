import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "MarketAI - Quantitative Market Prediction Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "change-this-in-production-to-a-secure-random-key-antigravity-ai"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./market_ai.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_REDIS: bool = False
    
    CRYPTO_ENABLED: bool = True
    CRYPTO_EXCHANGE: str = "binance"
    US_MARKET_API_KEY: str = ""
    FINNHUB_API_KEY: str = ""
    ALPHA_VANTAGE_API_KEY: str = ""
    INDIA_MARKET_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    
    DATASET_STORAGE_DIR: str = os.path.abspath("ml/datasets/records")
    MODEL_STORAGE_DIR: str = os.path.abspath("models")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.DATASET_STORAGE_DIR, exist_ok=True)
os.makedirs(settings.MODEL_STORAGE_DIR, exist_ok=True)
