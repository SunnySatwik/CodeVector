from sqlalchemy import Column
from sqlalchemy import BigInteger
from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy import DateTime
from sqlalchemy import Index

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True)

    name = Column(String, nullable=False)

    category = Column(String, nullable=False)

    price = Column(Numeric(10, 2), nullable=False)

    created_at = Column(DateTime, nullable=False)

    updated_at = Column(DateTime, nullable=False)


Index(
    "idx_products_feed",
    Product.updated_at.desc(),
    Product.id.desc()
)

Index(
    "idx_products_category_feed",
    Product.category,
    Product.updated_at.desc(),
    Product.id.desc()
)