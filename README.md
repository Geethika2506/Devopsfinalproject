# DevOps Shop — Final Project  
### *IE University — Software Development and DevOps*  
Author: **Nicolas Leyva**

---

# 1. Project Overview

**DevOps Shop** is an e-commerce demo API built for the **DevOps module final project** at IE University.

The application provides:
- User creation and management
- Product catalog with categories
- Shopping cart functionality
- Order creation and history

---

# 2. Features

- FastAPI backend
- In-memory product catalog (always available)
- SQLite database for users, carts, and orders
- Product browsing with categories
- Full REST API with documentation

---

# 3. API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| **GET** | `/` | Home endpoint |
| **GET** | `/health` | Health check |
| **GET** | `/products/` | List all products |
| **GET** | `/products/categories` | List categories |
| **GET** | `/products/category/{category}` | Products by category |
| **GET** | `/products/{id}` | Single product |
| **POST** | `/users/` | Create user |
| **GET** | `/users/` | List users |
| **GET** | `/cart/{user_id}` | Get user's cart |
| **POST** | `/cart/{cart_id}/items` | Add to cart |
| **POST** | `/orders/{user_id}` | Create order |
| **GET** | `/orders/user/{user_id}` | User's orders |

---

# 4. Running Locally

### Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app
```bash
uvicorn app.main:app --reload --port 8000
```

### Access
- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

---

# 5. Testing

```bash
pytest -v
```

---

# 6. Project Structure

```
├── app/
│   ├── main.py          # FastAPI app
│   ├── database.py      # SQLite setup
│   ├── models.py        # Database models
│   ├── schemas.py       # Pydantic schemas
│   ├── routers/
│   │   ├── products.py
│   │   ├── users.py
│   │   ├── cart.py
│   │   └── orders.py
│   └── services/
│       └── external_products.py
├── tests/
│   └── test_api.py
├── dockerfile
├── requirements.txt
└── README.md
```

---

# 7. Team

- **Nicolas Leyva** - Developer
- IE University BCSAI 2025
