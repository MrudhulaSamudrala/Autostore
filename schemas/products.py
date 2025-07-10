from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductOut(BaseModel):
    id: int
    name: str
    bin_id: int
    last_refilled: Optional[datetime] = None
    sale_count: Optional[int] = None
    price: float
    image_url: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = 0

    class Config:
        orm_mode = True 