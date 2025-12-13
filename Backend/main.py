"""FastAPI main application."""
import sys
import os
from pathlib import Path

# Add current directory to path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Include routers with /api prefix (for frontend)
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(cart.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(wishlist.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")

# Also include routers without prefix (for backward compatibility / direct API access)
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


# Serve frontend static files
# Check if frontend dist folder exists (production build)
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"

if frontend_dist.exists():
    # Serve static assets (js, css, images)
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        """Serve frontend for all non-API routes."""
        # If it's an API route, this won't match (routers are registered first)
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # Return index.html for SPA routing
        return FileResponse(frontend_dist / "index.html")