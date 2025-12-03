# backend/routers/products.py
"""Product CRUD endpoints."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from .. import crud, models
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(
    prefix="/products",
    tags=["products"],
    dependencies=[Depends(get_current_user)],
)


class ProductRating(BaseModel):
    rate: float = Field(default=0, ge=0)
    count: int = Field(default=0, ge=0)


class ProductCreate(BaseModel):
    title: str = Field(..., max_length=150)
    price: float = Field(..., ge=0)
    description: str | None = Field(default=None)
    category: str = Field(default="general", max_length=80)
    image: str | None = Field(default=None, max_length=255)
    rating: ProductRating = Field(default_factory=ProductRating)


class ProductRead(BaseModel):
    id: int
    title: str
    price: float
    description: str | None
    category: str
    image: str | None
    rating: ProductRating

    model_config = ConfigDict(from_attributes=True)


def _prepare_product_payload(payload: ProductCreate) -> dict:
    data = payload.model_dump()
    rating = data.pop("rating", {}) or {}
    data["rating_rate"] = rating.get("rate", 0)
    data["rating_count"] = rating.get("count", 0)
    return data


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> models.Product:
    data = _prepare_product_payload(payload)
    return crud.create_product(db, data=data)


@router.get("/", response_model=List[ProductRead])
def list_products(db: Session = Depends(get_db)) -> list[models.Product]:
    return list(crud.list_products(db))


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)) -> models.Product:
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product