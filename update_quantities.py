#!/usr/bin/env python3
"""
Update Product Quantities in SQLite Database
This script sets all product quantities to 25.
"""

import sqlite3

def update_quantities():
    """Update all product quantities to 25"""
    
    # Connect to SQLite database
    conn = sqlite3.connect("autostore.db")
    cursor = conn.cursor()
    
    print("🔄 Updating all product quantities to 25...")
    
    try:
        # Get all products with their current quantities
        cursor.execute("SELECT id, name, quantity FROM products")
        products = cursor.fetchall()
        
        updated_count = 0
        for product_id, name, old_quantity in products:
            # Set quantity to 25
            new_quantity = 25
            
            # Update the product
            cursor.execute(
                "UPDATE products SET quantity = ? WHERE id = ?", 
                (new_quantity, product_id)
            )
            
            print(f"   ✓ {name}: {old_quantity} → {new_quantity}")
            updated_count += 1
        
        # Commit the changes
        conn.commit()
        
        print(f"\n✅ Successfully updated {updated_count} products!")
        print("   All quantities are now set to 25")
        
    except Exception as e:
        print(f"❌ Error updating quantities: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_quantities() 