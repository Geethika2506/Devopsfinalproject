# SDDO Azure MVP

## Goal
Small cloud-native web API (FastAPI) deployed to Azure with CI/CD, monitoring, and basic DB. Demo date: 2025-12-04.

## Architecture
- FastAPI backend in a Docker container.
- Container stored in Azure Container Registry (ACR).
- Deployed to Azure App Service (Web App for Containers).
- Optional: Azure SQL Database for persistent storage.
- Application Insights for monitoring; logs shipped from container or enabled in App Service.

## How to run locally
1. python -m venv .venv && source .venv/bin/activate
2. pip install -r requirements.txt
3. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
4. Open http://localhost:8000/health

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

