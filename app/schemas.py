from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str  # Changed from 'title' to 'name'
    description: str | None = None
    price: float
    stock: int = 0  # Added stock field

class Product(ProductBase):
    id: int
    class Config:
        from_attributes = True  # Changed from orm_mode

class ProductCreate(ProductBase):
    pass

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItem(CartItemBase):
    id: int
    class Config:
        from_attributes = True

class Cart(BaseModel):
    id: int
    items: list[CartItem] = []
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str
    username: str | None = None  # Added username for frontend

class User(UserBase):
    id: int
    role: str | None = "user"
    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: str
    password: str
    username: str | None = None  # Added username

class Order(BaseModel):
    id: int
    total: float
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str