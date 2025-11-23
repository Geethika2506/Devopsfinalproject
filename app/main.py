from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI()

# CORS Setup
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MOCK DATABASE ---
mock_products = [
    {"id": 1, "name": "Azure Hoodie", "description": "Comfortable cloud hoodie", "price": 49.99, "stock": 10},
    {"id": 2, "name": "Python Mug", "description": "For your daily caffeine", "price": 12.50, "stock": 50},
    {"id": 3, "name": "DevOps Sticker Pack", "description": "Stick them everywhere", "price": 8.00, "stock": 100},
    {"id": 4, "name": "Docker T-Shirt", "description": "Container style fashion", "price": 29.99, "stock": 25},
    {"id": 5, "name": "Git Notebook", "description": "Commit your thoughts", "price": 15.00, "stock": 40},
    {"id": 6, "name": "Kubernetes Cap", "description": "Orchestrate your style", "price": 22.00, "stock": 30},
]

# Mock users database: {email: {username, password, email}}
mock_users_db = {}

# Mock active tokens: {token: email}
mock_tokens = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- DATA MODELS ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderCreate(BaseModel):
    items: List[OrderItem]

# --- HELPER FUNCTIONS ---
def get_current_user(token: str = Depends(oauth2_scheme)):
    if token not in mock_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email = mock_tokens[token]
    if email not in mock_users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return mock_users_db[email]

# --- ROUTES ---

@app.get("/products")
def get_products():
    return mock_products

@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    # Check if user already exists
    if user.email in mock_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Store user
    mock_users_db[user.email] = {
        "username": user.username,
        "email": user.email,
        "password": user.password  # In production, hash this!
    }
    
    return {"message": "User created successfully", "email": user.email}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # form_data.username contains the email (from frontend)
    # form_data.password contains the password
    
    email = form_data.username
    password = form_data.password
    
    # Check if user exists
    if email not in mock_users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    user = mock_users_db[email]
    if user["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token (in production, use JWT)
    token = f"token_{email}_{len(mock_tokens)}"
    mock_tokens[token] = email
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/users/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "email": current_user["email"]
    }

@app.post("/orders")
def create_order(
    order: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    print(f"Order received from {current_user['email']}: {order}")
    
    # Validate products exist and have stock
    for item in order.items:
        product = next((p for p in mock_products if p["id"] == item.product_id), None)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found"
            )
        if product["stock"] < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for {product['name']}"
            )
    
    return {
        "message": "Order placed successfully",
        "order_id": len(mock_tokens) + 100,
        "items": order.items
    }

@app.get("/")
def root():
    return {
        "message": "MiniStore API is running!",
        "endpoints": {
            "products": "/products",
            "register": "/users",
            "login": "/token",
            "profile": "/users/me",
            "orders": "/orders"
        }
    }

# --- RUNNER ---
if __name__ == "__main__":
    print("🚀 Starting MiniStore Backend Server...")
    print("📍 API Documentation: http://127.0.0.1:8000/docs")
    print("🛍️  Products Endpoint: http://127.0.0.1:8000/products")
    uvicorn.run(app, host="127.0.0.1", port=8000)