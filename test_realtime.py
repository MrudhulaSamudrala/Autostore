import requests
import json
import time

def test_realtime_bot_tracking():
    """Test the real-time bot tracking functionality"""
    
    # Test 1: Get current bot status
    print("=== Testing Bot Status ===")
    response = requests.get("http://localhost:8000/bots")
    bots = response.json()
    print(f"Current bots: {json.dumps(bots, indent=2)}")
    
    # Test 2: Create an order to assign a bot
    print("\n=== Testing Order Creation ===")
    order_data = {
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1}
        ]
    }
    
    response = requests.post("http://localhost:8000/orders/", json=order_data)
    order = response.json()
    print(f"Created order: {json.dumps(order, indent=2)}")
    
    # Test 3: Check bot status after order assignment
    print("\n=== Testing Bot Assignment ===")
    time.sleep(1)  # Wait for bot assignment
    response = requests.get("http://localhost:8000/bots")
    bots = response.json()
    print(f"Bots after order assignment: {json.dumps(bots, indent=2)}")
    
    # Test 4: Check orders
    print("\n=== Testing Orders ===")
    response = requests.get("http://localhost:8000/orders/")
    orders = response.json()
    print(f"Orders: {json.dumps(orders, indent=2)}")

if __name__ == "__main__":
    test_realtime_bot_tracking() 