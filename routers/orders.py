# orders.py - FastAPI router for order, bot, and bin management in AutoStore simulation
# Features: order creation, bot assignment, bin locking, real-time movement, WebSocket updates, robust error handling

import logging
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.orders import Order, OrderProduct
from models.products import Product
from models.bots import Bot
from models.bins import Bin
from db.database import Base
from typing import List
import time
import random
from utils.astar import whca_star, create_varied_path, update_bot_reservations, get_reservation_table_status
from pydantic import BaseModel
import json
from ws_manager import bots_ws_manager, orders_ws_manager
import asyncio
import datetime
import threading

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

class OrderItemIn(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemIn]

def assign_bot_to_order(order_id: int, db: Session):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order or order.assigned_bot_id:
        return
    
    # Get the first product to find the bin
    first_item = db.query(OrderProduct).filter(OrderProduct.order_id == order_id).first()
    if not first_item:
        return
    
    product = db.query(Product).filter(Product.id == first_item.product_id).first()
    if not product:
        return
    
    bin_obj = db.query(Bin).filter(Bin.id == product.bin_id).first()
    if not bin_obj:
        return
    
    # Find the nearest idle bot (only assign to idle bots)
    idle_bot = find_nearest_idle_bot(db, bin_obj.x, bin_obj.y)
    if idle_bot and idle_bot.status == "idle":
        order.assigned_bot_id = idle_bot.id
        order.status = "packing"
        db.commit()
        logger.debug(f"[DEBUG] Assigned bot {idle_bot.id} to order {order_id}")
    else:
        logger.debug(f"[DEBUG] No idle bots available for order {order_id}")

def assign_pending_orders_periodically(db: Session, interval: int = 2):
    """Periodically assign pending orders to available bots"""
    try:
        packing_orders = db.query(Order).filter(Order.status == "packing", Order.assigned_bot_id == None).all()
        for order in packing_orders:
            available_bot = db.query(Bot).filter(Bot.status == "idle").first()
            if available_bot:
                assign_bot_to_order(order.id, db)
                logger.debug(f"[DEBUG] Assigned bot {available_bot.id} to order {order.id}")
    except Exception as e:
        logger.warning(f"[WARNING] Could not assign pending orders (tables may not exist yet): {e}")
    finally:
        db.close()

# Start the background thread when the module is loaded
# Commented out to prevent running before tables are created
# threading.Thread(target=lambda: assign_pending_orders_periodically(SessionLocal()), daemon=True).start()

def is_cell_blocked(x, y, bots, bins, ignore_bot_id=None):
    # Returns True if cell is occupied by another bot or a bin
    for bot in bots:
        if bot.id != ignore_bot_id and bot.x == x and bot.y == y:
            return True
    for bin in bins:
        if hasattr(bin, 'x') and hasattr(bin, 'y') and bin.x == x and bin.y == y:
            return True
    return False

# Helper: Lock a bin (returns True if locked, False if already locked)
def lock_bin(db, bin_id, bot_id):
    from models.bin_locks import BinLock
    bin_lock = db.query(BinLock).filter(BinLock.id == bin_id).first()
    if not bin_lock:
        bin_lock = BinLock(id=bin_id, used_by=bot_id, status="Locked", waiting_list=[])
        db.add(bin_lock)
        db.commit()
        return True
    if bin_lock.status == "Available":
        bin_lock.status = "Locked"
        bin_lock.used_by = bot_id
        db.commit()
        return True
    # Already locked, queue this bot
    if bot_id not in bin_lock.waiting_list:
        bin_lock.waiting_list.append(bot_id)
        db.commit()
    return False

# Helper: Find nearest idle bot (simple Euclidean distance for now)
def find_nearest_idle_bot(db, bin_x, bin_y):
    bots = db.query(Bot).filter(Bot.status == "idle").all()
    if not bots:
        return None
    # Find nearest by distance
    nearest = min(bots, key=lambda b: (b.x - bin_x) ** 2 + (b.y - bin_y) ** 2)
    return nearest

def assign_pending_orders_loop():
    from db.database import SessionLocal
    while True:
        db = SessionLocal()
        try:
            pending_orders = db.query(Order).filter(Order.status == "pending").all()
            for order in pending_orders:
                # Try to assign a bot
                assign_bot_to_order(order.id, db)
        except Exception as e:
            logger.error(f"[AUTO-ASSIGN] Error: {e}")
        finally:
            db.close()
        time.sleep(2)  # Check every 2 seconds

from fastapi import FastAPI
from fastapi import APIRouter

router = APIRouter()

@router.on_event("startup")
def start_assign_pending_orders_loop():
    t = threading.Thread(target=assign_pending_orders_loop, daemon=True)
    t.start()

