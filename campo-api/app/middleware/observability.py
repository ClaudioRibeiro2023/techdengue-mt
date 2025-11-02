import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from prometheus_client import Counter, Histogram, Gauge
import json

# Configure JSON logging
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "service": "epi-api",
            "message": record.getMessage(),
        }
        
        # Add extra fields
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'method'):
            log_data['method'] = record.method
        if hasattr(record, 'path'):
            log_data['path'] = record.path
        if hasattr(record, 'status_code'):
            log_data['status_code'] = record.status_code
        if hasattr(record, 'latency_ms'):
            log_data['latency_ms'] = record.latency_ms
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
            
        return json.dumps(log_data)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_in_progress',
    'HTTP requests in progress',
    ['method', 'endpoint']
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status']
)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and propagate X-Request-ID."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get or generate request ID
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        
        # Store in request state
        request.state.request_id = request_id
        
        # Call next middleware/handler
        response = await call_next(request)
        
        # Add to response headers
        response.headers['X-Request-ID'] = request_id
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured JSON logging."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger("epi-api")
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Get request ID from state
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        try:
            response = await call_next(request)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Log request
            log_extra = {
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'latency_ms': round(latency_ms, 2),
            }
            
            # Add user ID if authenticated
            if hasattr(request.state, 'user_id'):
                log_extra['user_id'] = request.state.user_id
            
            self.logger.info(
                f"{request.method} {request.url.path} - {response.status_code}",
                extra=log_extra
            )
            
            return response
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            
            log_extra = {
                'request_id': request_id,
                'method': request.method,
                'path': request.url.path,
                'status_code': 500,
                'latency_ms': round(latency_ms, 2),
                'error': str(e)
            }
            
            self.logger.error(
                f"{request.method} {request.url.path} - ERROR: {str(e)}",
                extra=log_extra,
                exc_info=True
            )
            
            raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for Prometheus metrics collection."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics endpoint itself
        if request.url.path == '/metrics':
            return await call_next(request)
        
        method = request.method
        path = request.url.path
        
        # Normalize path (remove IDs)
        normalized_path = self._normalize_path(path)
        
        # Track active requests
        ACTIVE_REQUESTS.labels(method=method, endpoint=normalized_path).inc()
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Record metrics
            latency = time.time() - start_time
            status = response.status_code
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=normalized_path,
                status=status
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=normalized_path
            ).observe(latency)
            
            # Track errors
            if status >= 400:
                ERROR_COUNT.labels(
                    method=method,
                    endpoint=normalized_path,
                    status=status
                ).inc()
            
            return response
            
        except Exception as e:
            # Record error metrics
            REQUEST_COUNT.labels(
                method=method,
                endpoint=normalized_path,
                status=500
            ).inc()
            
            ERROR_COUNT.labels(
                method=method,
                endpoint=normalized_path,
                status=500
            ).inc()
            
            raise
            
        finally:
            # Decrement active requests
            ACTIVE_REQUESTS.labels(method=method, endpoint=normalized_path).dec()
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path to group similar endpoints."""
        # Remove UUIDs and numeric IDs
        import re
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{id}', path)
        path = re.sub(r'/\d+', '/{id}', path)
        return path
