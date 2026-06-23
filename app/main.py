from fastapi import FastAPI

from .database import Base
from .database import engine

from .models import Product

app = FastAPI(
    title="CodeVector Product Browser"
)

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Backend Running"}