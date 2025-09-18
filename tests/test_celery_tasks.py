import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Bond
from app.celery_tasks.tasks import sync_all_bonds_task, sync_bond_task


# Асинхронный мок для sync_moex_bond
def mock_sync_bond(isin: str, db):
    """Просто мокаем синхронизацию, ничего не делаем"""
    return None


@pytest.fixture
def db_session():
    """Создаём in-memory SQLite и таблицы перед тестом"""
    engine = create_engine("sqlite:///:memory:", echo=False, future=True)
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_sync_bond_task(db_session, monkeypatch):
    """Проверяем, что sync_bond_task выполняется без ошибок"""

    # Создаём тестовый бонд
    bond = Bond(isin="RU000A0JX0J2")
    db_session.add(bond)
    db_session.commit()

    # Мокаем синхронизацию бонда
    monkeypatch.setattr("app.celery_tasks.tasks.run_sync_moex_bond", mock_sync_bond)

    # Мокаем SessionLocal, чтобы Celery использовал in-memory базу
    monkeypatch.setattr("app.celery_tasks.tasks.SessionLocal", lambda: db_session)

    # Запускаем задачу
    sync_bond_task("RU000A0JX0J2")


def test_sync_all_bonds_task(db_session, monkeypatch):
    """Проверяем, что sync_all_bonds_task вызывает sync_bond_task для всех бондов"""

    # Добавляем несколько бондов
    bonds = [Bond(isin=f"RU000A0JX0J{i}") for i in range(3)]
    db_session.add_all(bonds)
    db_session.commit()

    # Мокаем sync_bond_task.delay
    called_isins = []

    def mock_delay(isin):
        called_isins.append(isin)

    monkeypatch.setattr("app.celery_tasks.tasks.sync_bond_task.delay", mock_delay)
    monkeypatch.setattr("app.celery_tasks.tasks.SessionLocal", lambda: db_session)

    # Запускаем sync_all_bonds_task
    sync_all_bonds_task()

    # Проверяем, что все бонды были переданы в sync_bond_task
    assert set(called_isins) == {b.isin for b in bonds}
