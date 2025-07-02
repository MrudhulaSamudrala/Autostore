from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.bins import Bin

router = APIRouter(prefix="/bins", tags=["bins"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
def list_bins(db: Session = Depends(get_db)):
    return db.query(Bin).all() 