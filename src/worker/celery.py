from celery import Celery
from celery.schedules import crontab

from src.config import config

celery_app = Celery(main="telegram_bot", broker=config.REDIS_URL)
celery_app.autodiscover_tasks()
celery_app.conf.beat_schedule = {
    "add-every-30-seconds": {
        "task": "src.worker.tasks.test_task",
        "schedule": crontab(minute="*/5", hour="6-23"),
    },
}
celery_app.conf.update(timezone="Europe/Moscow")
