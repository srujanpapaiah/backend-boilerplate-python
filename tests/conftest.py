"""Shared test fixtures.

Uses an in-memory SQLite database for fast, isolated tests.
Each test function gets its own database session that is rolled back.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import Settings, get_settings
from src.core.security import create_access_token
from src.db.session import get_db_session
from src.models.base import Base

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


def get_test_settings() -> Settings:
    return Settings(
        environment="testing",
        database_url="sqlite+aiosqlite:///",
        secret_key="test-secret-key",
        debug=True,
    )


@pytest.fixture(scope="session")
def event_loop():
    """Use a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return get_test_settings()


@pytest.fixture(scope="session")
async def test_engine(test_settings: Settings):
    engine = create_async_engine(test_settings.database_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession, test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    from src.app import create_app

    get_settings.cache_clear()

    app = create_app()

    async def _override_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override_db
    app.dependency_overrides[get_settings] = lambda: test_settings

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Generate authorization headers for a test user with id=1."""
    token = create_access_token(subject=1)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def make_auth_headers():
    """Factory fixture to generate auth headers for any user id."""

    def _make(user_id: int, **extra_claims: Any) -> dict[str, str]:
        token = create_access_token(subject=user_id, extra_claims=extra_claims or None)
        return {"Authorization": f"Bearer {token}"}

    return _make
