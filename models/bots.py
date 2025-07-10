from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from db.database import Base

class Bot(Base):
    __tablename__ = "bots"
    id = Column(Integer, primary_key=True, index=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    current_location_z = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="idle")  # idle, busy, charging, moving, packing
    assigned_order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    destination_bin = Column(JSON, nullable=True)  # [x, y, z] coordinates (JSONB in PostgreSQL)
    path = Column(JSON, nullable=True)  # [[x, y], [x, y], ...] path coordinates (JSONB in PostgreSQL)

    def __repr__(self):
        return f"<Bot id={self.id} status={self.status} pos=({self.x},{self.y},{self.current_location_z}) order={self.assigned_order_id}>" 