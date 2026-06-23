from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import get_db
from app.models import Product

router = APIRouter()


@router.get("/products")
def get_products(
    limit: int = 50,
    db: Session = Depends(get_db)
):

    products = (
        db.query(Product)
        .order_by(
            Product.updated_at.desc(),
            Product.id.desc()
        )
        .limit(limit)
        .all()
    )

    return products