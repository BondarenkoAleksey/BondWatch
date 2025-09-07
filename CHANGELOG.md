# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]
- MOEX API integration (bonds quotes, parameters)
- Background updates with Celery
- Docker setup
- Telegram notifications

---

## [0.2.0] - 2025-09-07
### Added
- Project restructured into `app/` (routers, models, schemas, database, crud).
- SQLAlchemy integration with SQLite.
- Alembic initialized with first migration (`bonds` table).
- CRUD operations for bonds via API.

---

## [0.1.0] - 2025-09-06
### Added
- Initial FastAPI app with in-memory storage.
- Endpoints:
  - `GET /bonds` — list of fake bonds
  - `POST /bonds` — add bond
  - `GET /bonds/{isin}` — get bond by ISIN
  - `PATCH /bonds/{isin}` — update bond
  - `GET /bonds/search` — filter by yield
