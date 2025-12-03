from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Cart, CartItem, User
from app.schemas import CartItemCreate, CartResponse

router = APIRouter()


@router.get("/{user_id}", response_model=CartResponse)
def get_cart(user_id: int, db: Session = Depends(get_db)):
    """Get cart for a specific user"""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


@router.post("/{user_id}", response_model=CartResponse)
def create_or_get_cart(user_id: int, db: Session = Depends(get_db)):
    """Create a cart for user or return existing cart"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if cart already exists
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if cart:
        return cart
    
    # Create new cart
    cart = Cart(user_id=user_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


@router.post("/{cart_id}/items")
def add_item_to_cart(cart_id: int, item: CartItemCreate, db: Session = Depends(get_db)):
    """Add an item to the cart"""
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # Check if item already in cart
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart_id,
        CartItem.product_id == item.product_id
    ).first()
    
    if existing_item:
        existing_item.quantity += item.quantity
    else:
        cart_item = CartItem(
            cart_id=cart_id,
            product_id=item.product_id,
            product_name=item.product_name,
            quantity=item.quantity,
            price=item.price
        )
        db.add(cart_item)
    
    db.commit()
    return {"message": "Item added to cart"}


@router.delete("/{cart_id}/items/{item_id}")
def remove_item_from_cart(cart_id: int, item_id: int, db: Session = Depends(get_db)):
    """Remove an item from the cart"""
    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart_id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    db.delete(item)
    db.commit()
    return {"message": "Item removed from cart"}


@router.delete("/{cart_id}/clear")
def clear_cart(cart_id: int, db: Session = Depends(get_db)):
    """Clear all items from cart"""
    db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
    db.commit()
    return {"message": "Cart cleared"}
