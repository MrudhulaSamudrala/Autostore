from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from db.database import Base

class Bin(Base):
    __tablename__ = "bins"
    bin_id = Column(Integer, primary_key=True, index=True)
    location_x = Column(Integer, nullable=False)
    location_y = Column(Integer, nullable=False)
    product_ids = Column(ARRAY(Integer), default=list)
    status = Column(String, nullable=False) 