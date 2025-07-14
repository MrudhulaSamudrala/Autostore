#!/usr/bin/env python3
"""
Test PostgreSQL Connection
This script tests the connection to PostgreSQL and shows database status.
"""

import psycopg2

def test_connection():
    """Test PostgreSQL connection"""
    print("🔄 Testing PostgreSQL connection...")
    
    try:
        # Test connection to postgres database
        conn = psycopg2.connect(
            user="postgres",
            password="post",
            host="localhost",
            port="5432",
            database="postgres"
        )
        print("✅ Connected to PostgreSQL server")
        conn.close()
        
        # Test connection to autostore database
        conn = psycopg2.connect(
            user="postgres",
            password="post",
            host="localhost",
            port="5432",
            database="autostore"
        )
        print("✅ Connected to autostore database")
        
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        print(f"📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Check data counts
        for table_name in ['bots', 'bins', 'products', 'orders']:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   📈 {table_name}: {count} records")
            except:
                print(f"   ❌ {table_name}: table not found")
        
        cursor.close()
        conn.close()
        
        print("\n✅ PostgreSQL connection test successful!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure PostgreSQL is running")
        print("   2. Check if postgres user exists with password 'post'")
        print("   3. Try: pg_ctl -D /path/to/postgres/data start")

if __name__ == "__main__":
    test_connection() 