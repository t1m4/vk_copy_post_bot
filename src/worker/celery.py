from celery import Celery
from celery.schedules import crontab

from src.config import config


# TODO finish
# @signals.worker_process_shutdown.connect()
# def stop_worker_process(*args: Any, **kwargs: Any) -> None:
#     """Some job on worker stop"""
#     asyncio.run(stop_services(dispatcher, vk_api_client, redis_client))

celery_app = Celery(main="telegram_bot", broker=config.REDIS_URL)
celery_app.autodiscover_tasks()
celery_app.conf.beat_schedule = {
    "add-every-30-seconds": {
        "task": "src.worker.tasks.test_task",
        "schedule": crontab(minute="*/5", hour="6-23"),
    },
}
celery_app.conf.update(timezone="Europe/Moscow")
