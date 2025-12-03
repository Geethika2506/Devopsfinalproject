"""Product API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend import crud, schemas

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/categories", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    """Get all unique product categories."""
    return crud.get_categories(db)


@router.get("/", response_model=List[schemas.ProductResponse])
def list_products(
    skip: int = 0,
    limit: int = Query(default=100, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all products, optionally filtered by category."""
    if category:
        return crud.get_products_by_category(db, category)
    return crud.get_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a single product by ID."""
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=schemas.ProductResponse, status_code=201)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    return crud.create_product(db, product)


@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    """Update an existing product."""
    updated = crud.update_product(db, product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product."""
    if not crud.delete_product(db, product_id):
        raise HTTPException(status_code=404, detail="Product not found")


