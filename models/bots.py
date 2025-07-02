from sqlalchemy import Column, Integer, String
from db.database import Base

class Bot(Base):
    __tablename__ = "bots"
    bot_id = Column(Integer, primary_key=True, index=True)
    current_location_x = Column(Integer, nullable=False)
    current_location_y = Column(Integer, nullable=False)
    status = Column(String, nullable=False) 