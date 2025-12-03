"""SQLAlchemy models for the mini store."""
from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text)
    category = Column(String(80), nullable=False, default="general")
    image = Column(String(255))
    rating_rate = Column(Float, nullable=False, default=0)
    rating_count = Column(Integer, nullable=False, default=0)

    orders = relationship("Order", back_populates="product", cascade="all, delete-orphan")

    @property
    def rating(self) -> dict[str, float | int]:
        """Expose FakeStore-style rating shape."""
        return {
            "rate": float(self.rating_rate or 0),
            "count": int(self.rating_count or 0),
        }


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)

    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    customer = relationship("Customer", back_populates="orders")
    product = relationship("Product", back_populates="orders")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
