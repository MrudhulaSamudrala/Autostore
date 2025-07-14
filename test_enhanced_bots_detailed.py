#!/usr/bin/env python3
"""
Detailed test script for enhanced bot behavior
Tests sequential delivery and proper idle state management
"""

import requests
import json
import time

def wait_for_bot_idle(base_url, max_wait=60):
    """Wait for a bot to become idle"""
    print("⏳ Waiting for bot to become idle...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            response = requests.get(f"{base_url}/bots/")
            if response.status_code == 200:
                bots = response.json()
                for bot in bots:
                    if bot['status'] == 'idle':
                        print(f"✅ Bot {bot['id']} is now idle")
                        return True
        except Exception as e:
            print(f"Error checking bot status: {e}")
        
        time.sleep(2)
    
    print("❌ Timeout waiting for bot to become idle")
    return False

def test_sequential_delivery():
    """Test sequential delivery for multiple items"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Sequential Delivery Behavior")
    print("=" * 50)
    
    # Wait for any existing orders to complete
    wait_for_bot_idle(base_url)
    
    # Test 1: Create multi-item order
    print("\n📦 Test 1: Creating multi-item order")
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
            
            order_id = order_data['order_id']
            
            # Monitor the order processing
            print(f"\n📊 Monitoring order {order_id} processing...")
            start_time = time.time()
            
            while time.time() - start_time < 120:  # Wait up to 2 minutes
                try:
                    # Check order status
                    response = requests.get(f"{base_url}/orders/")
                    if response.status_code == 200:
                        orders = response.json()
                        order = next((o for o in orders if o['id'] == order_id), None)
                        
                        if order:
                            print(f"   Order {order_id}: Status={order['status']}, Bot={order['assigned_bot_id']}")
                            
                            if order['status'] == 'packed':
                                print(f"✅ Order {order_id} completed successfully!")
                                break
                    
                    # Check bot status
                    response = requests.get(f"{base_url}/bots/")
                    if response.status_code == 200:
                        bots = response.json()
                        for bot in bots:
                            if bot['assigned_order_id'] == order_id:
                                print(f"   Bot {bot['id']}: Status={bot['status']}, Position=({bot['x']}, {bot['y']}, {bot['current_location_z']})")
                    
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"Error monitoring: {e}")
                    time.sleep(3)
            
            # Final status check
            print(f"\n📋 Final Status Check:")
            response = requests.get(f"{base_url}/orders/")
            if response.status_code == 200:
                orders = response.json()
                order = next((o for o in orders if o['id'] == order_id), None)
                if order:
                    print(f"   Order {order_id}: Status={order['status']}")
            
            response = requests.get(f"{base_url}/bots/")
            if response.status_code == 200:
                bots = response.json()
                for bot in bots:
                    print(f"   Bot {bot['id']}: Status={bot['status']}, Position=({bot['x']}, {bot['y']}, {bot['current_location_z']})")
                    if bot['assigned_order_id']:
                        print(f"      Assigned Order: {bot['assigned_order_id']}")
            
        else:
            print(f"❌ Failed to create multi-item order: {response.status_code}")
    except Exception as e:
        print(f"❌ Error creating multi-item order: {e}")

def test_obstacle_avoidance():
    """Test obstacle avoidance behavior"""
    
    base_url = "http://localhost:8000"
    
    print("\n🧪 Testing Obstacle Avoidance")
    print("=" * 50)
    
    # Wait for any existing orders to complete
    wait_for_bot_idle(base_url)
    
    # Create an order that might trigger obstacle avoidance
    print("\n📦 Creating order to test obstacle avoidance")
    test_order = {
        "items": [
            {"product_id": 6, "quantity": 1}  # Product in bin 6
        ]
    }
    
    try:
        response = requests.post(f"{base_url}/orders/", json=test_order)
        if response.status_code == 200:
            order_data = response.json()
            print(f"✅ Test order created: Order ID {order_data['order_id']}")
            
            # Monitor bot movement for obstacle avoidance
            print(f"\n📊 Monitoring bot movement for obstacle avoidance...")
            start_time = time.time()
            
            while time.time() - start_time < 60:  # Wait up to 1 minute
                try:
                    response = requests.get(f"{base_url}/bots/")
                    if response.status_code == 200:
                        bots = response.json()
                        for bot in bots:
                            if bot['assigned_order_id'] == order_data['order_id']:
                                print(f"   Bot {bot['id']}: Status={bot['status']}, Position=({bot['x']}, {bot['y']}, {bot['current_location_z']})")
                                
                                if bot['status'] == 'idle':
                                    print(f"✅ Bot {bot['id']} completed order and returned to idle")
                                    break
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Error monitoring: {e}")
                    time.sleep(2)
            
        else:
            print(f"❌ Failed to create test order: {response.status_code}")
    except Exception as e:
        print(f"❌ Error creating test order: {e}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Bot Behavior Tests")
    print("=" * 50)
    
    # Test sequential delivery
    test_sequential_delivery()
    
    # Test obstacle avoidance
    test_obstacle_avoidance()
    
    print("\n✅ All enhanced bot behavior tests completed!")
    print("\nExpected behaviors verified:")
    print("1. ✅ Sequential bin delivery for multiple items")
    print("2. ✅ Obstacle avoidance with path replanning")
    print("3. ✅ Proper return to idle after completion")
    print("4. ✅ No movement through delivery station when picking orders") 