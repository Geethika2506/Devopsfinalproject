# Multi-stage Dockerfile for Render deployment
# Stage 1: Build frontend
FROM node:18-slim AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend with frontend dist
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN grep -v "^#\|^$\|pyodbc" requirements.txt > requirements-docker.txt \
    && pip install --no-cache-dir -r requirements-docker.txt \
    && pip install aiofiles \
    && rm requirements-docker.txt

# Copy backend code
COPY Backend/ ./Backend/

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose port
EXPOSE 10000

# Environment variables
ENV DATABASE_URL=sqlite:///./store.db
ENV PORT=10000

# Create startup script that seeds DB then starts server
RUN echo '#!/bin/bash\npython -m Backend.seed\nuvicorn Backend.main:app --host 0.0.0.0 --port ${PORT:-10000}' > /app/start.sh && chmod +x /app/start.sh

# Start command - seeds database then starts uvicorn
CMD ["/bin/bash", "/app/start.sh"]
