from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from db.database import Base

class BinLock(Base):
    __tablename__ = "bin_locks"
    id = Column(Integer, ForeignKey("bins.id"), primary_key=True)
    used_by = Column(Integer, ForeignKey("bots.id"))
    status = Column(String, nullable=False)
    waiting_list = Column(ARRAY(Integer), default=list) 