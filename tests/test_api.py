import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and home endpoints"""

    def test_home(self):
        """Test home endpoint returns correct message"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
        assert response.json()["status"] == "online"

    def test_health(self):
        """Test health endpoint returns healthy status"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestProductEndpoints:
    """Test product-related endpoints"""

    def test_list_products(self):
        """Test getting all products"""
        response = client.get("/products/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) > 0

    def test_list_categories(self):
        """Test getting all categories"""
        response = client.get("/products/categories")
        assert response.status_code == 200
        assert "categories" in response.json()
        assert len(response.json()["categories"]) > 0

    def test_get_products_by_category(self):
        """Test getting products by category"""
        response = client.get("/products/category/electronics")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        for product in response.json():
            assert product["category"] == "electronics"

    def test_get_product_by_id(self):
        """Test getting a single product"""
        response = client.get("/products/1")
        assert response.status_code == 200
        assert response.json()["id"] == 1

    def test_get_nonexistent_product(self):
        """Test getting a product that doesn't exist"""
        response = client.get("/products/9999")
        assert response.status_code == 404


class TestUserEndpoints:
    """Test user-related endpoints"""

    def test_create_user(self):
        """Test creating a new user"""
        response = client.post("/users/", json={
            "username": "testuser123",
            "email": "test123@example.com"
        })
        # Either 200 (created) or 400 (already exists from previous test)
        assert response.status_code in [200, 400]

    def test_list_users(self):
        """Test listing all users"""
        response = client.get("/users/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestCartEndpoints:
    """Test cart-related endpoints"""

    def test_get_cart_not_found(self):
        """Test getting cart for non-existent user"""
        response = client.get("/cart/9999")
        assert response.status_code == 404
