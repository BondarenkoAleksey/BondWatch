from celery import Celery

celery = Celery(
    "bondwatch",
    # broker="redis://localhost:6379/0",
    # backend="redis://localhost:6379/1"
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/1"
)

# celery.conf.task_routes = {"app.celery_tasks.tasks.*": {"queue": "default"}}
celery.autodiscover_tasks(['app.celery_tasks'])

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Moscow",
    enable_utc=True,
)
