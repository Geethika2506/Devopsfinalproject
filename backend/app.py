"""FastAPI application entry point."""
from __future__ import annotations

from fastapi import FastAPI

from .database import Base, engine
from .routers import customers, orders, products

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini Store API", version="0.1.0")
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello from Mini Store"}
