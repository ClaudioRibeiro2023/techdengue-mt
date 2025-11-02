"""
ETL Router - Endpoints for SINAN and LIRAa import
"""
import os
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from app.schemas.etl import (
    SINANImportRequest,
    SINANImportResponse,
    LIRaaImportRequest,
    LIRaaImportResponse,
    ETLJobStatus,
    ETLJobList,
    ETLSource
)
from app.services.sinan_etl_service import SINANETLService
from app.services.liraa_etl_service import LIRaaETLService

router = APIRouter(prefix="/etl", tags=["ETL"])

# Database connection (TODO: move to dependency injection)
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'techdengue'),
    'user': os.getenv('DB_USER', 'techdengue'),
    'password': os.getenv('DB_PASSWORD', 'techdengue')
}


# ============================================================================
# SINAN ENDPOINTS
# ============================================================================

@router.post("/sinan/import", response_model=SINANImportResponse, status_code=202)
async def import_sinan(
    request: SINANImportRequest,
    background_tasks: BackgroundTasks
):
    """
    Importa dados do SINAN (Sistema de Informação de Agravos de Notificação)
    
    Processa arquivo CSV do SINAN e importa casos de dengue/zika/chikungunya/febre amarela
    para a tabela `indicador_epi`. O processamento é assíncrono via Celery.
    
    **Campos principais CSV SINAN:**
    - nu_notific: Número da notificação
    - dt_notific: Data da notificação
    - dt_sin_pri: Data dos primeiros sintomas
    - nm_pacient: Nome do paciente
    - id_municip: Código IBGE município (7 dígitos)
    - classi_fin: Classificação final (1=Confirmado lab, 5=Confirmado clínico, etc)
    - evolucao: Evolução (1=Cura, 2=Óbito por dengue, etc)
    
    **Processo:**
    1. Cria job ETL com status PENDING
    2. Dispara processamento async (Celery)
    3. Retorna job_id para tracking
    4. Agrega casos por município + semana epidemiológica
    5. Insere/atualiza em `indicador_epi`
    
    **Exemplo:**
    ```bash
    curl -X POST "http://localhost:8000/api/etl/sinan/import" \\
      -H "Content-Type: application/json" \\
      -d '{
        "file_path": "s3://bucket/sinan_dengue_2024.csv",
        "doenca_tipo": "DENGUE",
        "ano_epidemiologico": 2024,
        "overwrite": false,
        "batch_size": 500
      }'
    ```
    
    **Retorna (202 Accepted):**
    - job_id: ID para consultar status
    - status: PENDING
    - estimated_time_seconds: Tempo estimado
    """
    try:
        # Criar service
        service = SINANETLService(DB_CONFIG)
        
        # Validar CSV antes de processar
        validation = service.validate_sinan_csv(request.file_path)
        
        if not validation.is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "CSV SINAN inválido",
                    "errors": [e.model_dump() for e in validation.errors[:10]]
                }
            )
        
        # Criar job ETL
        job_id = service.create_job(
            source=ETLSource.SINAN,
            file_path=request.file_path,
            metadata={
                "doenca_tipo": request.doenca_tipo.value,
                "ano": request.ano_epidemiologico,
                "overwrite": request.overwrite
            }
        )
        
        # Disparar processamento async
        # TODO: Usar Celery task aqui
        # Por enquanto, processar síncrono em background
        background_tasks.add_task(
            service.process_sinan_import,
            job_id,
            request
        )
        
        # Estimar tempo
        total_rows = validation.total_rows
        estimated_seconds = int(total_rows / 100)  # ~100 registros/segundo
        
        return SINANImportResponse(
            job_id=job_id,
            status=ETLStatus.PENDING,
            message="Importação SINAN iniciada. Use /etl/jobs/{job_id} para acompanhar.",
            file_path=request.file_path,
            started_at=datetime.utcnow(),
            total_rows=total_rows,
            estimated_time_seconds=estimated_seconds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao iniciar importação SINAN: {str(e)}"
        )


# ============================================================================
# LIRAa ENDPOINTS
# ============================================================================

