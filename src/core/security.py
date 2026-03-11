"""Authentication utilities — JWT token creation/verification and password hashing."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from src.config import get_settings
from src.core.exceptions import UnauthorizedError


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str | int, extra_claims: dict[str, Any] | None = None) -> str:
    """Create a short-lived JWT access token."""
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire, "type": "access"}
    if extra_claims:
        payload.update(extra_claims)
    encoded: str = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded


def create_refresh_token(subject: str | int) -> str:
    """Create a long-lived JWT refresh token."""
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    payload: dict[str, Any] = {"sub": str(subject), "exp": expire, "type": "refresh"}
    encoded: str = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return encoded


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token. Raises UnauthorizedError on failure."""
    settings = get_settings()
    try:
        payload: dict[str, Any] = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as e:
        raise UnauthorizedError(message="Invalid or expired token") from e
    return payload
