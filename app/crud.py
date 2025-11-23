# app/crud.py
from sqlalchemy.orm import Session
from . import models, schemas


# Products


def create_product(db: Session, product: schemas.ProductCreate):
	p = models.Product(**product.dict())
	db.add(p)
	db.commit()
	db.refresh(p)
	return p


def list_products(db: Session, skip: int = 0, limit: int = 100):
	return db.query(models.Product).offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int):
	return db.query(models.Product).filter(models.Product.id == product_id).first()


# Users


def create_user(db: Session, user: schemas.UserCreate):
	u = models.User(email=user.email)
	db.add(u)
	db.commit()
	db.refresh(u)
	return u


# Cart


def create_cart(db: Session, user_id: int):
	cart = models.Cart(user_id=user_id)
	db.add(cart)
	db.commit()
	db.refresh(cart)
	return cart


def add_item_to_cart(db: Session, cart_id: int, item: schemas.CartItemBase):
	ci = models.CartItem(cart_id=cart_id, product_id=item.product_id, quantity=item.quantity)
	db.add(ci)
	db.commit()
	db.refresh(ci)
	return ci


# Orders


def create_order_from_cart(db: Session, cart_id: int):
	cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
	if not cart:
		return None
	total = 0.0
	for it in cart.items:
		# assume product relationship loaded
		total += (it.product.price if it.product else 0.0) * it.quantity
	order = models.Order(user_id=cart.user_id, total=total)
	db.add(order)
	db.commit()
	db.refresh(order)
	return order