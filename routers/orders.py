from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.orders import Order, OrderProduct
from models.products import Product
from models.bots import Bot
from models.bins import Bin
from db.database import Base
from typing import List
import time
from utils.astar import astar_grid

from pydantic import BaseModel

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
    """Assign an available bot to an order and calculate path"""
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            print(f"Order {order_id} not found")
            return None
        
        # Find available bot
        bot = db.query(Bot).filter(Bot.status == "idle").first()
        if not bot:
            print("No idle bots available")
            return None
        
        # Get the first product's bin for destination
        first_item = db.query(OrderProduct).filter(OrderProduct.order_id == order_id).first()
        if not first_item:
            print(f"No order items found for order {order_id}")
            return None
        
        product = db.query(Product).filter(Product.id == first_item.product_id).first()
        if not product:
            print(f"Product {first_item.product_id} not found")
            return None
        
        if not product.bin_id:
            print(f"Product {product.id} has no bin_id")
            return None
        
        bin_obj = db.query(Bin).filter(Bin.id == product.bin_id).first()
        if not bin_obj:
            print(f"Bin {product.bin_id} not found")
            return None
        
        # --- NEW LOGIC: Assign parking and delivery station ---
        # Each bot has a unique parking spot based on its id
        if bot.id == 1:
            parking_spot = (5, 5)
            parking_z = 5
        elif bot.id == 2:
            parking_spot = (5, 5)
            parking_z = 4
        else:
            parking_spot = (bot.x, bot.y)
            parking_z = bot.current_location_z
        delivery_station = (5, 0)  # Top right of grid
        delivery_z = parking_z     # Z stays fixed for each bot
        
        # Path: parking -> bin -> delivery
        path1 = astar_grid(parking_spot, (bin_obj.x, bin_obj.y), set(), (6, 6)) or []
        path2 = astar_grid((bin_obj.x, bin_obj.y), delivery_station, set(), (6, 6)) or []
        full_path = (path1[:-1] if path1 else []) + path2  # Avoid duplicate bin position
        
        # Update bot state
        bot.x, bot.y, bot.current_location_z = parking_spot[0], parking_spot[1], parking_z
        bot.status = "moving"
        bot.assigned_order_id = order_id
        bot.destination_bin = [bin_obj.x, bin_obj.y, bin_obj.z_location]
        bot.path = full_path if full_path else []
        
        # Update order
        order.assigned_bot_id = bot.id
        order.status = "packing"
        
        db.commit()
        db.refresh(bot)
        db.refresh(order)
        
        print(f"Successfully assigned bot {bot.id} to order {order_id}")
        return bot
        
    except Exception as e:
        print(f"Error in assign_bot_to_order: {e}")
        db.rollback()
        return None

@router.post("/orders/")
def create_order(order_data: OrderCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        order = Order(status="pending")
        db.add(order)
        db.commit()
        db.refresh(order)

        # Add order items with quantity
        for item in order_data.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                print(f"Product {item.product_id} not found, skipping...")
                continue
            order_item = OrderProduct(order_id=order.id, product_id=product.id, quantity=item.quantity)
            db.add(order_item)
        db.commit()
        db.refresh(order)

        # Assign available bot
        bot = assign_bot_to_order(order.id, db)
        if bot:
            background_tasks.add_task(process_order, order.id)
        
        return {
            "order_id": order.id,
            "status": order.status,
            "assigned_bot_id": order.assigned_bot_id,
            "items": [
                {
                    "product_id": oi.product_id,
                    "name": oi.product.name,
                    "quantity": oi.quantity
                }
                for oi in order.items
            ]
        }
    except Exception as e:
        print(f"Error creating order: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

def process_order(order_id: int):
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order or not order.assigned_bot_id:
            return
        bot = db.query(Bot).filter(Bot.id == order.assigned_bot_id).first()
        if not bot:
            return
        # Each bot has a unique parking spot based on its id
        if bot.id == 1:
            parking_spot = (5, 5)
            parking_z = 5
        elif bot.id == 2:
            parking_spot = (5, 5)
            parking_z = 4
        else:
            parking_spot = (bot.x, bot.y)
            parking_z = bot.current_location_z
        delivery_station = (5, 0)
        delivery_z = parking_z
        # Get the bin location from the assigned order
        first_item = db.query(OrderProduct).filter(OrderProduct.order_id == order_id).first()
        product = db.query(Product).filter(Product.id == first_item.product_id).first()
        bin_obj = db.query(Bin).filter(Bin.id == product.bin_id).first()
        bin_pos = (bin_obj.x, bin_obj.y)
        # 1. Move from parking to bin
        path1 = astar_grid(parking_spot, bin_pos, set(), (6, 6)) or []
        if path1:
            bot.path = path1
            bot.status = "moving"
            db.commit()
            for x, y in path1[1:]:
                bot.x, bot.y, bot.current_location_z = x, y, parking_z
                db.commit()
                time.sleep(0.2)
        # 2. Move from bin to delivery station
        path2 = astar_grid(bin_pos, delivery_station, set(), (6, 6)) or []
        if path2:
            bot.path = path2
            bot.status = "delivering"
            db.commit()
            for x, y in path2[1:]:
                bot.x, bot.y, bot.current_location_z = x, y, parking_z
                db.commit()
                time.sleep(0.2)
        # 3. Simulate delivery
        bot.status = "delivering"
        db.commit()
        time.sleep(1)
        # 4. Move from delivery station back to parking
        return_path = astar_grid((bot.x, bot.y), parking_spot, set(), (6, 6)) or []
        if return_path:
            bot.path = return_path
            bot.status = "returning"
            db.commit()
            for x, y in return_path[1:]:
                bot.x, bot.y, bot.current_location_z = x, y, parking_z
                db.commit()
                time.sleep(0.2)
        # 5. Complete order and reset bot
        order.status = "packed"
        bot.status = "idle"
        bot.assigned_order_id = None
        bot.destination_bin = None
        bot.path = None
        db.commit()
    finally:
        db.close()

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