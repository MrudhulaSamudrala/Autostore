#!/usr/bin/env python3
"""
Update Product Prices in SQLite Database
This script sets the price equal to the quantity for all products.
"""

import sqlite3

def update_prices():
    """Update product prices to match quantities"""
    
    # Connect to SQLite database
    conn = sqlite3.connect("autostore.db")
    cursor = conn.cursor()
    
    print("🔄 Updating product prices to match quantities...")
    
    try:
        # Get all products with their current prices and quantities
        cursor.execute("SELECT id, name, price, quantity FROM products")
        products = cursor.fetchall()
        
        updated_count = 0
        for product_id, name, old_price, quantity in products:
            # Set price equal to quantity
            new_price = quantity
            
            cursor.execute("""
                UPDATE products SET price = ? WHERE id = ?
            """, (new_price, product_id))
            
            print(f"   ✅ Product {product_id}: {name}")
            print(f"      Old price: {old_price} → New price: {new_price}")
            updated_count += 1
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ Updated {updated_count} products!")
        print(f"📊 All prices now match their quantities")
        
        # Show some examples
        print(f"\n📋 Sample of updated products:")
        cursor.execute("SELECT id, name, price, quantity FROM products LIMIT 5")
        samples = cursor.fetchall()
        for product_id, name, price, quantity in samples:
            print(f"   Product {product_id}: {name}")
            print(f"      Price: {price}, Quantity: {quantity}")
        
        conn.close()
        print(f"\n🚀 Database updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating prices: {e}")
        conn.close()

if __name__ == "__main__":
    update_prices() 