from fastapi import APIRouter, WebSocket, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.bots import Bot
from models.orders import Order
import asyncio

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
        result.append({
            "id": bot.id,
            "status": bot.status,
            "x": bot.x,
            "y": bot.y,
            "z": bot.current_location_z,
            "assigned_order_id": bot.assigned_order_id,
            "destination_bin": bot.destination_bin,
            "path": bot.path or []
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
                result.append({
                    "id": bot.id,
                    "status": bot.status,
                    "x": bot.x,
                    "y": bot.y,
                    "z": bot.current_location_z,
                    "assigned_order_id": bot.assigned_order_id,
                    "destination_bin": bot.destination_bin,
                    "path": bot.path or []
                })
            await websocket.send_json(result)
            await asyncio.sleep(0.5)
    finally:
        db.close() 