from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.middleware import RequestIDMiddleware, LoggingMiddleware, MetricsMiddleware, JSONFormatter
from app.routers import relatorios
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("relatorios-api")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.propagate = False

app = FastAPI(
    title="TechDengue Relatorios API",
    version="1.0.0",
    description="API para geração de relatórios PDF/A-1 (EPI01, EVD01) com hash e catálogos"
)

# Include routers
app.include_router(relatorios.router, prefix="/api")

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


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "relatorios-api",
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
    return {"status": "ok", "service": "relatorios-api", "version": "v1"}
