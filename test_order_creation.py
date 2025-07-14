#!/usr/bin/env python3
"""
Simple script to test order creation and observe picking logic
"""

import requests
import json
import time

def test_order_creation():
    """Create an order and monitor the picking process"""
    
    print("🧪 Testing Order Creation and Picking Logic")
    print("=" * 50)
    
    # Create a simple order
    order_data = {
        "items": [
            {"product_id": 1, "quantity": 1}
        ]
    }
    
    try:
        print("📦 Creating order...")
        response = requests.post("http://127.0.0.1:8000/orders/", json=order_data)
        
        if response.status_code == 200:
            order = response.json()
            print(f"✅ Order created: ID {order['order_id']}, Status: {order['status']}")
            
            # Monitor bot status for 10 seconds
            print("\n🤖 Monitoring bot status for 10 seconds...")
            for i in range(10):
                time.sleep(1)
                
                try:
                    bot_response = requests.get("http://127.0.0.1:8000/bots/")
                    if bot_response.status_code == 200:
                        bots = bot_response.json()
                        print(f"\n--- Second {i+1} ---")
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
                        print(f"❌ Failed to get bots: {bot_response.status_code}")
                except Exception as e:
                    print(f"❌ Error getting bots: {e}")
            
            print("\n✅ Monitoring complete!")
            
        else:
            print(f"❌ Failed to create order: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_order_creation() 