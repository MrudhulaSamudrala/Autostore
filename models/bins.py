from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from db.database import Base

class Bin(Base):
    __tablename__ = "bins"
    id = Column(Integer, primary_key=True, index=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    z_location = Column(Integer, nullable=False, default=0)
    product_ids = Column(ARRAY(Integer), default=list)
    status = Column(String, nullable=False) 