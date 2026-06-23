
from datetime import datetime, timedelta
from sqlalchemy import text
import random
from app.database import engine
print("SCRIPT STARTED")


CATEGORIES = [
    "electronics",
    "clothing",
    "books",
    "sports",
    "home",
    "beauty",
    "toys"
]

TOTAL_PRODUCTS = 50000
BATCH_SIZE = 5000


def generate_batch(size):
    now = datetime.utcnow()

    rows = []

    for i in range(size):
        created = now - timedelta(
            days=random.randint(0, 365)
        )

        rows.append(
            {
                "name": f"Product {i}",
                "category": random.choice(CATEGORIES),
                "price": round(random.uniform(10, 10000), 2),
                "created_at": created,
                "updated_at": created
            }
        )

    return rows


def seed():
    inserted = 0

    with engine.begin() as conn:

        while inserted < TOTAL_PRODUCTS:

            print("Generating batch...")

            batch = generate_batch(BATCH_SIZE)

            print("Batch generated")

            conn.execute(
                text("""
                    INSERT INTO products
                    (name, category, price, created_at, updated_at)
                    VALUES
                    (:name, :category, :price,
                     :created_at, :updated_at)
                """),
                batch
            )

            print("Batch inserted")

            inserted += len(batch)

            print(f"{inserted:,}/{TOTAL_PRODUCTS:,} inserted")


if __name__ == "__main__":
    seed()