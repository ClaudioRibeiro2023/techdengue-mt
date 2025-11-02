"""
Notification Tasks - Push notifications and alerts
"""
import os
import json
from datetime import datetime, timedelta
from celery import Task
import psycopg2
import requests

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
def send_push_notification(self, user_id: str, title: str, body: str, data: dict = None):
    """
    Send push notification via Firebase Cloud Messaging.
    
    Args:
        user_id: User identifier
        title: Notification title
        body: Notification body
        data: Additional data payload
    """
    fcm_server_key = os.getenv("FCM_SERVER_KEY")
    
    if not fcm_server_key:
        print("FCM_SERVER_KEY not configured, skipping notification")
        return {"status": "skipped", "reason": "no_fcm_key"}
    
    conn = self.db_conn
    
    try:
        with conn.cursor() as cur:
            # Get user's FCM tokens
            cur.execute("""
                SELECT fcm_token
                FROM usuario_device
                WHERE usuario_id = %s
                AND fcm_token IS NOT NULL
                AND active = true
            """, (user_id,))
            
            tokens = [row[0] for row in cur.fetchall()]
            
            if not tokens:
                return {"status": "skipped", "reason": "no_tokens"}
            
            # Send to FCM
            fcm_url = "https://fcm.googleapis.com/fcm/send"
            headers = {
                "Authorization": f"Bearer {fcm_server_key}",
                "Content-Type": "application/json"
            }
            
            success_count = 0
            failed_tokens = []
            
            for token in tokens:
                payload = {
                    "to": token,
                    "notification": {
                        "title": title,
                        "body": body,
                        "sound": "default"
                    },
                    "data": data or {},
                    "priority": "high"
                }
                
                response = requests.post(fcm_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success") == 1:
                        success_count += 1
                    else:
                        failed_tokens.append(token)
                else:
                    failed_tokens.append(token)
            
            # Mark failed tokens as inactive
            if failed_tokens:
                cur.execute("""
                    UPDATE usuario_device
                    SET active = false
                    WHERE fcm_token = ANY(%s)
                """, (failed_tokens,))
                conn.commit()
            
            return {
                "status": "sent",
                "success": success_count,
                "failed": len(failed_tokens)
            }
    
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(base=DatabaseTask, bind=True)
def send_daily_digest(self):
    """
    Send daily digest to managers.
    
    Includes:
    - Total activities completed
    - Total evidences uploaded
    - Sync status by device
    - Alerts and issues
    """
    conn = self.db_conn
    yesterday = datetime.utcnow() - timedelta(days=1)
    
    try:
        with conn.cursor() as cur:
            # Get yesterday's stats
            cur.execute("""
                SELECT 
                    COUNT(DISTINCT a.id) as atividades,
                    COUNT(DISTINCT e.id) as evidencias,
                    COUNT(DISTINCT s.device_id) as devices_ativos
                FROM atividade a
                LEFT JOIN evidencia e ON e.atividade_id = a.id
                LEFT JOIN sync_log s ON s.entity_id = a.id
                WHERE a.criado_em >= %s
            """, (yesterday,))
            
            stats = cur.fetchone()
            
            # Get users with GESTOR role
            cur.execute("""
                SELECT usuario_id
                FROM usuario_papel
                WHERE papel = 'GESTOR'
            """)
            
            managers = [row[0] for row in cur.fetchall()]
            
            # Send digest to each manager
            for manager_id in managers:
                send_push_notification.delay(
                    user_id=manager_id,
                    title="Resumo Diário - TechDengue",
                    body=f"{stats[0]} atividades, {stats[1]} evidências coletadas ontem",
                    data={
                        "type": "daily_digest",
                        "date": yesterday.isoformat(),
                        "atividades": stats[0],
                        "evidencias": stats[1],
                        "devices": stats[2]
                    }
                )
            
            return {
                "task": "send_daily_digest",
                "recipients": len(managers),
                "stats": {
                    "atividades": stats[0],
                    "evidencias": stats[1],
                    "devices": stats[2]
                }
            }
    
    except Exception as e:
        raise


@celery_app.task(base=DatabaseTask, bind=True)
def notify_sync_conflict(self, device_id: str, conflict_data: dict):
    """
    Notify user about sync conflict requiring manual resolution.
    
    Args:
        device_id: Device with conflict
        conflict_data: Conflict details
    """
    conn = self.db_conn
    
    try:
        with conn.cursor() as cur:
            # Get user from device
            cur.execute("""
                SELECT usuario_id
                FROM usuario_device
                WHERE device_id = %s
                LIMIT 1
            """, (device_id,))
            
            row = cur.fetchone()
            if not row:
                return {"status": "skipped", "reason": "no_user"}
            
            user_id = row[0]
            
            # Send notification
            return send_push_notification.delay(
                user_id=user_id,
                title="Conflito de Sincronização",
                body="Uma de suas atividades precisa de resolução manual",
                data={
                    "type": "sync_conflict",
                    "device_id": device_id,
                    **conflict_data
                }
            )
    
    except Exception as e:
        return {"status": "error", "error": str(e)}


@celery_app.task(base=DatabaseTask, bind=True)
def notify_report_ready(self, atividade_id: int, report_url: str):
    """
    Notify user that EVD01 report is ready for download.
    
    Args:
        atividade_id: Activity ID
        report_url: Download URL
    """
    conn = self.db_conn
    
    try:
        with conn.cursor() as cur:
            # Get activity owner
            cur.execute("""
                SELECT usuario_criacao
                FROM atividade
                WHERE id = %s
            """, (atividade_id,))
            
            row = cur.fetchone()
            if not row:
                return {"status": "skipped", "reason": "no_activity"}
            
            user_id = row[0]
            
            # Send notification
            return send_push_notification.delay(
                user_id=user_id,
                title="Relatório Pronto",
                body=f"Relatório EVD01 da atividade #{atividade_id} disponível",
                data={
                    "type": "report_ready",
                    "atividade_id": atividade_id,
                    "report_url": report_url
                }
            )
    
    except Exception as e:
        return {"status": "error", "error": str(e)}
