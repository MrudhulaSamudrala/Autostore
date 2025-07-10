from sqlalchemy import Column, Integer, String, ForeignKey, Date, TIMESTAMP, Numeric
from sqlalchemy.orm import relationship
from db.database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    bin_id = Column(Integer, ForeignKey("bins.id"), nullable=False)
    last_refilled = Column(TIMESTAMP)
    sale_count = Column(Integer, default=0)
    bin = relationship("Bin")
    price = Column(Numeric(10, 2), nullable=False, default=0)
    image_url = Column(String, nullable=True)
    category = Column(String, nullable=True)
    quantity = Column(Integer, default=0)
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, bin_id={self.bin_id}, category={self.category})>" 