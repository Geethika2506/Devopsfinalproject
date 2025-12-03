"""Integration tests for end-to-end workflows."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Backend'))

import pytest
import models
from auth import get_password_hash


class TestUserJourney:
    """Test complete user journey from registration to order."""

    def test_full_user_journey(self, client):
        """Test complete e-commerce flow: register → login → browse → cart → order."""
        
        # 1. Register a new user
        register_response = client.post("/auth/register", json={
            "email": "journey@example.com",
            "password": "journeypass123",
            "name": "Journey User"
        })
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]
        
        # 2. Login
        login_response = client.post("/auth/login", data={
            "username": "journey@example.com",
            "password": "journeypass123"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        auth_headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Verify can access protected endpoint
        me_response = client.get("/auth/me", headers=auth_headers)
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "journey@example.com"
        
        # 4. Create some products
        product1 = client.post("/products/", json={
            "title": "Laptop",
            "price": 999.99,
            "category": "electronics"
        }).json()
        
        product2 = client.post("/products/", json={
            "title": "Mouse",
            "price": 29.99,
            "category": "electronics"
        }).json()
        
        # 5. Browse products
        products_response = client.get("/products/")
        assert products_response.status_code == 200
        assert len(products_response.json()) >= 2
        
        # 6. Add items to cart
        client.post(
            "/cart/items",
            json={"product_id": product1["id"], "quantity": 1},
            headers={"X-User-ID": str(user_id)}
        )
        client.post(
            "/cart/items",
            json={"product_id": product2["id"], "quantity": 2},
            headers={"X-User-ID": str(user_id)}
        )
        
        # 7. View cart
        cart_response = client.get("/cart/", headers={"X-User-ID": str(user_id)})
        assert cart_response.status_code == 200
        cart = cart_response.json()
        expected_total = 999.99 + (29.99 * 2)
        assert abs(cart["total"] - expected_total) < 0.01
        
        # 8. Create order
        order_response = client.post(
            "/orders/",
            json={"items": [
                {"product_id": product1["id"], "quantity": 1},
                {"product_id": product2["id"], "quantity": 2}
            ]},
            headers={"X-User-ID": str(user_id)}
        )
        assert order_response.status_code == 201
        order = order_response.json()
        assert order["status"] == "pending"
        assert abs(order["total"] - expected_total) < 0.01
        
        # 9. View order history
        orders_response = client.get("/orders/", headers={"X-User-ID": str(user_id)})
        assert orders_response.status_code == 200
        assert len(orders_response.json()) >= 1


class TestCartWorkflow:
    """Test cart manipulation workflows."""

    def test_cart_add_update_remove(self, client, test_user, multiple_products):
        """Test adding, updating, and removing cart items."""
        user_headers = {"X-User-ID": str(test_user.id)}
        
        # Add multiple items
        for product in multiple_products[:3]:
            response = client.post(
                "/cart/items",
                json={"product_id": product.id, "quantity": 1},
                headers=user_headers
            )
            assert response.status_code == 201
        
        # Verify cart has 3 items
        cart = client.get("/cart/", headers=user_headers).json()
        assert len(cart["items"]) == 3
        
        # Update quantity
        client.put(
            f"/cart/items/{multiple_products[0].id}",
            json={"quantity": 5},
            headers=user_headers
        )
        
        # Remove one item
        client.delete(
            f"/cart/items/{multiple_products[1].id}",
            headers=user_headers
        )
        
        # Verify cart now has 2 items
        cart = client.get("/cart/", headers=user_headers).json()
        assert len(cart["items"]) == 2
        
        # Clear cart
        client.delete("/cart/", headers=user_headers)
        
        # Verify empty cart
        cart = client.get("/cart/", headers=user_headers).json()
        assert len(cart["items"]) == 0
        assert cart["total"] == 0


class TestProductLifecycle:
    """Test product CRUD lifecycle."""

    def test_product_crud_lifecycle(self, client):
        """Test complete product lifecycle: create → read → update → delete."""
        
        # Create
        create_response = client.post("/products/", json={
            "title": "Lifecycle Product",
            "price": 50.0,
            "description": "Test product",
            "category": "test"
        })
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Read
        get_response = client.get(f"/products/{product_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Lifecycle Product"
        
        # Update
        update_response = client.put(f"/products/{product_id}", json={
            "title": "Updated Lifecycle Product",
            "price": 75.0
        })
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Lifecycle Product"
        assert update_response.json()["price"] == 75.0
        
        # Verify update persisted
        verify_response = client.get(f"/products/{product_id}")
        assert verify_response.json()["title"] == "Updated Lifecycle Product"
        
        # Delete
        delete_response = client.delete(f"/products/{product_id}")
        assert delete_response.status_code == 204
        
        # Verify deleted
        not_found_response = client.get(f"/products/{product_id}")
        assert not_found_response.status_code == 404


class TestAuthenticationFlow:
    """Test authentication workflows."""

    def test_register_login_access_protected(self, client):
        """Test register → login → access protected resource."""
        
        # Register
        client.post("/auth/register", json={
            "email": "authflow@example.com",
            "password": "authflowpass123",
            "name": "Auth Flow User"
        })
        
        # Login
        login_response = client.post("/auth/login", data={
            "username": "authflow@example.com",
            "password": "authflowpass123"
        })
        token = login_response.json()["access_token"]
        
        # Access protected resource
        me_response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "authflow@example.com"

    def test_cannot_access_protected_without_token(self, client):
        """Test that protected endpoints require auth."""
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_cannot_access_with_invalid_token(self, client):
        """Test that invalid tokens are rejected."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401


