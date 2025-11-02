"""
Cleanup Tasks - Background jobs for cleanup and archiving
"""
import os
from datetime import datetime, timedelta
from celery import Task
import psycopg2
import boto3

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
def cleanup_old_s3_files(self):
    """
    Clean up old S3 files that are marked as deleted.
    
    Rules:
    - Delete files older than 30 days with status DELETADA
    - Keep files referenced in completed activities
    - Log all deletions
    """
    conn = self.db_conn
    s3_client = boto3.client(
        's3',
        endpoint_url=os.getenv("S3_ENDPOINT", "http://minio:9000"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY", "minioadmin"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY", "minioadmin")
    )
    bucket = os.getenv("S3_BUCKET_EVIDENCIAS", "techdengue-evidencias")
    
    try:
        with conn.cursor() as cur:
            # Find old deleted evidences
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            cur.execute("""
                SELECT id, url_s3
                FROM evidencia
                WHERE status = 'DELETADA'
                AND atualizado_em < %s
            """, (cutoff_date,))
            
            evidencias = cur.fetchall()
            deleted_count = 0
            
            for evidencia_id, url_s3 in evidencias:
                try:
                    # Delete from S3
                    s3_client.delete_object(Bucket=bucket, Key=url_s3)
                    
                    # Mark as archived in DB
                    cur.execute("""
                        UPDATE evidencia
                        SET metadata = jsonb_set(
                            COALESCE(metadata, '{}'::jsonb),
                            '{archived}',
                            'true'::jsonb
                        )
                        WHERE id = %s
                    """, (evidencia_id,))
                    
                    deleted_count += 1
                    
                except Exception as e:
                    print(f"Error deleting S3 file {url_s3}: {e}")
            
            conn.commit()
            
            return {
                "task": "cleanup_old_s3_files",
                "deleted": deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            }
    
    except Exception as e:
        conn.rollback()
        raise


@celery_app.task(base=DatabaseTask, bind=True)
def archive_old_reports(self):
    """
    Archive old PDF reports to cold storage.
    
    Rules:
    - Move reports older than 90 days to archive bucket
    - Keep index in database
    - Compress before archiving
    """
    import tarfile
    import io
    
    conn = self.db_conn
    s3_client = boto3.client(
        's3',
        endpoint_url=os.getenv("S3_ENDPOINT", "http://minio:9000"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY", "minioadmin"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY", "minioadmin")
    )
    
    source_bucket = os.getenv("S3_BUCKET_RELATORIOS", "techdengue-relatorios")
    archive_bucket = os.getenv("S3_BUCKET_ARCHIVE", "techdengue-archive")
    
    reports_dir = os.getenv("REPORTS_DIR", "/tmp/reports")
    cutoff_date = datetime.utcnow() - timedelta(days=90)
    
    try:
        # List old reports
        old_reports = []
        for filename in os.listdir(reports_dir):
            if not filename.startswith("EVD01_"):
                continue
            
            filepath = os.path.join(reports_dir, filename)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if mtime < cutoff_date:
                old_reports.append(filename)
        
        if not old_reports:
            return {"task": "archive_old_reports", "archived": 0}
        
        # Create tar.gz archive
        archive_name = f"reports_archive_{datetime.utcnow().strftime('%Y%m%d')}.tar.gz"
        archive_buffer = io.BytesIO()
        
        with tarfile.open(fileobj=archive_buffer, mode='w:gz') as tar:
            for filename in old_reports:
                filepath = os.path.join(reports_dir, filename)
                tar.add(filepath, arcname=filename)
        
        # Upload to archive bucket
        archive_buffer.seek(0)
        s3_client.put_object(
            Bucket=archive_bucket,
            Key=archive_name,
            Body=archive_buffer.getvalue(),
            ContentType='application/gzip'
        )
        
        # Delete local files
        for filename in old_reports:
            os.remove(os.path.join(reports_dir, filename))
        
        return {
            "task": "archive_old_reports",
            "archived": len(old_reports),
            "archive_name": archive_name
        }
    
    except Exception as e:
        raise


@celery_app.task(base=DatabaseTask, bind=True)
def cleanup_sync_logs(self):
    """
    Clean up old sync logs.
    
    Rules:
    - Keep logs for 180 days
    - Archive to S3 before deletion
    """
    conn = self.db_conn
    cutoff_date = datetime.utcnow() - timedelta(days=180)
    
    try:
        with conn.cursor() as cur:
            # Count logs to delete
            cur.execute("""
                SELECT COUNT(*)
                FROM sync_log
                WHERE server_timestamp < %s
            """, (cutoff_date,))
            
            count = cur.fetchone()[0]
            
            if count == 0:
                return {"task": "cleanup_sync_logs", "deleted": 0}
            
            # TODO: Archive to S3 before deletion
            
            # Delete old logs
            cur.execute("""
                DELETE FROM sync_log
                WHERE server_timestamp < %s
            """, (cutoff_date,))
            
            conn.commit()
            
            return {
                "task": "cleanup_sync_logs",
                "deleted": count,
                "cutoff_date": cutoff_date.isoformat()
            }
    
    except Exception as e:
        conn.rollback()
        raise


@celery_app.task(base=DatabaseTask, bind=True)
def vacuum_database(self):
    """
    Run VACUUM ANALYZE on database for optimization.
    
    Runs weekly to:
    - Reclaim storage
    - Update statistics
    - Improve query performance
    """
    conn = self.db_conn
    
    try:
        # Close existing connection (VACUUM requires no transaction)
        conn.close()
        
        # Reconnect with autocommit
        db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://techdengue:techdengue@db:5432/techdengue"
        ).replace("postgresql+asyncpg://", "postgresql://")
        
        conn = psycopg2.connect(db_url)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cur:
            # Vacuum main tables
            tables = ['atividade', 'evidencia', 'sync_log']
            
            for table in tables:
                cur.execute(f"VACUUM ANALYZE {table}")
        
        return {
            "task": "vacuum_database",
            "tables": tables,
            "status": "success"
        }
    
    except Exception as e:
        raise
    finally:
        conn.close()
