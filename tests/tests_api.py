"""API tests for the Online Store."""
import pytest


# Health & Root Tests
class TestHealthEndpoints:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "Online Store API running!"

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


# Product Tests
class TestProducts:
    def test_create_product(self, client):
        product_data = {
            "title": "Test Product",
            "price": 29.99,
            "description": "A test product",
            "category": "electronics"
        }
        response = client.post("/products/", json=product_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Product"
        assert data["price"] == 29.99
        assert "id" in data

    def test_list_products(self, client):
        # Create a product first
        client.post("/products/", json={"title": "Product 1", "price": 10.0, "category": "test"})
        client.post("/products/", json={"title": "Product 2", "price": 20.0, "category": "test"})
        
        response = client.get("/products/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_product(self, client):
        # Create a product
        create_response = client.post("/products/", json={"title": "Single Product", "price": 15.0, "category": "test"})
        product_id = create_response.json()["id"]
        
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Single Product"

    def test_get_product_not_found(self, client):
        response = client.get("/products/9999")
        assert response.status_code == 404

    def test_update_product(self, client):
        # Create a product
        create_response = client.post("/products/", json={"title": "Old Title", "price": 10.0, "category": "test"})
        product_id = create_response.json()["id"]
        
        # Update it
        response = client.put(f"/products/{product_id}", json={"title": "New Title"})
        assert response.status_code == 200
        assert response.json()["title"] == "New Title"

    def test_delete_product(self, client):
        # Create a product
        create_response = client.post("/products/", json={"title": "To Delete", "price": 5.0, "category": "test"})
        product_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/products/{product_id}")
        assert response.status_code == 204
        
        # Verify it's gone
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 404


# User Tests
class TestUsers:
    def test_create_user(self, client):
        user_data = {"email": "test@example.com", "name": "Test User", "password": "password123"}
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201
        assert response.json()["email"] == "test@example.com"

    def test_create_duplicate_user(self, client):
        user_data = {"email": "duplicate@example.com", "name": "User 1", "password": "password123"}
        client.post("/users/", json=user_data)
        
        # Try to create with same email
        response = client.post("/users/", json={"email": "duplicate@example.com", "name": "User 2", "password": "password123"})
        assert response.status_code == 400

    def test_list_users(self, client):
        client.post("/users/", json={"email": "user1@example.com", "password": "password123"})
        client.post("/users/", json={"email": "user2@example.com", "password": "password123"})
        
        response = client.get("/users/")
        assert response.status_code == 200
        assert len(response.json()) == 2


# Cart Tests
class TestCart:
    def test_add_to_cart(self, client):
        # Create user and product
        user_response = client.post("/users/", json={"email": "cart@example.com", "password": "password123"})
        user_id = user_response.json()["id"]
        
        product_response = client.post("/products/", json={"title": "Cart Item", "price": 25.0, "category": "test"})
        product_id = product_response.json()["id"]
        
        # Add to cart
        response = client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": 2},
            headers={"X-User-ID": str(user_id)}
        )
        assert response.status_code == 201

    def test_get_cart(self, client):
        # Create user and product
        user_response = client.post("/users/", json={"email": "getcart@example.com", "password": "password123"})
        user_id = user_response.json()["id"]
        
        product_response = client.post("/products/", json={"title": "Cart Product", "price": 50.0, "category": "test"})
        product_id = product_response.json()["id"]
        
        # Add to cart
        client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": 1},
            headers={"X-User-ID": str(user_id)}
        )
        
        # Get cart
        response = client.get("/cart/", headers={"X-User-ID": str(user_id)})
        assert response.status_code == 200
        assert response.json()["total"] == 50.0


# Order Tests
class TestOrders:
    def test_create_order(self, client):
        # Create user and product
        user_response = client.post("/users/", json={"email": "order@example.com", "password": "password123"})
        user_id = user_response.json()["id"]
        
        product_response = client.post("/products/", json={"title": "Order Item", "price": 100.0, "category": "test"})
        product_id = product_response.json()["id"]
        
        # Create order
        response = client.post(
            "/orders/",
            json={"items": [{"product_id": product_id, "quantity": 2}]},
            headers={"X-User-ID": str(user_id)}
        )
        assert response.status_code == 201
        assert response.json()["total"] == 200.0

    def test_list_orders(self, client):
        # Create user and product
        user_response = client.post("/users/", json={"email": "listorders@example.com", "password": "password123"})
        user_id = user_response.json()["id"]
        
        product_response = client.post("/products/", json={"title": "Order Product", "price": 30.0, "category": "test"})
        product_id = product_response.json()["id"]
        
        # Create order
        client.post(
            "/orders/",
            json={"items": [{"product_id": product_id, "quantity": 1}]},
            headers={"X-User-ID": str(user_id)}
        )
        
        # List orders
        response = client.get("/orders/", headers={"X-User-ID": str(user_id)})
        assert response.status_code == 200
        assert len(response.json()) == 1
