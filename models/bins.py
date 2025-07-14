from sqlalchemy import Column, Integer, String, JSON
from db.database import Base

class Bin(Base):
    __tablename__ = "bins"
    id = Column(Integer, primary_key=True, index=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    z_location = Column(Integer, nullable=False, default=0)
    original_x = Column(Integer, nullable=True)  # New: original grid x
    original_y = Column(Integer, nullable=True)  # New: original grid y
    original_z = Column(Integer, nullable=True)  # New: original grid z
    product_ids = Column(JSON, default=list)  # Changed from ARRAY to JSON for SQLite compatibility
    status = Column(String, nullable=False) 