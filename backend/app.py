"""FastAPI application entry point."""
from __future__ import annotations

from fastapi import FastAPI

from .database import create_all_tables
from .routers import auth, customers, orders, products

create_all_tables()

app = FastAPI(title="Mini Store API", version="0.1.0")
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(orders.router)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello from Mini Store"}
