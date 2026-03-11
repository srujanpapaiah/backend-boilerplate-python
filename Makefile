.PHONY: help install dev run test lint format migrate docker-up docker-down clean seed

PYTHON := python3
UV := uv

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─── Setup ──────────────────────────────────────────────────────────────────────

install: ## Install production dependencies
	$(UV) sync --no-dev

dev: ## Install all dependencies including dev
	$(UV) sync
	$(UV) run pre-commit install

# ─── Development ────────────────────────────────────────────────────────────────

run: ## Run the development server
	$(UV) run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run the production server with gunicorn
	$(UV) run gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker \
		--bind 0.0.0.0:8000 --access-logfile - --error-logfile -

shell: ## Open an IPython shell with app context
	$(UV) run ipython

# ─── Code Quality ───────────────────────────────────────────────────────────────

lint: ## Run all linters
	$(UV) run ruff check src tests
	$(UV) run ruff format --check src tests
	$(UV) run mypy src

format: ## Auto-format code
	$(UV) run ruff check --fix src tests
	$(UV) run ruff format src tests

check: lint test ## Run all checks (lint + test)

# ─── Testing ────────────────────────────────────────────────────────────────────

test: ## Run all tests
	$(UV) run pytest

test-unit: ## Run unit tests only
	$(UV) run pytest -m unit

test-integration: ## Run integration tests only
	$(UV) run pytest -m integration

test-cov: ## Run tests with coverage report
	$(UV) run pytest --cov-report=html
	@echo "Coverage report generated at htmlcov/index.html"

test-fast: ## Run tests in parallel
	$(UV) run pytest -n auto

# ─── Database ───────────────────────────────────────────────────────────────────

migrate: ## Run database migrations
	$(UV) run alembic upgrade head

migrate-down: ## Rollback last migration
	$(UV) run alembic downgrade -1

migrate-create: ## Create a new migration (usage: make migrate-create MSG="add users table")
	$(UV) run alembic revision --autogenerate -m "$(MSG)"

seed: ## Seed the database with sample data
	$(UV) run python scripts/seed.py

# ─── Docker ─────────────────────────────────────────────────────────────────────

docker-up: ## Start all services with Docker Compose
	docker compose up -d

docker-down: ## Stop all Docker services
	docker compose down

docker-build: ## Build the application Docker image
	docker compose build

docker-logs: ## View Docker logs
	docker compose logs -f app

docker-reset: ## Reset Docker environment (removes volumes)
	docker compose down -v && docker compose up -d

# ─── Utilities ──────────────────────────────────────────────────────────────────

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete 2>/dev/null || true
	rm -rf dist build *.egg-info

generate-key: ## Generate a secure secret key
	@openssl rand -hex 32
