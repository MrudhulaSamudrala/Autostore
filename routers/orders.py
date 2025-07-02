from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.orders import Order
from models.products import Product
from models.bots import Bot
from models.bins import Bin
from models.bin_locks import BinLock
from datetime import datetime
from utils.astar import astar, manhattan

router = APIRouter(prefix="/orders", tags=["orders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

@router.post("/")
def create_order(customer_name: str, product_id: int, db: Session = Depends(get_db)):
    # 1. Find the product and its bin
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    bin_ = db.query(Bin).filter(Bin.bin_id == product.bin_id).first()
    if not bin_:
        raise HTTPException(status_code=404, detail="Bin not found")

    # 2. Find all idle bots
    idle_bots = db.query(Bot).filter(Bot.status == "idle").all()
    if not idle_bots:
        raise HTTPException(status_code=400, detail="No idle bots available")

    # 3. Find nearest bot using A*
    def neighbors_fn(pos):
        x, y = pos
        return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    min_path = None
    min_bot = None
    min_len = float('inf')
    bin_pos = (bin_.location_x, bin_.location_y)
    for bot in idle_bots:
        bot_pos = (bot.current_location_x, bot.current_location_y)
        path = astar(bot_pos, bin_pos, neighbors_fn, manhattan)
        if path and len(path) < min_len:
            min_len = len(path)
            min_path = path
            min_bot = bot
    if not min_bot:
        raise HTTPException(status_code=400, detail="No path found for any bot")

    # 4. Lock the bin (if not already locked)
    bin_lock = db.query(BinLock).filter(BinLock.bin_id == bin_.bin_id).first()
    if bin_lock and bin_lock.status == "Locked":
        # Add bot to waiting list
        if min_bot.bot_id not in bin_lock.waiting_list:
            bin_lock.waiting_list.append(min_bot.bot_id)
        db.commit()
        raise HTTPException(status_code=409, detail="Bin is locked, bot added to waiting list")
    elif not bin_lock:
        bin_lock = BinLock(bin_id=bin_.bin_id, used_by=min_bot.bot_id, status="Locked", waiting_list=[])
        db.add(bin_lock)
    else:
        bin_lock.used_by = min_bot.bot_id
        bin_lock.status = "Locked"
        bin_lock.waiting_list = []

    # 5. Create the order
    order = Order(
        customer_name=customer_name,
        product_id=product_id,
        warehouse_location=f"{bin_.location_x},{bin_.location_y}",
        status="processing",
        timestamp=datetime.utcnow(),
        bot_id=min_bot.bot_id
    )
    db.add(order)

    # 6. Update bot status
    min_bot.status = "busy"
    db.commit()
    db.refresh(order)
    return {"order_id": order.order_id, "bot_id": min_bot.bot_id} 