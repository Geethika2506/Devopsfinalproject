"""Seed script to populate database with sample data."""
import sys
import os

# Add current directory to path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
from models import Product

# Sample products data (fallback when API is unavailable)
SAMPLE_PRODUCTS = [
    {
        "title": "Fjallraven Backpack",
        "price": 109.95,
        "description": "Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve.",
        "category": "men's clothing",
        "image": "https://fakestoreapi.com/img/81fPKd-2AYL._AC_SL1500_.jpg",
        "rating": {"rate": 3.9, "count": 120}
    },
    {
        "title": "Mens Casual Premium Slim Fit T-Shirts",
        "price": 22.30,
        "description": "Slim-fitting style, contrast raglan long sleeve, lightweight & soft fabric for comfortable wearing.",
        "category": "men's clothing",
        "image": "https://fakestoreapi.com/img/71-3HjGNDUL._AC_SY879._SX._UX._SY._UY_.jpg",
        "rating": {"rate": 4.1, "count": 259}
    },
    {
        "title": "Mens Cotton Jacket",
        "price": 55.99,
        "description": "Great outance comfortable wearing and target, perfect for daily use.",
        "category": "men's clothing",
        "image": "https://fakestoreapi.com/img/71li-ujtlUL._AC_UX679_.jpg",
        "rating": {"rate": 4.7, "count": 500}
    },
    {
        "title": "Women's 3-in-1 Snowboard Jacket",
        "price": 56.99,
        "description": "Perfect for outdoor activities. Note: The Alarm Clock display has been removed.",
        "category": "women's clothing",
        "image": "https://fakestoreapi.com/img/51Y5NI-I5jL._AC_UX679_.jpg",
        "rating": {"rate": 2.6, "count": 235}
    },
    {
        "title": "Gold Petite Micropave Diamond Ring",
        "price": 168.00,
        "description": "Classic Created Wedding Engagement Solitaire Diamond Promise Ring for Her.",
        "category": "jewelery",
        "image": "https://fakestoreapi.com/img/71YAIFU48IL._AC_UL640_QL65_ML3_.jpg",
        "rating": {"rate": 3.9, "count": 70}
    },
    {
        "title": "Solid Gold Petite Micropave",
        "price": 695.00,
        "description": "Satisfaction Guaranteed. Return or exchange any order within 30 days.",
        "category": "jewelery",
        "image": "https://fakestoreapi.com/img/61sbMiUnoGL._AC_UL640_QL65_ML3_.jpg",
        "rating": {"rate": 4.6, "count": 400}
    },
    {
        "title": "WD 2TB External Hard Drive",
        "price": 64.00,
        "description": "USB 3.0 and USB 2.0 Compatibility. Fast data transfers. Improve lag time.",
        "category": "electronics",
        "image": "https://fakestoreapi.com/img/61IBBVJvSDL._AC_SY879_.jpg",
        "rating": {"rate": 3.3, "count": 203}
    },
    {
        "title": "SanDisk SSD PLUS 1TB Internal SSD",
        "price": 109.00,
        "description": "Easy upgrade for faster boot up, shutdown, application load and response.",
        "category": "electronics",
        "image": "https://fakestoreapi.com/img/61U7T1koQqL._AC_SX679_.jpg",
        "rating": {"rate": 2.9, "count": 470}
    },
    {
        "title": "Silicon Power 256GB SSD",
        "price": 109.00,
        "description": "3D NAND flash are applied to deliver high performance.",
        "category": "electronics",
        "image": "https://fakestoreapi.com/img/71kWymZ+c+L._AC_SX679_.jpg",
        "rating": {"rate": 4.8, "count": 319}
    },
    {
        "title": "WD 4TB Gaming Drive",
        "price": 114.00,
        "description": "Expand your PS4 gaming experience. Play any game from your drive.",
        "category": "electronics",
        "image": "https://fakestoreapi.com/img/61mtL65D4cL._AC_SX679_.jpg",
        "rating": {"rate": 4.8, "count": 400}
    },
    {
        "title": "Acer SB220Q Monitor",
        "price": 599.00,
        "description": "21.5 inch Full HD widescreen IPS display with AMD Free Sync technology.",
        "category": "electronics",
        "image": "https://fakestoreapi.com/img/81QpkIctqPL._AC_SX679_.jpg",
        "rating": {"rate": 2.9, "count": 250}
    },
    {
        "title": "Samsung 49-Inch Gaming Monitor",
        "price": 999.99,
        "description": "49 Inch Super Ultrawide Dual QHD curved monitor with Quantum Dot technology.",
        "category": "electronics",
        "image": "https://fakestoreapi.com/img/81Zt42ioCgL._AC_SX679_.jpg",
        "rating": {"rate": 2.2, "count": 140}
    },
    {
        "title": "BIYLACLESEN Women's Parka",
        "price": 29.95,
        "description": "Military style parka jacket with removable hood.",
        "category": "women's clothing",
        "image": "https://fakestoreapi.com/img/51eg55uWmdL._AC_UX679_.jpg",
        "rating": {"rate": 3.6, "count": 235}
    },
    {
        "title": "Rain Jacket Women Windbreaker",
        "price": 39.99,
        "description": "Lightweight, perfect for trip or hiking.",
        "category": "women's clothing",
        "image": "https://fakestoreapi.com/img/71HblAHs5xL._AC_UY879_-2.jpg",
        "rating": {"rate": 3.8, "count": 679}
    },
    {
        "title": "MBJ Women's Short Sleeve Boat Neck",
        "price": 9.85,
        "description": "Made in USA. Super soft and lightweight.",
        "category": "women's clothing",
        "image": "https://fakestoreapi.com/img/71z3kpMAYsL._AC_UY879_.jpg",
        "rating": {"rate": 4.7, "count": 130}
    },
    {
        "title": "Opna Women's Short Sleeve T-Shirt",
        "price": 7.95,
        "description": "100% Polyester. Machine wash. Lightweight breathable fabric.",
        "category": "women's clothing",
        "image": "https://fakestoreapi.com/img/51eg55uWmdL._AC_UX679_.jpg",
        "rating": {"rate": 4.5, "count": 146}
    }
]


def seed_products():
    """Seed products into database."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Seeding products from sample data...")
        
        for item in SAMPLE_PRODUCTS:
            # Check if product already exists (by title)
            existing = db.query(Product).filter(Product.title == item["title"]).first()
            if existing:
                print(f"  Skipping (exists): {item['title'][:50]}...")
                continue
            
            product = Product(
                title=item.get("title", "Unknown"),
                price=float(item.get("price", 0)),
                description=item.get("description", ""),
                category=item.get("category", "general"),
                image=item.get("image", ""),
                rating_rate=float(item.get("rating", {}).get("rate", 0)),
                rating_count=int(item.get("rating", {}).get("count", 0))
            )
            db.add(product)
            print(f"  Added: {item['title'][:40]}...")
        
        db.commit()
        print(f"\nDatabase seeded successfully!")
        
        # Show count
        total = db.query(Product).count()
        print(f"Total products in database: {total}")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


def clear_products():
    """Clear all products from database."""
    db = SessionLocal()
    try:
        count = db.query(Product).delete()
        db.commit()
        print(f"Deleted {count} products")
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        clear_products()
    else:
        seed_products()
