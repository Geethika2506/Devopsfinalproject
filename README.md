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
4. `export API_KEY=<your-local-key>` (match whatever the frontend uses)
5. `uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000`
6. Browse http://localhost:8000 to see the welcome payload; interactive docs live at http://localhost:8000/docs.

### Frontend (React + Vite)
1. `cd app/Frontend`
2. `npm install`
3. `npm run dev`
4. Open the printed Vite URL (defaults to http://localhost:5173). Requests are proxied to http://localhost:8000/api and include the `x-api-key` header you provide in the UI.

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

