"""Health-check endpoints for load balancers and orchestrators."""

from __future__ import annotations

from fastapi import APIRouter, status

from src.api.v1.schemas.common import HealthResponse
from src.config import get_settings

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
)
async def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get(
    "/ready",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
)
async def readiness_check() -> HealthResponse:
    """Check that downstream dependencies (DB, Redis) are reachable."""
    settings = get_settings()
    # In production, add actual DB/Redis connectivity checks here
    return HealthResponse(
        status="ready",
        version=settings.app_version,
        environment=settings.environment,
    )
