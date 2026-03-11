# FastAPI Boilerplate

Enterprise-grade Python FastAPI boilerplate designed to be the starting point for production backend services. Built with patterns used at top tech companies.

## Features

- **FastAPI** with async support and automatic OpenAPI docs
- **Clean Architecture** — API / Service / Repository / Model layers
- **SQLAlchemy 2.x** async ORM with Alembic migrations
- **Pydantic v2** for request/response validation and settings
- **JWT Authentication** with access + refresh tokens
- **Structured Logging** via structlog (JSON in prod, pretty in dev)
- **Docker** multi-stage build with Compose for local development
- **CI/CD** with GitHub Actions (lint, test, security scan, Docker build)
- **Code Quality** — ruff (linting + formatting), mypy (strict), pre-commit hooks
- **Testing** — pytest-asyncio with factories, coverage enforcement (80%+)
- **Observability** — OpenTelemetry, Sentry, Prometheus-ready
- **Security** — CORS, security headers, rate limiting, secret detection
- **AI-Ready** — Cursor rules, Claude instructions, Copilot instructions, Windsurf rules

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Docker & Docker Compose (for databases)

### 1. Clone and install

```bash
git clone <repo-url> my-project
cd my-project
cp .env.example .env
make dev
```

### 2. Start infrastructure

```bash
make docker-up    # Starts PostgreSQL and Redis
```

### 3. Run migrations

```bash
make migrate
```

### 4. Start development server

```bash
make run
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API docs.

## Project Structure

```
.
├── src/
│   ├── main.py                 # App entry point
│   ├── app.py                  # App factory (create_app)
│   ├── config/
│   │   └── settings.py         # Pydantic-settings configuration
│   ├── core/
│   │   ├── security.py         # JWT & password hashing
│   │   ├── dependencies.py     # FastAPI DI type aliases
│   │   ├── exceptions.py       # Domain exception hierarchy
│   │   ├── middleware.py        # Request ID, timing, security headers
│   │   └── logging.py          # Structured logging setup
│   ├── api/
│   │   └── v1/
│   │       ├── router.py       # Aggregate v1 routers
│   │       ├── endpoints/      # Route handlers
│   │       └── schemas/        # Pydantic request/response models
│   ├── services/               # Business logic
│   ├── repositories/           # Data access layer
│   ├── models/                 # SQLAlchemy ORM models
│   └── db/
│       └── session.py          # Engine & session factory
├── tests/
│   ├── conftest.py             # Shared fixtures
│   ├── factories/              # Test data builders
│   ├── unit/                   # Fast isolated tests
│   ├── integration/            # API integration tests
│   └── e2e/                    # End-to-end tests
├── alembic/                    # Database migrations
├── scripts/                    # Utility scripts
├── .github/workflows/          # CI/CD pipelines
├── Dockerfile                  # Multi-stage production image
├── docker-compose.yml          # Local dev infrastructure
├── pyproject.toml              # Project config (deps, tools)
└── Makefile                    # Developer commands
```

## Development Commands

| Command | Description |
|---------|-------------|
| `make dev` | Install all dependencies + pre-commit hooks |
| `make run` | Start dev server with hot reload |
| `make lint` | Run ruff check + format check + mypy |
| `make format` | Auto-fix lint issues and format code |
| `make test` | Run all tests with coverage |
| `make test-unit` | Run unit tests only |
| `make test-integration` | Run integration tests only |
| `make migrate` | Apply database migrations |
| `make migrate-create MSG="..."` | Generate new migration |
| `make docker-up` | Start Docker services |
| `make docker-down` | Stop Docker services |
| `make clean` | Remove caches and build artifacts |

## Adding a New Feature

1. **Schema** — Define Pydantic models in `src/api/v1/schemas/`
2. **Model** — Create SQLAlchemy model in `src/models/`, import in `__init__.py`
3. **Repository** — Add data access in `src/repositories/`
4. **Service** — Add business logic in `src/services/`
5. **Endpoint** — Add route handler in `src/api/v1/endpoints/`
6. **Router** — Wire it in `src/api/v1/router.py`
7. **Migration** — `make migrate-create MSG="add feature"` then `make migrate`
8. **Tests** — Unit tests in `tests/unit/`, integration in `tests/integration/`
9. **Validate** — `make lint && make test`

## Configuration

All configuration is via environment variables. See `.env.example` for the full list.

Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | `development`, `staging`, `production`, `testing` |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Async PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `SECRET_KEY` | — | JWT signing key (generate with `make generate-key`) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |

## API Design

- All endpoints versioned under `/api/v1/`
- Consistent response envelopes:
  - Success: `{"data": ..., "message": "Success"}`
  - Paginated: `{"data": [...], "total": N, "skip": 0, "limit": 20}`
  - Error: `{"error": {"message": "...", "status_code": 400}}`
- JWT Bearer authentication on protected routes
- Health endpoints: `GET /api/v1/health` and `GET /api/v1/ready`

## Deployment

### Docker

```bash
docker compose up -d            # Local
docker build -t app:latest .    # Build production image
```

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Generate a strong `SECRET_KEY` (`make generate-key`)
- [ ] Configure real `DATABASE_URL` and `REDIS_URL`
- [ ] Set `CORS_ORIGINS` to your frontend domain(s)
- [ ] Configure `SENTRY_DSN` for error tracking
- [ ] Disable debug docs (automatic when `ENVIRONMENT=production`)
- [ ] Run behind a reverse proxy (nginx, AWS ALB, etc.)
- [ ] Set up log aggregation for JSON structured logs

## License

MIT
