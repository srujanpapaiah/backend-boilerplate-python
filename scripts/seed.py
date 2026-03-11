"""Seed the database with sample data for development."""

from __future__ import annotations

import asyncio

from src.config import get_settings
from src.core.security import hash_password
from src.db.session import async_session_factory
from src.models.user import User


async def seed() -> None:
    settings = get_settings()
    if settings.is_production:
        msg = "Cannot seed in production"
        raise RuntimeError(msg)

    async with async_session_factory() as session:
        users = [
            User(
                email="admin@example.com",
                hashed_password=hash_password("admin123456"),
                full_name="Admin User",
                is_active=True,
                is_superuser=True,
            ),
            User(
                email="user@example.com",
                hashed_password=hash_password("user123456"),
                full_name="Regular User",
                is_active=True,
                is_superuser=False,
            ),
        ]
        session.add_all(users)
        await session.commit()
        print(f"Seeded {len(users)} users")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(seed())
