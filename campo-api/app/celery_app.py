"""
Celery App Configuration - Background jobs
"""
import os
from celery import Celery
from celery.schedules import crontab

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Initialize Celery
celery_app = Celery(
    "campo_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        'app.tasks.cleanup_tasks',
        'app.tasks.report_tasks',
        'app.tasks.notification_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Cuiaba',  # MT timezone
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    # S3 cleanup - daily at 2 AM
    'cleanup-old-s3-files': {
        'task': 'app.tasks.cleanup_tasks.cleanup_old_s3_files',
        'schedule': crontab(hour=2, minute=0),
    },
    # Archive old reports - daily at 3 AM
    'archive-old-reports': {
        'task': 'app.tasks.cleanup_tasks.archive_old_reports',
        'schedule': crontab(hour=3, minute=0),
    },
    # Sync metrics aggregation - every 15 minutes
    'aggregate-sync-metrics': {
        'task': 'app.tasks.report_tasks.aggregate_sync_metrics',
        'schedule': crontab(minute='*/15'),
    },
    # Send daily digest - daily at 8 AM
    'send-daily-digest': {
        'task': 'app.tasks.notification_tasks.send_daily_digest',
        'schedule': crontab(hour=8, minute=0),
    },
}

# Task routes
celery_app.conf.task_routes = {
    'app.tasks.cleanup_tasks.*': {'queue': 'cleanup'},
    'app.tasks.report_tasks.*': {'queue': 'reports'},
    'app.tasks.notification_tasks.*': {'queue': 'notifications'},
}

if __name__ == '__main__':
    celery_app.start()
