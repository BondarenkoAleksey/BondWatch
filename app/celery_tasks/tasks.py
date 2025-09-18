import asyncio
import logging

from app.celery_tasks.celery_app import celery
from app.database import SessionLocal
from app.models import Bond
from app.routers.moex import sync_moex_bond

logger = logging.getLogger(__name__)

def run_sync_moex_bond(isin: str, db):
    """Sync wrapper for async function."""
    return asyncio.run(sync_moex_bond(isin, db))

@celery.task
def sync_bond_task(isin: str):
    db = SessionLocal()
    try:
        logger.info(f"Start syncing bond {isin}")
        run_sync_moex_bond(isin, db)
        logger.info(f"Finished syncing bond {isin}")
    finally:
        db.close()


@celery.task
def sync_all_bonds_task():
    db = SessionLocal()
    try:
        bonds = db.query(Bond).all()
        for bond in bonds:
            sync_bond_task.delay(bond.isin)
    finally:
        db.close()
