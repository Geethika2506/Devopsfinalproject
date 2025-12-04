"""Prometheus metrics for FastAPI application."""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0]
)

REQUESTS_IN_PROGRESS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress',
    ['method', 'endpoint']
)

# Business metrics
ORDERS_TOTAL = Counter(
    'orders_total',
    'Total number of orders placed'
)

USERS_REGISTERED = Counter(
    'users_registered_total',
    'Total number of users registered'
)

PRODUCTS_VIEWED = Counter(
    'products_viewed_total',
    'Total number of product views',
    ['product_id']
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics."""
    
    async def dispatch(self, request: Request, call_next):
        method = request.method
        # Normalize endpoint path (remove IDs for cleaner metrics)
        path = request.url.path
        
        # Skip metrics endpoint from being tracked
        if path == "/metrics":
            return await call_next(request)
        
        # Track in-progress requests
        REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).inc()
        
        # Time the request
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise e
        finally:
            # Record metrics
            duration = time.time() - start_time
            REQUEST_COUNT.labels(method=method, endpoint=path, status_code=status_code).inc()
            REQUEST_LATENCY.labels(method=method, endpoint=path).observe(duration)
            REQUESTS_IN_PROGRESS.labels(method=method, endpoint=path).dec()
        
        return response


def get_metrics():
    """Generate Prometheus metrics."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
