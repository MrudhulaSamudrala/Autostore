from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from db.database import Base

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    warehouse_location = Column(String)
    status = Column(String, nullable=False)
    timestamp = Column(TIMESTAMP)
    bot_id = Column(Integer, ForeignKey("bots.bot_id")) 