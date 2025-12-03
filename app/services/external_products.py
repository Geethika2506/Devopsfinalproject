# In-memory product catalog
# This ensures the app works without external API dependencies

PRODUCTS = [
    # Electronics
    {"id": 1, "name": "Smartphone Pro", "price": 999.99, "category": "electronics", "image": "/images/smartphone.jpg"},
    {"id": 2, "name": "Wireless Headphones", "price": 199.99, "category": "electronics", "image": "/images/headphones.jpg"},
    {"id": 3, "name": "Laptop Ultra", "price": 1499.99, "category": "electronics", "image": "/images/laptop.jpg"},
    {"id": 4, "name": "Smart Watch", "price": 349.99, "category": "electronics", "image": "/images/smartwatch.jpg"},
    {"id": 5, "name": "Tablet Pro", "price": 799.99, "category": "electronics", "image": "/images/tablet.jpg"},
    
    # Clothing
    {"id": 6, "name": "Classic T-Shirt", "price": 29.99, "category": "clothing", "image": "/images/tshirt.jpg"},
    {"id": 7, "name": "Denim Jeans", "price": 79.99, "category": "clothing", "image": "/images/jeans.jpg"},
    {"id": 8, "name": "Running Shoes", "price": 129.99, "category": "clothing", "image": "/images/shoes.jpg"},
    {"id": 9, "name": "Winter Jacket", "price": 199.99, "category": "clothing", "image": "/images/jacket.jpg"},
    {"id": 10, "name": "Baseball Cap", "price": 24.99, "category": "clothing", "image": "/images/cap.jpg"},
    
    # Home
    {"id": 11, "name": "Coffee Maker", "price": 89.99, "category": "home", "image": "/images/coffeemaker.jpg"},
    {"id": 12, "name": "Desk Lamp", "price": 49.99, "category": "home", "image": "/images/lamp.jpg"},
    {"id": 13, "name": "Throw Pillow Set", "price": 39.99, "category": "home", "image": "/images/pillows.jpg"},
    {"id": 14, "name": "Wall Clock", "price": 34.99, "category": "home", "image": "/images/clock.jpg"},
    {"id": 15, "name": "Plant Pot Set", "price": 29.99, "category": "home", "image": "/images/pots.jpg"},
    
    # Books
    {"id": 16, "name": "Python Programming", "price": 49.99, "category": "books", "image": "/images/python-book.jpg"},
    {"id": 17, "name": "DevOps Handbook", "price": 44.99, "category": "books", "image": "/images/devops-book.jpg"},
    {"id": 18, "name": "Cloud Architecture", "price": 54.99, "category": "books", "image": "/images/cloud-book.jpg"},
    {"id": 19, "name": "Machine Learning Basics", "price": 59.99, "category": "books", "image": "/images/ml-book.jpg"},
    {"id": 20, "name": "Web Development Guide", "price": 39.99, "category": "books", "image": "/images/web-book.jpg"},
]

CATEGORIES = ["electronics", "clothing", "home", "books"]


def get_all_products():
    """Return all products"""
    return PRODUCTS


def get_product_by_id(product_id: int):
    """Return a single product by ID"""
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None


def get_products_by_category(category: str):
    """Return all products in a category"""
    return [p for p in PRODUCTS if p["category"] == category.lower()]


def get_categories():
    """Return all available categories"""
    return CATEGORIES