@router.post("/liraa/import", response_model=LIRaaImportResponse, status_code=202)
async def import_liraa(
    request: LIRaaImportRequest,
    background_tasks: BackgroundTasks
):
    """
    Importa dados do LIRAa (Levantamento Rápido de Índices para Aedes aegypti)
    
    Processa arquivo CSV do LIRAa e calcula índices entomológicos (IIP, IB, IDC)
    para avaliação de risco de dengue por município.
    
    **Campos principais CSV LIRAa:**
    - municipio_codigo: Código IBGE (7 dígitos)
    - ano: Ano do levantamento
    - ciclo: Ciclo LIRAa (1-6, bimestral)
    - imoveis_pesquisados: Total de imóveis visitados
    - imoveis_positivos: Imóveis com larvas/pupas de Aedes
    - depositos_inspecionados: Total de depósitos verificados
    - depositos_positivos: Depósitos com larvas/pupas
    - iip, ib, idc: Índices (calculados se não fornecidos)
    
    **Índices Calculados:**
    - IIP = (Imóveis positivos / Imóveis pesquisados) × 100
    - IB = (Depósitos positivos / Imóveis pesquisados) × 100
    - IDC = (Depósitos positivos / Depósitos inspecionados) × 100
    
    **Classificação de Risco (IIP):**
    - BAIXO: IIP < 1%
    - MÉDIO: 1% ≤ IIP < 3.9%
    - ALTO: 3.9% ≤ IIP < 5%
    - MUITO_ALTO: IIP ≥ 5%
    
    **Exemplo:**
    ```bash
    curl -X POST "http://localhost:8000/api/etl/liraa/import" \\
      -H "Content-Type: application/json" \\
      -d '{
        "file_path": "s3://bucket/liraa_mt_2024_ciclo1.csv",
        "ano": 2024,
        "ciclo": 1,
        "calcular_indices": true,
        "overwrite": false
      }'
    ```
    """
    try:
        # Criar service
        service = LIRaaETLService(DB_CONFIG)
        
        # Validar CSV
        validation = service.validate_liraa_csv(request.file_path)
        
        if not validation.is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "CSV LIRAa inválido",
                    "errors": [e.model_dump() for e in validation.errors[:10]]
                }
            )
        
        # Criar job ETL
        job_id = service.create_job(
            source=ETLSource.LIRAA,
            file_path=request.file_path,
            metadata={
                "ano": request.ano,
                "ciclo": request.ciclo,
                "calcular_indices": request.calcular_indices
            }
        )
        
        # Disparar processamento async
        background_tasks.add_task(
            service.process_liraa_import,
            job_id,
            request
        )
        
        # Estimar tempo
        total_rows = validation.total_rows
        estimated_seconds = int(total_rows / 50)  # ~50 registros/segundo (cálculos)
        
        return LIRaaImportResponse(
            job_id=job_id,
            status=ETLStatus.PENDING,
            message="Importação LIRAa iniciada. Use /etl/jobs/{job_id} para acompanhar.",
            file_path=request.file_path,
            started_at=datetime.utcnow(),
            total_rows=total_rows,
            estimated_time_seconds=estimated_seconds
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao iniciar importação LIRAa: {str(e)}"
        )


# ============================================================================
# JOB STATUS ENDPOINTS
# ============================================================================

@router.get("/jobs/{job_id}", response_model=ETLJobStatus)
async def get_job_status(job_id: str):
    """
    Consulta status de um job ETL
    
    Retorna informações detalhadas sobre o progresso da importação:
    - Status atual (PENDING, PROCESSING, COMPLETED, FAILED, PARTIAL)
    - Progresso (linhas processadas/total)
    - Taxa de sucesso
    - Erros encontrados
    - Timestamps
    
    **Exemplo:**
    ```bash
    curl "http://localhost:8000/api/etl/jobs/550e8400-e29b-41d4-a716-446655440000"
    ```
    
    **Response:**
    ```json
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "source": "SINAN",
      "status": "PROCESSING",
      "total_rows": 10000,
      "processed_rows": 5000,
      "success_rows": 4950,
      "error_rows": 50,
      "progress_percentage": 50.0,
      "success_rate": 99.0
    }
    ```
    """
    # Tentar ambos services (SINAN e LIRAa)
    for ServiceClass in [SINANETLService, LIRaaETLService]:
        service = ServiceClass(DB_CONFIG)
        job = service.get_job_status(job_id)
        if job:
            return job
    
    raise HTTPException(
        status_code=404,
        detail=f"Job {job_id} não encontrado"
    )


@router.get("/jobs", response_model=ETLJobList)
async def list_jobs(
    source: Optional[ETLSource] = None,
    status: Optional[ETLStatus] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    Lista jobs ETL com filtros opcionais
    
    **Parâmetros:**
    - source: SINAN ou LIRAa
    - status: PENDING, PROCESSING, COMPLETED, FAILED, PARTIAL
    - page: Página (1-indexed)
    - page_size: Itens por página (1-100)
    
    **Exemplo:**
    ```bash
    curl "http://localhost:8000/api/etl/jobs?source=SINAN&status=COMPLETED&page=1&page_size=20"
    ```
    """
    # TODO: Implementar query com filtros
    # Por enquanto, retornar lista vazia
    return ETLJobList(
        jobs=[],
        total=0,
        page=page,
        page_size=page_size
    )
