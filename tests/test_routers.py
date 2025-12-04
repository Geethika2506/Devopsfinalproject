"""Tests for API router endpoints."""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Backend'))

from auth import create_access_token


class TestAuthRouter:
    """Test authentication endpoints."""

    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post("/auth/register", json={
            "email": "newuser@example.com",
            "password": "password123",
            "name": "New User"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert "id" in data
        assert "password" not in data  # Password should not be returned

    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email fails."""
        response = client.post("/auth/register", json={
            "email": test_user.email,
            "password": "password123",
            "name": "Another User"
        })
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        """Test registration with invalid email fails."""
        response = client.post("/auth/register", json={
            "email": "not-an-email",
            "password": "password123"
        })
        
        assert response.status_code == 422  # Validation error

    def test_register_short_password(self, client):
        """Test registration with short password fails."""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "short"  # Less than 6 characters
        })
        
        assert response.status_code == 422

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post("/auth/login", data={
            "username": test_user.email,  # OAuth2 uses 'username' field
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_json_success(self, client, test_user):
        """Test login with JSON body."""
        response = client.post("/auth/login/json", json={
            "email": test_user.email,
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post("/auth/login", data={
            "username": test_user.email,
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post("/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 401

    def test_me_endpoint(self, client, auth_headers):
        """Test /auth/me endpoint."""
        response = client.get("/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        assert "email" in response.json()


class TestProductsRouter:
    """Test products endpoints."""

    def test_create_product(self, client):
        """Test creating a product."""
        response = client.post("/products/", json={
            "title": "New Product",
            "price": 29.99,
            "description": "A great product",
            "category": "electronics"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Product"
        assert data["price"] == 29.99
        assert "id" in data

    def test_list_products(self, client, multiple_products):
        """Test listing all products."""
        response = client.get("/products/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_list_products_with_category(self, client, multiple_products):
        """Test filtering products by category."""
        response = client.get("/products/?category=electronics")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(p["category"] == "electronics" for p in data)

    def test_get_product(self, client, test_product):
        """Test getting a single product."""
        response = client.get(f"/products/{test_product.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_product.id
        assert data["title"] == test_product.title

    def test_get_product_not_found(self, client):
        """Test getting non-existent product."""
        response = client.get("/products/9999")
        
        assert response.status_code == 404

    def test_update_product(self, client, test_product):
        """Test updating a product."""
        response = client.put(f"/products/{test_product.id}", json={
            "title": "Updated Title",
            "price": 39.99
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["price"] == 39.99

    def test_update_product_partial(self, client, test_product):
        """Test partial product update."""
        original_price = test_product.price
        response = client.put(f"/products/{test_product.id}", json={
            "title": "Only Title Changed"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Only Title Changed"
        assert data["price"] == original_price

    def test_delete_product(self, client, test_product):
        """Test deleting a product."""
        response = client.delete(f"/products/{test_product.id}")
        
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(f"/products/{test_product.id}")
        assert response.status_code == 404

    def test_get_categories(self, client, multiple_products):
        """Test getting product categories."""
        response = client.get("/products/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert "electronics" in data
        assert "clothing" in data
        assert "books" in data


class TestUsersRouter:
    """Test users endpoints."""

    def test_create_user(self, client):
        """Test creating a user."""
        response = client.post("/users/", json={
            "email": "newuser@example.com",
            "name": "New User",
            "password": "password123"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"

    def test_create_duplicate_user(self, client, test_user):
        """Test creating user with duplicate email."""
        response = client.post("/users/", json={
            "email": test_user.email,
            "name": "Duplicate",
            "password": "password123"
        })
        
        assert response.status_code == 400

    def test_list_users(self, client, test_user):
        """Test listing users."""
        response = client.get("/users/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_user(self, client, test_user):
        """Test getting a specific user."""
        response = client.get(f"/users/{test_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id


class TestCartRouter:
    """Test cart endpoints."""

    def test_add_to_cart(self, client, test_user, test_product):
        """Test adding item to cart."""
        response = client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 2},
            headers={"X-User-ID": str(test_user.id)}
        )
        
        assert response.status_code == 201

    def test_get_cart(self, client, test_user, test_product):
        """Test getting cart contents."""
        # Add item first
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 2},
            headers={"X-User-ID": str(test_user.id)}
        )
        
        response = client.get(
            "/cart/",
            headers={"X-User-ID": str(test_user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == test_product.price * 2

    def test_update_cart_item(self, client, test_user, test_product):
        """Test updating cart item quantity."""
        # Add item first
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 1},
            headers={"X-User-ID": str(test_user.id)}
        )
        
        response = client.put(
            f"/cart/items/{test_product.id}?quantity=5",
            headers={"X-User-ID": str(test_user.id)}
        )
        
        assert response.status_code == 200

    def test_remove_from_cart(self, client, test_user, test_product):
        """Test removing item from cart."""
        # Add item first
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 1},
            headers={"X-User-ID": str(test_user.id)}
        )
        
        response = client.delete(
            f"/cart/items/{test_product.id}",
            headers={"X-User-ID": str(test_user.id)}
        )
        
        assert response.status_code == 204

    def test_clear_cart(self, client, test_user, test_product):
        """Test clearing all cart items."""
        # Add items
        client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 2},
            headers={"X-User-ID": str(test_user.id)}
        )
        
        response = client.delete(
            "/cart/",
            headers={"X-User-ID": str(test_user.id)}
        )
        
        assert response.status_code == 204


class TestOrdersRouter:
    """Test orders endpoints."""

    def test_create_order(self, client, test_user, test_product):
        """Test creating an order."""
        token = create_access_token({"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.post(
            "/orders/",
            json={"items": [{"product_id": test_product.id, "quantity": 2}]},
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["total"] == test_product.price * 2
        assert data["status"] == "pending"

    def test_list_orders(self, client, test_user, test_product):
        """Test listing user orders."""
        token = create_access_token({"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create an order first
        client.post(
            "/orders/",
            json={"items": [{"product_id": test_product.id, "quantity": 1}]},
            headers=headers
        )
        
        response = client.get(
            "/orders/",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_get_order(self, client, test_user, test_product):
        """Test getting a specific order."""
        token = create_access_token({"sub": str(test_user.id)})
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create an order first
        create_response = client.post(
            "/orders/",
            json={"items": [{"product_id": test_product.id, "quantity": 1}]},
            headers=headers
        )
        order_id = create_response.json()["id"]
        
        response = client.get(
            f"/orders/{order_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        assert response.json()["id"] == order_id


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "message" in response.json()

    def test_health(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
