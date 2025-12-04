"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# Product schemas
class ProductBase(BaseModel):
    title: str
    price: float
    description: Optional[str] = None
    category: str = "general"
    image: Optional[str] = None
    rating_rate: float = 0.0
    rating_count: int = 0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    title: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None


class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Auth schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100, description="Password must be 6-100 characters")
    name: Optional[str] = Field(None, max_length=200)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


# Alias for backward compatibility
User = UserResponse


# Cart schemas
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemCreate(CartItemBase):
    pass


class CartItemResponse(CartItemBase):
    id: int
    product: ProductResponse

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total: float


# Order schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = 1


class OrderItemResponse(OrderItemBase):
    id: int
    price: float
    product: ProductResponse

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    items: List[OrderItemBase]


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total: float
    created_at: datetime
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


# Wishlist schemas
class WishlistItemCreate(BaseModel):
    product_id: int


class WishlistItemResponse(BaseModel):
    id: int
    product_id: int
    created_at: datetime
    product: ProductResponse

    model_config = ConfigDict(from_attributes=True)


class WishlistResponse(BaseModel):
    items: List[WishlistItemResponse]
    count: int


# Review schemas
class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewCreate(ReviewBase):
    product_id: int


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ProductReviewsResponse(BaseModel):
    product_id: int
    average_rating: float
    total_reviews: int
    reviews: List[ReviewResponse]

