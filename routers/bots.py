from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.bots import Bot

router = APIRouter(prefix="/bots", tags=["bots"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def list_bots(db: Session = Depends(get_db)):
    return db.query(Bot).all() 