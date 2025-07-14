from db.database import SessionLocal
from models.bots import Bot
from models.bins import Bin

def reset_bots_and_bins():
    db = SessionLocal()
    try:
        # Reset all bots
        bots = db.query(Bot).all()
        for bot in bots:
            bot.carried_bin_id = None
            bot.status = "idle"
            # Optionally, reset bot position to parking if you have parking_x/parking_y fields
            # bot.x = bot.parking_x
            # bot.y = bot.parking_y

        # Reset all bins
        bins = db.query(Bin).all()
        for bin in bins:
            bin.status = "available"
            # Reset bin position to its original grid location if available
            if bin.original_x is not None and bin.original_y is not None and bin.original_z is not None:
                bin.x = bin.original_x
                bin.y = bin.original_y
                bin.z_location = bin.original_z
        db.commit()
        print("All bots and bins have been reset to a clean state.")
    except Exception as e:
        db.rollback()
        print("Error during reset:", e)
    finally:
        db.close()

if __name__ == "__main__":
    reset_bots_and_bins() 