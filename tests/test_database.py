"""Tests for database configuration and models."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from sqlalchemy import inspect

import database
import models


class TestDatabaseConfiguration:
    """Test database setup and configuration."""

    def test_database_url_configured(self):
        """Test that DATABASE_URL is configured."""
        assert database.DATABASE_URL is not None
        assert len(database.DATABASE_URL) > 0

    def test_engine_created(self):
        """Test that database engine is created."""
        assert database.engine is not None

    def test_session_local_configured(self):
        """Test that SessionLocal is configured."""
        assert database.SessionLocal is not None

    def test_base_declared(self):
        """Test that declarative Base is declared."""
        assert database.Base is not None

    def test_get_db_yields_session(self):
        """Test that get_db yields a session."""
        gen = database.get_db()
        session = next(gen)
        
        assert session is not None
        
        # Clean up
        try:
            next(gen)
        except StopIteration:
            pass


class TestModels:
    """Test SQLAlchemy models."""

    def test_product_model_columns(self, db):
        """Test Product model has correct columns."""
        inspector = inspect(models.Product)
        columns = [c.name for c in inspector.columns]
        
        assert "id" in columns
        assert "title" in columns
        assert "price" in columns
        assert "description" in columns
        assert "category" in columns
        assert "image" in columns
        assert "rating_rate" in columns
        assert "rating_count" in columns
        assert "created_at" in columns

    def test_user_model_columns(self, db):
        """Test User model has correct columns."""
        inspector = inspect(models.User)
        columns = [c.name for c in inspector.columns]
        
        assert "id" in columns
        assert "email" in columns
        assert "password_hash" in columns
        assert "name" in columns
        assert "is_active" in columns
        assert "created_at" in columns

    def test_order_model_columns(self, db):
        """Test Order model has correct columns."""
        inspector = inspect(models.Order)
        columns = [c.name for c in inspector.columns]
        
        assert "id" in columns
        assert "user_id" in columns
        assert "status" in columns
        assert "total" in columns
        assert "created_at" in columns

    def test_order_item_model_columns(self, db):
        """Test OrderItem model has correct columns."""
        inspector = inspect(models.OrderItem)
        columns = [c.name for c in inspector.columns]
        
        assert "id" in columns
        assert "order_id" in columns
        assert "product_id" in columns
        assert "quantity" in columns
        assert "price" in columns

    def test_cart_item_model_columns(self, db):
        """Test CartItem model has correct columns."""
        inspector = inspect(models.CartItem)
        columns = [c.name for c in inspector.columns]
        
        assert "id" in columns
        assert "user_id" in columns
        assert "product_id" in columns
        assert "quantity" in columns

    def test_product_creation(self, db):
        """Test creating a Product."""
        product = models.Product(
            title="Test",
            price=10.0,
            category="test"
        )
        db.add(product)
        db.commit()
        
        assert product.id is not None
        assert product.rating_rate == 0.0  # Default
        assert product.rating_count == 0  # Default

    def test_user_creation(self, db):
        """Test creating a User."""
        user = models.User(
            email="test@test.com",
            password_hash="hash",
            name="Test"
        )
        db.add(user)
        db.commit()
        
        assert user.id is not None
        assert user.is_active == 1  # Default active

    def test_user_email_unique(self, db):
        """Test that User email is unique."""
        user1 = models.User(email="same@test.com", password_hash="hash1")
        db.add(user1)
        db.commit()
        
        user2 = models.User(email="same@test.com", password_hash="hash2")
        db.add(user2)
        
        with pytest.raises(Exception):  # IntegrityError
            db.commit()

    def test_order_relationship(self, db, test_user, test_product):
        """Test Order relationships."""
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            quantity=1,
            price=test_product.price
        )
        db.add(order_item)
        db.commit()
        
        # Test relationships
        assert order.user == test_user
        assert len(order.items) == 1
        assert order.items[0].product == test_product

    def test_cart_item_relationship(self, db, test_user, test_product):
        """Test CartItem relationships."""
        cart_item = models.CartItem(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=2
        )
        db.add(cart_item)
        db.commit()
        
        assert cart_item.user == test_user
        assert cart_item.product == test_product

    def test_order_cascade_delete(self, db, test_user, test_product):
        """Test that deleting an order cascades to order items."""
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            quantity=1,
            price=test_product.price
        )
        db.add(order_item)
        db.commit()
        
        order_item_id = order_item.id
        
        # Delete order
        db.delete(order)
        db.commit()
        
        # Order item should also be deleted (cascade)
        deleted_item = db.query(models.OrderItem).filter(
            models.OrderItem.id == order_item_id
        ).first()
        assert deleted_item is None
