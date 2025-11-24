# backend/routers/products.py
"""Product CRUD endpoints."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from .. import crud, models
from ..auth import require_api_key
from ..database import get_db

router = APIRouter(
    prefix="/products",
    tags=["products"],
    dependencies=[Depends(require_api_key)],
)


class ProductCreate(BaseModel):
    name: str = Field(..., max_length=100)
    price: float = Field(..., ge=0)
    description: str | None = Field(default=None, max_length=255)


class ProductRead(BaseModel):
    id: int
    name: str
    price: float
    description: str | None

    model_config = ConfigDict(from_attributes=True)


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> models.Product:
    return crud.create_product(db, data=payload.model_dump())


@router.get("/", response_model=List[ProductRead])
def list_products(db: Session = Depends(get_db)) -> list[models.Product]:
    return list(crud.list_products(db))


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)) -> models.Product:
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product