#!/usr/bin/env python3
"""
Sync bins.product_ids field with actual products in each bin
This script updates the bins.product_ids JSON field to match the products table
"""

import sqlite3
import json

def sync_bin_product_ids():
    """Sync bins.product_ids with products table"""
    
    conn = sqlite3.connect("autostore.db")
    cursor = conn.cursor()
    
    print("🔄 Syncing bins.product_ids with products table...")
    print("=" * 60)
    
    # Get all bins
    cursor.execute("SELECT id FROM bins ORDER BY id")
    bins = cursor.fetchall()
    
    updated_count = 0
    
    for (bin_id,) in bins:
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
        
        if product_ids:
            print(f"📦 Bin {bin_id}: Updated with {len(product_ids)} products - {product_ids}")
            updated_count += 1
        else:
            print(f"📦 Bin {bin_id}: No products (empty)")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("=" * 60)
    print(f"✅ Sync complete! Updated {updated_count} bins with products.")
    print(f"📊 Total bins processed: {len(bins)}")
    
    # Verify the sync worked for the delivery station bins
    print("\n🔍 Verifying delivery station bins (5, 0):")
    print("=" * 60)
    
    conn = sqlite3.connect("autostore.db")
    cursor = conn.cursor()
    
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
        
        print(f"📦 Bin {bin_id}: Position ({x}, {y}, {z}) - Status: {status}")
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
    
    conn.close()
    print("✅ Verification complete!")

if __name__ == "__main__":
    sync_bin_product_ids() 