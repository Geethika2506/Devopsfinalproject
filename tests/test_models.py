"""Comprehensive tests for SQLAlchemy models."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from datetime import datetime
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

import models
from auth import get_password_hash


class TestProductModel:
    """Test Product model."""

    def test_create_product_minimal(self, db):
        """Test creating a product with minimal required fields."""
        product = models.Product(
            title="Minimal Product",
            price=9.99,
            category="test"
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        assert product.id is not None
        assert product.title == "Minimal Product"
        assert product.price == 9.99
        assert product.category == "test"

    def test_create_product_full(self, db):
        """Test creating a product with all fields."""
        product = models.Product(
            title="Full Product",
            price=199.99,
            description="A fully described product",
            category="electronics",
            image="http://example.com/image.jpg",
            rating_rate=4.5,
            rating_count=100
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        assert product.id is not None
        assert product.title == "Full Product"
        assert product.price == 199.99
        assert product.description == "A fully described product"
        assert product.category == "electronics"
        assert product.image == "http://example.com/image.jpg"
        assert product.rating_rate == 4.5
        assert product.rating_count == 100

    def test_product_default_values(self, db):
        """Test Product default values."""
        product = models.Product(
            title="Default Test",
            price=10.0,
            category="test"
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        assert product.description is None
        assert product.image is None
        assert product.rating_rate == 0.0
        assert product.rating_count == 0
        assert product.created_at is not None

    def test_product_created_at_auto(self, db):
        """Test that created_at is automatically set."""
        product = models.Product(
            title="Timestamp Test",
            price=5.0,
            category="test"
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        assert product.created_at is not None
        assert isinstance(product.created_at, datetime)

    def test_product_price_float(self, db):
        """Test product price as float."""
        product = models.Product(
            title="Price Test",
            price=99.999,
            category="test"
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
        assert isinstance(product.price, float)

    def test_product_order_items_relationship(self, db, test_user):
        """Test Product to OrderItems relationship."""
        product = models.Product(
            title="Relationship Test",
            price=50.0,
            category="test"
        )
        db.add(product)
        db.commit()
        
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        
        order_item = models.OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=2,
            price=product.price
        )
        db.add(order_item)
        db.commit()
        
        assert len(product.order_items) == 1
        assert product.order_items[0].quantity == 2


class TestUserModel:
    """Test User model."""

    def test_create_user_minimal(self, db):
        """Test creating a user with minimal fields."""
        user = models.User(
            email="minimal@test.com",
            password_hash="somehash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        assert user.email == "minimal@test.com"

    def test_create_user_full(self, db):
        """Test creating a user with all fields."""
        user = models.User(
            email="full@test.com",
            password_hash=get_password_hash("password123"),
            name="Full User",
            is_active=1
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        assert user.email == "full@test.com"
        assert user.name == "Full User"
        assert user.is_active == 1

    def test_user_default_active(self, db):
        """Test user is active by default."""
        user = models.User(
            email="active@test.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.is_active == 1

    def test_user_email_unique_constraint(self, db):
        """Test that email must be unique."""
        user1 = models.User(
            email="duplicate@test.com",
            password_hash="hash1"
        )
        db.add(user1)
        db.commit()
        
        user2 = models.User(
            email="duplicate@test.com",
            password_hash="hash2"
        )
        db.add(user2)
        
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_user_orders_relationship(self, db):
        """Test User to Orders relationship."""
        user = models.User(
            email="orders@test.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        
        order1 = models.Order(user_id=user.id)
        order2 = models.Order(user_id=user.id)
        db.add_all([order1, order2])
        db.commit()
        
        assert len(user.orders) == 2

    def test_user_cart_items_relationship(self, db, test_product):
        """Test User to CartItems relationship."""
        user = models.User(
            email="cart@test.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        
        cart_item = models.CartItem(
            user_id=user.id,
            product_id=test_product.id,
            quantity=3
        )
        db.add(cart_item)
        db.commit()
        
        assert len(user.cart_items) == 1
        assert user.cart_items[0].quantity == 3

    def test_user_created_at_auto(self, db):
        """Test that user created_at is auto-set."""
        user = models.User(
            email="timestamp@test.com",
            password_hash="hash"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.created_at is not None

    def test_user_inactive(self, db):
        """Test creating an inactive user."""
        user = models.User(
            email="inactive@test.com",
            password_hash="hash",
            is_active=0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.is_active == 0


class TestOrderModel:
    """Test Order model."""

    def test_create_order(self, db, test_user):
        """Test creating an order."""
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        db.refresh(order)
        
        assert order.id is not None
        assert order.user_id == test_user.id

    def test_order_default_status(self, db, test_user):
        """Test order default status is pending."""
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        db.refresh(order)
        
        assert order.status == "pending"

    def test_order_default_total(self, db, test_user):
        """Test order default total is 0."""
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        db.refresh(order)
        
        assert order.total == 0.0

    def test_order_with_status(self, db, test_user):
        """Test creating order with specific status."""
        order = models.Order(
            user_id=test_user.id,
            status="completed",
            total=150.0
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        assert order.status == "completed"
        assert order.total == 150.0

    def test_order_user_relationship(self, db, test_user):
        """Test Order to User relationship."""
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        db.refresh(order)
        
        assert order.user == test_user
        assert order.user.email == test_user.email

    def test_order_items_relationship(self, db, test_user, test_product):
        """Test Order to OrderItems relationship."""
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        
        item1 = models.OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            quantity=1,
            price=test_product.price
        )
        db.add(item1)
        db.commit()
        
        assert len(order.items) == 1

    def test_order_cascade_delete_items(self, db, test_user, test_product):
        """Test that deleting order cascades to items."""
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        
        item = models.OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            quantity=1,
            price=10.0
        )
        db.add(item)
        db.commit()
        
        item_id = item.id
        
        db.delete(order)
        db.commit()
        
        # Item should be deleted due to cascade
        deleted_item = db.query(models.OrderItem).filter(
            models.OrderItem.id == item_id
        ).first()
        assert deleted_item is None

    def test_order_created_at_auto(self, db, test_user):
        """Test order created_at is auto-set."""
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        db.refresh(order)
        
        assert order.created_at is not None


class TestOrderItemModel:
    """Test OrderItem model."""

    def test_create_order_item(self, db, test_user, test_product):
        """Test creating an order item."""
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        
        item = models.OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            quantity=3,
            price=29.99
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        
        assert item.id is not None
        assert item.order_id == order.id
        assert item.product_id == test_product.id
        assert item.quantity == 3
        assert item.price == 29.99

    def test_order_item_default_quantity(self, db, test_user, test_product):
        """Test order item default quantity is 1."""
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        
        item = models.OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            price=10.0
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        
        assert item.quantity == 1

    def test_order_item_order_relationship(self, db, test_user, test_product):
        """Test OrderItem to Order relationship."""
        order = models.Order(user_id=test_user.id, total=100.0)
        db.add(order)
        db.commit()
        
        item = models.OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            quantity=1,
            price=100.0
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        
        assert item.order == order
        assert item.order.total == 100.0

    def test_order_item_product_relationship(self, db, test_user, test_product):
        """Test OrderItem to Product relationship."""
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        
        item = models.OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            quantity=1,
            price=test_product.price
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        
        assert item.product == test_product
        assert item.product.title == test_product.title

    def test_order_item_price_at_order_time(self, db, test_user, test_product):
        """Test that order item price is captured at order time."""
        original_price = test_product.price
        
        order = models.Order(user_id=test_user.id)
        db.add(order)
        db.commit()
        
        item = models.OrderItem(
            order_id=order.id,
            product_id=test_product.id,
            quantity=1,
            price=original_price
        )
        db.add(item)
        db.commit()
        
        # Change product price
        test_product.price = original_price + 50
        db.commit()
        
        # Order item price should remain unchanged
        db.refresh(item)
        assert item.price == original_price


class TestCartItemModel:
    """Test CartItem model."""

    def test_create_cart_item(self, db, test_user, test_product):
        """Test creating a cart item."""
        item = models.CartItem(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=2
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        
        assert item.id is not None
        assert item.user_id == test_user.id
        assert item.product_id == test_product.id
        assert item.quantity == 2

    def test_cart_item_default_quantity(self, db, test_user, test_product):
        """Test cart item default quantity is 1."""
        item = models.CartItem(
            user_id=test_user.id,
            product_id=test_product.id
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        
        assert item.quantity == 1

    def test_cart_item_user_relationship(self, db, test_user, test_product):
        """Test CartItem to User relationship."""
        item = models.CartItem(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=1
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        
        assert item.user == test_user
        assert item.user.email == test_user.email

    def test_cart_item_product_relationship(self, db, test_user, test_product):
        """Test CartItem to Product relationship."""
        item = models.CartItem(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=1
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        
        assert item.product == test_product
        assert item.product.title == test_product.title

    def test_cart_item_update_quantity(self, db, test_user, test_product):
        """Test updating cart item quantity."""
        item = models.CartItem(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=1
        )
        db.add(item)
        db.commit()
        
        item.quantity = 5
        db.commit()
        db.refresh(item)
        
        assert item.quantity == 5

    def test_multiple_cart_items_same_user(self, db, test_user, multiple_products):
        """Test user can have multiple cart items."""
        items = []
        for product in multiple_products[:3]:
            item = models.CartItem(
                user_id=test_user.id,
                product_id=product.id,
                quantity=1
            )
            items.append(item)
        
        db.add_all(items)
        db.commit()
        
        user_cart = db.query(models.CartItem).filter(
            models.CartItem.user_id == test_user.id
        ).all()
        
        assert len(user_cart) == 3


class TestModelTableNames:
    """Test model table names are correct."""

    def test_product_table_name(self):
        """Test Product table name."""
        assert models.Product.__tablename__ == "products"

    def test_user_table_name(self):
        """Test User table name."""
        assert models.User.__tablename__ == "users"

    def test_order_table_name(self):
        """Test Order table name."""
        assert models.Order.__tablename__ == "orders"

    def test_order_item_table_name(self):
        """Test OrderItem table name."""
        assert models.OrderItem.__tablename__ == "order_items"

    def test_cart_item_table_name(self):
        """Test CartItem table name."""
        assert models.CartItem.__tablename__ == "cart_items"


class TestModelPrimaryKeys:
    """Test model primary keys."""

    def test_product_primary_key(self, db):
        """Test Product has auto-incrementing primary key."""
        p1 = models.Product(title="P1", price=10.0, category="test")
        p2 = models.Product(title="P2", price=20.0, category="test")
        db.add_all([p1, p2])
        db.commit()
        
        assert p1.id is not None
        assert p2.id is not None
        assert p2.id > p1.id

    def test_user_primary_key(self, db):
        """Test User has auto-incrementing primary key."""
        u1 = models.User(email="u1@test.com", password_hash="h1")
        u2 = models.User(email="u2@test.com", password_hash="h2")
        db.add_all([u1, u2])
        db.commit()
        
        assert u1.id is not None
        assert u2.id is not None
        assert u2.id > u1.id

    def test_order_primary_key(self, db, test_user):
        """Test Order has auto-incrementing primary key."""
        o1 = models.Order(user_id=test_user.id)
        o2 = models.Order(user_id=test_user.id)
        db.add_all([o1, o2])
        db.commit()
        
        assert o1.id is not None
        assert o2.id is not None
        assert o2.id > o1.id


class TestModelForeignKeys:
    """Test model foreign key constraints.
    
    Note: SQLite doesn't enforce FK constraints by default.
    These tests verify the FK relationships exist in the schema.
    """

    def test_order_has_user_foreign_key(self):
        """Test Order has user_id foreign key defined."""
        inspector = inspect(models.Order)
        fks = list(inspector.mapper.relationships.keys())
        assert "user" in fks

    def test_order_item_has_order_foreign_key(self):
        """Test OrderItem has order_id foreign key defined."""
        inspector = inspect(models.OrderItem)
        fks = list(inspector.mapper.relationships.keys())
        assert "order" in fks

    def test_order_item_has_product_foreign_key(self):
        """Test OrderItem has product_id foreign key defined."""
        inspector = inspect(models.OrderItem)
        fks = list(inspector.mapper.relationships.keys())
        assert "product" in fks

    def test_cart_item_has_user_foreign_key(self):
        """Test CartItem has user_id foreign key defined."""
        inspector = inspect(models.CartItem)
        fks = list(inspector.mapper.relationships.keys())
        assert "user" in fks

    def test_cart_item_has_product_foreign_key(self):
        """Test CartItem has product_id foreign key defined."""
        inspector = inspect(models.CartItem)
        fks = list(inspector.mapper.relationships.keys())
        assert "product" in fks
