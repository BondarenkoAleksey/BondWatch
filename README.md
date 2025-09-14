# BondWatch

Учебный проект для работы с облигациями и данными Московской биржи (MOEX) на базе **FastAPI**.  
Проект развивается пошагово — каждая итерация добавляет новый инструмент или функциональность.  

---

## Roadmap
- **Stage 1:** Basic FastAPI app with fake in-memory bonds (✅ done)
- **Stage 2:** Add SQLAlchemy + Alembic migrations (✅ done)
- **Stage 3:** Integrate MOEX API (🚧 in progress)
- **Stage 4:** Celery + Redis for background tasks
- **Stage 5:** Docker / docker-compose setup
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
