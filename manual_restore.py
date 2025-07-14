#!/usr/bin/env python3
"""
Manual Database Restore for AutoStore
Run this script to populate your database with sample data.
"""

import sqlite3
import os

def create_database():
    """Create SQLite database and populate with data"""
    print("🔄 Creating AutoStore Database...")
    
    # Remove existing database if it exists
    if os.path.exists("autostore.db"):
        os.remove("autostore.db")
        print("✅ Removed existing database")
    
    # Create new database
    conn = sqlite3.connect("autostore.db")
    cursor = conn.cursor()
    
    # Create tables
    print("1. Creating tables...")
    
    # Bots table
    cursor.execute("""
        CREATE TABLE bots (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'idle',
            current_x REAL DEFAULT 0.0,
            current_y REAL DEFAULT 0.0,
            current_z REAL DEFAULT 0.0,
            target_x REAL DEFAULT 0.0,
            target_y REAL DEFAULT 0.0,
            target_z REAL DEFAULT 0.0,
            battery_level REAL DEFAULT 100.0,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Bins table
    cursor.execute("""
        CREATE TABLE bins (
            id INTEGER PRIMARY KEY,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            z INTEGER NOT NULL,
            status TEXT DEFAULT 'available',
            product_id INTEGER,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Products table
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER DEFAULT 0,
            sale_count INTEGER DEFAULT 0,
            bin_id INTEGER,
            image_url TEXT,
            category TEXT,
            last_refilled TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bin_id) REFERENCES bins (id)
        )
    """)
    
    # Orders table
    cursor.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            total_amount REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)
    
    print("   ✅ Tables created successfully")
    
    # Insert sample data
    print("2. Inserting sample data...")
    
    # Insert bots
    bots_data = [
        (1, "Bot-001", "idle", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 100.0),
        (2, "Bot-002", "idle", 5.0, 0.0, 0.0, 5.0, 0.0, 0.0, 100.0)
    ]
    cursor.executemany("""
        INSERT INTO bots (id, name, status, current_x, current_y, current_z, 
                         target_x, target_y, target_z, battery_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, bots_data)
    print("   ✅ Created 2 bots")
    
    # Insert bins (6x6x6 grid = 216 bins)
    bins_data = []
    bin_id = 1
    for x in range(6):
        for y in range(6):
            for z in range(6):
                bins_data.append((bin_id, x, y, z, "available", None))
                bin_id += 1
    
    cursor.executemany("""
        INSERT INTO bins (id, x, y, z, status, product_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, bins_data)
    print("   ✅ Created 216 bins (6x6x6 grid)")
    
    # Insert products with bin assignments
    products_data = [
        (1, "Apple", 1.99, 50, 0, 1),
        (2, "Banana", 0.99, 75, 0, 2),
        (3, "Orange", 2.49, 30, 0, 3),
        (4, "Milk", 3.99, 25, 0, 4),
        (5, "Bread", 2.99, 40, 0, 5)
    ]
    cursor.executemany("""
        INSERT INTO products (id, name, price, quantity, sale_count, bin_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, products_data)
    print("   ✅ Created 5 products")
    
    # Insert sample orders
    orders_data = [
        (1, "John Doe", "completed", 5.98, "2024-01-01 10:00:00", "2024-01-01 10:15:00"),
        (2, "Jane Smith", "pending", 3.99, "2024-01-01 11:00:00", None)
    ]
    cursor.executemany("""
        INSERT INTO orders (id, customer_name, status, total_amount, created_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, orders_data)
    print("   ✅ Created 2 sample orders")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print("✅ Database restoration completed successfully!")
    print("📊 Summary:")
    print("   - 2 bots created")
    print("   - 216 bins created (6x6x6 grid)")
    print("   - 5 products created")
    print("   - 2 sample orders created")
    print("\n🚀 You can now start your backend with: uvicorn main:app --reload")

if __name__ == "__main__":
    try:
        create_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please make sure you have write permissions in the current directory.") 