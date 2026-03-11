"""User service — business logic for user operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.exceptions import ConflictError, NotFoundError
from src.core.security import hash_password
from src.repositories.user import UserRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from src.models.user import User


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)

    async def create_user(self, *, email: str, password: str, full_name: str | None = None) -> User:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise ConflictError(f"User with email '{email}' already exists")
        return await self.repo.create(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
        )

    async def get_user(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User", user_id)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.repo.get_by_email(email)

    async def list_users(self, *, skip: int = 0, limit: int = 100) -> list[User]:
        users = await self.repo.get_all(skip=skip, limit=limit)
        return list(users)

    async def update_user(self, user_id: int, **kwargs: object) -> User:
        if "password" in kwargs:
            kwargs["hashed_password"] = hash_password(str(kwargs.pop("password")))
        user = await self.repo.update(user_id, **kwargs)
        if user is None:
            raise NotFoundError("User", user_id)
        return user

    async def delete_user(self, user_id: int) -> None:
        deleted = await self.repo.delete(user_id)
        if not deleted:
            raise NotFoundError("User", user_id)
