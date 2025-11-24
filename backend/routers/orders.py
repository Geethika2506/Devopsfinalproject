"""Order endpoints for linking customers and products."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from .. import crud, models
from ..auth import require_api_key
from ..database import get_db

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
    dependencies=[Depends(require_api_key)],
)


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
    customer = crud.get_customer(db, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    product = crud.get_product(db, payload.product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return crud.create_order(db, data=payload.model_dump())


@router.get("/", response_model=List[OrderRead])
def list_orders(db: Session = Depends(get_db)) -> list[models.Order]:
    return list(crud.list_orders(db))


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)) -> models.Order:
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
