"""Reviews router for product reviews."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from database import get_db
from models import Review, Product, User
from schemas import (
    ReviewCreate, ReviewUpdate, ReviewResponse, 
    ProductReviewsResponse
)
from auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/product/{product_id}", response_model=ProductReviewsResponse)
def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get all reviews for a product."""
    # Check if product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    
    # Calculate average rating
    avg_rating = 0.0
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
    
    return ProductReviewsResponse(
        product_id=product_id,
        average_rating=round(avg_rating, 1),
        total_reviews=len(reviews),
        reviews=reviews
    )


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a review for a product."""
    # Check if product exists
    product = db.query(Product).filter(Product.id == review.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if user already reviewed this product
    existing = db.query(Review).filter(
        Review.user_id == current_user.id,
        Review.product_id == review.product_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product. Use PUT to update."
        )
    
    # Create review
    db_review = Review(
        user_id=current_user.id,
        product_id=review.product_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    # Update product rating
    _update_product_rating(db, review.product_id)
    
    return db_review


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a review."""
    db_review = db.query(Review).filter(Review.id == review_id).first()
    
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if db_review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own reviews"
        )
    
    # Update fields
    if review_update.rating is not None:
        db_review.rating = review_update.rating
    if review_update.comment is not None:
        db_review.comment = review_update.comment
    
    db.commit()
    db.refresh(db_review)
    
    # Update product rating
    _update_product_rating(db, db_review.product_id)
    
    return db_review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a review."""
    db_review = db.query(Review).filter(Review.id == review_id).first()
    
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if db_review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )
    
    product_id = db_review.product_id
    db.delete(db_review)
    db.commit()
    
    # Update product rating
    _update_product_rating(db, product_id)
    
    return None


@router.get("/user/me", response_model=List[ReviewResponse])
def get_my_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reviews by the current user."""
    reviews = db.query(Review).filter(Review.user_id == current_user.id).all()
    return reviews


def _update_product_rating(db: Session, product_id: int):
    """Helper function to update product's average rating."""
    result = db.query(
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('count')
    ).filter(Review.product_id == product_id).first()
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.rating_rate = round(result.avg_rating or 0, 1)
        product.rating_count = result.count or 0
        db.commit()
