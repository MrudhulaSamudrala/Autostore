#!/usr/bin/env python3
"""
Check for bins containing items at the delivery station position (5, 0)
"""

import sqlite3
import json

def check_delivery_station_bins():
    """Check for bins at delivery station position (5, 0)"""
    
    conn = sqlite3.connect("autostore.db")
    cursor = conn.cursor()
    
    print("🔍 Checking for bins at delivery station position (5, 0)...")
    print("=" * 60)
    
    # Check for bins at delivery station position (5, 0)
    cursor.execute("""
        SELECT id, x, y, z_location, status, product_ids 
        FROM bins 
        WHERE x = 5 AND y = 0
        ORDER BY z_location
    """)
    
    delivery_bins = cursor.fetchall()
    
    if not delivery_bins:
        print("❌ No bins found at delivery station position (5, 0)")
    else:
        print(f"✅ Found {len(delivery_bins)} bins at delivery station position (5, 0):")
        print()
        
        for bin_data in delivery_bins:
            bin_id, x, y, z, status, product_ids_json = bin_data
            
            # Parse product_ids
            try:
                product_ids = json.loads(product_ids_json) if product_ids_json else []
            except:
                product_ids = []
            
            print(f"📦 Bin {bin_id}:")
            print(f"   Position: ({x}, {y}, {z})")
            print(f"   Status: {status}")
            print(f"   Products: {len(product_ids)} items")
            
            if product_ids:
                print(f"   Product IDs: {product_ids}")
                
                # Get product details
                cursor.execute("""
                    SELECT id, name, price, quantity 
                    FROM products 
                    WHERE id IN ({})
                """.format(','.join('?' * len(product_ids))), product_ids)
                
                products = cursor.fetchall()
                if products:
                    print("   Product Details:")
                    for prod_id, name, price, quantity in products:
                        print(f"     - {name}: ${price} (Qty: {quantity})")
            else:
                print("   No products in this bin")
            print()
    
    # Also check for bins with "in-use" status (might be at delivery station)
    print("🔍 Checking for bins with 'in-use' status (potentially at delivery station)...")
    print("=" * 60)
    
    cursor.execute("""
        SELECT id, x, y, z_location, status, product_ids 
        FROM bins 
        WHERE status = 'in-use'
        ORDER BY id
    """)
    
    in_use_bins = cursor.fetchall()
    
    if not in_use_bins:
        print("❌ No bins with 'in-use' status found")
    else:
        print(f"✅ Found {len(in_use_bins)} bins with 'in-use' status:")
        print()
        
        for bin_data in in_use_bins:
            bin_id, x, y, z, status, product_ids_json = bin_data
            
            # Parse product_ids
            try:
                product_ids = json.loads(product_ids_json) if product_ids_json else []
            except:
                product_ids = []
            
            print(f"📦 Bin {bin_id}:")
            print(f"   Position: ({x}, {y}, {z})")
            print(f"   Status: {status}")
            print(f"   Products: {len(product_ids)} items")
            
            if product_ids:
                print(f"   Product IDs: {product_ids}")
                
                # Get product details
                cursor.execute("""
                    SELECT id, name, price, quantity 
                    FROM products 
                    WHERE id IN ({})
                """.format(','.join('?' * len(product_ids))), product_ids)
                
                products = cursor.fetchall()
                if products:
                    print("   Product Details:")
                    for prod_id, name, price, quantity in products:
                        print(f"     - {name}: ${price} (Qty: {quantity})")
            else:
                print("   No products in this bin")
            print()
    
    # Check for any bins with products
    print("🔍 Checking for all bins containing products...")
    print("=" * 60)
    
    cursor.execute("""
        SELECT id, x, y, z_location, status, product_ids 
        FROM bins 
        WHERE product_ids != '[]' AND product_ids IS NOT NULL
        ORDER BY id
    """)
    
    bins_with_products = cursor.fetchall()
    
    if not bins_with_products:
        print("❌ No bins found containing products")
    else:
        print(f"✅ Found {len(bins_with_products)} bins containing products:")
        print()
        
        for bin_data in bins_with_products:
            bin_id, x, y, z, status, product_ids_json = bin_data
            
            # Parse product_ids
            try:
                product_ids = json.loads(product_ids_json) if product_ids_json else []
            except:
                product_ids = []
            
            print(f"📦 Bin {bin_id}:")
            print(f"   Position: ({x}, {y}, {z})")
            print(f"   Status: {status}")
            print(f"   Products: {len(product_ids)} items")
            
            if product_ids:
                print(f"   Product IDs: {product_ids}")
                
                # Get product details
                cursor.execute("""
                    SELECT id, name, price, quantity 
                    FROM products 
                    WHERE id IN ({})
                """.format(','.join('?' * len(product_ids))), product_ids)
                
                products = cursor.fetchall()
                if products:
                    print("   Product Details:")
                    for prod_id, name, price, quantity in products:
                        print(f"     - {name}: ${price} (Qty: {quantity})")
            print()
    
    conn.close()
    print("✅ Check complete!")

if __name__ == "__main__":
    check_delivery_station_bins() 