from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import tuple_
from datetime import datetime

from app.database import get_db
from app.models import Product
from app.services.pagination import (
    encode_cursor,
    decode_cursor
)

router = APIRouter()


@router.get("/products")
def get_products(
    limit: int = 50,
    category: str | None = None,
    cursor: str | None = None,
    snapshot: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)

    # Snapshot consistency
    if snapshot is None:
        snapshot_dt = datetime.utcnow()
    else:
        snapshot_dt = datetime.fromisoformat(snapshot)

    query = query.filter(
        Product.updated_at <= snapshot_dt
    )

    # Category filter
    if category:
        query = query.filter(
            Product.category == category
        )

    # Cursor pagination
    if cursor:
        decoded = decode_cursor(cursor)

        cursor_updated_at = datetime.fromisoformat(
            decoded["updated_at"]
        )

        cursor_id = decoded["id"]

        query = query.filter(
            tuple_(
                Product.updated_at,
                Product.id
            ) < (
                cursor_updated_at,
                cursor_id
            )
        )

    products = (
        query
        .order_by(
            Product.updated_at.desc(),
            Product.id.desc()
        )
        .limit(limit)
        .all()
    )

    next_cursor = None

    if products:
        last_product = products[-1]

        next_cursor = encode_cursor(
            last_product.updated_at,
            last_product.id
        )

    return {
        "items": products,
        "next_cursor": next_cursor,
        "snapshot": snapshot_dt.isoformat()
    }