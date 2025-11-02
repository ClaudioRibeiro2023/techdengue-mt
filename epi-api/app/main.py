from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.middleware import RequestIDMiddleware, LoggingMiddleware, MetricsMiddleware, JSONFormatter
from app.routers import etl, mapa
import logging

# Configure JSON logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("epi-api")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.propagate = False

# Create FastAPI app
app = FastAPI(
    title="TechDengue EPI API",
    version="1.0.0",
    description="API para ETL de indicadores epidemiológicos e relatórios EPI"
)

# Include routers
app.include_router(etl.router, prefix="/api")
app.include_router(mapa.router, prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add observability middlewares (order matters!)
app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "epi-api",
        "version": "1.0.0"
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/api/v1/health")
async def health_v1():
    return {"status": "ok", "service": "epi-api", "version": "v1"}
