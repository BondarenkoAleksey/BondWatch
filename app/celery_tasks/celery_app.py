from celery import Celery

from app.core.logging_config import setup_logging

celery = Celery(
    "bondwatch",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1"
)

celery.autodiscover_tasks(['app.celery_tasks'])

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Moscow",
    enable_utc=True,
)

setup_logging()
