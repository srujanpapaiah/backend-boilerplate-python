"""Seed the database with sample data for development.

Idempotent — skips users that already exist.
"""

from __future__ import annotations

import asyncio

from src.config import get_settings
from src.core.security import hash_password
from src.db.session import _get_session_factory
from src.models.user import User
from src.repositories.user import UserRepository

SEED_USERS = [
    {
        "email": "admin@example.com",
        "password": "admin123456",
        "full_name": "Admin User",
        "is_active": True,
        "is_superuser": True,
    },
    {
        "email": "user@example.com",
        "password": "user123456",
        "full_name": "Regular User",
        "is_active": True,
        "is_superuser": False,
    },
]


async def seed() -> None:
    settings = get_settings()
    if settings.is_production:
        msg = "Cannot seed in production"
        raise RuntimeError(msg)

    factory = _get_session_factory()
    async with factory() as session:
        repo = UserRepository(session)
        created = 0
        for user_data in SEED_USERS:
            existing = await repo.get_by_email(user_data["email"])
            if existing:
                print(f"  Skipping {user_data['email']} (already exists)")  # noqa: T201
                continue
            user = User(
                email=user_data["email"],
                hashed_password=hash_password(str(user_data["password"])),
                full_name=user_data.get("full_name"),
                is_active=user_data.get("is_active", True),
                is_superuser=user_data.get("is_superuser", False),
            )
            session.add(user)
            created += 1
        await session.commit()
        print(f"Seeded {created} new users ({len(SEED_USERS) - created} skipped)")  # noqa: T201


if __name__ == "__main__":
    asyncio.run(seed())
