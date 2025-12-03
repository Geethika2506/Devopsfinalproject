"""Reusable CRUD helpers for the store domain."""
from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy.orm import Session

from . import models


# Product helpers

def create_product(db: Session, *, data: dict) -> models.Product:
    product = models.Product(**data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def list_products(db: Session) -> Iterable[models.Product]:
    return db.query(models.Product).all()


def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.id == product_id).first()


# Customer helpers

def create_customer(db: Session, *, data: dict) -> models.Customer:
    customer = models.Customer(**data)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customer_by_email(db: Session, email: str) -> Optional[models.Customer]:
    return db.query(models.Customer).filter(models.Customer.email == email).first()


def list_customers(db: Session) -> Iterable[models.Customer]:
    return db.query(models.Customer).all()


# Order helpers

def create_order(db: Session, *, data: dict) -> models.Order:
    order = models.Order(**data)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> Optional[models.Order]:
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def list_orders(db: Session) -> Iterable[models.Order]:
    return db.query(models.Order).all()


# User helpers

def create_user(db: Session, *, email: str, password_hash: str) -> models.User:
    user = models.User(email=email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()
