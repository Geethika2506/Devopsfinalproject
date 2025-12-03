"""Unit tests for CRUD operations."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Backend'))

import pytest
import crud
import models
import schemas


class TestProductCRUD:
    """Test Product CRUD operations."""

    def test_create_product(self, db):
        """Test creating a product."""
        product_data = schemas.ProductCreate(
            title="New Product",
            price=19.99,
            description="A new product",
            category="test"
        )
        product = crud.create_product(db, product_data)
        
        assert product.id is not None
        assert product.title == "New Product"
        assert product.price == 19.99
        assert product.category == "test"

    def test_get_product(self, db, test_product):
        """Test getting a product by ID."""
        product = crud.get_product(db, test_product.id)
        
        assert product is not None
        assert product.id == test_product.id
        assert product.title == test_product.title

    def test_get_product_not_found(self, db):
        """Test getting a non-existent product."""
        product = crud.get_product(db, 9999)
        assert product is None

    def test_get_products(self, db, multiple_products):
        """Test getting all products."""
        products = crud.get_products(db)
        
        assert len(products) == 5

    def test_get_products_with_pagination(self, db, multiple_products):
        """Test pagination on products list."""
        products = crud.get_products(db, skip=0, limit=2)
        assert len(products) == 2
        
        products = crud.get_products(db, skip=2, limit=2)
        assert len(products) == 2

    def test_get_products_by_category(self, db, multiple_products):
        """Test filtering products by category."""
        electronics = crud.get_products_by_category(db, "electronics")
        assert len(electronics) == 2
        
        clothing = crud.get_products_by_category(db, "clothing")
        assert len(clothing) == 2

    def test_get_categories(self, db, multiple_products):
        """Test getting unique categories."""
        categories = crud.get_categories(db)
        
        assert len(categories) == 3
        assert "electronics" in categories
        assert "clothing" in categories
        assert "books" in categories

    def test_update_product(self, db, test_product):
        """Test updating a product."""
        update_data = schemas.ProductUpdate(title="Updated Title", price=39.99)
        updated = crud.update_product(db, test_product.id, update_data)
        
        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.price == 39.99
        # Original fields should remain unchanged
        assert updated.category == test_product.category

    def test_update_product_partial(self, db, test_product):
        """Test partial product update."""
        original_price = test_product.price
        update_data = schemas.ProductUpdate(title="Only Title Changed")
        updated = crud.update_product(db, test_product.id, update_data)
        
        assert updated.title == "Only Title Changed"
        assert updated.price == original_price

    def test_update_product_not_found(self, db):
        """Test updating a non-existent product."""
        update_data = schemas.ProductUpdate(title="Ghost")
        updated = crud.update_product(db, 9999, update_data)
        assert updated is None

    def test_delete_product(self, db, test_product):
        """Test deleting a product."""
        result = crud.delete_product(db, test_product.id)
        assert result is True
        
        # Verify it's deleted
        product = crud.get_product(db, test_product.id)
        assert product is None

    def test_delete_product_not_found(self, db):
        """Test deleting a non-existent product."""
        result = crud.delete_product(db, 9999)
        assert result is False


class TestUserCRUD:
    """Test User CRUD operations."""

    def test_create_user(self, db):
        """Test creating a user directly via model."""
        from auth import get_password_hash
        hashed = get_password_hash("password123")
        user = models.User(
            email="newuser@example.com",
            name="New User",
            password_hash=hashed
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.name == "New User"

    def test_get_user(self, db, test_user):
        """Test getting a user by ID."""
        user = crud.get_user(db, test_user.id)
        
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email

    def test_get_user_not_found(self, db):
        """Test getting a non-existent user."""
        user = crud.get_user(db, 9999)
        assert user is None

    def test_get_user_by_email(self, db, test_user):
        """Test getting a user by email."""
        user = crud.get_user_by_email(db, test_user.email)
        
        assert user is not None
        assert user.id == test_user.id

    def test_get_user_by_email_not_found(self, db):
        """Test getting a user by non-existent email."""
        user = crud.get_user_by_email(db, "nonexistent@example.com")
        assert user is None

    def test_get_users(self, db, test_user):
        """Test getting all users."""
        # Create additional users
        for i in range(3):
            user = models.User(
                email=f"user{i}@example.com",
                password_hash="hash",
                name=f"User {i}"
            )
            db.add(user)
        db.commit()
        
        users = crud.get_users(db)
        assert len(users) == 4  # test_user + 3 new users


class TestCartCRUD:
    """Test Cart CRUD operations."""

    def test_add_to_cart(self, db, test_user, test_product):
        """Test adding an item to cart."""
        item_data = schemas.CartItemCreate(product_id=test_product.id, quantity=2)
        cart_item = crud.add_to_cart(db, test_user.id, item_data)
        
        assert cart_item.user_id == test_user.id
        assert cart_item.product_id == test_product.id
        assert cart_item.quantity == 2

    def test_add_to_cart_existing_item(self, db, test_user, test_product):
        """Test adding more of an existing item to cart."""
        item_data = schemas.CartItemCreate(product_id=test_product.id, quantity=2)
        crud.add_to_cart(db, test_user.id, item_data)
        
        # Add more of the same item
        more_data = schemas.CartItemCreate(product_id=test_product.id, quantity=3)
        cart_item = crud.add_to_cart(db, test_user.id, more_data)
        
        assert cart_item.quantity == 5  # 2 + 3

    def test_get_cart_items(self, db, test_user, multiple_products):
        """Test getting all cart items for a user."""
        # Add multiple items to cart
        for product in multiple_products[:3]:
            item_data = schemas.CartItemCreate(product_id=product.id, quantity=1)
            crud.add_to_cart(db, test_user.id, item_data)
        
        cart_items = crud.get_cart_items(db, test_user.id)
        assert len(cart_items) == 3

    def test_update_cart_item(self, db, test_user, test_product):
        """Test updating cart item quantity."""
        item_data = schemas.CartItemCreate(product_id=test_product.id, quantity=2)
        crud.add_to_cart(db, test_user.id, item_data)
        
        updated = crud.update_cart_item(db, test_user.id, test_product.id, 5)
        assert updated.quantity == 5

    def test_update_cart_item_to_zero_removes(self, db, test_user, test_product):
        """Test setting cart item quantity to 0 removes it."""
        item_data = schemas.CartItemCreate(product_id=test_product.id, quantity=2)
        crud.add_to_cart(db, test_user.id, item_data)
        
        result = crud.update_cart_item(db, test_user.id, test_product.id, 0)
        assert result is None
        
        # Verify it's removed
        items = crud.get_cart_items(db, test_user.id)
        assert len(items) == 0

    def test_remove_from_cart(self, db, test_user, test_product):
        """Test removing an item from cart."""
        item_data = schemas.CartItemCreate(product_id=test_product.id, quantity=2)
        crud.add_to_cart(db, test_user.id, item_data)
        
        result = crud.remove_from_cart(db, test_user.id, test_product.id)
        assert result is True
        
        items = crud.get_cart_items(db, test_user.id)
        assert len(items) == 0

    def test_remove_from_cart_not_found(self, db, test_user):
        """Test removing non-existent cart item."""
        result = crud.remove_from_cart(db, test_user.id, 9999)
        assert result is False

    def test_clear_cart(self, db, test_user, multiple_products):
        """Test clearing all items from cart."""
        # Add multiple items
        for product in multiple_products[:3]:
            item_data = schemas.CartItemCreate(product_id=product.id, quantity=1)
            crud.add_to_cart(db, test_user.id, item_data)
        
        crud.clear_cart(db, test_user.id)
        
        items = crud.get_cart_items(db, test_user.id)
        assert len(items) == 0


class TestOrderCRUD:
    """Test Order CRUD operations."""

    def test_create_order(self, db, test_user, test_product):
        """Test creating an order."""
        items = [schemas.OrderItemBase(product_id=test_product.id, quantity=2)]
        order = crud.create_order(db, test_user.id, items)
        
        assert order.id is not None
        assert order.user_id == test_user.id
        assert order.status == "pending"
        assert order.total == test_product.price * 2

    def test_create_order_multiple_items(self, db, test_user, multiple_products):
        """Test creating an order with multiple items."""
        items = [
            schemas.OrderItemBase(product_id=multiple_products[0].id, quantity=1),
            schemas.OrderItemBase(product_id=multiple_products[1].id, quantity=2),
        ]
        order = crud.create_order(db, test_user.id, items)
        
        expected_total = multiple_products[0].price + (multiple_products[1].price * 2)
        assert order.total == expected_total
        assert len(order.items) == 2

    def test_get_orders(self, db, test_user, test_product):
        """Test getting user orders."""
        # Create multiple orders
        for i in range(3):
            items = [schemas.OrderItemBase(product_id=test_product.id, quantity=1)]
            crud.create_order(db, test_user.id, items)
        
        orders = crud.get_orders(db, test_user.id)
        assert len(orders) == 3

    def test_get_order(self, db, test_user, test_product):
        """Test getting a specific order."""
        items = [schemas.OrderItemBase(product_id=test_product.id, quantity=1)]
        created_order = crud.create_order(db, test_user.id, items)
        
        order = crud.get_order(db, created_order.id)
        assert order is not None
        assert order.id == created_order.id

    def test_get_order_not_found(self, db):
        """Test getting a non-existent order."""
        order = crud.get_order(db, 9999)
        assert order is None
