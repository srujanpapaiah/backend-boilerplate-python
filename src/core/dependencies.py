"""Shared FastAPI dependencies used across the application."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.core.exceptions import ForbiddenError, UnauthorizedError
from src.core.security import decode_token
from src.db.session import get_db_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
TokenStr = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user_id(token: TokenStr) -> int:
    """Extract and validate the current user ID from a JWT access token.

    Rejects refresh tokens to prevent their use on protected endpoints.
    """
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise UnauthorizedError(message="Access token required")
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError(message="Invalid token payload")
    try:
        return int(user_id)
    except (ValueError, TypeError) as e:
        raise UnauthorizedError(message="Invalid token payload") from e


async def require_superuser(user_id: CurrentUserId, session: DbSession) -> int:
    """Dependency that ensures the current user is a superuser."""
    from src.repositories.user import UserRepository

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None or not user.is_superuser:
        raise ForbiddenError(message="Superuser access required")
    return user_id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
SuperuserId = Annotated[int, Depends(require_superuser)]
