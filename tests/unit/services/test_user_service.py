"""Unit tests for UserService."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from src.core.exceptions import ConflictError, NotFoundError
from src.services.user import UserService
from tests.factories.user import create_test_user

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.unit


class TestUserService:
    async def test_create_user(self, db_session: AsyncSession) -> None:
        svc = UserService(db_session)
        user = await svc.create_user(email="new@example.com", password="password123")
        assert user.email == "new@example.com"
        assert user.hashed_password != "password123"

    async def test_create_user_duplicate_email_raises(self, db_session: AsyncSession) -> None:
        await create_test_user(db_session, email="dup@example.com")
        svc = UserService(db_session)
        with pytest.raises(ConflictError):
            await svc.create_user(email="dup@example.com", password="password123")

    async def test_get_user(self, db_session: AsyncSession) -> None:
        user = await create_test_user(db_session, email="get@example.com")
        svc = UserService(db_session)
        found = await svc.get_user(user.id)
        assert found.id == user.id

    async def test_get_user_not_found_raises(self, db_session: AsyncSession) -> None:
        svc = UserService(db_session)
        with pytest.raises(NotFoundError):
            await svc.get_user(99999)

    async def test_list_users(self, db_session: AsyncSession) -> None:
        await create_test_user(db_session, email="list1@example.com")
        await create_test_user(db_session, email="list2@example.com")
        svc = UserService(db_session)
        users = await svc.list_users()
        assert len(users) >= 2

    async def test_delete_user(self, db_session: AsyncSession) -> None:
        user = await create_test_user(db_session, email="delete@example.com")
        svc = UserService(db_session)
        await svc.delete_user(user.id)
        with pytest.raises(NotFoundError):
            await svc.get_user(user.id)
