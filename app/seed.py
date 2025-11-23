from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Product, User
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def seed_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if products already exist
        existing = db.query(Product).first()
        if existing:
            print("Database already seeded!")
            return
        
        # Create sample products
        products = [
            Product(name="Laptop", description="High-performance laptop for work and gaming", price=999.99, stock=15),
            Product(name="Wireless Mouse", description="Ergonomic wireless mouse with precision tracking", price=29.99, stock=50),
            Product(name="Mechanical Keyboard", description="RGB mechanical keyboard with blue switches", price=89.99, stock=30),
            Product(name="USB-C Hub", description="7-in-1 USB-C hub with HDMI and card reader", price=49.99, stock=25),
            Product(name="Monitor 27\"", description="4K UHD monitor with HDR support", price=399.99, stock=10),
            Product(name="Webcam HD", description="1080p webcam with auto-focus", price=79.99, stock=20),
            Product(name="Headphones", description="Noise-cancelling wireless headphones", price=199.99, stock=18),
            Product(name="External SSD", description="1TB portable SSD with USB 3.2", price=129.99, stock=40),
            Product(name="Phone Stand", description="Adjustable phone stand for desk", price=19.99, stock=100),
        ]
        
        db.add_all(products)
        
        # Create a test user
        test_user = User(
            email="test@example.com",
            username="testuser",
            password=get_password_hash("password123"),
            role="user"
        )
        db.add(test_user)
        
        db.commit()
        print("✅ Database seeded successfully!")
        print("📦 Added 9 products")
        print("👤 Test user created:")
        print("   Email: test@example.com")
        print("   Password: password123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()