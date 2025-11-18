from fastapi import FastAPI
from app.routers import products, cart, orders

app = FastAPI()

app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)

@app.get("/")
def home():
    return {"message": "Online Store API running!"}
