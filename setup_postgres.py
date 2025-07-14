#!/usr/bin/env python3
"""
PostgreSQL Setup for AutoStore
This script sets up the PostgreSQL database and runs the setup queries.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json

def setup_postgres_database():
    """Setup PostgreSQL database and run setup queries"""
    print("🔄 Setting up PostgreSQL Database for AutoStore...")
    
    # Database configuration
    DB_NAME = "autostore"
    DB_USER = "postgres"
    DB_PASSWORD = "post"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    
    try:
        # Connect to PostgreSQL server (not to a specific database)
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database="postgres"  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        print("1. Creating database...")
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"   ✅ Database '{DB_NAME}' created successfully")
        else:
            print(f"   ✅ Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
        
        # Connect to the new database
        conn = psycopg2.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Create tables
        print("2. Creating tables...")
        
        # Create bots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bots (
                id INTEGER PRIMARY KEY,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                current_location_z INTEGER NOT NULL,
                status VARCHAR(50) NOT NULL,
                assigned_order_id INTEGER,
                destination_bin JSONB,
                path JSONB
            )
        """)
        
        # Create bins table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bins (
                id INTEGER PRIMARY KEY,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                z_location INTEGER NOT NULL,
                product_ids JSONB NOT NULL,
                status VARCHAR(50) NOT NULL
            )
        """)
        
        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                bin_id INTEGER NOT NULL,
                last_refilled TIMESTAMP,
                sale_count INTEGER DEFAULT 0,
                price DECIMAL(10,2) NOT NULL,
                image_url VARCHAR(500),
                category VARCHAR(100),
                quantity INTEGER DEFAULT 0
            )
        """)
        
        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                status VARCHAR(50) NOT NULL,
                total_amount DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create bin_locks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bin_locks (
                id INTEGER PRIMARY KEY,
                bin_id INTEGER NOT NULL,
                locked_by INTEGER,
                locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                waiting_list JSONB
            )
        """)
        
        print("   ✅ Tables created successfully")
        
        # Clear existing data
        print("3. Clearing existing data...")
        cursor.execute("DELETE FROM bin_locks")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM bots")
        cursor.execute("DELETE FROM bins")
        print("   ✅ Existing data cleared")
        
        # Insert bots
        print("4. Creating bots...")
        cursor.execute("""
            INSERT INTO bots (id, x, y, current_location_z, status) VALUES
            (1, 5, 5, 1, 'idle'),
            (2, 5, 5, 4, 'idle')
        """)
        print("   ✅ Created 2 bots")
        
        # Insert bins (6x6x6 grid = 216 bins)
        print("5. Creating bins...")
        bins_created = 0
        for x in range(6):
            for y in range(6):
                for z in range(6):
                    bin_id = x + y * 6 + z * 36 + 1
                    cursor.execute("""
                        INSERT INTO bins (id, x, y, z_location, product_ids, status) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (bin_id, x, y, z, json.dumps([]), "available"))
                    bins_created += 1
        
        print(f"   ✅ Created {bins_created} bins (6x6x6 grid)")
        
        # Insert sample products
        print("6. Creating sample products...")
        products_data = [
            (1, "Apple", 1, 1.99, 50),
            (2, "Banana", 2, 0.99, 75),
            (3, "Orange", 3, 2.49, 30),
            (4, "Milk", 4, 3.99, 25),
            (5, "Bread", 5, 2.99, 40)
        ]
        
        for product_id, name, bin_id, price, quantity in products_data:
            cursor.execute("""
                INSERT INTO products (id, name, bin_id, price, quantity) 
                VALUES (%s, %s, %s, %s, %s)
            """, (product_id, name, bin_id, price, quantity))
        
        print(f"   ✅ Created {len(products_data)} sample products")
        
        # Commit all changes
        conn.commit()
        
        # Show summary
        print("\n📊 Database Summary:")
        cursor.execute("SELECT COUNT(*) FROM bots")
        bots_count = cursor.fetchone()[0]
        print(f"   Bots: {bots_count}")
        
        cursor.execute("SELECT COUNT(*) FROM bins")
        bins_count = cursor.fetchone()[0]
        print(f"   Bins: {bins_count}")
        
        cursor.execute("SELECT COUNT(*) FROM products")
        products_count = cursor.fetchone()[0]
        print(f"   Products: {products_count}")
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        orders_count = cursor.fetchone()[0]
        print(f"   Orders: {orders_count}")
        
        print("\n✅ PostgreSQL database setup complete!")
        print("🚀 You can now start your application:")
        print("   uvicorn main:app --reload")
        
    except Exception as e:
        print(f"❌ Error setting up PostgreSQL database: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_postgres_database() 