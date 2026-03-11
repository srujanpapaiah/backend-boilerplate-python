"""Unit tests for UserRepository."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.repositories.user import UserRepository
from tests.factories.user import create_test_user

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.unit


class TestUserRepository:
    async def test_get_by_email(self, db_session: AsyncSession) -> None:
        user = await create_test_user(db_session, email="repo@example.com")
        repo = UserRepository(db_session)
        found = await repo.get_by_email("repo@example.com")
        assert found is not None
        assert found.id == user.id

    async def test_get_by_email_not_found(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        found = await repo.get_by_email("nonexistent@example.com")
        assert found is None

    async def test_create(self, db_session: AsyncSession) -> None:
        repo = UserRepository(db_session)
        user = await repo.create(
            email="created@example.com",
            hashed_password="hashed",
            full_name="Created User",
        )
        assert user.id is not None
        assert user.email == "created@example.com"

    async def test_delete(self, db_session: AsyncSession) -> None:
        user = await create_test_user(db_session, email="del_repo@example.com")
        repo = UserRepository(db_session)
        result = await repo.delete(user.id)
        assert result is True
        assert await repo.get_by_id(user.id) is None
