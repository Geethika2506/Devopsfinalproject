# app/routers/products.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db
from app.auth import get_current_user
import httpx
from typing import List

router = APIRouter(prefix="/products", tags=["Products"])

# Cache for external products
_products_cache = None

async def fetch_external_products():
    """Fetch products from Fake Store API"""
    global _products_cache
    
    if _products_cache is not None:
        return _products_cache
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://fakestoreapi.com/products")
            if response.status_code == 200:
                products = response.json()
                # Transform to match our schema
                _products_cache = [
                    {
                        "id": p["id"],
                        "name": p["title"],
                        "description": p["description"],
                        "price": float(p["price"]),
                        "stock": 50,  # Fake store API doesn't have stock
                        "image": p.get("image", "")
                    }
                    for p in products
                ]
                return _products_cache
    except Exception as e:
        print(f"Error fetching external products: {e}")
    
    return []


@router.get("/", response_model=List[dict])
async def read_products(skip: int = 0, limit: int = 100):
    """Get products from external API"""
    products = await fetch_external_products()
    return products[skip:skip+limit]


@router.get("/{product_id}", response_model=dict)
async def read_product(product_id: int):
    """Get single product"""
    products = await fetch_external_products()
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


# Optional: Keep ability to add custom products to database
@router.post("/custom", response_model=schemas.Product, status_code=status.HTTP_201_CREATED)
def create_custom_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    """Add custom products to database (requires authentication)"""
    return crud.create_product(db=db, product=product)