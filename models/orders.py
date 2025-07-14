from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
import datetime
from sqlalchemy.orm import relationship, backref
from db.database import Base

class OrderProduct(Base):
    __tablename__ = "order_products"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)

    product = relationship("Product")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending")  # "pending", "packing", "packed"
    assigned_bot_id = Column(Integer, ForeignKey("bots.id"), nullable=True)
    items = relationship("OrderProduct", backref="order", cascade="all, delete-orphan") 