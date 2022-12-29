import asyncio
from typing import Any

from celery import Celery, signals
from celery.schedules import crontab

from main import start_services, stop_services
from src import error_reporting
from src.config import config

celery_event_loop = asyncio.new_event_loop()


@signals.worker_process_init.connect()
def start_worker_process(*args: Any, **kwargs: Any) -> None:
    """Some job on worker process start"""
    error_reporting.init(config.SENTRY_DSN, config.ENVIRONMENT)
    celery_event_loop.run_until_complete(start_services())


@signals.worker_process_shutdown.connect()
def stop_worker_process(*args: Any, **kwargs: Any) -> None:
    """Some job on worker process stop"""
    celery_event_loop.run_until_complete(stop_services())


celery_app = Celery(main="telegram_bot", broker=config.REDIS_URL)
celery_app.autodiscover_tasks()
celery_app.conf.beat_schedule = {
    "add-every-30-seconds": {
        "task": "src.worker.tasks.test_task",
        "schedule": crontab(minute="*/5", hour="6-23"),
    },
}
celery_app.conf.update(timezone="Europe/Moscow")
