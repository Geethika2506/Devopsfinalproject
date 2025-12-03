from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas import Product
from app.services.external_products import (
    get_all_products,
    get_product_by_id,
    get_products_by_category,
    get_categories
)

router = APIRouter()


@router.get("/", response_model=List[Product])
def list_products():
    """Get all products"""
    return get_all_products()


@router.get("/categories")
def list_categories():
    """Get all product categories"""
    return {"categories": get_categories()}


@router.get("/category/{category}", response_model=List[Product])
def list_products_by_category(category: str):
    """Get all products in a specific category"""
    products = get_products_by_category(category)
    if not products:
        raise HTTPException(status_code=404, detail=f"No products found in category: {category}")
    return products


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    """Get a single product by ID"""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
