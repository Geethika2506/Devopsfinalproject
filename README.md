# SDDO Azure MVP

## Goal
Small cloud-native web API (FastAPI) deployed to Azure with CI/CD, monitoring, and basic DB. Demo date: 2025-12-04.

## Architecture
- FastAPI backend in a Docker container.
- Container stored in Azure Container Registry (ACR).
- Deployed to Azure App Service (Web App for Containers).
- Optional: Azure SQL Database for persistent storage.
- Application Insights for monitoring; logs shipped from container or enabled in App Service.

## Local development

### Backend (FastAPI)
1. `cd backend`
2. `python -m venv .venv && source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `export SECRET_KEY="dev-secret"` (pick any string) and optionally `export ACCESS_TOKEN_EXPIRE_MINUTES=120`
5. `uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000`
6. Browse http://localhost:8000 for the welcome payload; interactive docs live at http://localhost:8000/docs.

Available auth endpoints:
- `POST /auth/register` → `{ email, password }`
- `POST /auth/token` (OAuth2 password form) → returns bearer token
- `GET /auth/me` → returns the authenticated user

API routes (`/products`, `/customers`, `/orders`) now require a valid `Authorization: Bearer <token>` header supplied by a logged-in user.

> Product schema now mirrors https://fakestoreapi.com/products: `title`, `price`, `category`, `description`, `image`, and nested `rating { rate, count }`.

### Seed FakeStore sample catalog
1. `cd backend`
2. (optional) remove any previous SQLite file if the schema changed: `rm ../store.db`
3. `python -m backend.cli seed-fakestore`
  - Add `--limit 10` to only import the first N products.
  - The script truncates the `products` table before reloading data.

Use `python -m backend.cli dump-products --output exported.json` to snapshot whatever is currently in the DB.

### Frontend (React + Vite)
1. `cd app/Frontend`
2. `npm install`
3. `npm run dev`
4. Open the printed Vite URL (defaults to http://localhost:5173). The dev server proxies `/api/*` to http://localhost:8000.

Dashboard workflow:
- Use the **Create account** form (email + password) to hit `/auth/register` and then the **Log in** form to obtain a bearer token.
- Once signed in, requests automatically include `Authorization: Bearer <token>` and you can manage FakeStore-style products, customers, and orders.
- Use `python -m backend.cli seed-fakestore` to preload the catalog, or add products via the form (title/category/price/image/rating).

### Tests
- `cd backend && pytest`

The `app/Frontend` dashboard can seed products, customers, and orders against the running API via the provided forms. Enter the same API key configured on the backend to enable requests.

## CI/CD (Azure DevOps)
- `azure-pipelines.yml` contains pipeline:
  - Install deps, run tests (pytest)
  - Build Docker image
  - Push to ACR
  - Deploy image to App Service for Containers

## Provisioning on Azure
- Use `create-azure-resources.sh` for quick resource creation.
- Configure ACR & Web App environment variables (DATABASE_URL, APPINSIGHTS_INSTRUMENTATIONKEY)

## Monitoring
- Add Application Insights via Azure Portal or `az monitor` CLI.
- App logs printed to stdout are captured by App Service and Application Insights.
- Create dashboards in Application Insights for: availability (ping / health), server requests, failures, response time.

## Definition of Done (example)
- API endpoints working + tests pass
- CI pipeline executes build/test/deploy
- App deployed in Azure and reachable
- Monitoring enabled (AI) and dashboard added
- README + Scrum docs (backlog, sprint review, retrospective)

