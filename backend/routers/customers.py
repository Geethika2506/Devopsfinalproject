"""Customer CRUD endpoints."""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.orm import Session

from .. import crud, models
from ..auth import require_api_key
from ..database import get_db

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    dependencies=[Depends(require_api_key)],
)


class CustomerCreate(BaseModel):
    name: str = Field(..., max_length=100)
    email: EmailStr


class CustomerRead(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


@router.post("/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)) -> models.Customer:
    existing = crud.get_customer_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    return crud.create_customer(db, data=payload.model_dump())


@router.get("/", response_model=List[CustomerRead])
def list_customers(db: Session = Depends(get_db)) -> list[models.Customer]:
    return list(crud.list_customers(db))


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, db: Session = Depends(get_db)) -> models.Customer:
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer
