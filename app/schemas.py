from pydantic import BaseModel

class ProductBase(BaseModel):
    title: str
    description: str | None = None
    price: float

class Product(ProductBase):
    id: int
    class Config:
        orm_mode = True

class ProductCreate(ProductBase):
    pass

class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItem(CartItemBase):
    id: int
    class Config:
        orm_mode = True

class Cart(BaseModel):
    id: int
    items: list[CartItem] = []
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class User(UserBase):
    id: int
    class Config:
        orm_mode = True

class Order(BaseModel):
    id: int
    total: float
    class Config:
        orm_mode = True
