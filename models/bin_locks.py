from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from db.database import Base

class BinLock(Base):
    __tablename__ = "bin_locks"
    bin_id = Column(Integer, ForeignKey("bins.bin_id"), primary_key=True)
    used_by = Column(Integer, ForeignKey("bots.bot_id"))
    status = Column(String, nullable=False)
    waiting_list = Column(ARRAY(Integer), default=list) 