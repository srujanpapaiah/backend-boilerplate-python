"""User test factories for generating test data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.security import hash_password
from src.models.user import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


def build_user(
    *,
    user_id: int | None = None,
    email: str = "test@example.com",
    password: str = "securepassword123",
    full_name: str | None = "Test User",
    is_active: bool = True,
    is_superuser: bool = False,
) -> User:
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        is_active=is_active,
        is_superuser=is_superuser,
    )
    if user_id is not None:
        user.id = user_id
    return user


async def create_test_user(session: AsyncSession, **kwargs: object) -> User:
    user = build_user(**kwargs)  # type: ignore[arg-type]
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user
