# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import products, users, cart, orders

# create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DevOps Shop API")

# Allow your React dev server to call the API
origins = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers with prefixes
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(users.router,    prefix="/users",    tags=["Users"])
app.include_router(cart.router,     prefix="/cart",     tags=["Cart"])
app.include_router(orders.router,   prefix="/orders",   tags=["Orders"])


@app.get("/health")
def health():
    return {"status": "ok"}