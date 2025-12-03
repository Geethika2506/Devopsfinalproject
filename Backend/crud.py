"""CRUD operations for all models."""
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List, Optional
from backend import models, schemas


# Product CRUD
def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
    return db.query(models.Product).offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_products_by_category(db: Session, category: str) -> List[models.Product]:
    return db.query(models.Product).filter(models.Product.category == category).all()


def get_categories(db: Session) -> List[str]:
    """Get all unique product categories."""
    results = db.query(distinct(models.Product.category)).all()
    return [r[0] for r in results if r[0]]


def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: schemas.ProductUpdate) -> Optional[models.Product]:
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False


# User CRUD
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
    return db.query(models.User).offset(skip).limit(limit).all()


# Cart CRUD
def get_cart_items(db: Session, user_id: int) -> List[models.CartItem]:
    return db.query(models.CartItem).filter(models.CartItem.user_id == user_id).all()


def add_to_cart(db: Session, user_id: int, item: schemas.CartItemCreate) -> models.CartItem:
    # Check if item already in cart
    existing = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.product_id == item.product_id
    ).first()
    
    if existing:
        existing.quantity += item.quantity
        db.commit()
        db.refresh(existing)
        return existing
    
    db_item = models.CartItem(user_id=user_id, **item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_cart_item(db: Session, user_id: int, product_id: int, quantity: int) -> Optional[models.CartItem]:
    item = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.product_id == product_id
    ).first()
    
    if item:
        if quantity <= 0:
            db.delete(item)
            db.commit()
            return None
        item.quantity = quantity
        db.commit()
        db.refresh(item)
    return item


def remove_from_cart(db: Session, user_id: int, product_id: int) -> bool:
    item = db.query(models.CartItem).filter(
        models.CartItem.user_id == user_id,
        models.CartItem.product_id == product_id
    ).first()
    
    if item:
        db.delete(item)
        db.commit()
        return True
    return False


def clear_cart(db: Session, user_id: int) -> None:
    db.query(models.CartItem).filter(models.CartItem.user_id == user_id).delete()
    db.commit()


# Order CRUD
def create_order(db: Session, user_id: int, items: List[schemas.OrderItemBase]) -> models.Order:
    # Create order
    db_order = models.Order(user_id=user_id)
    db.add(db_order)
    db.flush()  # Get order ID
    
    total = 0.0
    for item in items:
        product = get_product(db, item.product_id)
        if product:
            order_item = models.OrderItem(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=product.price
            )
            db.add(order_item)
            total += product.price * item.quantity
    
    db_order.total = total
    db.commit()
    db.refresh(db_order)
    return db_order


def get_orders(db: Session, user_id: int) -> List[models.Order]:
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()


def get_order(db: Session, order_id: int) -> Optional[models.Order]:
    return db.query(models.Order).filter(models.Order.id == order_id).first()


def update_order_status(db: Session, order_id: int, status: str) -> Optional[models.Order]:
    order = get_order(db, order_id)
    if order:
        order.status = status
        db.commit()
        db.refresh(order)
    return order

