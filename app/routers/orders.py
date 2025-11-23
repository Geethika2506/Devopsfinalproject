# app/routers/orders.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/from-cart/{cart_id}", response_model=schemas.Order)
def create_order(cart_id: int, db: Session = Depends(get_db)):
	order = crud.create_order_from_cart(db, cart_id)
	if not order:
		raise HTTPException(404, "Cart not found or empty")
	return order