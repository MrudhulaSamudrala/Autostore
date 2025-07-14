from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import orders, products, bins, bots
from db.database import Base, engine
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import asyncio
from db.database import SessionLocal
from models.orders import Order, OrderProduct
from models.bots import Bot
from models.bins import Bin
from models.products import Product
from ws_manager import orders_ws_manager, bots_ws_manager
import datetime
import threading

print("About to create tables")
Base.metadata.create_all(bind=engine)
print("Tables created")

# Reset stuck bots on startup
def reset_stuck_bots():
    db = SessionLocal()
    try:
        bots = db.query(Bot).filter(Bot.status != "idle").all()
        for bot in bots:
            bot.status = "idle"
            bot.assigned_order_id = None
            bot.destination_bin = None
            bot.path = []
            bot.full_path = None
        db.commit()
    except Exception as e:
        print(f"[WARNING] Could not reset bots: {e}")
    finally:
        db.close()

# Now that tables are created, reset bins
from routers.orders import reset_all_bins_available

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("[STARTUP] Initializing application...")
    
    # Reset stuck bots
    reset_stuck_bots()
    
    # Reset all bins to available
    reset_all_bins_available()
    
    print("[STARTUP] Application initialization complete")

# CORS middleware should be added before routers/static files
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001", "*"],  # Add both, or "*" for debugging
    allow_credentials=True,
    allow_methods=["*"],  # Or ["GET", "POST", ...]
    allow_headers=["*"],
)

# Serve static files for product images
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(orders)
app.include_router(products)
app.include_router(bins)
app.include_router(bots)

# --- WebSocket Event Manager ---

@app.websocket("/ws/bots")
async def websocket_bots(websocket: WebSocket):
    print("[DEBUG] WebSocket client connected to /ws/bots")
    await bots_ws_manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(3600)  # Keep alive
    except WebSocketDisconnect:
        bots_ws_manager.disconnect(websocket)

@app.websocket("/ws/orders")
async def websocket_orders(websocket: WebSocket):
    print("[DEBUG] WebSocket client connected to /ws/orders")
    await orders_ws_manager.connect(websocket)
    try:
        # Send an initial message right after connecting
        await websocket.send_json({"event": "connected", "message": "WebSocket connection established"})
        while True:
            try:
                await websocket.send_json({"event": "ping"})
                await asyncio.sleep(30)
            except RuntimeError as e:
                if "Cannot call 'send' once a close message has been sent" in str(e):
                    print("[DEBUG] WebSocket closed, stopping ping loop")
                    break
                else:
                    raise e
    except (WebSocketDisconnect, asyncio.CancelledError, RuntimeError) as e:
        print(f"[DEBUG] WebSocket /ws/orders disconnected: {type(e).__name__}")
        orders_ws_manager.disconnect(websocket)

@app.get("/test-cors")
def test_cors():
    return {"message": "CORS is working"}

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/admin/reset_bots")
def admin_reset_bots():
    reset_stuck_bots()
    return {"status": "success", "message": "All bots reset to idle."} 

async def packing_timeout_watchdog():
    while True:
        db = SessionLocal()
        try:
            now = datetime.datetime.utcnow()
            # Find orders stuck in 'packing' for more than 5 minutes
            stuck_orders = db.query(Order).filter(Order.status == 'packing').all()
            for order in stuck_orders:
                # Assume order has a created_at or updated_at timestamp
                # If not, skip this logic or add a timestamp field
                last_update = getattr(order, 'updated_at', None) or getattr(order, 'created_at', None)
                if not last_update:
                    continue
                if (now - last_update).total_seconds() > 300:
                    # Mark order as packed
                    order.status = 'packed'
                    db.commit()
                    # Find associated bot
                    bot = db.query(Bot).filter(Bot.assigned_order_id == order.id).first()
                    if bot:
                        bot.status = 'idle'
                        bot.assigned_order_id = None
                        bot.destination_bin = None
                        bot.path = []
                        bot.full_path = None
                        db.commit()
                        # Broadcast bot update
                        await bots_ws_manager.broadcast({
                            'event': 'status_update',
                            'bot_id': bot.id,
                            'bot_status': bot.status,
                            'assigned_order_id': bot.assigned_order_id
                        })
                    # Find associated bin(s)
                    order_items = db.query(OrderProduct).filter(OrderProduct.order_id == order.id).all()
                    for item in order_items:
                        product = db.query(Product).filter(Product.id == item.product_id).first()
                        if product and product.bin_id:
                            bin_obj = db.query(Bin).filter(Bin.id == product.bin_id).first()
                            if bin_obj and bin_obj.status == 'in-use':
                                bin_obj.status = 'available'
                                db.commit()
                                # Broadcast bin update
                                await bots_ws_manager.broadcast({
                                    'event': 'status_update',
                                    'bin_id': bin_obj.id,
                                    'bin_status': bin_obj.status
                                })
                    # Broadcast order update
                    await orders_ws_manager.broadcast({
                        'event': 'status_update',
                        'order_id': order.id,
                        'order_status': order.status
                    })
        finally:
            db.close()
        await asyncio.sleep(60)

# Start the watchdog on startup
threading.Thread(target=lambda: asyncio.run(packing_timeout_watchdog()), daemon=True).start() 