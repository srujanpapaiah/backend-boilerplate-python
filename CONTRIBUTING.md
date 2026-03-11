# Contributing Guide

Thank you for contributing! This document covers the conventions and workflow for this project.

## Development Setup

```bash
git clone <repo-url>
cd <repo>
cp .env.example .env
make dev           # Install deps + pre-commit hooks
make docker-up     # Start Postgres + Redis
make migrate       # Apply migrations
make run           # Start dev server
```

## Workflow

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make your changes following the architecture patterns (see README).

3. Add tests for your changes.

4. Run checks locally:
   ```bash
   make lint    # Must pass
   make test    # Must pass with 80%+ coverage
   ```

5. Commit with a descriptive message following [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   feat: add user profile picture upload
   fix: handle null email in registration
   docs: update API response examples
   refactor: extract auth middleware
   test: add integration tests for payments
   ```

6. Push and open a Pull Request against `main`.

## Code Standards

- **Type annotations** on all functions (use `from __future__ import annotations`)
- **Async/await** for all I/O operations
- **Structured logging** via structlog — no `print()`
- **Domain exceptions** — raise from `src/core/exceptions.py`
- **Repository pattern** — all SQL in `src/repositories/`
- **Pydantic v2** schemas for all API inputs/outputs
- **Tests required** for all new features and bug fixes

## Architecture

```
Endpoint → Service → Repository → Model
   ↑           ↑          ↑
 Schema    Exception    DB Session
```

- **Endpoints**: Parse HTTP, call service, return response
- **Services**: Business logic, validation, orchestration
- **Repositories**: Data access, queries
- **Models**: ORM definitions

## Testing

```bash
make test              # All tests
make test-unit         # Unit tests only (fast)
make test-integration  # Integration tests (needs DB)
```

- Unit tests go in `tests/unit/` and should mock external dependencies
- Integration tests go in `tests/integration/` and use the test database
- Use factories from `tests/factories/` to create test data
- All tests must have `@pytest.mark.unit` or `@pytest.mark.integration` markers

## Review Checklist

Before requesting review, verify:

- [ ] Code follows the project architecture
- [ ] Type annotations are complete
- [ ] Tests are written and passing
- [ ] Linter and type checker pass (`make lint`)
- [ ] Migration created if schema changed
- [ ] No hardcoded configuration values
- [ ] No `print()` statements
- [ ] API docs are up to date (check `/docs`)
