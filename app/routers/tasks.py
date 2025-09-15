import time

from fastapi import APIRouter
from celery.result import AsyncResult

from app.celery_tasks.tasks import sync_bond_task, sync_all_bonds_task
from app.celery_tasks.celery_app import celery

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/sync/{isin}")
def sync_bond(isin: str):
    """Запустить синхронизацию конкретного бонда в фоне."""
    task = sync_bond_task.delay(isin)
    return {"task_id": task.id, "status": "PENDING"}


@router.post("/sync_all")
def sync_all_bonds():
    """Запустить обновление всех бондов в фоне."""
    task = sync_all_bonds_task.delay()
    # time.sleep(30)
    return {"task_id": task.id, "status": "PENDING"}


@router.get("/{task_id}")
def get_task_status(task_id: str):
    """Проверить статус фоновой задачи."""
    result = AsyncResult(task_id, app=celery)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None
    }