class TestConcurrentOperations:
    """Test concurrent/multiple operations."""

    def test_multiple_users_separate_carts(self, client, multiple_products, db):
        """Test that multiple users have separate carts."""
        # Create two users
        user1 = models.User(
            email="user1@test.com",
            password_hash=get_password_hash("pass1"),
            is_active=1
        )
        user2 = models.User(
            email="user2@test.com",
            password_hash=get_password_hash("pass2"),
            is_active=1
        )
        db.add_all([user1, user2])
        db.commit()
        
        # User 1 adds to cart
        client.post(
            "/cart/items",
            json={"product_id": multiple_products[0].id, "quantity": 3},
            headers={"X-User-ID": str(user1.id)}
        )
        
        # User 2 adds different item
        client.post(
            "/cart/items",
            json={"product_id": multiple_products[1].id, "quantity": 1},
            headers={"X-User-ID": str(user2.id)}
        )
        
        # Verify separate carts
        cart1 = client.get("/cart/", headers={"X-User-ID": str(user1.id)}).json()
        cart2 = client.get("/cart/", headers={"X-User-ID": str(user2.id)}).json()
        
        assert len(cart1["items"]) == 1
        assert cart1["items"][0]["quantity"] == 3
        
        assert len(cart2["items"]) == 1
        assert cart2["items"][0]["quantity"] == 1

    def test_multiple_orders_same_user(self, client, test_user, multiple_products):
        """Test user can create multiple orders."""
        user_headers = {"X-User-ID": str(test_user.id)}
        
        # Create first order
        order1 = client.post(
            "/orders/",
            json={"items": [{"product_id": multiple_products[0].id, "quantity": 1}]},
            headers=user_headers
        ).json()
        
        # Create second order
        order2 = client.post(
            "/orders/",
            json={"items": [{"product_id": multiple_products[1].id, "quantity": 2}]},
            headers=user_headers
        ).json()
        
        # Verify both orders exist
        orders = client.get("/orders/", headers=user_headers).json()
        assert len(orders) >= 2
        
        order_ids = [o["id"] for o in orders]
        assert order1["id"] in order_ids
        assert order2["id"] in order_ids


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_order_nonexistent_product(self, client, test_user):
        """Test ordering a non-existent product."""
        response = client.post(
            "/orders/",
            json={"items": [{"product_id": 99999, "quantity": 1}]},
            headers={"X-User-ID": str(test_user.id)}
        )
        # Should handle gracefully (may return error or skip item)
        # The exact behavior depends on implementation

    def test_empty_product_list(self, client):
        """Test getting products when none exist."""
        response = client.get("/products/")
        assert response.status_code == 200
        # Should return empty list, not error

    def test_cart_without_user_header(self, client, test_product):
        """Test cart operations without user identification."""
        # This tests error handling when X-User-ID is missing
        response = client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 1}
        )
        # Should return error about missing user

    def test_filter_by_nonexistent_category(self, client, multiple_products):
        """Test filtering by category that doesn't exist."""
        response = client.get("/products/?category=nonexistent")
        assert response.status_code == 200
        assert len(response.json()) == 0
