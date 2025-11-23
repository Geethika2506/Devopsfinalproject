"""Order endpoints for linking customers and products."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderCreate(BaseModel):
    customer_id: int
    product_id: int
    quantity: int = Field(default=1, gt=0)


class OrderRead(BaseModel):
    id: int
    customer_id: int
    product_id: int
    quantity: int

    model_config = ConfigDict(from_attributes=True)


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)) -> models.Order:
    customer = db.query(models.Customer).filter(models.Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    product = db.query(models.Product).filter(models.Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    order = models.Order(**payload.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/", response_model=List[OrderRead])
def list_orders(db: Session = Depends(get_db)) -> list[models.Order]:
    return db.query(models.Order).all()


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)) -> models.Order:
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
