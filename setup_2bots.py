import psycopg2
import os

def setup_2bots():
    """Setup 2 bots at top right corner of 6x6x6 grid"""
    
    # Database connection parameters
    DB_PARAMS = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'autostore'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_PARAMS)
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
            cursor.execute("ALTER TABLE bots ADD COLUMN destination_bin JSONB")
            print("   ✓ Added destination_bin")
        except:
            print("   - destination_bin already exists")
        
        try:
            cursor.execute("ALTER TABLE bots ADD COLUMN path JSONB")
            print("   ✓ Added path")
        except:
            print("   - path already exists")
        
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
                path = NULL
        """)
        
        # Commit changes
        conn.commit()
        print("3. Setup complete!")
        
        # Show current bots
        cursor.execute("SELECT id, x, y, current_location_z, status FROM bots ORDER BY id")
        bots = cursor.fetchall()
        print(f"\nCurrent bots ({len(bots)} total):")
        for bot in bots:
            print(f"   Bot {bot[0]}: Position ({bot[1]}, {bot[2]}, {bot[3]}) - Status: {bot[4]}")
        
        print(f"\nGrid Layout (6x6x6):")
        print(f"   - X: 0 to 5")
        print(f"   - Y: 0 to 5") 
        print(f"   - Z: 0 to 5")
        print(f"   - Bots positioned at top right corner (5,5)")
        
        conn.close()
        print("\n✅ 2 bots ready at top right corner!")
        print("Start your FastAPI server and dashboard to see them in action.")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("Please check your database connection parameters.")

if __name__ == "__main__":
    from db.database import SessionLocal
    from models.bots import Bot
    db = SessionLocal()
    for bot in db.query(Bot).all():
        bot.status = "idle"
        bot.assigned_order_id = None
        bot.destination_bin = None
        bot.path = None
    db.commit()
    db.close()
    print("All bots reset to idle and cleared.") 