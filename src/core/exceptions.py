"""Centralized exception hierarchy and FastAPI exception handlers.

All domain exceptions inherit from AppError so they can be handled
uniformly by the global exception handler middleware.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.logging import get_logger

logger = get_logger(__name__)


# ── Base Exceptions ──────────────────────────────────────────────────────────


class AppError(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(message)


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str = "Resource", identifier: Any = None) -> None:
        detail = f"{resource} not found" if identifier is None else f"{resource} with id '{identifier}' not found"
        super().__init__(message=detail, status_code=status.HTTP_404_NOT_FOUND)


class ConflictError(AppError):
    """Raised when a uniqueness constraint is violated."""

    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT)


class UnauthorizedError(AppError):
    """Raised when authentication fails or is missing."""

    def __init__(self, message: str = "Not authenticated") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(AppError):
    """Raised when the user lacks required permissions."""

    def __init__(self, message: str = "Not enough permissions") -> None:
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN)


class BadRequestError(AppError):
    """Raised for invalid client input that doesn't fit validation."""

    def __init__(self, message: str = "Bad request", detail: Any = None) -> None:
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class RateLimitExceededError(AppError):
    """Raised when a client exceeds the rate limit."""

    def __init__(self, retry_after: int = 60) -> None:
        super().__init__(
            message="Rate limit exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers={"Retry-After": str(retry_after)},
        )


# ── Exception Handlers ──────────────────────────────────────────────────────


def _error_response(
    status_code: int,
    message: str,
    detail: Any = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {"error": {"message": message, "status_code": status_code}}
    if detail is not None:
        body["error"]["detail"] = detail
    return JSONResponse(status_code=status_code, content=body, headers=headers)


def register_exception_handlers(app: FastAPI) -> None:
    """Wire global exception handlers into the FastAPI application."""

    @app.exception_handler(AppError)
    async def app_exception_handler(_request: Request, exc: AppError) -> JSONResponse:
        logger.warning("app_exception", message=exc.message, status_code=exc.status_code)
        return _error_response(exc.status_code, exc.message, exc.detail, exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning("validation_error", errors=exc.errors())
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Validation error",
            detail=exc.errors(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", exc_info=exc)
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Internal server error",
        )
