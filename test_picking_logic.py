#!/usr/bin/env python3
"""
Test script to verify bin picking logic
"""

import requests
import json
import time
import sqlite3

def test_picking_logic():
    """Test the bin picking and carrying functionality"""
    
    print("🧪 Testing Bin Picking Logic")
    print("=" * 50)
    
    # 1. Create a single item order
    print("\n📦 Test 1: Creating single item order...")
    order_data = {
        "items": [
            {"product_id": 1, "quantity": 1}
        ]
    }
    
    try:
        response = requests.post("http://127.0.0.1:8000/orders/", json=order_data)
        if response.status_code == 200:
            order = response.json()
            print(f"✅ Order created: ID {order['order_id']}, Status: {order['status']}")
            order_id = order['order_id']
        else:
            print(f"❌ Failed to create order: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        return
    
    # 2. Check bot status after a few seconds
    print("\n🤖 Test 2: Checking bot status...")
    time.sleep(3)
    
    try:
        response = requests.get("http://127.0.0.1:8000/bots/")
        if response.status_code == 200:
            bots = response.json()
            print("Bot Status:")
            for bot in bots:
                print(f"   Bot {bot['id']}: Status={bot['status']}, Position=({bot['x']}, {bot['y']}, {bot.get('z', bot.get('current_location_z', 0))})")
                if bot.get('carried_bin_id'):
                    print(f"      🎒 Carrying Bin: {bot['carried_bin_id']}")
                if bot.get('assigned_order_id'):
                    print(f"      📋 Assigned Order: {bot['assigned_order_id']}")
        else:
            print(f"❌ Failed to get bots: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting bots: {e}")
    
    # 3. Check order status
    print("\n📋 Test 3: Checking order status...")
    try:
        response = requests.get("http://127.0.0.1:8000/orders/")
        if response.status_code == 200:
            orders = response.json()
            print("Order Status:")
            for order in orders[-5:]:  # Show last 5 orders
                print(f"   Order {order['id']}: Status={order['status']}, Bot={order.get('assigned_bot_id', 'None')}")
        else:
            print(f"❌ Failed to get orders: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting orders: {e}")
    
    # 4. Check database directly for carried bins
    print("\n🗄️ Test 4: Checking database for carried bins...")
    try:
        conn = sqlite3.connect("autostore.db")
        cursor = conn.cursor()
        
        # Check bots with carried bins
        cursor.execute("SELECT id, status, carried_bin_id, x, y, current_location_z FROM bots WHERE carried_bin_id IS NOT NULL")
        carried_bots = cursor.fetchall()
        
        if carried_bots:
            print("Bots carrying bins:")
            for bot in carried_bots:
                print(f"   Bot {bot[0]}: Status={bot[1]}, Carrying Bin={bot[2]}, Position=({bot[3]}, {bot[4]}, {bot[5]})")
        else:
            print("   No bots are currently carrying bins")
        
        # Check bin status
        cursor.execute("SELECT id, x, y, z_location, status FROM bins WHERE status = 'in-use'")
        in_use_bins = cursor.fetchall()
        
        if in_use_bins:
            print("Bins in use:")
            for bin in in_use_bins:
                print(f"   Bin {bin[0]}: Position=({bin[1]}, {bin[2]}, {bin[3]}), Status={bin[4]}")
        else:
            print("   No bins are currently in use")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    
    print("\n✅ Picking logic test completed!")
    print("\nExpected behaviors:")
    print("1. ✅ Bot should pick up bin when reaching bin location")
    print("2. ✅ Bin should disappear from grid when carried")
    print("3. ✅ Bot should show carrying status")
    print("4. ✅ Bin should reappear when dropped at delivery station")

if __name__ == "__main__":
    test_picking_logic() 