@router.post("/orders/")
async def create_order(order_data: OrderCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        logger.info("STEP 1: Creating order")
        order = Order(status="pending")
        db.add(order)
        db.commit()
        db.refresh(order)
        # Broadcast status update immediately
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(orders_ws_manager.broadcast({
                    "event": "status_update",
                    "order_id": order.id,
                    "order_status": order.status
                }))
        except Exception as e:
            logger.error(f"[WS] Failed to broadcast order status update: {e}")
        logger.info(f"STEP 2: Order created with id {order.id}")

        items = []
        for item in order_data.items:
            logger.info(f"STEP 3: Adding item {item.product_id}")
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                logger.error(f"ERROR: Product {item.product_id} not found")
                continue
            order_item = OrderProduct(order_id=order.id, product_id=product.id, quantity=item.quantity)
            db.add(order_item)
            items.append({"product_id": product.id, "name": product.name, "quantity": item.quantity})
        db.commit()
        db.refresh(order)
        logger.info("STEP 4: Order items added")

        first_item = db.query(OrderProduct).filter(OrderProduct.order_id == order.id).first()
        if not first_item:
            logger.error("ERROR: No order items found")
            return {
                "order_id": order.id,
                "status": order.status,
                "assigned_bot_id": None,
                "items": items
            }
        product = db.query(Product).filter(Product.id == first_item.product_id).first()
        if not product or not product.bin_id:
            logger.error("ERROR: Product or bin_id missing")
            return {
                "order_id": order.id,
                "status": order.status,
                "assigned_bot_id": None,
                "items": items
            }
        bin_obj = db.query(Bin).filter(Bin.id == product.bin_id).first()
        if not bin_obj:
            logger.error("ERROR: Bin not found")
            return {
                "order_id": order.id,
                "status": order.status,
                "assigned_bot_id": None,
                "items": items
            }
        logger.info(f"STEP 5: Bin found: {bin_obj.id}")

        bot = find_nearest_idle_bot(db, bin_obj.x, bin_obj.y)
        if not bot:
            logger.info("No idle bot found, order remains pending.")
            return {
                "order_id": order.id,
                "status": order.status,
                "assigned_bot_id": None,
                "items": items
            }
        logger.info(f"STEP 6: Bot found: {bot.id}")

        locked = lock_bin(db, bin_obj.id, bot.id)
        if not locked:
            logger.error("ERROR: Bin could not be locked")
            return {
                "order_id": order.id,
                "status": order.status,
                "assigned_bot_id": None,
                "items": items
            }
        logger.info("STEP 7: Bin locked")

        # Standardize bin status
        bin_obj.status = "locked"
        db.commit()
        await bots_ws_manager.broadcast({
            "event": "status_update",
            "bin_id": bin_obj.id,
            "bin_status": "locked"
        })

        # Set bot to parking station
        if bot.id == 1:
            bot.x, bot.y = 5, 5  # Parking 1
            bot.current_location_z = 5
        elif bot.id == 2:
            bot.x, bot.y = 5, 4  # Parking 2
            bot.current_location_z = 4
        else:
            bot.x, bot.y = 5, (bot.id % 5)  # Spread additional bots
            bot.current_location_z = 0
        bot.status = 'packing'
        bot.assigned_order_id = order.id
        bot.destination_bin = [bin_obj.x, bin_obj.y, getattr(bin_obj, 'z_location', 0), bin_obj.id]
        bot.path = []
        bot.full_path = None
        order.assigned_bot_id = bot.id
        order.status = 'packing'
        db.commit()
        db.refresh(bot)
        db.refresh(order)
        logger.info("STEP 8: Bot assigned and order updated (status=packing)")
        response = {
            "order_id": order.id,
            "status": order.status,
            "assigned_bot_id": bot.id if bot else None,
            "items": items
        }
        # After assigning the bot and committing changes:
        if bot and order.assigned_bot_id:
            import asyncio
            asyncio.create_task(process_order_enhanced(order.id))
            logger.info(f"Started order processing for order {order.id} with bot {bot.id}")
        return response
    except Exception as e:
        logger.error(f"ERROR in create_order: {e}")
        return {"error": str(e)}

# Add this helper at the top of the file (or before simulate_bot_order)
def lerp(a, b, t):
    return a + (b - a) * t

# Simulate bot order fulfillment and emit WebSocket events
async def simulate_bot_order(order_id: int, bot_id: int, bin_id: int):
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        bin_obj = db.query(Bin).filter(Bin.id == bin_id).first()

        # 1. Move from parking to bin (stepwise)
        start_pos = (bot.x, bot.y)
        bin_pos = (bin_obj.x, bin_obj.y)
        path_to_bin = create_varied_path(start_pos, bin_pos, (6, 6), bot.id, int(time.time()))
        logger.info(f"[PATH] Bot {bot.id} path to bin: {path_to_bin}")
        if path_to_bin:
            for idx, (x, y) in enumerate(path_to_bin):
                bot.x, bot.y = x, y
                bot.status = "moving_to_bin"
                db.commit()
                logger.info(f"[MOVE] Bot {bot.id} step {idx+1}/{len(path_to_bin)}: moving to bin {bin_obj.id} at ({x}, {y}), status={bot.status}")
                await bots_ws_manager.broadcast({
                    "event": "bot_move",
                    "bot_id": bot.id,
                    "x": x,
                    "y": y,
                    "z": bot.current_location_z,
                    "status": "moving_to_bin"
                })
                await asyncio.sleep(0.1)

        # 2. Pick up bin
        if bot.x == bin_obj.x and bot.y == bin_obj.y:
            bin_obj.status = "in_transit"
            bot.carried_bin_id = bin_obj.id
            bot.status = "carrying"
            db.commit()
            logger.info(f"Bot {bot.id} picking up bin {bin_obj.id} at ({bot.x}, {bot.y})")
            await bots_ws_manager.broadcast({
                "event": "bin_pickup",
                "bot_id": bot.id,
                "bin_id": bin_obj.id,
                "bin_status": "in_transit"
            })
            await asyncio.sleep(0.1)
        else:
            logger.warning(f"Bot {bot.id} not at bin {bin_obj.id} position for pickup! Bot at ({bot.x}, {bot.y}), bin at ({bin_obj.x}, {bin_obj.y})")

        # 3. Move to delivery station (stepwise)
        delivery_pos = (5, 0)
        path_to_delivery = create_varied_path(bin_pos, delivery_pos, (6, 6), bot.id, int(time.time()))
        logger.info(f"[PATH] Bot {bot.id} path to delivery: {path_to_delivery}")
        if path_to_delivery:
            for idx, (x, y) in enumerate(path_to_delivery):
                bot.x, bot.y = x, y
                bot.status = "delivering"
                db.commit()
                logger.info(f"[MOVE] Bot {bot.id} step {idx+1}/{len(path_to_delivery)}: delivering bin {bin_obj.id} to delivery at ({x}, {y}), status={bot.status}")
                await bots_ws_manager.broadcast({
                    "event": "bot_move",
                    "bot_id": bot.id,
                    "x": x,
                    "y": y,
                    "z": bot.current_location_z,
                    "status": "delivering"
                })
                await asyncio.sleep(0.1)

        # 4. Drop bin at delivery
        bot.carried_bin_id = None
        bin_obj.status = "delivered"
        db.commit()
        await bots_ws_manager.broadcast({
            "event": "bin_drop",
            "bot_id": bot.id,
            "bin_id": bin_obj.id,
            "bin_status": "delivered"
        })
        await asyncio.sleep(0.1)

        # 5. Return to parking (stepwise)
        parking_pos = (5, 5) if bot.id == 1 else (5, 4)
        path_to_parking = create_varied_path(delivery_pos, parking_pos, (6, 6), bot.id, int(time.time()))
        logger.info(f"[PATH] Bot {bot.id} path to parking: {path_to_parking}")
        if path_to_parking:
            for idx, (x, y) in enumerate(path_to_parking):
                bot.x, bot.y = x, y
                bot.status = "returning"
                db.commit()
                logger.info(f"[MOVE] Bot {bot.id} step {idx+1}/{len(path_to_parking)}: returning to parking at ({x}, {y}), status={bot.status}")
                await bots_ws_manager.broadcast({
                    "event": "bot_move",
                    "bot_id": bot.id,
                    "x": x,
                    "y": y,
                    "z": bot.current_location_z,
                    "status": "returning"
                })
                await asyncio.sleep(0.1)

        # 6. Set bot to idle
        bot.status = "idle"
        db.commit()
        await bots_ws_manager.broadcast({
            "event": "bot_update",
            "bot_id": bot.id,
            "status": "idle"
        })

    finally:
        db.close()

async def broadcast_bot_status(bot):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    await bots_ws_manager.broadcast({
        "event": "status_update", 
        "bot_id": bot.id, 
        "bot_status": bot.status, 
        "assigned_order_id": bot.assigned_order_id,
        "carried_bin_id": bot.carried_bin_id
    })

# Enhanced order processing with async movement and WebSocket updates
async def process_order_enhanced(order_id: int):
    """
    Enhanced order processing with:
    - Sequential bin delivery for multiple items
    - Better obstacle avoidance
    - No movement through delivery station when picking orders
    - Return to idle after completing all items
    """
    logger.debug(f"[DEBUG] (ASYNC) process_order_enhanced called for order_id={order_id}")
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order or not order.assigned_bot_id:
            logger.debug(f"[DEBUG] Order {order_id} not found or no assigned bot")
            return
        bot = db.query(Bot).filter(Bot.id == order.assigned_bot_id).first()
        if not bot:
            logger.debug(f"[DEBUG] Bot {order.assigned_bot_id} not found for order {order_id}")
            return

        # Immediately set bot to moving status
        bot.status = "moving"
        db.commit()
        await broadcast_bot_status(bot)  # Make sure this broadcasts via WebSocket

        # Get the first product's bin location
        first_item = db.query(OrderProduct).filter(OrderProduct.order_id == order_id).first()
        if not first_item:
            return

        product = db.query(Product).filter(Product.id == first_item.product_id).first()
        if not product or not product.bin_id:
            return

        bin_obj = db.query(Bin).filter(Bin.id == product.bin_id).first()
        if not bin_obj:
            return

        # Generate path to bin
        start_pos = (bot.x, bot.y)
        bin_pos = (bin_obj.x, bin_obj.y)
        path = create_varied_path(start_pos, bin_pos, (6, 6), bot.id, int(time.time()))
        logger.info(f"[ORDER {order_id}] Bot {bot.id} starting to move from {start_pos} to bin at {bin_pos}")
        logger.info(f"[ORDER {order_id}] Calculated path to bin: {path}")
        
        if path:
            bot.path = path
            bot.status = "moving"
            db.commit()
            await broadcast_bot_status(bot)
            for i, (x, y) in enumerate(path[1:], 1):
                logger.info(f"[ORDER {order_id}] Bot {bot.id} moving to ({x}, {y}) step {i}/{len(path)-1}")
                bot.x, bot.y = x, y
                db.commit()
                await broadcast_bot_status(bot)
                # If bot is carrying a bin, update bin coordinates and broadcast
                if getattr(bot, 'carried_bin_id', None):
                    bin_obj = db.query(Bin).filter(Bin.id == bot.carried_bin_id).first()
                    if bin_obj:
                        bin_obj.x = bot.x
                        bin_obj.y = bot.y
                        bin_obj.z_location = bot.current_location_z
                        db.commit()
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                asyncio.ensure_future(bots_ws_manager.broadcast({
                                    'event': 'bin_move',
                                    'bin_id': bin_obj.id,
                                    'x': bin_obj.x,
                                    'y': bin_obj.y,
                                    'z': bin_obj.z_location,
                                    'bin_status': bin_obj.status
                                }))
                        except:
                            pass
                await asyncio.sleep(1.0)

        # Get all items in the order
        order_items = db.query(OrderProduct).filter(OrderProduct.order_id == order_id).all()
        if not order_items:
            logger.debug(f"[DEBUG] No items found for order {order_id}")
            return
        
        # Each bot has a unique parking spot based on its id
        if bot.id == 1:
            parking_spot = (5, 0)
            parking_z = 5
        elif bot.id == 2:
            parking_spot = (5, 0)
            parking_z = 4
        else:
            parking_spot = (bot.x, bot.y)
            parking_z = bot.current_location_z
        
        delivery_station = (5, 0)
        delivery_z = parking_z
        current_time = int(time.time()) % 1000
        
        logger.info(f"Processing order {order_id} with {len(order_items)} items")
        
        # Set order status to 'packing' at the start
        order.status = "packing"
        order.updated_at = datetime.datetime.utcnow()
        db.commit()
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(orders_ws_manager.broadcast({
                    "event": "status_update",
                    "order_id": order.id,
                    "order_status": order.status
                }))
        except Exception as e:
            logger.error(f"[WS] Failed to broadcast order status update: {e}")

        # Process each item sequentially
        for item_index, order_item in enumerate(order_items):
            logger.info(f"Processing item {item_index + 1}/{len(order_items)}")
            
            # Get product and bin for this item
            product = db.query(Product).filter(Product.id == order_item.product_id).first()
            if not product or not product.bin_id:
                logger.debug(f"[DEBUG] Product {order_item.product_id} or bin_id missing for item {item_index + 1}")
                continue
                
            bin_obj = db.query(Bin).filter(Bin.id == product.bin_id).first()
            if not bin_obj:
                logger.debug(f"[DEBUG] Bin {product.bin_id} not found for item {item_index + 1}")
                continue
            
            bin_pos = (bin_obj.x, bin_obj.y)
            
            # 1. Move from current position to bin (avoid delivery station)
            start_pos = (bot.x, bot.y)
            path_to_bin = create_path_avoiding_delivery_station(start_pos, bin_pos, (6, 6), bot.id, current_time)
            
            if path_to_bin:
                bot.path = path_to_bin
                bot.full_path = json.dumps(path_to_bin)
                bot.status = "moving"
                db.commit()
                await broadcast_bot_status(bot)
                
                for i, (x, y) in enumerate(path_to_bin[1:], 1):
                    logger.debug(f"[DEBUG] Bot {bot.id} moving to bin ({x}, {y}) step {i}/{len(path_to_bin)-1}")
                    
                    # Enhanced obstacle detection and avoidance
                    if is_cell_blocked(x, y, db.query(Bot).all(), db.query(Bin).all(), ignore_bot_id=bot.id):
                        logger.debug(f"[DEBUG] Obstacle detected at ({x}, {y}), replanning path")
                        # Replan path avoiding obstacles
                        new_path = create_path_avoiding_obstacles((bot.x, bot.y), bin_pos, (6, 6), bot.id, current_time + i)
                        if new_path:
                            bot.path = new_path
                            bot.full_path = json.dumps(new_path)
                            db.commit()
                            continue  # Restart loop with new path
                        else:
                            logger.debug(f"[DEBUG] Could not find alternative path, skipping this item")
                            break
                    
                    update_bot_reservations(bot.id, (bot.x, bot.y), (x, y), current_time + i)
                    bot.x, bot.y, bot.current_location_z = x, y, parking_z
                    db.commit()
                    await broadcast_bot_status(bot)
                    # If bot is carrying a bin, update bin coordinates and broadcast
                    if getattr(bot, 'carried_bin_id', None):
                        bin_obj = db.query(Bin).filter(Bin.id == bot.carried_bin_id).first()
                        if bin_obj:
                            bin_obj.x = bot.x
                            bin_obj.y = bot.y
                            bin_obj.z_location = bot.current_location_z
                            db.commit()
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    asyncio.ensure_future(bots_ws_manager.broadcast({
                                        'event': 'bin_move',
                                        'bin_id': bin_obj.id,
                                        'x': bin_obj.x,
                                        'y': bin_obj.y,
                                        'z': bin_obj.z_location,
                                        'bin_status': bin_obj.status
                                    }))
                            except:
                                pass
                    
                    # Send WebSocket update for smooth movement
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.ensure_future(bots_ws_manager.broadcast({
                                "event": "bot_move", 
                                "bot_id": bot.id, 
                                "x": x, 
                                "y": y, 
                                "z": bot.current_location_z, 
                                "assigned_order_id": bot.assigned_order_id
                            }))
                    except:
                        pass
                    await asyncio.sleep(1.0)
            
            # 2. Pick up bin (simulate)
            if bot.x == bin_obj.x and bot.y == bin_obj.y:
                logger.info(f"[ORDER {order_id}] Bot {bot.id} reached bin {bin_obj.id} at ({bot.x}, {bot.y})")
                logger.debug(f"[DEBUG] Bot {bot.id} picking up bin {bin_obj.id}")
                bot.status = "carrying"
                bot.carried_bin_id = bin_obj.id
                bin_obj.status = "in-use"
                db.commit()
                # Broadcast bin status update for 'in-use'
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.ensure_future(bots_ws_manager.broadcast({
                            "event": "status_update",
                            "bin_id": bin_obj.id,
                            "bin_status": "in-use"
                        }))
                except:
                    pass
                # Broadcast bin pickup event
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.ensure_future(bots_ws_manager.broadcast({
                            "event": "bin_pickup",
                            "bot_id": bot.id,
                            "bin_id": bin_obj.id,
                            "bot_x": bot.x,
                            "bot_y": bot.y,
                            "bot_z": bot.current_location_z
                        }))
                except:
                    pass
                await asyncio.sleep(0.1)  # Simulate picking up time
            else:
                logger.warning(f"[DEBUG] Bot {bot.id} not at bin {bin_obj.id} position for pickup! Bot at ({bot.x}, {bot.y}), bin at ({bin_obj.x}, {bin_obj.y})")
            
            # 3. Move from bin to delivery station
            path_to_delivery = create_varied_path(bin_pos, delivery_station, (6, 6), bot.id, current_time + len(path_to_bin)) or []
            if path_to_delivery:
                bot.path = path_to_delivery
                bot.full_path = json.dumps(path_to_bin[:-1] + path_to_delivery) if path_to_bin else json.dumps(path_to_delivery)
                bot.status = "delivering"
                db.commit()
                await broadcast_bot_status(bot)
                
                for i, (x, y) in enumerate(path_to_delivery[1:], 1):
                    logger.debug(f"[DEBUG] Bot {bot.id} delivering to ({x}, {y}) step {i}/{len(path_to_delivery)-1}")
                    
                    # Obstacle check for delivery path
                    if is_cell_blocked(x, y, db.query(Bot).all(), db.query(Bin).all(), ignore_bot_id=bot.id):
                        logger.debug(f"[DEBUG] Obstacle detected during delivery at ({x}, {y}), replanning")
                        new_path = create_path_avoiding_obstacles((bot.x, bot.y), delivery_station, (6, 6), bot.id, current_time + len(path_to_bin) + i)
                        if new_path:
                            bot.path = new_path
                            bot.full_path = json.dumps(path_to_bin[:-1] + new_path) if path_to_bin else json.dumps(new_path)
                            db.commit()
                            continue
                    
                    update_bot_reservations(bot.id, (bot.x, bot.y), (x, y), current_time + len(path_to_bin) + i)
                    bot.x, bot.y, bot.current_location_z = x, y, parking_z
                    db.commit()
                    await broadcast_bot_status(bot)
                    # If bot is carrying a bin, update bin coordinates and broadcast
                    if getattr(bot, 'carried_bin_id', None):
                        bin_obj = db.query(Bin).filter(Bin.id == bot.carried_bin_id).first()
                        if bin_obj:
                            bin_obj.x = bot.x
                            bin_obj.y = bot.y
                            bin_obj.z_location = bot.current_location_z
                            db.commit()
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    asyncio.ensure_future(bots_ws_manager.broadcast({
                                        'event': 'bin_move',
                                        'bin_id': bin_obj.id,
                                        'x': bin_obj.x,
                                        'y': bin_obj.y,
                                        'z': bin_obj.z_location,
                                        'bin_status': bin_obj.status
                                    }))
                            except:
                                pass
                    
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.ensure_future(bots_ws_manager.broadcast({
                                "event": "bot_move", 
                                "bot_id": bot.id, 
                                "x": x, 
                                "y": y, 
                                "z": bot.current_location_z, 
                                "assigned_order_id": bot.assigned_order_id
                            }))
                    except:
                        pass
                    await asyncio.sleep(1.0)
            
            # 4. Deliver bin at delivery station
            logger.debug(f"[DEBUG] Bot {bot.id} delivering bin {bin_obj.id} at delivery station")
            bot.status = "delivering"
            bot.carried_bin_id = None
            db.commit()

            # Broadcast bin drop event (bin disappears from bot and grid)
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(bots_ws_manager.broadcast({
                        "event": "bin_drop",
                        "bot_id": bot.id,
                        "bin_id": bin_obj.id,
                        "delivery_x": 5,
                        "delivery_y": 0,
                        "delivery_z": bot.current_location_z
                    }))
            except:
                pass

            # 5. Return to parking spot (always, even for last item)
            return_path = create_path_avoiding_delivery_station(delivery_station, parking_spot, (6, 6), bot.id, current_time + len(path_to_bin) + len(path_to_delivery))
            if return_path:
                bot.path = return_path
                bot.status = "returning"
                db.commit()
                await broadcast_bot_status(bot)
                for i, (x, y) in enumerate(return_path[1:], 1):
                    logger.debug(f"[DEBUG] Bot {bot.id} returning to parking ({x}, {y}) step {i}/{len(return_path)-1}")
                    update_bot_reservations(bot.id, (bot.x, bot.y), (x, y), current_time + len(path_to_bin) + len(path_to_delivery) + i)
                    bot.x, bot.y, bot.current_location_z = x, y, parking_z
                    db.commit()
                    await broadcast_bot_status(bot)
                    # If bot is carrying a bin, update bin coordinates and broadcast
                    if getattr(bot, 'carried_bin_id', None):
                        bin_obj = db.query(Bin).filter(Bin.id == bot.carried_bin_id).first()
                        if bin_obj:
                            bin_obj.x = bot.x
                            bin_obj.y = bot.y
                            bin_obj.z_location = bot.current_location_z
                            db.commit()
                            try:
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    asyncio.ensure_future(bots_ws_manager.broadcast({
                                        'event': 'bin_move',
                                        'bin_id': bin_obj.id,
                                        'x': bin_obj.x,
                                        'y': bin_obj.y,
                                        'z': bin_obj.z_location,
                                        'bin_status': bin_obj.status
                                    }))
                            except:
                                pass
                    await asyncio.sleep(1.0)

            # After bot returns to parking, set order status to 'packed' and broadcast
            order.status = "packed"
            order.updated_at = datetime.datetime.utcnow()
            db.commit()
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(orders_ws_manager.broadcast({
                        "event": "status_update",
                        "order_id": order.id,
                        "order_status": order.status
                    }))
            except Exception as e:
                logger.error(f"[WS] Failed to broadcast order status update: {e}")

            # After bot returns to parking, wait 2 seconds, then make bin visible at delivery station
            logger.info(f"[BIN RETURN] Preparing to return bin {bin_obj.id} to grid at (5, 0)")
            await asyncio.sleep(2.0)
            try:
                bin_obj.status = "available"
                bin_obj.x = 5
                bin_obj.y = 0
                bin_obj.z_location = bot.current_location_z
                db.commit()
                logger.info(f"[BIN RETURN] Bin {bin_obj.id} status set to 'available' and position set to (5, 0, {bot.current_location_z})")
                # Release bin lock
                bin_lock = db.query(BinLock).filter(BinLock.id == bin_obj.id).first()
                if bin_lock:
                    bin_lock.status = "available"
                    bin_lock.used_by = None
                    db.commit()
                # Broadcast bin return move
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(bots_ws_manager.broadcast({
                        "event": "bin_return_move",
                        "bin_id": bin_obj.id,
                        "x": 5,
                        "y": 0,
                        "z": bot.current_location_z
                    }))
                logger.info(f"[BIN RETURN] bin_return_move event sent for bin {bin_obj.id}")
                await asyncio.sleep(2.0)
                # Final bin return event
                if loop.is_running():
                    asyncio.ensure_future(bots_ws_manager.broadcast({
                        "event": "bin_return",
                        "bin_id": bin_obj.id,
                        "x": 5,
                        "y": 0,
                        "z": bot.current_location_z
                    }))
                logger.info(f"[BIN RETURN] bin_return event sent for bin {bin_obj.id}")
            except Exception as e:
                logger.error(f"[BIN RETURN] Error returning bin: {e}")

        # After bin returns to delivery station and status is set to available
        await asyncio.sleep(2.0)
        # Move bin back to original grid position
        if bin_obj.original_x is not None and bin_obj.original_y is not None and bin_obj.original_z is not None:
            bin_obj.x = bin_obj.original_x
            bin_obj.y = bin_obj.original_y
            bin_obj.z_location = bin_obj.original_z
            bin_obj.status = "available"
            db.commit()
            logger.info(f"[BIN RESTORE] Bin {bin_obj.id} restored to original position ({bin_obj.x}, {bin_obj.y}, {bin_obj.z_location}) and set to 'available'")
            # Broadcast status update for bin
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(bots_ws_manager.broadcast({
                    "event": "status_update",
                    "bin_id": bin_obj.id,
                    "bin_status": "available"
                }))

        # 6. Complete order and return to idle
        logger.debug(f"[DEBUG] About to mark order {order_id} as packed")
        order.status = "packed"
        order.updated_at = datetime.datetime.utcnow()
        db.commit()
        logger.debug(f"[DEBUG] Order {order_id} marked as packed and committed to DB")
        # Broadcast order status update to /ws/orders
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.ensure_future(orders_ws_manager.broadcast({
                    "event": "status_update",
                    "order_id": order.id,
                    "order_status": order.status
                }))
        except Exception as e:
            logger.error(f"[WS] Failed to broadcast order status update: {e}")
        
        # Return to parking spot after completing all items
        final_return_path = create_path_avoiding_delivery_station((bot.x, bot.y), parking_spot, (6, 6), bot.id, current_time)
        if final_return_path:
            bot.path = final_return_path
            bot.status = "returning"
            db.commit()
            await broadcast_bot_status(bot)
            
            for i, (x, y) in enumerate(final_return_path[1:], 1):
                logger.debug(f"[DEBUG] Bot {bot.id} final return to parking ({x}, {y}) step {i}/{len(final_return_path)-1}")
                bot.x, bot.y, bot.current_location_z = x, y, parking_z
                db.commit()
                await broadcast_bot_status(bot)
                # If bot is carrying a bin, update bin coordinates and broadcast
                if getattr(bot, 'carried_bin_id', None):
                    bin_obj = db.query(Bin).filter(Bin.id == bot.carried_bin_id).first()
                    if bin_obj:
                        bin_obj.x = bot.x
                        bin_obj.y = bot.y
                        bin_obj.z_location = bot.current_location_z
                        db.commit()
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                asyncio.ensure_future(bots_ws_manager.broadcast({
                                    'event': 'bin_move',
                                    'bin_id': bin_obj.id,
                                    'x': bin_obj.x,
                                    'y': bin_obj.y,
                                    'z': bin_obj.z_location,
                                    'bin_status': bin_obj.status
                                }))
                        except:
                            pass
                await asyncio.sleep(1.0)
        
        # Set bot to idle
        bot.status = "idle"
        bot.assigned_order_id = None
        bot.destination_bin = None
        bot.path = []
        bot.full_path = None
        db.commit()
        await broadcast_bot_status(bot)
        
        logger.debug(f"[DEBUG] Bot {bot.id} returned to idle state")
        
    finally:
        db.close()

def create_path_avoiding_delivery_station(start, goal, grid_size, bot_id, current_time):
    """
    Create path that avoids the delivery station area when picking up orders
    """
    delivery_station = (5, 0)
    
    # If goal is delivery station, use normal pathfinding
    if goal == delivery_station:
        return create_varied_path(start, goal, grid_size, bot_id, current_time)
    
    # If start is delivery station, use normal pathfinding
    if start == delivery_station:
        return create_varied_path(start, goal, grid_size, bot_id, current_time)
    
    # For other paths, avoid delivery station area
    def is_delivery_station_area(x, y):
        return x == 5 and y == 0
    
    # Use A* with delivery station as obstacle
    path = whca_star(start, goal, grid_size, bot_id, current_time)
    if not path:
        return None
    
    # Check if path goes through delivery station
    for x, y in path:
        if is_delivery_station_area(x, y):
            # Try alternative path by going around delivery station
            alternative_path = create_alternative_path_around_delivery(start, goal, grid_size, bot_id, current_time)
            return alternative_path
    
    return path

def create_alternative_path_around_delivery(start, goal, grid_size, bot_id, current_time):
    """
    Create alternative path that goes around the delivery station
    """
    # Try different waypoints to avoid delivery station
    waypoints = [
        (4, 1), (4, 2), (4, 3), (4, 4), (4, 5),  # Left of delivery station
        (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),  # Further left
        (2, 1), (2, 2), (2, 3), (2, 4), (2, 5),  # Even further left
    ]
    
    for waypoint in waypoints:
        # Check if waypoint is reachable
        path1 = whca_star(start, waypoint, grid_size, bot_id, current_time)
        if path1:
            path2 = whca_star(waypoint, goal, grid_size, bot_id, current_time + len(path1))
            if path2:
                # Combine paths (remove duplicate waypoint)
                return path1[:-1] + path2
    
    # If no alternative found, return original path
    return create_varied_path(start, goal, grid_size, bot_id, current_time)

def create_path_avoiding_obstacles(start, goal, grid_size, bot_id, current_time):
    """
    Create path that avoids obstacles by using different strategies
    """
    # Strategy 1: Try with increased clearance
    path = whca_star(start, goal, grid_size, bot_id, current_time)
    if path:
        return path
    
    # Strategy 2: Try with different time offset
    for time_offset in [10, 20, 30, 50, 100]:
        path = whca_star(start, goal, grid_size, bot_id, current_time + time_offset)
        if path:
            return path
    
    # Strategy 3: Try with different waypoints
    waypoints = [
        (start[0] + 1, start[1]), (start[0] - 1, start[1]),
        (start[0], start[1] + 1), (start[0], start[1] - 1),
        (goal[0] + 1, goal[1]), (goal[0] - 1, goal[1]),
        (goal[0], goal[1] + 1), (goal[0], goal[1] - 1),
    ]
    
    for waypoint in waypoints:
        if 0 <= waypoint[0] < grid_size[0] and 0 <= waypoint[1] < grid_size[1]:
            path1 = whca_star(start, waypoint, grid_size, bot_id, current_time)
            if path1:
                path2 = whca_star(waypoint, goal, grid_size, bot_id, current_time + len(path1))
                if path2:
                    return path1[:-1] + path2
    
    # Strategy 4: Fallback to direct path
    return [start, goal]

@router.get("/orders/")
def list_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    result = []
    for order in orders:
        result.append({
            "id": order.id,
            "status": order.status,
            "assigned_bot_id": order.assigned_bot_id,
            "items": [
                {
                    "product_id": oi.product_id,
                    "name": oi.product.name,
                    "quantity": oi.quantity,
                    "price": float(oi.product.price),
                    "image_url": oi.product.image_url,
                    "bin_id": oi.product.bin_id
                }
                for oi in order.items
            ]
        })
    return result 

@router.get("/bots/")
def list_bots(db: Session = Depends(get_db)):
    bots = db.query(Bot).all()
    result = []
    for bot in bots:
        result.append({
            "id": bot.id,
            "x": bot.x,
            "y": bot.y,
            "z": bot.current_location_z,  # Map current_location_z to z for frontend compatibility
            "current_location_z": bot.current_location_z,
            "status": bot.status,
            "assigned_order_id": bot.assigned_order_id,
            "destination_bin": bot.destination_bin,
            "path": bot.path,
            "full_path": json.loads(bot.full_path) if bot.full_path else [],
            "carried_bin_id": bot.carried_bin_id,  # Include carried bin information
        })
    return result 

# Move this to after tables are created
# reset_all_bins_available()

def reset_all_bins_available():
    """Reset all bins to available status on startup"""
    try:
        db = SessionLocal()
        bins = db.query(Bin).all()
        for bin_obj in bins:
            bin_obj.status = "available"
            logger.debug(f"Bin {bin_obj.id} status after reset: {bin_obj.status}")
        db.commit()
        logger.debug("[DEBUG] All bins reset to 'available' on startup.")
    except Exception as e:
        logger.warning(f"[WARNING] Could not reset bins (tables may not exist yet): {e}")
    finally:
        db.close()

reset_all_bins_available() 

@router.post("/admin/reset_bins/")
async def admin_reset_bins(db: Session = Depends(get_db)):
    from models.bin_locks import BinLock
    bins = db.query(Bin).all()
    # Step 0: Delete all bin locks
    db.query(BinLock).delete()
    db.commit()
    # Step 1: Set all bins to 'available' and broadcast
    for bin_obj in bins:
        bin_obj.status = "available"
        db.commit()
        db.refresh(bin_obj)
        await bots_ws_manager.broadcast({"event": "status_update", "bin_id": bin_obj.id, "bin_status": "available"})
    logger.debug("[DEBUG] All bins reset to 'available' and all bin locks deleted via admin endpoint.")
    return {"message": "All bins reset to available and all locks deleted"} 

@router.post("/admin/clear_orders/")
async def admin_clear_orders(db: Session = Depends(get_db)):
    db.query(OrderProduct).delete()
    db.query(Order).delete()
    db.commit()
    return {"message": "All orders and order history cleared."} 

@router.websocket("/ws/orders")
async def ws_orders(websocket: WebSocket):
    await orders_ws_manager.connect(websocket)
    try:
        await websocket.send_json({"event": "connected", "message": "WebSocket connection established"})
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"event": "ping"})
    except WebSocketDisconnect:
        orders_ws_manager.disconnect(websocket) 