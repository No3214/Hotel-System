"""
Kozbeyli Konagi - Celery Task Queue
Redis-backed distributed task queue replacing APScheduler.
Supports periodic tasks (beat) and async task execution.
"""
import os
import subprocess
import logging
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env')

logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Celery app
celery_app = Celery(
    'kozbeyli',
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    timezone='Europe/Istanbul',
    enable_utc=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
    beat_schedule={
        'breakfast-prep': {
            'task': 'celery_tasks.breakfast_prep_task',
            'schedule': crontab(hour=1, minute=0),
            'options': {'queue': 'scheduled'},
        },
        'morning-reminders': {
            'task': 'celery_tasks.morning_reminders_task',
            'schedule': crontab(hour=8, minute=30),
            'options': {'queue': 'scheduled'},
        },
        'checkout-cleaning': {
            'task': 'celery_tasks.checkout_cleaning_task',
            'schedule': crontab(hour=12, minute=30),
            'options': {'queue': 'scheduled'},
        },
        'evening-room-check': {
            'task': 'celery_tasks.evening_room_check_task',
            'schedule': crontab(hour=18, minute=0),
            'options': {'queue': 'scheduled'},
        },
        'whatsapp-reservation-reminders': {
            'task': 'celery_tasks.whatsapp_reservation_reminders_task',
            'schedule': crontab(hour=10, minute=0),
            'options': {'queue': 'scheduled'},
        },
        'whatsapp-checkout-thanks': {
            'task': 'celery_tasks.whatsapp_checkout_thanks_task',
            'schedule': crontab(hour=14, minute=0),
            'options': {'queue': 'scheduled'},
        },
        'auto-publish-content': {
            'task': 'celery_tasks.auto_publish_content_task',
            'schedule': crontab(hour=10, minute=0),
            'options': {'queue': 'scheduled'},
        },
    },
)

# Import tasks so they are registered
import celery_tasks  # noqa: F401

# Beat and Worker process references
_beat_process = None
_worker_process = None


def start_celery_beat():
    """Start Celery beat scheduler and worker as background subprocesses."""
    global _beat_process, _worker_process
    cwd = str(Path(__file__).parent)
    try:
        _worker_process = subprocess.Popen(
            ['/root/.venv/bin/celery', '-A', 'celery_app', 'worker', '--loglevel=info', '--concurrency=2', '-Q', 'celery,scheduled'],
            cwd=cwd,
            stdout=open('/var/log/supervisor/celery_worker.log', 'a'),
            stderr=open('/var/log/supervisor/celery_worker.err.log', 'a'),
        )
        logger.info(f"Celery worker started (PID: {_worker_process.pid})")
    except Exception as e:
        logger.warning(f"Celery worker could not start: {e}")

    try:
        _beat_process = subprocess.Popen(
            ['/root/.venv/bin/celery', '-A', 'celery_app', 'beat', '--loglevel=info'],
            cwd=cwd,
            stdout=open('/var/log/supervisor/celery_beat.log', 'a'),
            stderr=open('/var/log/supervisor/celery_beat.err.log', 'a'),
        )
        logger.info(f"Celery beat started (PID: {_beat_process.pid})")
    except Exception as e:
        logger.warning(f"Celery beat could not start: {e}")


def stop_celery_beat():
    """Stop Celery beat and worker subprocesses."""
    global _beat_process, _worker_process
    if _beat_process:
        _beat_process.terminate()
        _beat_process = None
    if _worker_process:
        _worker_process.terminate()
        _worker_process = None
    logger.info("Celery processes stopped")
