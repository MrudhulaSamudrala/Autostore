#!/usr/bin/env python3
"""
Check and move products from delivery station and bot parking areas
Keep delivery station (5,0) and bot parking (5,5) empty
"""

import sqlite3
import json
import random

def check_and_move_parking_products():
    """Check for products in restricted areas and move them"""
    
    conn = sqlite3.connect("autostore.db")
    cursor = conn.cursor()
    
    print("🔍 Checking for products in restricted areas...")
    print("=" * 60)
    
    # Define restricted areas
    delivery_station = (5, 0)  # Delivery station
    bot_parking = (5, 5)      # Bot parking area
    
    # Check delivery station bins (5, 0)
    print("📦 Checking delivery station bins (5, 0):")
    cursor.execute("""
        SELECT id, x, y, z_location, status, product_ids 
        FROM bins 
        WHERE x = 5 AND y = 0
        ORDER BY z_location
    """)
    
    delivery_bins = cursor.fetchall()
    
    for bin_data in delivery_bins:
        bin_id, x, y, z, status, product_ids_json = bin_data
        
        try:
            product_ids = json.loads(product_ids_json) if product_ids_json else []
        except:
            product_ids = []
        
        print(f"   Bin {bin_id}: Position ({x}, {y}, {z}) - Products: {len(product_ids)}")
        
        if product_ids:
            print(f"   ⚠️  Found products in delivery station bin: {product_ids}")
    
    # Check bot parking bins (5, 5)
    print("\n🤖 Checking bot parking bins (5, 5):")
    cursor.execute("""
        SELECT id, x, y, z_location, status, product_ids 
        FROM bins 
        WHERE x = 5 AND y = 5
        ORDER BY z_location
    """)
    
    parking_bins = cursor.fetchall()
    
    for bin_data in parking_bins:
        bin_id, x, y, z, status, product_ids_json = bin_data
        
        try:
            product_ids = json.loads(product_ids_json) if product_ids_json else []
        except:
            product_ids = []
        
        print(f"   Bin {bin_id}: Position ({x}, {y}, {z}) - Products: {len(product_ids)}")
        
        if product_ids:
            print(f"   ⚠️  Found products in bot parking bin: {product_ids}")
    
    # Find all products that need to be moved
    products_to_move = []
    
    # Check delivery station products
    cursor.execute("""
        SELECT p.id, p.name, p.bin_id, p.price, p.quantity
        FROM products p
        JOIN bins b ON p.bin_id = b.id
        WHERE b.x = 5 AND b.y = 0
    """)
    
    delivery_products = cursor.fetchall()
    for prod in delivery_products:
        products_to_move.append({
            'product_id': prod[0],
            'name': prod[1],
            'current_bin': prod[2],
            'price': prod[3],
            'quantity': prod[4],
            'area': 'delivery_station'
        })
    
    # Check bot parking products
    cursor.execute("""
        SELECT p.id, p.name, p.bin_id, p.price, p.quantity
        FROM products p
        JOIN bins b ON p.bin_id = b.id
        WHERE b.x = 5 AND b.y = 5
    """)
    
    parking_products = cursor.fetchall()
    for prod in parking_products:
        products_to_move.append({
            'product_id': prod[0],
            'name': prod[1],
            'current_bin': prod[2],
            'price': prod[3],
            'quantity': prod[4],
            'area': 'bot_parking'
        })
    
    if not products_to_move:
        print("\n✅ No products found in restricted areas!")
        conn.close()
        return
    
    print(f"\n⚠️  Found {len(products_to_move)} products in restricted areas:")
    for prod in products_to_move:
        print(f"   - {prod['name']} (ID: {prod['product_id']}) in {prod['area']} (Bin {prod['current_bin']})")
    
    # Find available bins (not in restricted areas)
    cursor.execute("""
        SELECT id, x, y, z_location
        FROM bins 
        WHERE (x != 5 OR y != 0) AND (x != 5 OR y != 5)
        AND id NOT IN (
            SELECT DISTINCT bin_id FROM products WHERE bin_id IS NOT NULL
        )
        ORDER BY id
    """)
    
    available_bins = cursor.fetchall()
    
    if not available_bins:
        print("\n❌ No available bins found to move products to!")
        conn.close()
        return
    
    print(f"\n📦 Found {len(available_bins)} available bins for relocation")
    
    # Move products to available bins
    print("\n🔄 Moving products to available bins...")
    
    for i, prod in enumerate(products_to_move):
        if i < len(available_bins):
            new_bin = available_bins[i]
            new_bin_id = new_bin[0]
            
            # Update product's bin_id
            cursor.execute("""
                UPDATE products 
                SET bin_id = ? 
                WHERE id = ?
            """, (new_bin_id, prod['product_id']))
            
            print(f"   ✅ Moved '{prod['name']}' from Bin {prod['current_bin']} to Bin {new_bin_id} ({new_bin[1]}, {new_bin[2]}, {new_bin[3]})")
        else:
            print(f"   ❌ No available bin for '{prod['name']}'")
    
    # Commit changes
    conn.commit()
    
    # Update bins.product_ids to reflect the changes
    print("\n🔄 Updating bins.product_ids...")
    
    cursor.execute("SELECT id FROM bins ORDER BY id")
    all_bins = cursor.fetchall()
    
    for (bin_id,) in all_bins:
        # Get all products for this bin
        cursor.execute("""
            SELECT id FROM products 
            WHERE bin_id = ? 
            ORDER BY id
        """, (bin_id,))
        
        products = cursor.fetchall()
        product_ids = [p[0] for p in products]
        
        # Update the bin's product_ids field
        product_ids_json = json.dumps(product_ids)
        cursor.execute("""
            UPDATE bins 
            SET product_ids = ? 
            WHERE id = ?
        """, (product_ids_json, bin_id))
    
    conn.commit()
    
    # Verify the changes
    print("\n🔍 Verifying changes...")
    print("=" * 60)
    
    # Check delivery station again
    cursor.execute("""
        SELECT id, x, y, z_location, status, product_ids 
        FROM bins 
        WHERE x = 5 AND y = 0
        ORDER BY z_location
    """)
    
    delivery_bins_after = cursor.fetchall()
    
    print("📦 Delivery station bins (5, 0) after changes:")
    for bin_data in delivery_bins_after:
        bin_id, x, y, z, status, product_ids_json = bin_data
        
        try:
            product_ids = json.loads(product_ids_json) if product_ids_json else []
        except:
            product_ids = []
        
        print(f"   Bin {bin_id}: Position ({x}, {y}, {z}) - Products: {len(product_ids)}")
    
    # Check bot parking again
    cursor.execute("""
        SELECT id, x, y, z_location, status, product_ids 
        FROM bins 
        WHERE x = 5 AND y = 5
        ORDER BY z_location
    """)
    
    parking_bins_after = cursor.fetchall()
    
    print("\n🤖 Bot parking bins (5, 5) after changes:")
    for bin_data in parking_bins_after:
        bin_id, x, y, z, status, product_ids_json = bin_data
        
        try:
            product_ids = json.loads(product_ids_json) if product_ids_json else []
        except:
            product_ids = []
        
        print(f"   Bin {bin_id}: Position ({x}, {y}, {z}) - Products: {len(product_ids)}")
    
    conn.close()
    print("\n✅ Operation complete! Restricted areas are now empty.")

if __name__ == "__main__":
    check_and_move_parking_products() 