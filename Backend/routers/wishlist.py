"""Wishlist router for user wishlists."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Wishlist, Product, User
from schemas import WishlistItemCreate, WishlistItemResponse, WishlistResponse
from auth import get_current_user

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("", response_model=WishlistResponse)
def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's wishlist."""
    items = db.query(Wishlist).filter(Wishlist.user_id == current_user.id).all()
    return WishlistResponse(items=items, count=len(items))


@router.post("", response_model=WishlistItemResponse, status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
    item: WishlistItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a product to the wishlist."""
    # Check if product exists
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if already in wishlist
    existing = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == item.product_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product already in wishlist"
        )
    
    # Add to wishlist
    wishlist_item = Wishlist(
        user_id=current_user.id,
        product_id=item.product_id
    )
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    
    return wishlist_item


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a product from the wishlist."""
    wishlist_item = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == product_id
    ).first()
    
    if not wishlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not in wishlist"
        )
    
    db.delete(wishlist_item)
    db.commit()
    return None


@router.get("/check/{product_id}")
def check_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if a product is in the user's wishlist."""
    exists = db.query(Wishlist).filter(
        Wishlist.user_id == current_user.id,
        Wishlist.product_id == product_id
    ).first() is not None
    
    return {"in_wishlist": exists}
