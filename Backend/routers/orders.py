"""Order API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User
from auth import get_current_user
import crud, schemas

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=List[schemas.OrderResponse])
def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders for the current user."""
    return crud.get_orders(db, current_user.id)


@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific order."""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return order


@router.post("/", response_model=schemas.OrderResponse, status_code=201)
def create_order(
    order: schemas.OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order from provided items."""
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")
    
    # Verify all products exist
    for item in order.items:
        if not crud.get_product(db, item.product_id):
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
    
    return crud.create_order(db, current_user.id, order.items)


@router.post("/from-cart", response_model=schemas.OrderResponse, status_code=201)
def create_order_from_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create an order from the user's current cart."""
    cart_items = crud.get_cart_items(db, current_user.id)
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Convert cart items to order items
    order_items = [
        schemas.OrderItemBase(product_id=item.product_id, quantity=item.quantity)
        for item in cart_items
    ]
    
    # Create order and clear cart
    order = crud.create_order(db, current_user.id, order_items)
    crud.clear_cart(db, current_user.id)
    
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

