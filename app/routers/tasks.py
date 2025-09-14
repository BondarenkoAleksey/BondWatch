from fastapi import APIRouter
from app.celery_tasks.tasks import sync_all_bonds_task


router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/sync_all")
def run_sync_all():
    """Запустить фоновое обновление всех бондов."""
    sync_all_bonds_task.delay()
    return {"status": "sync_all_bonds_task started"}
