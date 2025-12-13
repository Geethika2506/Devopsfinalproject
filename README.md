# Online Store - DevOps Final Project

## 🚀 Live Demo
**[https://the-shop-app.onrender.com](https://the-shop-app.onrender.com)**

## Overview
Full-stack e-commerce application with FastAPI backend, React frontend, and JWT authentication. Features user authentication, product browsing, shopping cart, wishlist, reviews, and order management.

## Tech Stack
- **Backend:** FastAPI, SQLAlchemy, SQLite
- **Frontend:** React + Vite
- **Auth:** JWT tokens with Argon2 password hashing
- **Deployment:** Render (Docker)
- **CI/CD:** GitHub Actions

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Git
- Docker (optional, for containerized deployment)

---

## Option A: Run with Docker (Recommended)

**Easiest way to run the entire app:**

```bash
# Clone and navigate to project
git clone https://github.com/Geethika2506/Devopsfinalproject.git
cd Devopsfinalproject

# Start both frontend and backend
docker-compose up

# Or build fresh and start
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
cd c:\Users\YourName\Devopsfinalproject
python -m venv .venv
.venv\Scripts\activate
pip install -r requirement.txt
python backend/seed.py
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**macOS/Linux:**
```bash
cd /path/to/DevOpsFinalProject
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirement.txt
python backend/seed.py
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Backend will be available at: **http://127.0.0.1:8000**

### 2. Frontend Setup (Terminal 2 - New Window)
```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: **http://localhost:5173**

### 3. Access the Application
| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://127.0.0.1:8000 |
| **API Documentation** | http://127.0.0.1:8000/docs |
| **ReDoc** | http://127.0.0.1:8000/redoc |

### 4. Features
- ✅ User registration & login with JWT authentication
- ✅ Product browsing with category filtering
- ✅ Shopping cart management
- ✅ Order placement
- ✅ Responsive UI
- ✅ 16 sample products with images

### 5. Stopping the Servers
Press `Ctrl+C` in each terminal to stop the servers.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login/json` | POST | Login (returns JWT) |
| `/api/auth/me` | GET | Get current user (requires auth) |
| `/api/products/` | GET | List products (optional: `?category=`) |
| `/api/products/categories` | GET | List categories |
| `/api/cart/` | GET/POST | View/add to cart |
| `/api/orders/` | GET/POST | View/create orders |
| `/api/wishlist/` | GET/POST | View/manage wishlist |
| `/api/reviews/` | GET/POST | Product reviews |

## Features
- ✅ User registration & login with email/password
- ✅ JWT-based authentication
- ✅ Product catalog with category filters
- ✅ Shopping cart functionality
- ✅ Wishlist management
- ✅ Product reviews & ratings
- ✅ Order placement
- ✅ Responsive React UI

## CI/CD Pipeline
GitHub Actions workflow (`.github/workflows/`):
1. Run tests with pytest
2. Build Docker image (multi-stage: Node.js + Python)
3. Deploy to Render automatically

## Deployment
The app is deployed on **Render** using Docker:
- Frontend and backend served from single container
- Database seeded automatically on startup
- Auto-deploy on push to `cd-pipeline` branch

## Environment Variables
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Database connection string |
| `SECRET_KEY` | JWT signing key |
| `PORT` | Server port (set by Render) |

## Testing
```bash
source .venv/bin/activate
python -m pytest tests/ -v --cov=Backend
```

## Project Structure
```
├── Backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic validation schemas
│   ├── crud.py              # Database CRUD operations
│   ├── database.py          # Database connection setup
│   ├── auth.py              # JWT authentication logic
│   ├── seed.py              # Database seeding script
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Auth endpoints (/auth)
│       ├── products.py      # Product endpoints (/products)
│       ├── cart.py          # Cart endpoints (/cart)
│       ├── orders.py        # Order endpoints (/orders)
│       ├── users.py         # User endpoints (/users)
│       ├── wishlist.py      # Wishlist endpoints (/wishlist)
│       └── reviews.py       # Review endpoints (/reviews)
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React application
│   │   └── main.jsx         # React entry point
│   ├── package.json
│   └── Dockerfile
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_auth.py         # Authentication tests
│   ├── test_crud.py         # CRUD operation tests
│   ├── test_database.py     # Database tests
│   ├── test_models.py       # Model tests
│   ├── test_routers.py      # API endpoint tests
│   ├── test_features.py     # Wishlist & review tests
│   └── test_integration.py  # Integration tests
├── .github/workflows/
│   └── cd-pipeline_the-shop-app.yml  # CI/CD pipeline
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.yml       # Local development
├── requirements.txt         # Python dependencies
└── README.md
```

