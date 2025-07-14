#!/usr/bin/env python3
"""
Debug script to test order assignment logic step by step
"""

import requests
import sqlite3
import json

def debug_order_assignment():
    """Debug the order assignment process"""
    
    print("🔍 Debugging Order Assignment")
    print("=" * 50)
    
    # 1. Check current bot status
    print("\n1️⃣ Checking bot status...")
    try:
        response = requests.get("http://127.0.0.1:8000/bots/")
        if response.status_code == 200:
            bots = response.json()
            for bot in bots:
                print(f"   Bot {bot['id']}: Status={bot['status']}, Pos=({bot['x']}, {bot['y']}, {bot['z']})")
        else:
            print(f"❌ Failed to get bots: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting bots: {e}")
    
    # 2. Check product and bin information
    print("\n2️⃣ Checking product and bin info...")
    try:
        conn = sqlite3.connect("autostore.db")
        cursor = conn.cursor()
        
        # Check products
        cursor.execute("SELECT id, name, bin_id FROM products LIMIT 5")
        products = cursor.fetchall()
        print("   Products:")
        for product in products:
            print(f"      Product {product[0]}: {product[1]}, Bin={product[2]}")
        
        # Check bins
        cursor.execute("SELECT id, x, y, z_location, status FROM bins LIMIT 5")
        bins = cursor.fetchall()
        print("   Bins:")
        for bin in bins:
            print(f"      Bin {bin[0]}: Pos=({bin[1]}, {bin[2]}, {bin[3]}), Status={bin[4]}")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    
    # 3. Test order creation with debug info
    print("\n3️⃣ Testing order creation...")
    order_data = {
        "items": [
            {"product_id": 1, "quantity": 1}
        ]
    }
    
    try:
        print("   Creating order...")
        response = requests.post("http://127.0.0.1:8000/orders/", json=order_data)
        
        if response.status_code == 200:
            order = response.json()
            print(f"   ✅ Order created: ID {order['order_id']}, Status: {order['status']}")
            print(f"   Assigned Bot: {order.get('assigned_bot_id', 'None')}")
            
            # Check order details in database
            conn = sqlite3.connect("autostore.db")
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, status, assigned_bot_id FROM orders WHERE id = ?", (order['order_id'],))
            order_db = cursor.fetchone()
            if order_db:
                print(f"   DB Order {order_db[0]}: Status={order_db[1]}, Bot={order_db[2]}")
            
            # Check bot status after order creation
            cursor.execute("SELECT id, status, assigned_order_id FROM bots")
            bots_db = cursor.fetchall()
            print("   Bot status after order creation:")
            for bot in bots_db:
                print(f"      Bot {bot[0]}: Status={bot[1]}, Order={bot[2]}")
            
            conn.close()
            
        else:
            print(f"   ❌ Failed to create order: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error creating order: {e}")

if __name__ == "__main__":
    debug_order_assignment() 