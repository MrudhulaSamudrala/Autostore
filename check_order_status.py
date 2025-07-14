#!/usr/bin/env python3
"""
Script to check current order and bot status
"""

import requests
import sqlite3

def check_status():
    """Check current order and bot status"""
    
    print("🔍 Checking Current Status")
    print("=" * 50)
    
    # Check orders
    try:
        response = requests.get("http://127.0.0.1:8000/orders/")
        if response.status_code == 200:
            orders = response.json()
            print("\n📋 Orders:")
            for order in orders[-5:]:  # Show last 5 orders
                print(f"   Order {order['id']}: Status={order['status']}, Bot={order.get('assigned_bot_id', 'None')}")
                if order.get('items'):
                    print(f"      Items: {len(order['items'])}")
        else:
            print(f"❌ Failed to get orders: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting orders: {e}")
    
    # Check bots
    try:
        response = requests.get("http://127.0.0.1:8000/bots/")
        if response.status_code == 200:
            bots = response.json()
            print("\n🤖 Bots:")
            for bot in bots:
                status = bot.get('status', 'unknown')
                pos = f"({bot.get('x', 0)}, {bot.get('y', 0)}, {bot.get('z', 0)})"
                carried = bot.get('carried_bin_id')
                order_id = bot.get('assigned_order_id')
                
                print(f"   Bot {bot['id']}: {status} at {pos}")
                if carried:
                    print(f"      🎒 Carrying Bin: {carried}")
                if order_id:
                    print(f"      📋 Order: {order_id}")
        else:
            print(f"❌ Failed to get bots: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting bots: {e}")
    
    # Check database directly
    print("\n🗄️ Database Check:")
    try:
        conn = sqlite3.connect("autostore.db")
        cursor = conn.cursor()
        
        # Check orders
        cursor.execute("SELECT id, status, assigned_bot_id FROM orders ORDER BY id DESC LIMIT 5")
        orders = cursor.fetchall()
        print("   Orders in DB:")
        for order in orders:
            print(f"      Order {order[0]}: Status={order[1]}, Bot={order[2]}")
        
        # Check bots
        cursor.execute("SELECT id, status, assigned_order_id, carried_bin_id, x, y, current_location_z FROM bots")
        bots = cursor.fetchall()
        print("   Bots in DB:")
        for bot in bots:
            print(f"      Bot {bot[0]}: Status={bot[1]}, Order={bot[2]}, Carried={bot[3]}, Pos=({bot[4]}, {bot[5]}, {bot[6]})")
        
        # Check bins
        cursor.execute("SELECT id, status, x, y, z_location FROM bins WHERE status != 'available' LIMIT 10")
        bins = cursor.fetchall()
        print("   Non-available bins:")
        for bin in bins:
            print(f"      Bin {bin[0]}: Status={bin[1]}, Pos=({bin[2]}, {bin[3]}, {bin[4]})")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_status() 