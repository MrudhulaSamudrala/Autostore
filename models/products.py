from sqlalchemy import Column, Integer, String, ForeignKey, Date, TIMESTAMP
from db.database import Base

class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    bin_id = Column(Integer, ForeignKey("bins.bin_id"), nullable=False)
    expiry_date = Column(Date)
    last_refilled = Column(TIMESTAMP)
    sale_count = Column(Integer, default=0) 