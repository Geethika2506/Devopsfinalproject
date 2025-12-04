# The Shop App - DevOps Final Project

## Overview
Full-stack e-commerce application with FastAPI backend, React frontend, and JWT authentication. Features user authentication, product browsing, shopping cart, wishlist, reviews, and order management.

## Tech Stack
- **Backend:** FastAPI, SQLAlchemy, SQLite (local) / PostgreSQL (prod)
- **Frontend:** React + Vite
- **Auth:** JWT tokens with bcrypt password hashing
- **Infrastructure:** Docker, Azure Container Registry, Azure Web App
- **CI/CD:** GitHub Actions

## Features
- ✅ User registration & login with JWT authentication
- ✅ Product browsing with category filtering
- ✅ Shopping cart management
- ✅ Wishlist functionality (add/remove favorites)
- ✅ Product reviews and ratings
- ✅ User profile with order history
- ✅ Order placement
- ✅ Responsive UI
- ✅ 20 sample products pre-seeded

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git

---

## Option A: Run with Docker (Recommended)

```bash
# Clone and navigate to project
git clone https://github.com/Geethika2506/Devopsfinalproject.git
cd Devopsfinalproject

# Start both frontend and backend
docker-compose up --build
```

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |

**Stop containers:**
```bash
docker-compose down
```

---

## Option B: Run Without Docker (Manual Setup)

### 1. Backend Setup (Terminal 1)

**Windows:**
```powershell
cd Devopsfinalproject
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirement.txt
cd backend
python seed.py
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**macOS/Linux:**
```bash
cd Devopsfinalproject
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
cd backend
python seed.py
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend available at: **http://localhost:8000**

### 2. Frontend Setup (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: **http://localhost:5173**

---

## API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login/json` | POST | Login (returns JWT) |
| `/auth/me` | GET | Get current user (auth required) |

### Products
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/products/` | GET | List products (optional: `?category=`) |
| `/products/{id}` | GET | Get product by ID |
| `/products/categories` | GET | List all categories |

### Cart
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cart/` | GET | View cart (auth required) |
| `/cart/` | POST | Add item to cart |
| `/cart/{item_id}` | DELETE | Remove item from cart |

### Orders
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/orders/` | GET | Get user's orders (auth required) |
| `/orders/` | POST | Create new order |

### Wishlist
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/wishlist` | GET | Get user's wishlist (auth required) |
| `/wishlist` | POST | Add product to wishlist |
| `/wishlist/{product_id}` | DELETE | Remove from wishlist |

### Reviews
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reviews` | POST | Create a review (auth required) |
| `/reviews/product/{product_id}` | GET | Get reviews for a product |
| `/reviews/user/me` | GET | Get current user's reviews |

### Health
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |

---

## Testing

Run all 177 tests:
```bash
# Activate virtual environment first
cd Devopsfinalproject
.\.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Run tests
python -m pytest tests/ -v
```

---

## Project Structure

```
Devopsfinalproject/
├── backend/
│   ├── main.py           # FastAPI application entry
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # Database configuration
│   ├── auth.py           # JWT authentication
│   ├── crud.py           # Database operations
│   ├── seed.py           # Database seeder
│   └── routers/          # API route handlers
│       ├── auth.py
│       ├── products.py
│       ├── cart.py
│       ├── orders.py
│       ├── wishlist.py
│       ├── reviews.py
│       └── users.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx       # Main React component
│   │   ├── App.css       # Styles
│   │   └── main.jsx      # Entry point
│   ├── package.json
│   └── vite.config.js
├── tests/                # Test suite (177 tests)
├── docker-compose.yml
├── dockerfile
├── requirement.txt
└── README.md
```

---

## CI/CD Pipeline

GitHub Actions workflows automatically:
1. Run all tests on push/PR
2. Build Docker images
3. Push to Azure Container Registry
4. Deploy to Azure Web App

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Database connection string |
| `SECRET_KEY` | JWT signing key |
| `AZURE_CLIENT_ID` | Azure service principal |
| `AZURE_CLIENT_SECRET` | Azure credentials |
| `AZURE_TENANT_ID` | Azure tenant |

---

## Team
- DevOps Final Project - Year 2

## License
MIT License

