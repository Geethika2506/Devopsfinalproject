"""Order API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud, schemas

router = APIRouter(prefix="/orders", tags=["orders"])


def get_current_user_id(x_user_id: int = Header(..., description="User ID header")) -> int:
    """Simple user identification via header (for demo purposes)."""
    return x_user_id


@router.get("/", response_model=List[schemas.OrderResponse])
def list_orders(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all orders for the current user."""
    return crud.get_orders(db, user_id)


@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get a specific order."""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return order


@router.post("/", response_model=schemas.OrderResponse, status_code=201)
def create_order(
    order: schemas.OrderCreate,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create a new order from provided items."""
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")
    
    # Verify all products exist
    for item in order.items:
        if not crud.get_product(db, item.product_id):
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
    
    return crud.create_order(db, user_id, order.items)


@router.post("/from-cart", response_model=schemas.OrderResponse, status_code=201)
def create_order_from_cart(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Create an order from the user's current cart."""
    cart_items = crud.get_cart_items(db, user_id)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Convert cart items to order items
    order_items = [
        schemas.OrderItemBase(product_id=item.product_id, quantity=item.quantity)
        for item in cart_items
    ]
    
    # Create order and clear cart
    order = crud.create_order(db, user_id, order_items)
    crud.clear_cart(db, user_id)
    
    return order


@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update order status (admin endpoint)."""
    if status not in ["pending", "completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    order = crud.update_order_status(db, order_id, status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": f"Order status updated to {status}"}

