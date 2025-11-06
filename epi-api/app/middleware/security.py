"""
Security Middleware - Rate Limiting, Headers, CORS
"""
from fastapi import Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware usando token bucket algorithm
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[datetime]] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        # Obter identificador (IP ou user_id)
        client_id = self._get_client_id(request)
        
        # Limpar requests antigos
        cutoff_time = datetime.now() - timedelta(minutes=1)
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff_time
        ]
        
        # Verificar limite
        if len(self.requests[client_id]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_id}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later.",
                headers={"Retry-After": "60"}
            )
        
        # Registrar request
        self.requests[client_id].append(datetime.now())
        
        # Processar request
        response = await call_next(request)
        
        # Adicionar headers de rate limit
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests_per_minute - len(self.requests[client_id])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int((datetime.now() + timedelta(minutes=1)).timestamp())
        )
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Obtém identificador único do cliente"""
        # Preferir user_id se autenticado
        if hasattr(request.state, "user_id"):
            return f"user:{request.state.user_id}"
        
        # Usar IP como fallback
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0]}"
        
        return f"ip:{request.client.host}"


# ============================================================================
# SECURITY HEADERS
# ============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adiciona security headers em todas as respostas
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://keycloak.techdengue.mt.gov.br"
        )
        
        # Remove headers expostos
        response.headers.pop("Server", None)
        response.headers.pop("X-Powered-By", None)
        
        return response


# ============================================================================
# CORS CONFIGURATION
# ============================================================================

def configure_cors(app):
    """
    Configura CORS com whitelist de origens
    """
    
    # Origens permitidas
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:6000",
        "http://localhost:6080",
        "http://localhost:5173",
        "https://techdengue.mt.gov.br",
        "https://app.techdengue.mt.gov.br",
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Request-ID",
            "X-Correlation-ID",
        ],
        expose_headers=[
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
            "X-Total-Count",
            "X-File-Hash",
            "X-File-Size",
        ],
        max_age=3600,  # Cache preflight por 1 hora
    )


# ============================================================================
# REQUEST ID
# ============================================================================

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Adiciona Request ID único para rastreamento
    """
    
    async def dispatch(self, request: Request, call_next):
        import uuid
        
        # Obter ou gerar request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Adicionar ao state
        request.state.request_id = request_id
        
        # Processar request
        response = await call_next(request)
        
        # Adicionar ao response
        response.headers["X-Request-ID"] = request_id
        
        return response


# ============================================================================
# INTEGRATION
# ============================================================================

def setup_security_middleware(app):
    """
    Configura todos os middlewares de segurança
    """
    
    # Request ID (primeiro)
    app.add_middleware(RequestIDMiddleware)
    
    # Security Headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Rate Limiting
    # Valores diferentes por ambiente
    import os
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        requests_per_minute = 60
    elif env == "staging":
        requests_per_minute = 120
    else:  # development
        requests_per_minute = 1000
    
    app.add_middleware(RateLimitMiddleware, requests_per_minute=requests_per_minute)
    
    # CORS
    configure_cors(app)
    
    logger.info(f"Security middleware configured (env={env}, rate_limit={requests_per_minute})")
