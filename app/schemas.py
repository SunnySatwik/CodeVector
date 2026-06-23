from pydantic import BaseModel
from datetime import datetime


class ProductResponse(BaseModel):
    id: int
    name: str
    category: str
    price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductsPage(BaseModel):
    items: list[ProductResponse]
    next_cursor: str | None
    snapshot: str