#!/usr/bin/env python3
"""
Remove duplicate products from SQLite database.
Keeps only one product per name, updates references in bins, and deletes duplicates.
"""

import sqlite3
from collections import defaultdict

def remove_duplicates():
    conn = sqlite3.connect("autostore.db")
    cursor = conn.cursor()
    
    print("🔍 Finding duplicate products...")
    # Find all products grouped by name
    cursor.execute("SELECT id, name FROM products")
    products = cursor.fetchall()
    name_to_ids = defaultdict(list)
    for prod_id, name in products:
        name_to_ids[name].append(prod_id)
    
    duplicates = {name: ids for name, ids in name_to_ids.items() if len(ids) > 1}
    print(f"Found {len(duplicates)} duplicate product names.")
    
    for name, ids in duplicates.items():
        ids.sort()
        keep_id = ids[0]
        remove_ids = ids[1:]
        print(f"\nKeeping: {name} (ID {keep_id}), Removing: {remove_ids}")
        # Update bins table: replace removed product_ids with keep_id
        # bins.product_ids is assumed to be a JSON array of IDs as string
        for rid in remove_ids:
            # Update bins: replace rid with keep_id in product_ids array
            cursor.execute("SELECT id, product_ids FROM bins WHERE instr(product_ids, ?) > 0", (str(rid),))
            bins = cursor.fetchall()
            for bin_id, prod_ids_json in bins:
                # Replace rid with keep_id in the JSON string
                new_json = prod_ids_json.replace(str(rid), str(keep_id))
                cursor.execute("UPDATE bins SET product_ids = ? WHERE id = ?", (new_json, bin_id))
        # Delete duplicate products
        cursor.executemany("DELETE FROM products WHERE id = ?", [(rid,) for rid in remove_ids])
    conn.commit()
    print("\n✅ Duplicate removal complete. Each product now appears only once.")
    conn.close()

if __name__ == "__main__":
    remove_duplicates() 