# app/routers/cart.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db


router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("/create/{user_id}", response_model=schemas.Cart)
def create_cart(user_id: int, db: Session = Depends(get_db)):
	return crud.create_cart(db, user_id)


@router.post("/{cart_id}/add", response_model=schemas.Cart)
def add_to_cart(cart_id: int, item: schemas.CartItemBase, db: Session = Depends(get_db)):
	ci = crud.add_item_to_cart(db, cart_id, item)
	cart = db.query("Cart").filter_by(id=cart_id).first() # simplified
	return db.query("carts").filter_by(id=cart_id).first() # simplified placeholder


@router.get("/{cart_id}", response_model=schemas.Cart)
def view_cart(cart_id: int, db: Session = Depends(get_db)):
	cart = db.query("carts").filter_by(id=cart_id).first()
	if not cart:
		raise HTTPException(404, "Cart not found")
	return cart
