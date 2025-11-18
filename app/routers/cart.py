from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/create/{user_id}", response_model=schemas.Cart)
def create_cart(user_id: int, db: Session = Depends(get_db)):
    cart = models.Cart(user_id=user_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart

@router.post("/{cart_id}/add")
def add_to_cart(cart_id: int, item: schemas.CartItemBase, db: Session = Depends(get_db)):
    cart_item = models.CartItem(cart_id=cart_id, **item.dict())
    db.add(cart_item)
    db.commit()
    return {"message": "Item added"}

@router.get("/{cart_id}", response_model=schemas.Cart)
def view_cart(cart_id: int, db: Session = Depends(get_db)):
    return db.query(models.Cart).get(cart_id)
