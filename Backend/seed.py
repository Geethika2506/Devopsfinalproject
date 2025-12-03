"""Seed script to populate database with sample data from FakeStoreAPI."""
import requests
from database import SessionLocal, engine, Base
from models import Product

# FakeStoreAPI endpoint - can be changed to any compatible API
FAKE_STORE_API_URL = "https://fakestoreapi.com/products"


def seed_products(api_url: str = FAKE_STORE_API_URL):
    """Fetch products from fake API and insert into database."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print(f"Fetching products from {api_url}...")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        products_data = response.json()
        
        print(f"Found {len(products_data)} products")
        
        for item in products_data:
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
            print(f"  Added: {item['title'][:50]}...")
        
        db.commit()
        print(f"\nDatabase seeded successfully!")
        
        # Show count
        total = db.query(Product).count()
        print(f"Total products in database: {total}")
        
    except requests.RequestException as e:
        print(f"Error fetching from API: {e}")
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
    elif len(sys.argv) > 1:
        # Use custom API URL if provided
        seed_products(sys.argv[1])
    else:
        seed_products()
