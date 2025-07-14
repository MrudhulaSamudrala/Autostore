#!/usr/bin/env python3
"""
Script to check bin locks and debug bot assignment
"""

import sqlite3

def check_bin_locks():
    """Check bin locks and debug bot assignment"""
    
    print("🔒 Checking Bin Locks")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("autostore.db")
        cursor = conn.cursor()
        
        # Check if bin_locks table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bin_locks'")
        if not cursor.fetchone():
            print("❌ bin_locks table does not exist!")
            return
        
        # Check bin locks
        cursor.execute("SELECT id, used_by, status, waiting_list FROM bin_locks")
        locks = cursor.fetchall()
        print("🔒 Bin Locks:")
        if locks:
            for lock in locks:
                print(f"   Bin {lock[0]}: Used by={lock[1]}, Status={lock[2]}, Waiting={lock[3]}")
        else:
            print("   No bin locks found")
        
        # Check bots
        cursor.execute("SELECT id, status, assigned_order_id, carried_bin_id FROM bots")
        bots = cursor.fetchall()
        print("\n🤖 Bots:")
        for bot in bots:
            print(f"   Bot {bot[0]}: Status={bot[1]}, Order={bot[2]}, Carried={bot[3]}")
        
        # Check orders
        cursor.execute("SELECT id, status, assigned_bot_id FROM orders ORDER BY id DESC LIMIT 5")
        orders = cursor.fetchall()
        print("\n📋 Recent Orders:")
        for order in orders:
            print(f"   Order {order[0]}: Status={order[1]}, Bot={order[2]}")
        
        # Check bins
        cursor.execute("SELECT id, status, x, y FROM bins WHERE id <= 5")
        bins = cursor.fetchall()
        print("\n📦 Bins (first 5):")
        for bin in bins:
            print(f"   Bin {bin[0]}: Status={bin[1]}, Pos=({bin[2]}, {bin[3]})")
        
        # Test the lock_bin function logic
        print("\n🧪 Testing lock_bin logic for Bin 1:")
        
        # Check if bin 1 has a lock
        cursor.execute("SELECT id, used_by, status, waiting_list FROM bin_locks WHERE id = 1")
        bin1_lock = cursor.fetchone()
        
        if bin1_lock:
            print(f"   Bin 1 lock exists: Used by={bin1_lock[1]}, Status={bin1_lock[2]}")
            if bin1_lock[2] == "Available":
                print("   ✅ Bin 1 should be lockable")
            else:
                print("   ❌ Bin 1 is already locked")
        else:
            print("   ✅ Bin 1 has no lock - should be lockable")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_bin_locks() 