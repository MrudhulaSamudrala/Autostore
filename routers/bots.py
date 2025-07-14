from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.bots import Bot
from models.orders import Order
import asyncio
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/bots")
def get_bots(db: Session = Depends(get_db)):
    bots = db.query(Bot).all()
    result = []
    for bot in bots:
        # Only allow valid statuses
        valid_statuses = ["idle", "packing", "moving", "carrying", "delivering", "returning"]
        status = bot.status if bot.status in valid_statuses else "idle"
        result.append({
            "id": bot.id,
            "status": status,
            "x": bot.x,
            "y": bot.y,
            "z": bot.current_location_z,
            "assigned_order_id": bot.assigned_order_id,
            "destination_bin": bot.destination_bin,
            "path": bot.path or [],
            "full_path": json.loads(bot.full_path) if bot.full_path else []
        })
    return result

@router.websocket("/ws/bots")
async def ws_bots(websocket: WebSocket):
    await websocket.accept()
    db = SessionLocal()
    try:
        while True:
            bots = db.query(Bot).all()
            result = []
            for bot in bots:
                # Only allow valid statuses
                valid_statuses = ["idle", "packing", "moving", "carrying", "delivering", "returning"]
                status = bot.status if bot.status in valid_statuses else "idle"
                result.append({
                    "id": bot.id,
                    "status": status,
                    "x": bot.x,
                    "y": bot.y,
                    "z": bot.current_location_z,
                    "assigned_order_id": bot.assigned_order_id,
                    "destination_bin": bot.destination_bin,
                    "path": bot.path or [],
                    "full_path": json.loads(bot.full_path) if bot.full_path else []
                })
            # Send with event type for frontend compatibility
            await websocket.send_json({"event": "bots_update", "bots": result})
            await asyncio.sleep(0.5)  # SLOWER: 0.5 seconds for less frequent updates
    except WebSocketDisconnect:
        print("WebSocket /ws/bots disconnected")
    finally:
        db.close() 