from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, users, cart, orders
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DevOps Shop API",
    description="E-commerce API for DevOps Final Project",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])


@app.get("/")
def home():
    return {"message": "DevOps Shop API running!", "status": "online"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
