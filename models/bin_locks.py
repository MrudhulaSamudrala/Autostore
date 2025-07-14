from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from db.database import Base

class BinLock(Base):
    __tablename__ = "bin_locks"
    id = Column(Integer, ForeignKey("bins.id"), primary_key=True)
    used_by = Column(Integer, ForeignKey("bots.id"))
    status = Column(String, nullable=False)
    waiting_list = Column(JSON, default=list)  # Changed from ARRAY to JSON for SQLite compatibility 