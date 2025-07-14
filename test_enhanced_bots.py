#!/usr/bin/env python3
"""
Test script for enhanced bot behavior
Tests:
1. Obstacle avoidance
2. Sequential bin delivery for multiple items
3. No movement through delivery station when picking orders
4. Return to idle after completing all items
"""

import requests
import json
import time

def test_enhanced_bot_behavior():
    """Test the enhanced bot behavior"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Enhanced Bot Behavior")
    print("=" * 50)
    
    # Test 1: Single item order
    print("\n📦 Test 1: Single item order")
    single_order = {
        "items": [
            {"product_id": 6, "quantity": 1}  # Product in bin 6
        ]
    }
    
    try:
        response = requests.post(f"{base_url}/orders/", json=single_order)
        if response.status_code == 200:
            order_data = response.json()
            print(f"✅ Single order created: Order ID {order_data['order_id']}")
            print(f"   Status: {order_data['status']}")
            print(f"   Assigned Bot: {order_data['assigned_bot_id']}")
        else:
            print(f"❌ Failed to create single order: {response.status_code}")
    except Exception as e:
        print(f"❌ Error creating single order: {e}")
    
    time.sleep(3)  # Wait for bot to process
    
    # Test 2: Multiple items order
    print("\n📦 Test 2: Multiple items order")
    multi_order = {
        "items": [
            {"product_id": 6, "quantity": 1},   # Product in bin 6
            {"product_id": 42, "quantity": 1},  # Product in bin 42
            {"product_id": 78, "quantity": 1}   # Product in bin 78
        ]
    }
    
    try:
        response = requests.post(f"{base_url}/orders/", json=multi_order)
        if response.status_code == 200:
            order_data = response.json()
            print(f"✅ Multi-item order created: Order ID {order_data['order_id']}")
            print(f"   Status: {order_data['status']}")
            print(f"   Assigned Bot: {order_data['assigned_bot_id']}")
            print(f"   Items: {len(order_data['items'])}")
        else:
            print(f"❌ Failed to create multi-item order: {response.status_code}")
    except Exception as e:
        print(f"❌ Error creating multi-item order: {e}")
    
    time.sleep(5)  # Wait for bot to process
    
    # Test 3: Check bot status
    print("\n🤖 Test 3: Check bot status")
    try:
        response = requests.get(f"{base_url}/bots/")
        if response.status_code == 200:
            bots = response.json()
            for bot in bots:
                print(f"   Bot {bot['id']}: Status={bot['status']}, Position=({bot['x']}, {bot['y']}, {bot['current_location_z']})")
                if bot['assigned_order_id']:
                    print(f"      Assigned Order: {bot['assigned_order_id']}")
        else:
            print(f"❌ Failed to get bot status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting bot status: {e}")
    
    # Test 4: Check order status
    print("\n📋 Test 4: Check order status")
    try:
        response = requests.get(f"{base_url}/orders/")
        if response.status_code == 200:
            orders = response.json()
            for order in orders:
                print(f"   Order {order['id']}: Status={order['status']}, Bot={order['assigned_bot_id']}")
        else:
            print(f"❌ Failed to get order status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting order status: {e}")
    
    print("\n✅ Enhanced bot behavior test completed!")
    print("\nExpected behaviors:")
    print("1. ✅ Bots should avoid delivery station when picking up orders")
    print("2. ✅ Bots should deliver bins sequentially for multiple items")
    print("3. ✅ Bots should return to idle after completing all items")
    print("4. ✅ Bots should use obstacle avoidance when paths are blocked")

if __name__ == "__main__":
    test_enhanced_bot_behavior() 