"""Seed script to populate database with sample data."""
import sys
import os

# Add current directory to path so imports work
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
from models import Product

# Sample products data with reliable placeholder images
SAMPLE_PRODUCTS = [
    {
        "title": "Fjallraven Backpack",
        "price": 109.95,
        "description": "Your perfect pack for everyday use and walks in the forest. Stash your laptop (up to 15 inches) in the padded sleeve.",
        "category": "men's clothing",
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400",
        "rating": {"rate": 3.9, "count": 120}
    },
    {
        "title": "Mens Casual Premium Slim Fit T-Shirts",
        "price": 22.30,
        "description": "Slim-fitting style, contrast raglan long sleeve, lightweight & soft fabric for comfortable wearing.",
        "category": "men's clothing",
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400",
        "rating": {"rate": 4.1, "count": 259}
    },
    {
        "title": "Mens Cotton Jacket",
        "price": 55.99,
        "description": "Great outance comfortable wearing and target, perfect for daily use.",
        "category": "men's clothing",
        "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400",
        "rating": {"rate": 4.7, "count": 500}
    },
    {
        "title": "Women's 3-in-1 Snowboard Jacket",
        "price": 56.99,
        "description": "Perfect for outdoor activities. Warm and comfortable.",
        "category": "women's clothing",
        "image": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400",
        "rating": {"rate": 2.6, "count": 235}
    },
    {
        "title": "Gold Petite Micropave Diamond Ring",
        "price": 168.00,
        "description": "Classic Created Wedding Engagement Solitaire Diamond Promise Ring for Her.",
        "category": "jewelery",
        "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=400",
        "rating": {"rate": 3.9, "count": 70}
    },
    {
        "title": "Solid Gold Petite Micropave",
        "price": 695.00,
        "description": "Satisfaction Guaranteed. Return or exchange any order within 30 days.",
        "category": "jewelery",
        "image": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=400",
        "rating": {"rate": 4.6, "count": 400}
    },
    {
        "title": "WD 2TB External Hard Drive",
        "price": 64.00,
        "description": "USB 3.0 and USB 2.0 Compatibility. Fast data transfers. Improve lag time.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1531492746076-161ca9bcad58?w=400",
        "rating": {"rate": 3.3, "count": 203}
    },
    {
        "title": "SanDisk SSD PLUS 1TB Internal SSD",
        "price": 109.00,
        "description": "Easy upgrade for faster boot up, shutdown, application load and response.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=400",
        "rating": {"rate": 2.9, "count": 470}
    },
    {
        "title": "Silicon Power 256GB SSD",
        "price": 109.00,
        "description": "3D NAND flash are applied to deliver high performance.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=400",
        "rating": {"rate": 4.8, "count": 319}
    },
    {
        "title": "WD 4TB Gaming Drive",
        "price": 114.00,
        "description": "Expand your PS4 gaming experience. Play any game from your drive.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1625961332771-3f40b0e2bdcf?w=400",
        "rating": {"rate": 4.8, "count": 400}
    },
    {
        "title": "Acer SB220Q Monitor",
        "price": 599.00,
        "description": "21.5 inch Full HD widescreen IPS display with AMD Free Sync technology.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400",
        "rating": {"rate": 2.9, "count": 250}
    },
    {
        "title": "Samsung 49-Inch Gaming Monitor",
        "price": 999.99,
        "description": "49 Inch Super Ultrawide Dual QHD curved monitor with Quantum Dot technology.",
        "category": "electronics",
        "image": "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=400",
        "rating": {"rate": 2.2, "count": 140}
    },
    {
        "title": "BIYLACLESEN Women's Parka",
        "price": 29.95,
        "description": "Military style parka jacket with removable hood.",
        "category": "women's clothing",
        "image": "https://images.unsplash.com/photo-1544022613-e87ca75a784a?w=400",
        "rating": {"rate": 3.6, "count": 235}
    },
    {
        "title": "Rain Jacket Women Windbreaker",
        "price": 39.99,
        "description": "Lightweight, perfect for trip or hiking.",
        "category": "women's clothing",
        "image": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=400",
        "rating": {"rate": 3.8, "count": 679}
    },
    {
        "title": "MBJ Women's Short Sleeve Boat Neck",
        "price": 9.85,
        "description": "Made in USA. Super soft and lightweight.",
        "category": "women's clothing",
        "image": "https://images.unsplash.com/photo-1485462537746-965f33f7f6a7?w=400",
        "rating": {"rate": 4.7, "count": 130}
    },
    {
        "title": "Opna Women's Short Sleeve T-Shirt",
        "price": 7.95,
        "description": "100% Polyester. Machine wash. Lightweight breathable fabric.",
        "category": "women's clothing",
        "image": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=400",
        "rating": {"rate": 4.5, "count": 146}
    }
]


def seed_products():
    """Seed products into database."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Clear existing products first to update images
        existing_count = db.query(Product).count()
        if existing_count > 0:
            print(f"Clearing {existing_count} existing products...")
            db.query(Product).delete()
            db.commit()
        
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
