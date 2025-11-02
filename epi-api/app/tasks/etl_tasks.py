"""
Celery Tasks for ETL processing (SINAN and LIRAa)
"""
import os
from celery import Task

from app.celery_app import celery_app
from app.services.sinan_etl_service import SINANETLService
from app.services.liraa_etl_service import LIRaaETLService
from app.schemas.etl import (
    SINANImportRequest,
    LIRaaImportRequest,
    ETLStatus
)


# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'techdengue'),
    'user': os.getenv('DB_USER', 'techdengue'),
    'password': os.getenv('DB_PASSWORD', 'techdengue')
}


@celery_app.task(
    name='etl.process_sinan_import',
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutos
)
def process_sinan_import_task(
    self: Task,
    job_id: str,
    request_data: dict
) -> dict:
    """
    Processa importação SINAN de forma assíncrona
    
    Args:
        job_id: ID do job ETL
        request_data: Dados do SINANImportRequest
        
    Returns:
        Dict com estatísticas do processamento
    """
    try:
        # Recriar request object
        request = SINANImportRequest(**request_data)
        
        # Criar service
        service = SINANETLService(DB_CONFIG)
        
        # Processar
        result = service.process_sinan_import(job_id, request)
        
        return {
            'job_id': job_id,
            'status': 'success',
            'result': result
        }
        
    except Exception as e:
        # Atualizar status para FAILED
        service = SINANETLService(DB_CONFIG)
        service.update_job_status(
            job_id,
            ETLStatus.FAILED,
            error_message=str(e)
        )
        
        # Retry com backoff exponencial
        raise self.retry(exc=e, countdown=min(2 ** self.request.retries * 60, 3600))


@celery_app.task(
    name='etl.process_liraa_import',
    bind=True,
    max_retries=3,
    default_retry_delay=300
)
def process_liraa_import_task(
    self: Task,
    job_id: str,
    request_data: dict
) -> dict:
    """
    Processa importação LIRAa de forma assíncrona
    
    Args:
        job_id: ID do job ETL
        request_data: Dados do LIRaaImportRequest
        
    Returns:
        Dict com estatísticas do processamento
    """
    try:
        # Recriar request object
        request = LIRaaImportRequest(**request_data)
        
        # Criar service
        service = LIRaaETLService(DB_CONFIG)
        
        # Processar
        result = service.process_liraa_import(job_id, request)
        
        return {
            'job_id': job_id,
            'status': 'success',
            'result': result
        }
        
    except Exception as e:
        # Atualizar status para FAILED
        service = LIRaaETLService(DB_CONFIG)
        service.update_job_status(
            job_id,
            ETLStatus.FAILED,
            error_message=str(e)
        )
        
        # Retry
        raise self.retry(exc=e, countdown=min(2 ** self.request.retries * 60, 3600))


@celery_app.task(name='etl.cleanup_old_jobs')
def cleanup_old_etl_jobs() -> dict:
    """
    Remove jobs ETL antigos (>90 dias) com status COMPLETED ou FAILED
    
    Agendado para rodar semanalmente
    
    Returns:
        Dict com quantidade de jobs removidos
    """
    import psycopg2
    from datetime import datetime, timedelta
    
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # Deletar jobs completados/falhados com mais de 90 dias
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            cur.execute("""
                DELETE FROM etl_jobs
                WHERE status IN ('COMPLETED', 'FAILED', 'PARTIAL')
                  AND completed_at < %s
            """, (cutoff_date,))
            
            deleted_count = cur.rowcount
            conn.commit()
            
            return {
                'deleted_jobs': deleted_count,
                'cutoff_date': cutoff_date.isoformat()
            }
    finally:
        conn.close()


@celery_app.task(name='etl.get_jobs_stats')
def get_etl_jobs_stats() -> dict:
    """
    Retorna estatísticas dos jobs ETL
    
    Returns:
        Dict com estatísticas por status e source
    """
    import psycopg2
    
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # Contar por status
            cur.execute("""
                SELECT status, source, COUNT(*) as count
                FROM etl_jobs
                GROUP BY status, source
                ORDER BY status, source
            """)
            
            stats = {}
            for row in cur.fetchall():
                status, source, count = row
                key = f"{source}_{status}"
                stats[key] = count
            
            # Total geral
            cur.execute("SELECT COUNT(*) FROM etl_jobs")
            stats['total'] = cur.fetchone()[0]
            
            return stats
    finally:
        conn.close()
