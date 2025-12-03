# Online Store - DevOps Final Project

## Overview
Full-stack e-commerce application with FastAPI backend, React frontend, and JWT authentication. Deployed to Azure with CI/CD pipeline.

## Tech Stack
- **Backend:** FastAPI, SQLAlchemy, SQLite (local) / Azure SQL (prod)
- **Frontend:** React + Vite
- **Auth:** JWT tokens with bcrypt password hashing
- **Infrastructure:** Docker, Azure Container Registry, Azure App Service

## Quick Start

### 1. Backend Setup (Terminal 1)
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirement.txt

# Seed database with sample products
PYTHONPATH=. python backend/seed.py

# Start backend server (keep this terminal running)
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup (Terminal 2 - New Window)
```bash
cd frontend
npm install
npm run dev
```

### 3. Access the App
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

### 4. Stopping the Servers
- Press `Ctrl+C` in each terminal to stop the running server
- If a port is stuck, kill the process:
  ```bash
  # Kill backend (uvicorn)
  pkill -f uvicorn
  
  # Kill frontend (vite/node)
  pkill -f vite
  ```

## API Endpoints

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

