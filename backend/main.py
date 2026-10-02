"""
FastAPI Main Application Entrypoint
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.database import init_db
from backend.market_data.streamer import market_streamer

from backend.api.v1.assets import router as assets_router
from backend.api.v1.market import router as market_router
from backend.api.v1.predictions import router as predictions_router
from backend.api.v1.models import router as models_router
from backend.api.v1.training import router as training_router
from backend.api.v1.datasets import router as datasets_router
from backend.api.v1.backtests import router as backtests_router
from backend.api.v1.portfolio import router as portfolio_router
from backend.api.v1.system import router as system_router
from backend.api.v1.ir import router as ir_router
from backend.websocket.routes import ws_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[Server] Initializing database...")
    await init_db()
    print("[Server] Starting real-time market data streamers...")
    await market_streamer.start()
    yield
    # Shutdown
    print("[Server] Stopping market data streamers...")
    await market_streamer.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Institutional-Grade AI/ML/DL Stock & Crypto Market Prediction Platform",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev/terminal access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 Routers
app.include_router(assets_router, prefix=settings.API_V1_STR)
app.include_router(market_router, prefix=settings.API_V1_STR)
app.include_router(predictions_router, prefix=settings.API_V1_STR)
app.include_router(models_router, prefix=settings.API_V1_STR)
app.include_router(training_router, prefix=settings.API_V1_STR)
app.include_router(datasets_router, prefix=settings.API_V1_STR)
app.include_router(backtests_router, prefix=settings.API_V1_STR)
app.include_router(portfolio_router, prefix=settings.API_V1_STR)
app.include_router(system_router, prefix=settings.API_V1_STR)
app.include_router(ir_router, prefix=settings.API_V1_STR)

# WebSockets
app.include_router(ws_router)

@app.get("/")
async def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "RUNNING",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
