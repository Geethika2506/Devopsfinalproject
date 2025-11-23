from sqlalchemy.orm import Session
from app import models, schemas
from sqlalchemy.orm import Session
from typing import List, Optional

def get_user_by_email(db: Session, email: str) :
    	return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str) -> models.User:
	db_user = models.User(email=user.email, password=hashed_password)
	db.add(db_user)
	db.commit()
	db.refresh(db_user)

	# create empty cart for user
	cart = models.Cart(user_id=db_user.id)
	db.add(cart)
	db.commit()
	db.refresh(cart)

	return db_user


# Products
def list_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
	return db.query(models.Product).offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int) -> Optional[models.Product]:
	return db.query(models.Product).filter(models.Product.id == product_id).first()

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(
        name=product.name,  # Changed from title
        description=product.description,
        price=product.price,
        stock=product.stock
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Cart
def get_cart_by_user(db: Session, user_id: int) -> Optional[models.Cart]:
	return db.query(models.Cart).filter(models.Cart.user_id == user_id).first()


def add_item_to_cart(db: Session, user_id: int, item: schemas.CartItemBase) -> models.CartItem:
	cart = get_cart_by_user(db, user_id)
	if cart is None:
		cart = models.Cart(user_id=user_id)
		db.add(cart)
		db.commit()
		db.refresh(cart)

	# ensure product exists
	product = get_product(db, item.product_id)
	if not product:
		raise ValueError("Product not found")

	# check existing item
	existing = db.query(models.CartItem).filter(
		models.CartItem.cart_id == cart.id,
		models.CartItem.product_id == item.product_id
	).first()

	if existing:
		existing.quantity += item.quantity
		db.add(existing)
		db.commit()
		db.refresh(existing)
		return existing

	new_item = models.CartItem(cart_id=cart.id, product_id=item.product_id, quantity=item.quantity)
	db.add(new_item)
	db.commit()
	db.refresh(new_item)
	return new_item


def list_cart_items(db: Session, user_id: int) -> List[models.CartItem]:
	cart = get_cart_by_user(db, user_id)
	if not cart:
		return []
	return cart.items
