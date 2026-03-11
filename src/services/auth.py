"""Authentication service — login, token refresh, registration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.exceptions import UnauthorizedError
from src.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from src.services.user import UserService

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class TokenPair:
    """Value object holding an access/refresh token pair."""

    __slots__ = ("access_token", "refresh_token", "token_type")

    def __init__(self, access_token: str, refresh_token: str) -> None:
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = "bearer"


class AuthService:
    """Handles login, token refresh, and credential verification."""

    def __init__(self, session: AsyncSession) -> None:
        self.user_service = UserService(session)

    async def login(self, email: str, password: str) -> TokenPair:
        """Authenticate a user by email/password and return a token pair."""
        user = await self.user_service.get_user_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedError(message="Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError(message="Account is disabled")
        return TokenPair(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def refresh(self, refresh_token: str) -> TokenPair:
        """Exchange a valid refresh token for a new token pair."""
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError(message="Invalid token type")
        user_id = payload.get("sub")
        if user_id is None:
            raise UnauthorizedError(message="Invalid token payload")
        user = await self.user_service.get_user(int(user_id))
        if not user.is_active:
            raise UnauthorizedError(message="Account is disabled")
        return TokenPair(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
