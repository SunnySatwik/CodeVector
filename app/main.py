from fastapi import FastAPI

from .database import Base
from .database import engine

from .models import Product
from app.routes.products import router as products_router


app = FastAPI(
    title="CodeVector Product Browser"
)
app.include_router(products_router)
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Backend Running"}