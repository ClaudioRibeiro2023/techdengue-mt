from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.middleware import RequestIDMiddleware, LoggingMiddleware, MetricsMiddleware, JSONFormatter
from app.routers import atividades, evidencias, relatorios_evd01, sync
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("campo-api")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.propagate = False

app = FastAPI(
    title="TechDengue Campo API",
    version="1.0.0",
    description="API para atividades de campo, evidências e relatórios EVD"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# Include routers
app.include_router(atividades.router, prefix="/api")
app.include_router(evidencias.router, prefix="/api")
app.include_router(relatorios_evd01.router, prefix="/api")
app.include_router(sync.router, prefix="/api")


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "campo-api",
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
    return {"status": "ok", "service": "campo-api", "version": "v1"}
