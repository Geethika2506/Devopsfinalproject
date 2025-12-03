# Backend Dockerfile - FastAPI Application
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirement.txt .

# Install Python dependencies (skip pyodbc for ARM compatibility)
RUN grep -v "^#\|^$\|pyodbc" requirement.txt > requirements-docker.txt \
    && pip install --no-cache-dir -r requirements-docker.txt \
    && rm requirements-docker.txt

# Copy backend code
COPY backend/ ./backend/

# Expose port
EXPOSE 8000

# Environment variables (can be overridden at runtime)
ENV DATABASE_URL=sqlite:///./store.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]


