"""Shared FastAPI dependencies used across the application."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import Settings, get_settings
from src.core.exceptions import UnauthorizedError
from src.core.security import decode_token
from src.db.session import get_db_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
TokenStr = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user_id(token: TokenStr) -> int:
    payload = decode_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError(message="Invalid token payload")
    return int(user_id)


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
