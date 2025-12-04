"""Tests for wishlist and reviews features."""
import pytest
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Backend'))

from models import User, Product, Wishlist, Review
from auth import get_password_hash, create_access_token


class TestWishlist:
    """Tests for wishlist functionality."""
    
    def test_get_empty_wishlist(self, client, db):
        """Test getting empty wishlist."""
        # Create user
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        db.add(user)
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/wishlist", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["count"] == 0
    
    def test_add_to_wishlist(self, client, db):
        """Test adding product to wishlist."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add_all([user, product])
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/wishlist", json={"product_id": product.id}, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == product.id
    
    def test_add_duplicate_to_wishlist(self, client, db):
        """Test adding duplicate product to wishlist fails."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add_all([user, product])
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        client.post("/wishlist", json={"product_id": product.id}, headers=headers)
        response = client.post("/wishlist", json={"product_id": product.id}, headers=headers)
        assert response.status_code == 400
        assert "already in wishlist" in response.json()["detail"]
    
    def test_add_nonexistent_product_to_wishlist(self, client, db):
        """Test adding nonexistent product fails."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        db.add(user)
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/wishlist", json={"product_id": 9999}, headers=headers)
        assert response.status_code == 404
    
    def test_remove_from_wishlist(self, client, db):
        """Test removing product from wishlist."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add_all([user, product])
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        client.post("/wishlist", json={"product_id": product.id}, headers=headers)
        response = client.delete(f"/wishlist/{product.id}", headers=headers)
        assert response.status_code == 204
    
    def test_remove_nonexistent_from_wishlist(self, client, db):
        """Test removing product not in wishlist fails."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        db.add(user)
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.delete("/wishlist/9999", headers=headers)
        assert response.status_code == 404
    
    def test_check_wishlist_true(self, client, db):
        """Test checking product in wishlist returns true."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add_all([user, product])
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        client.post("/wishlist", json={"product_id": product.id}, headers=headers)
        response = client.get(f"/wishlist/check/{product.id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["in_wishlist"] is True
    
    def test_check_wishlist_false(self, client, db):
        """Test checking product not in wishlist returns false."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add_all([user, product])
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get(f"/wishlist/check/{product.id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["in_wishlist"] is False
    
    def test_wishlist_requires_auth(self, client, db):
        """Test wishlist endpoints require authentication."""
        response = client.get("/wishlist")
        assert response.status_code == 401


class TestReviews:
    """Tests for reviews functionality."""
    
    def test_get_product_reviews_empty(self, client, db):
        """Test getting reviews for product with no reviews."""
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add(product)
        db.commit()
        
        response = client.get(f"/reviews/product/{product.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == product.id
        assert data["average_rating"] == 0.0
        assert data["total_reviews"] == 0
        assert data["reviews"] == []
    
    def test_create_review(self, client, db):
        """Test creating a review."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add_all([user, product])
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/reviews",
            json={"product_id": product.id, "rating": 5, "comment": "Great product!"},
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == "Great product!"
        assert data["product_id"] == product.id
    
    def test_create_duplicate_review_fails(self, client, db):
        """Test user cannot review same product twice."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add_all([user, product])
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        client.post("/reviews", json={"product_id": product.id, "rating": 5}, headers=headers)
        response = client.post("/reviews", json={"product_id": product.id, "rating": 4}, headers=headers)
        assert response.status_code == 400
        assert "already reviewed" in response.json()["detail"]
    
    def test_create_review_invalid_rating(self, client, db):
        """Test review with invalid rating fails."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add_all([user, product])
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/reviews", json={"product_id": product.id, "rating": 6}, headers=headers)
        assert response.status_code == 422
    
    def test_create_review_nonexistent_product(self, client, db):
        """Test reviewing nonexistent product fails."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        db.add(user)
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post("/reviews", json={"product_id": 9999, "rating": 5}, headers=headers)
        assert response.status_code == 404
    
    def test_update_review(self, client, db):
        """Test updating a review."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add_all([user, product])
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        create_response = client.post("/reviews", json={"product_id": product.id, "rating": 3}, headers=headers)
        review_id = create_response.json()["id"]
        
        response = client.put(
            f"/reviews/{review_id}",
            json={"rating": 5, "comment": "Updated comment"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == "Updated comment"
    
    def test_delete_review(self, client, db):
        """Test deleting a review."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add_all([user, product])
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        create_response = client.post("/reviews", json={"product_id": product.id, "rating": 5}, headers=headers)
        review_id = create_response.json()["id"]
        
        response = client.delete(f"/reviews/{review_id}", headers=headers)
        assert response.status_code == 204
    
    def test_get_my_reviews(self, client, db):
        """Test getting user's own reviews."""
        user = User(email="test@example.com", password_hash=get_password_hash("pass123"), name="Test")
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add_all([user, product])
        db.commit()
        
        token = create_access_token({"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        client.post("/reviews", json={"product_id": product.id, "rating": 5}, headers=headers)
        
        response = client.get("/reviews/user/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["product_id"] == product.id
    
    def test_average_rating_calculation(self, client, db):
        """Test average rating is calculated correctly."""
        user1 = User(email="user1@test.com", password_hash=get_password_hash("pass"), name="User 1")
        user2 = User(email="user2@test.com", password_hash=get_password_hash("pass"), name="User 2")
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add_all([user1, user2, product])
        db.commit()
        
        # User 1 creates review
        token1 = create_access_token({"sub": str(user1.id)})
        client.post("/reviews", json={"product_id": product.id, "rating": 5}, headers={"Authorization": f"Bearer {token1}"})
        
        # User 2 creates review
        token2 = create_access_token({"sub": str(user2.id)})
        client.post("/reviews", json={"product_id": product.id, "rating": 3}, headers={"Authorization": f"Bearer {token2}"})
        
        response = client.get(f"/reviews/product/{product.id}")
        data = response.json()
        assert data["average_rating"] == 4.0
        assert data["total_reviews"] == 2
    
    def test_reviews_require_auth_for_create(self, client, db):
        """Test creating review requires authentication."""
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add(product)
        db.commit()
        
        response = client.post("/reviews", json={"product_id": product.id, "rating": 5})
        assert response.status_code == 401
    
    def test_get_reviews_public(self, client, db):
        """Test getting reviews is public."""
        product = Product(title="Test Product", price=29.99, category="electronics")
        db.add(product)
        db.commit()
        
        response = client.get(f"/reviews/product/{product.id}")
        assert response.status_code == 200
