from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/from-cart/{cart_id}", response_model=schemas.Order)
def create_order(cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).get(cart_id)

    total = sum(item.product.price * item.quantity for item in cart.items)

    order = models.Order(user_id=cart.user_id, total=total)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order
