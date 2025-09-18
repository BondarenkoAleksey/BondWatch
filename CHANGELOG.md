# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.6.1] — 2025-09-18
### Added
- Integration with Tinkoff Invest API:
  - Fetching user accounts list.
  - Displaying portfolio (via API and Telegram bot).
- New Telegram bot command `/portfolio`.
- Support for environment variable `TINKOFF_INVEST_TOKEN`.

---

## [0.6.0] - 2025-09-17
### Added
- Telegram bot integration with /start, /sync_all, /bond commands
- Docker service for the bot
- Environment variable TELEGRAM_TOKEN support

---

## [0.5.0] - 2025-09-16
### Added
- Dockerfile для FastAPI-приложения
- docker-compose с сервисами:
  - `api` (FastAPI)
  - `redis` (брокер Redis)
  - `worker` (Celery worker)
  - `flower` (мониторинг фоновых задач через Flower)
- Инструкции в README по запуску проекта через Docker

---

## [0.4.0] - 2025-09-15
### Added
- **Celery + Redis** integration for background tasks:
  - `sync_bond_task` — update a single bond by ISIN
  - `sync_all_bonds_task` — update all bonds in DB
  - test task `test_task_sleep` for simulating long-running jobs
- New router `/tasks` to trigger background jobs via API
- Celery worker & Flower launch instructions in README

---

## [0.3.0] - 2025-09-14
### Added
- MOEX API integration:
  - `GET /moex/bonds/{isin}` — get bond data from MOEX by ISIN
  - `POST /moex/bonds/{isin}/sync` — sync bond and coupon schedule from MOEX to local DB
  - `GET /moex/bonds/{isin}/coupons` — get coupons for a bond from MOEX
- `/bonds/upcoming_coupons` endpoint — get bonds with upcoming coupons from local database
- Swagger request body examples added for relevant POST/PATCH routes
- Fixed `/bonds` endpoints for proper creation, patching, and validation

---

## [0.2.0] - 2025-09-07
### Added
- Project restructured into `app/` (routers, models, schemas, database, crud)
- SQLAlchemy integration with SQLite
- Alembic initialized with first migration (`bonds` table)
- CRUD operations for bonds via API

---

## [0.1.0] - 2025-09-06
### Added
- Initial FastAPI app with in-memory storage
- Endpoints:
  - `GET /bonds` — list of fake bonds
  - `POST /bonds` — add bond
  - `GET /bonds/{isin}` — get bond by ISIN
  - `PATCH /bonds/{isin}` — update bond
  - `GET /bonds/search` — filter by yield
