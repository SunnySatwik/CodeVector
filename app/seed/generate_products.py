from faker import Faker
from datetime import datetime, timedelta
from sqlalchemy import text

from app.database import engine

fake = Faker()

CATEGORIES = [
    "electronics",
    "clothing",
    "books",
    "sports",
    "home",
    "beauty",
    "toys"
]

TOTAL_PRODUCTS = 200_000
BATCH_SIZE = 5000


def generate_batch(size):
    now = datetime.utcnow()

    rows = []

    for _ in range(size):
        created = now - timedelta(
            days=fake.random_int(min=0, max=365)
        )

        rows.append(
            {
                "name": fake.word().title() + " Product",
                "category": fake.random_element(CATEGORIES),
                "price": round(fake.pyfloat(
                    left_digits=4,
                    right_digits=2,
                    positive=True
                ), 2),
                "created_at": created,
                "updated_at": created
            }
        )

    return rows


def seed():
    inserted = 0

    with engine.begin() as conn:

        while inserted < TOTAL_PRODUCTS:

            batch = generate_batch(BATCH_SIZE)

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

            inserted += BATCH_SIZE

            print(
                f"{inserted}/{TOTAL_PRODUCTS} inserted"
            )

    print("Done")


if __name__ == "__main__":
    seed()