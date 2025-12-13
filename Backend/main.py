"""FastAPI main application."""
import sys
import os

# Add current directory to path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import products, cart, orders, users, auth, wishlist, reviews

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Online Store API",
    description="A simple e-commerce REST API for DevOps demo",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:5176",
        "https://devopsfinalproject.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(users.router)
app.include_router(wishlist.router)
app.include_router(reviews.router)


@app.get("/")
def home():
    """Root endpoint."""
    return {"message": "Online Store API running!"}


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "online-store-api"}