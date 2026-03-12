# AGENTS.md

## Cursor Cloud specific instructions

### Services overview

| Service | Purpose | How to start |
|---------|---------|-------------|
| **FastAPI app** | Main API server | `make run` (port 8000) |
| **PostgreSQL 16** | Primary database | `docker run -d --name postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=app_db -p 5432:5432 postgres:16-alpine` |
| **Redis 7** | Optional (no active usage in src/) | Not required for dev/test |

### Quick start after VM provisioning

1. Ensure Docker is running and start PostgreSQL (see above).
2. Copy `.env.example` to `.env` and set `SECRET_KEY` (use `make generate-key`).
3. Run migrations: `make migrate`. If `alembic/versions/` is empty, create the initial migration first with `make migrate-create MSG="initial schema"`.
4. Start the dev server: `make run` — Swagger UI at http://localhost:8000/docs.

### Non-obvious caveats

- **Tests do NOT need PostgreSQL or Docker.** They use in-memory SQLite via `aiosqlite`. Just `make test` works with zero external services.
- **Pre-commit install** may fail if `core.hooksPath` is set in git config. Fix with `git config --unset-all core.hooksPath` before `make dev`.
- **Login response** returns `access_token`/`refresh_token` at the top level (not nested under `data`), unlike other endpoints which wrap in `{"data": ..., "message": ...}`.
- All common dev commands are documented in `CLAUDE.md` and the `Makefile`.
