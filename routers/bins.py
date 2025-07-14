from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.bins import Bin
from models.bin_locks import BinLock
from models.bots import Bot

router = APIRouter(prefix="/bins", tags=["bins"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def list_bins(db: Session = Depends(get_db)):
    bins = db.query(Bin).all()
    bin_locks = {bl.id: bl for bl in db.query(BinLock).all()}
    bots = db.query(Bot).all()
    # Find bins currently being carried by a bot (not on grid)
    bins_in_use = set()
    for bot in bots:
        # If bot is assigned an order and has a destination_bin, assume it's carrying the bin if bot.status is 'moving', 'delivering', or 'carrying'
        if bot.destination_bin and bot.status in ["moving", "delivering", "carrying"]:
            # Try to get bin id from destination_bin (could be [x, y, z, bin_id] or similar)
            if isinstance(bot.destination_bin, list) and len(bot.destination_bin) > 2:
                bin_id = bot.destination_bin[3] if len(bot.destination_bin) > 3 else None
                if bin_id:
                    bins_in_use.add(bin_id)

    result = []
    for b in bins:
        # Default to available
        status = "available"
        # If bin is being carried by a bot
        if b.id in bins_in_use or b.status == "in-use":
            status = "in-use"
        # Else if bin is locked for a bot (reserved, but not picked up)
        elif b.id in bin_locks and bin_locks[b.id].status == "Locked":
            status = "locked"
        # Else if bin is on grid and not locked or in use
        else:
            status = "available"
        result.append({
            "id": b.id,
            "x": b.x,
            "y": b.y,
            "z_location": b.z_location,
            "status": status
        })
    return result 