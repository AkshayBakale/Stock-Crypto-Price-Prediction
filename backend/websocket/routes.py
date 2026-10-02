"""
WebSocket Endpoints
- /ws/market: Real-time high frequency ticker broadcast
- /ws/training: Real-time model training progress and epoch curves
- /ws/system: Real-time latency and health heartbeat
"""

import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.market_data.streamer import market_streamer
from backend.api.v1.training import training_ws_subscribers

ws_router = APIRouter(tags=["WebSockets"])

@ws_router.websocket("/ws/market")
async def websocket_market_stream(websocket: WebSocket):
    await websocket.accept()
    queue = market_streamer.subscribe_ticks()
    try:
        # Send initial snapshot of all latest ticks
        for sym, tick in list(market_streamer._latest_ticks.items()):
            await websocket.send_text(json.dumps({"type": "TICK", "data": tick}))

        while True:
            # Wait for next tick from streamer queue
            tick_data = await queue.get()
            await websocket.send_text(json.dumps({"type": "TICK", "data": tick_data}))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WebSocketMarket] Client error: {e}")
    finally:
        market_streamer.unsubscribe_ticks(queue)

@ws_router.websocket("/ws/training")
async def websocket_training_stream(websocket: WebSocket):
    await websocket.accept()
    queue = asyncio.Queue()
    training_ws_subscribers.append(queue)
    try:
        while True:
            progress_data = await queue.get()
            await websocket.send_text(json.dumps({"type": "TRAINING_UPDATE", "data": progress_data}))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[WebSocketTraining] Client error: {e}")
    finally:
        if queue in training_ws_subscribers:
            training_ws_subscribers.remove(queue)
