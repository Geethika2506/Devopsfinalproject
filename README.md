# Online Store - DevOps Final Project

## Overview
Full-stack e-commerce application with FastAPI backend, React frontend, and JWT authentication. Features user authentication, product browsing, shopping cart, and order management.

## Tech Stack
- **Backend:** FastAPI, SQLAlchemy, SQLite (local) / Azure SQL (prod)
- **Frontend:** React + Vite
- **Auth:** JWT tokens with Argon2 password hashing
- **Database:** SQLite (local development)
- **Infrastructure:** Docker, Azure Container Registry, Azure App Service

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 16+
- Git

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
- ✅ 20 sample products pre-seeded from FakeStoreAPI

### 5. Stopping the Servers
Press `Ctrl+C` in each terminal to stop the servers.

**Windows - Kill by Process:**
```powershell
# Kill backend (Python)
taskkill /F /IM python.exe

# Kill frontend (Node)
taskkill /F /IM node.exe
```## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/auth/register` | POST | Register new user |
| `/auth/login/json` | POST | Login (returns JWT) |
| `/auth/me` | GET | Get current user (requires auth) |
| `/products/` | GET | List products (optional: `?category=`) |
| `/products/categories` | GET | List categories |
| `/cart/` | GET/POST | View/add to cart |
| `/orders/` | GET/POST | View/create orders |

## Features
- ✅ User registration & login with email/password
- ✅ JWT-based authentication
- ✅ Product catalog with category filters
- ✅ Shopping cart functionality
- ✅ Order placement
- ✅ Responsive React UI

## CI/CD (Azure DevOps)
Pipeline in `azure-pipelines.yml`:
1. Install dependencies & run tests
2. Build Docker image
3. Push to Azure Container Registry
4. Deploy to Azure App Service

## Azure Setup
Run `create-azure-resources.sh` to provision:
- Azure Container Registry
- Azure App Service
- Azure SQL Database (optional)
- Application Insights

## Environment Variables
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Database connection string |
| `SECRET_KEY` | JWT signing key |
| `APPINSIGHTS_INSTRUMENTATIONKEY` | Azure monitoring |

## Testing
```bash
source .venv/bin/activate
python -m pytest tests/tests_api.py -v
```

