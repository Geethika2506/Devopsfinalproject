"""Cart API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud, schemas

router = APIRouter(prefix="/cart", tags=["cart"])


def get_current_user_id(x_user_id: int = Header(..., description="User ID header")) -> int:
    """Simple user identification via header (for demo purposes)."""
    return x_user_id


@router.get("/", response_model=schemas.CartResponse)
def get_cart(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get the current user's cart."""
    items = crud.get_cart_items(db, user_id)
    total = sum(item.product.price * item.quantity for item in items if item.product)
    return schemas.CartResponse(items=items, total=total)


@router.post("/items", response_model=schemas.CartItemResponse, status_code=201)
def add_item_to_cart(
    item: schemas.CartItemCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Add an item to the cart."""
    # Verify product exists
    product = crud.get_product(db, item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return crud.add_to_cart(db, user_id, item)


@router.put("/items/{product_id}")
def update_cart_item(
    product_id: int,
    quantity: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Update quantity of an item in cart."""
    result = crud.update_cart_item(db, user_id, product_id, quantity)
    if result is None and quantity > 0:
        raise HTTPException(status_code=404, detail="Item not in cart")
    return {"message": "Cart updated"}


@router.delete("/items/{product_id}", status_code=204)
def remove_cart_item(
    product_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Remove an item from cart."""
    if not crud.remove_from_cart(db, user_id, product_id):
        raise HTTPException(status_code=404, detail="Item not in cart")


@router.delete("/", status_code=204)
def clear_cart(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Clear all items from cart."""
    crud.clear_cart(db, user_id)
