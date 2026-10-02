from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from datetime import datetime

from backend.market_data.streamer import market_streamer

router = APIRouter(prefix="/portfolio", tags=["Paper Trading"])

# In-Memory Paper Trading State
paper_portfolio = {
    "cash": 100000.0,
    "initial_capital": 100000.0,
    "positions": {}, # {symbol: {quantity, avg_entry_price}}
    "orders": []
}

class OrderRequest(BaseModel):
    symbol: str = Field(..., example="BTCUSDT")
    side: str = Field(..., example="BUY") # BUY, SELL
    quantity: float = Field(..., gt=0.0)

@router.get("", response_model=Dict[str, Any])
async def get_portfolio_summary():
    """Fetch live paper trading balance, open positions, and total equity."""
    total_position_val = 0.0
    positions_list = []

    for sym, pos in paper_portfolio["positions"].items():
        qty = pos["quantity"]
        if qty > 0:
            ticker = await market_streamer.get_latest_ticker(sym)
            curr_price = float(ticker.get("price", pos["avg_entry_price"]))
            pos_val = qty * curr_price
            entry_val = qty * pos["avg_entry_price"]
            unrealized_pnl = pos_val - entry_val
            unrealized_pct = (unrealized_pnl / entry_val) * 100.0 if entry_val > 0 else 0.0
            
            total_position_val += pos_val
            positions_list.append({
                "symbol": sym,
                "quantity": round(qty, 4),
                "avg_entry_price": round(pos["avg_entry_price"], 2),
                "current_price": round(curr_price, 2),
                "position_value": round(pos_val, 2),
                "unrealized_pnl": round(unrealized_pnl, 2),
                "unrealized_pnl_pct": round(unrealized_pct, 2)
            })

    total_equity = paper_portfolio["cash"] + total_position_val
    total_pnl = total_equity - paper_portfolio["initial_capital"]
    total_pnl_pct = (total_pnl / paper_portfolio["initial_capital"]) * 100.0

    return {
        "mode": "PAPER TRADING",
        "cash": round(paper_portfolio["cash"], 2),
        "total_equity": round(total_equity, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 2),
        "positions": positions_list,
        "orders": list(reversed(paper_portfolio["orders"][-20:]))
    }

@router.post("/orders", response_model=Dict[str, Any])
async def submit_paper_order(req: OrderRequest):
    """Submit a paper market order."""
    clean_sym = req.symbol.upper().strip()
    ticker = await market_streamer.get_latest_ticker(clean_sym)
    price = float(ticker.get("price", 0.0))
    if price <= 0:
        raise HTTPException(status_code=400, detail=f"Cannot execute order: no live market price for {clean_sym}")

    total_cost = req.quantity * price
    fee = total_cost * 0.0005 # 5 bps

    if req.side.upper() == "BUY":
        if paper_portfolio["cash"] < (total_cost + fee):
            raise HTTPException(status_code=400, detail="Insufficient virtual cash balance")
        
        paper_portfolio["cash"] -= (total_cost + fee)
        curr_pos = paper_portfolio["positions"].get(clean_sym, {"quantity": 0.0, "avg_entry_price": 0.0})
        old_qty = curr_pos["quantity"]
        new_qty = old_qty + req.quantity
        new_avg = ((old_qty * curr_pos["avg_entry_price"]) + total_cost) / new_qty
        
        paper_portfolio["positions"][clean_sym] = {
            "quantity": new_qty,
            "avg_entry_price": new_avg
        }
    elif req.side.upper() == "SELL":
        curr_pos = paper_portfolio["positions"].get(clean_sym, {"quantity": 0.0, "avg_entry_price": 0.0})
        if curr_pos["quantity"] < req.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient position to sell. Owned: {curr_pos['quantity']}")
        
        paper_portfolio["cash"] += (total_cost - fee)
        new_qty = curr_pos["quantity"] - req.quantity
        if new_qty <= 1e-6:
            paper_portfolio["positions"].pop(clean_sym, None)
        else:
            curr_pos["quantity"] = new_qty
            paper_portfolio["positions"][clean_sym] = curr_pos
    else:
        raise HTTPException(status_code=400, detail="Side must be BUY or SELL")

    order_record = {
        "order_id": f"ORD_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{len(paper_portfolio['orders'])+1}",
        "symbol": clean_sym,
        "side": req.side.upper(),
        "quantity": req.quantity,
        "price": price,
        "fee": round(fee, 2),
        "status": "FILLED",
        "timestamp": datetime.utcnow().isoformat()
    }
    paper_portfolio["orders"].append(order_record)
    return order_record
