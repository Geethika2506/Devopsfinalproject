"""Pytest configuration and shared fixtures."""
import sys
import os

# Add Backend to path BEFORE any imports, matching how main.py does it
# This ensures we use the same module instances
backend_path = os.path.join(os.path.dirname(__file__), '..', 'Backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Now import using the same style as backend modules
from database import Base, get_db
from main import app
import models
from auth import get_password_hash

# Test database (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency with test database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client with fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """Create a test user and return it."""
    hashed_password = get_password_hash("testpassword123")
    user = models.User(
        email="testuser@example.com",
        password_hash=hashed_password,
        name="Test User",
        is_active=1
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_product(db):
    """Create a test product and return it."""
    product = models.Product(
        title="Test Product",
        price=29.99,
        description="A test product",
        category="electronics",
        image="http://example.com/image.jpg",
        rating_rate=4.5,
        rating_count=100
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/auth/login",
        data={"username": test_user.email, "password": "testpassword123"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def multiple_products(db):
    """Create multiple test products."""
    products = [
        models.Product(title="Product 1", price=10.0, category="electronics"),
        models.Product(title="Product 2", price=20.0, category="electronics"),
        models.Product(title="Product 3", price=30.0, category="clothing"),
        models.Product(title="Product 4", price=40.0, category="clothing"),
        models.Product(title="Product 5", price=50.0, category="books"),
    ]
    db.add_all(products)
    db.commit()
    return products
