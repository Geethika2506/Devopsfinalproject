# Use official Python slim image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy app dependencies first (for Docker caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app folder
COPY . .

# Expose the port that Azure Web App will listen to
EXPOSE 8000

# Start FastAPI using Gunicorn + Uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]
