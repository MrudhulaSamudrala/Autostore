#!/usr/bin/env python3
"""
Restore AutoStore Database
This script recreates the database with initial data for the warehouse automation system.
"""

from db.database import SessionLocal, engine
from models.bots import Bot
from models.bins import Bin
from models.products import Product
from models.orders import Order
from models.bin_locks import BinLock
from sqlalchemy import text
import json

def restore_database():
    """Restore the database with initial data"""
    print("🔄 Restoring AutoStore Database...")
    
    # Create tables
    print("1. Creating database tables...")
    from db.database import Base
    Base.metadata.create_all(bind=engine)
    print("   ✅ Tables created successfully")
    
    db = SessionLocal()
    
    try:
        # Clear existing data
        print("2. Clearing existing data...")
        db.query(BinLock).delete()
        db.query(Order).delete()
        db.query(Bot).delete()
        db.query(Bin).delete()
        db.query(Product).delete()
        db.commit()
        print("   ✅ Existing data cleared")
        
        # Create bots
        print("3. Creating bots...")
        bots_data = [
            {"id": 1, "x": 5, "y": 0, "current_location_z": 0, "status": "idle"},
            {"id": 2, "x": 5, "y": 0, "current_location_z": 0, "status": "idle"}
        ]
        
        for bot_data in bots_data:
            bot = Bot(**bot_data)
            db.add(bot)
        
        db.commit()
        print(f"   ✅ Created {len(bots_data)} bots")
        
        # Create bins (6x6x6 grid = 216 bins)
        print("4. Creating bins...")
        bins_created = 0
        for x in range(6):
            for y in range(6):
                for z in range(6):
                    bin_id = x + y * 6 + z * 36 + 1
                    bin_data = {
                        "id": bin_id,
                        "x": x,
                        "y": y,
                        "z_location": z,
                        "product_ids": json.dumps([]),  # Empty product list
                        "status": "available"
                    }
                    bin_obj = Bin(**bin_data)
                    db.add(bin_obj)
                    bins_created += 1
        
        db.commit()
        print(f"   ✅ Created {bins_created} bins (6x6x6 grid)")
        
        # Create sample products
        print("5. Creating sample products...")
        products_data = [
            {"id": 1, "name": "Apple", "price": 1.99, "quantity": 50, "sale_count": 0},
            {"id": 2, "name": "Banana", "price": 0.99, "quantity": 75, "sale_count": 0},
            {"id": 3, "name": "Orange", "price": 2.49, "quantity": 30, "sale_count": 0},
            {"id": 4, "name": "Milk", "price": 3.99, "quantity": 25, "sale_count": 0},
            {"id": 5, "name": "Bread", "price": 2.99, "quantity": 40, "sale_count": 0}
        ]
        
        for product_data in products_data:
            product = Product(**product_data)
            db.add(product)
        
        db.commit()
        print(f"   ✅ Created {len(products_data)} sample products")
        
        # Show summary
        print("\n📊 Database Summary:")
        print(f"   Bots: {db.query(Bot).count()}")
        print(f"   Bins: {db.query(Bin).count()}")
        print(f"   Products: {db.query(Product).count()}")
        print(f"   Orders: {db.query(Order).count()}")
        
        print("\n✅ Database restored successfully!")
        print("🚀 You can now start your application:")
        print("   uvicorn main:app --reload")
        
    except Exception as e:
        print(f"❌ Error restoring database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    restore_database() 