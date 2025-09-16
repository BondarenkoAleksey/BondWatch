# BondWatch

Учебный проект для работы с облигациями и данными Московской биржи (MOEX) на базе **FastAPI**.  
Проект развивается пошагово — каждая итерация добавляет новый инструмент или функциональность.  

---

## Roadmap
- **Stage 1:** Basic FastAPI app with fake in-memory bonds (✅ done)
- **Stage 2:** Add SQLAlchemy + Alembic migrations (✅ done)
- **Stage 3:** Integrate MOEX API (✅ done)
- **Stage 4:** Celery + Redis for background tasks (✅ done)
- **Stage 5:** Docker / docker-compose setup (✅ done)
- **Stage 6:** Integrations (Telegram bot, T-Investments)
- **Stage 7:** Advanced (auth, tests, logging, CI/CD)

---

## Stage 1 — Minimal API
Реализован минимальный FastAPI-приложение c фиктивными данными облигаций:
- `GET /bonds` — список облигаций (in-memory).
- `POST /bonds` — добавление новой облигации.
- `GET /bonds/{isin}` — получение облигации по ISIN.
- `GET /bonds/search` — поиск облигаций по доходности.
- `PATCH /bonds/{isin}` — обновление облигации.

Все данные хранятся в памяти, без базы.

---

## Stage 2 — Database integration
Добавлено подключение базы данных и миграции:
- SQLAlchemy ORM (`app/database.py`).
- Модель `Bond` (`app/models.py`).
- Pydantic-схемы (`app/schemas.py`).
- CRUD-операции (`app/crud.py`).
- Роуты вынесены в `app/routers/bonds.py`.
- Alembic настроен, создана и применена первая миграция (`bonds` table).

---

## Stage 3 — Интеграция с MOEX API
На этом этапе начата работа с данными Московской биржи (MOEX).  

Добавлены роуты:
- `GET /bonds/upcoming_coupons` — получить список облигаций с ближайшими купонами (по локальной БД).
- `GET /moex/bonds/{isin}` — получить данные по облигации с MOEX по ISIN.
- `GET /moex/bonds/{isin}/coupons` — получить график купонов с MOEX.
- `POST /moex/bonds/{isin}/sync` — синхронизировать данные облигации и купонного графика с MOEX в локальную базу.

Дополнительно:
- В Swagger добавлены примеры для удобства.
- Исправлены существующие роуты `/bonds`, чтобы они корректно работали с БД.

---

## Stage 4 — Фоновые задачи (Celery + Redis)

На этом этапе добавлена интеграция с **Celery** для фонового обновления облигаций:

- `sync_bond_task` — синхронизация конкретного бонда по ISIN.
- `sync_all_bonds_task` — синхронизация всех бондов в базе.
- Тестовая задача `test_task_sleep` — имитация долгой работы.

---



## Stage 5 — Docker / docker-compose setup

Добавлены Dockerfile и docker-compose для разворачивания всего проекта:  
- `api` — FastAPI-приложение  
- `redis` — брокер для Celery  
- `worker` — Celery worker  
- `flower` — мониторинг задач

---

## Запуск проекта

### Локально (dev)
1. Установить зависимости:
   ```bash
   pip install -r requirements.txt
2. Применить миграции:
   ```bash
   alembic upgrade head
3. Запустить сервер:
   ```bash
   uvicorn app.main:app --reload
4. Документация доступна по адресу:
   ```bash
   http://127.0.0.1:8000/docs

### Запуск Celery

1. Запустить Redis (локально или в Docker):
   ```bash
   docker run -p 6379:6379 redis

2. Запустить Celery worker:
   ```bash
   celery -A app.celery_tasks.celery_app.celery worker --loglevel=info

3. (Опционально) Запустить Flower для мониторинга задач:
   ```bash
   celery -A app.celery_tasks.celery_app.celery flower --port=5555

### Запуск через Docker

1. Собрать и запустить контейнеры:
   ```bash
   docker-compose up --build
Приложение будет доступно:

- API: http://127.0.0.1:8000/docs
- Flower (мониторинг задач): http://127.0.0.1:5555

Для обновления всех облигаций:
- Вызвать ручку POST /tasks/sync_all в Swagger.