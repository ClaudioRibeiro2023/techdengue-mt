"""
Report Tasks - Automated report generation and aggregation
"""
import os
from datetime import datetime, timedelta
from celery import Task
import psycopg2
from psycopg2.extras import RealDictCursor

from app.celery_app import celery_app


class DatabaseTask(Task):
    """Base task with database connection"""
    _db_conn = None
    
    @property
    def db_conn(self):
        if self._db_conn is None:
            db_url = os.getenv(
                "DATABASE_URL",
                "postgresql://techdengue:techdengue@db:5432/techdengue"
            ).replace("postgresql+asyncpg://", "postgresql://")
            self._db_conn = psycopg2.connect(db_url)
        return self._db_conn


@celery_app.task(base=DatabaseTask, bind=True)
def aggregate_sync_metrics(self):
    """
    Aggregate sync metrics for monitoring.
    
    Creates hourly aggregations of:
    - Sync operations count
    - Success rate
    - Average processing time
    - Active devices
    """
    conn = self.db_conn
    now = datetime.utcnow()
    hour_start = now.replace(minute=0, second=0, microsecond=0)
    hour_end = hour_start + timedelta(hours=1)
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Aggregate metrics
            cur.execute("""
                INSERT INTO sync_metrics_hourly (
                    period_start,
                    total_operations,
                    success_count,
                    error_count,
                    conflict_count,
                    unique_devices,
                    avg_processing_ms
                )
                SELECT 
                    %s as period_start,
                    COUNT(*) as total_operations,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as error_count,
                    SUM(CASE WHEN status = 'conflict' THEN 1 ELSE 0 END) as conflict_count,
                    COUNT(DISTINCT device_id) as unique_devices,
                    AVG(EXTRACT(EPOCH FROM (server_timestamp - client_timestamp)) * 1000) as avg_processing_ms
                FROM sync_log
                WHERE server_timestamp >= %s
                AND server_timestamp < %s
                ON CONFLICT (period_start) DO UPDATE SET
                    total_operations = EXCLUDED.total_operations,
                    success_count = EXCLUDED.success_count,
                    error_count = EXCLUDED.error_count,
                    conflict_count = EXCLUDED.conflict_count,
                    unique_devices = EXCLUDED.unique_devices,
                    avg_processing_ms = EXCLUDED.avg_processing_ms
            """, (hour_start, hour_start, hour_end))
            
            conn.commit()
            
            return {
                "task": "aggregate_sync_metrics",
                "period": hour_start.isoformat(),
                "status": "success"
            }
    
    except Exception as e:
        conn.rollback()
        raise


@celery_app.task(base=DatabaseTask, bind=True)
def generate_weekly_report(self):
    """
    Generate weekly activity report for all municipalities.
    
    Includes:
    - Activities by type
    - Evidences collected
    - Coverage by sector
    - Performance metrics
    """
    conn = self.db_conn
    week_start = datetime.utcnow() - timedelta(days=7)
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Aggregate by municipality
            cur.execute("""
                SELECT 
                    municipio_cod_ibge,
                    COUNT(DISTINCT a.id) as total_atividades,
                    COUNT(DISTINCT CASE WHEN a.status = 'CONCLUIDA' THEN a.id END) as concluidas,
                    COUNT(DISTINCT e.id) as total_evidencias,
                    json_object_agg(
                        a.tipo, 
                        COUNT(DISTINCT a.id)
                    ) as por_tipo
                FROM atividade a
                LEFT JOIN evidencia e ON e.atividade_id = a.id
                WHERE a.criado_em >= %s
                GROUP BY municipio_cod_ibge
            """, (week_start,))
            
            municipalities = cur.fetchall()
            
            # Save aggregated report
            report_data = {
                "period_start": week_start.isoformat(),
                "period_end": datetime.utcnow().isoformat(),
                "municipalities": [dict(m) for m in municipalities]
            }
            
            cur.execute("""
                INSERT INTO weekly_reports (
                    week_start,
                    report_data,
                    generated_at
                ) VALUES (%s, %s, %s)
            """, (
                week_start,
                psycopg2.extras.Json(report_data),
                datetime.utcnow()
            ))
            
            conn.commit()
            
            return {
                "task": "generate_weekly_report",
                "period": week_start.isoformat(),
                "municipalities": len(municipalities)
            }
    
    except Exception as e:
        conn.rollback()
        raise


@celery_app.task(base=DatabaseTask, bind=True)
def auto_generate_evd01(self, atividade_id: int):
    """
    Auto-generate EVD01 report when activity is completed.
    
    Args:
        atividade_id: Activity ID
    """
    from app.services.evd01_generator import EVD01Generator
    from app.services.atividade_service import AtividadeService
    from app.services.evidencia_service import EvidenciaService
    
    try:
        # Get activity
        atividade_service = AtividadeService(self.db_conn.dsn)
        atividade = atividade_service.get_by_id(atividade_id)
        
        if not atividade or atividade.status != "CONCLUIDA":
            return {"status": "skipped", "reason": "not_completed"}
        
        # Get evidences
        evidencia_service = EvidenciaService(self.db_conn.dsn)
        evidencias_list = evidencia_service.list_by_atividade(atividade_id)
        
        if evidencias_list.total == 0:
            return {"status": "skipped", "reason": "no_evidences"}
        
        # Generate report
        generator = EVD01Generator()
        
        atividade_dict = {
            "id": atividade.id,
            "tipo": atividade.tipo.value,
            "status": atividade.status.value,
            "municipio_cod_ibge": atividade.municipio_cod_ibge,
            "criado_em": atividade.criado_em.isoformat()
        }
        
        evidencias_dict = [
            {
                "id": ev.id,
                "tipo": ev.tipo.value,
                "hash_sha256": ev.hash_sha256,
                "tamanho_bytes": ev.tamanho_bytes,
                "criado_em": ev.criado_em.isoformat()
            }
            for ev in evidencias_list.items
        ]
        
        filepath, filename, merkle_dict = generator.generate(
            atividade=atividade_dict,
            evidencias=evidencias_dict
        )
        
        # Notify user
        from app.tasks.notification_tasks import notify_report_ready
        notify_report_ready.delay(
            atividade_id=atividade_id,
            report_url=f"/relatorios/download/{filename}"
        )
        
        return {
            "task": "auto_generate_evd01",
            "atividade_id": atividade_id,
            "filename": filename,
            "status": "success"
        }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}
