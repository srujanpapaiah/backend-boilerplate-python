"""Shared schema primitives reused across all API versions."""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict

DataT = TypeVar("DataT")


class APIResponse[DataT](BaseModel):
    """Standard envelope for successful responses."""

    data: DataT
    message: str = "Success"


class PaginatedResponse[DataT](BaseModel):
    """Paginated list envelope."""

    data: list[DataT]
    total: int
    skip: int
    limit: int


class ErrorDetail(BaseModel):
    message: str
    status_code: int
    detail: Any = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    version: str
    environment: str
