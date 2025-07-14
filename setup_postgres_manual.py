#!/usr/bin/env python3
"""
PostgreSQL Manual Setup for AutoStore
This script sets up PostgreSQL database and provides manual data insertion.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json
import os

def setup_postgres_database():
    """Setup PostgreSQL database and create tables"""
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
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            print(f"1. Creating database '{DB_NAME}'...")
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print("   ✅ Database created successfully")
        else:
            print(f"1. Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
        
        # Now connect to the autostore database
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
        
        # Bots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bots (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                status VARCHAR(50) DEFAULT 'idle',
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
            CREATE TABLE IF NOT EXISTS bins (
                id SERIAL PRIMARY KEY,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                z INTEGER NOT NULL,
                status VARCHAR(50) DEFAULT 'available',
                product_id INTEGER,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER DEFAULT 0,
                sale_count INTEGER DEFAULT 0,
                bin_id INTEGER,
                image_url TEXT,
                category VARCHAR(100),
                last_refilled TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bin_id) REFERENCES bins (id)
            )
        """)
        
        # Orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                customer_name VARCHAR(200) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                total_amount REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        print("   ✅ Tables created successfully")
        
        # Insert initial data
        print("3. Inserting initial data...")
        
        # Insert bots
        cursor.execute("""
            INSERT INTO bots (name, status, current_x, current_y, current_z, target_x, target_y, target_z, battery_level)
            VALUES 
                ('Bot-001', 'idle', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 100.0),
                ('Bot-002', 'idle', 5.0, 0.0, 0.0, 5.0, 0.0, 0.0, 100.0)
            ON CONFLICT DO NOTHING
        """)
        print("   ✅ Created 2 bots")
        
        # Insert bins (6x6x6 grid = 216 bins)
        for x in range(6):
            for y in range(6):
                for z in range(6):
                    cursor.execute("""
                        INSERT INTO bins (x, y, z, status, product_id)
                        VALUES (%s, %s, %s, 'available', NULL)
                        ON CONFLICT DO NOTHING
                    """, (x, y, z))
        
        print("   ✅ Created 216 bins (6x6x6 grid)")
        
        # Commit and close
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ PostgreSQL setup completed successfully!")
        print("\n📊 Database Summary:")
        print("   - Database: autostore")
        print("   - Host: localhost:5432")
        print("   - User: postgres")
        print("   - 2 bots created")
        print("   - 216 bins created")
        print("\n🔧 Next Steps:")
        print("   1. Run: python add_products_manual.py")
        print("   2. Start backend: uvicorn main:app --reload")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure PostgreSQL is running")
        print("   2. Check if postgres user exists with password 'post'")
        print("   3. Try: pg_ctl -D /path/to/postgres/data start")

if __name__ == "__main__":
    setup_postgres_database() 