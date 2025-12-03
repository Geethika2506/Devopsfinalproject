from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    username: str
    email: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True


# Product schemas
class Product(BaseModel):
    id: int
    name: str
    price: float
    category: str
    image: Optional[str] = None


# Cart schemas
class CartItemCreate(BaseModel):
    product_id: int
    product_name: str
    quantity: int = 1
    price: float


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: float

    class Config:
        orm_mode = True


class CartResponse(BaseModel):
    id: int
    user_id: int
    items: List[CartItemResponse] = []

    class Config:
        orm_mode = True


# Order schemas
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    price: float

    class Config:
        orm_mode = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        orm_mode = True
