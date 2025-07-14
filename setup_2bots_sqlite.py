import sqlite3
import os

def setup_2bots_sqlite():
    """Setup 2 bots at top right corner of 6x6x6 grid for SQLite"""
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect("autostore.db")
        cursor = conn.cursor()
        
        print("Setting up 2 bots at top right corner of 6x6x6 grid...")
        
        # Add new columns if they don't exist
        print("1. Adding real-time tracking columns...")
        try:
            cursor.execute("ALTER TABLE bots ADD COLUMN assigned_order_id INTEGER")
            print("   ✓ Added assigned_order_id")
        except:
            print("   - assigned_order_id already exists")
        
        try:
            cursor.execute("ALTER TABLE bots ADD COLUMN destination_bin TEXT")
            print("   ✓ Added destination_bin")
        except:
            print("   - destination_bin already exists")
        
        try:
            cursor.execute("ALTER TABLE bots ADD COLUMN path TEXT")
            print("   ✓ Added path")
        except:
            print("   - path already exists")
        
        try:
            cursor.execute("ALTER TABLE bots ADD COLUMN full_path TEXT")
            print("   ✓ Added full_path")
        except:
            print("   - full_path already exists")
        
        # Clear existing bots and add 2 bots at top right corner
        print("2. Setting up 2 bots...")
        cursor.execute("DELETE FROM bots")
        cursor.execute("""
            INSERT INTO bots (id, x, y, current_location_z, status) VALUES
            (1, 5, 5, 1, 'idle'),  -- Bot 1 at (5,5,1)
            (2, 5, 5, 4, 'idle')   -- Bot 2 at (5,5,4)
        """)
        
        # Set default values
        cursor.execute("""
            UPDATE bots SET 
                assigned_order_id = NULL,
                destination_bin = NULL,
                path = NULL,
                full_path = NULL
        """)
        
        # Create 216 bins if they don't exist
        print("3. Setting up 216 bins...")
        cursor.execute("DELETE FROM bins")
        
        # Insert 216 bins (6x6x6 grid)
        bin_id = 1
        for z in range(6):
            for y in range(6):
                for x in range(6):
                    cursor.execute("""
                        INSERT INTO bins (id, x, y, z_location, status, product_ids)
                        VALUES (?, ?, ?, ?, 'available', '[]')
                    """, (bin_id, x, y, z))
                    bin_id += 1
        
        # Commit changes
        conn.commit()
        print("4. Setup complete!")
        
        # Show current bots
        cursor.execute("SELECT id, x, y, current_location_z, status FROM bots ORDER BY id")
        bots = cursor.fetchall()
        print(f"\nCurrent bots ({len(bots)} total):")
        for bot in bots:
            print(f"   Bot {bot[0]}: Position ({bot[1]}, {bot[2]}, {bot[3]}) - Status: {bot[4]}")
        
        # Show bin count
        cursor.execute("SELECT COUNT(*) FROM bins")
        bin_count = cursor.fetchone()[0]
        print(f"\nCurrent bins ({bin_count} total):")
        print(f"   - Grid Layout: 6x6x6 = 216 bins")
        print(f"   - X: 0 to 5")
        print(f"   - Y: 0 to 5") 
        print(f"   - Z: 0 to 5")
        print(f"   - Bots positioned at top right corner (5,5)")
        
        conn.close()
        print("\n✅ 2 bots and 216 bins ready!")
        print("Start your FastAPI server and dashboard to see them in action.")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("Please check your database connection.")

if __name__ == "__main__":
    setup_2bots_sqlite() 