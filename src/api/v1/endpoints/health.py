"""Health-check endpoints for load balancers and orchestrators."""

from __future__ import annotations

from fastapi import APIRouter, status

from src.api.v1.schemas.common import HealthResponse
from src.config import get_settings
from src.core.dependencies import DbSession
from src.core.logging import get_logger

router = APIRouter(tags=["Health"])
logger = get_logger(__name__)


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
)
async def health_check() -> HealthResponse:
    """Lightweight liveness check — confirms the process is running."""
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
async def readiness_check(session: DbSession) -> HealthResponse:
    """Readiness probe — verifies the database connection is alive."""
    settings = get_settings()
    try:
        await session.execute(
            __import__("sqlalchemy").text("SELECT 1"),
        )
    except Exception:
        logger.warning("readiness_check_failed", exc_info=True)
        return HealthResponse(
            status="not_ready",
            version=settings.app_version,
            environment=settings.environment,
        )
    return HealthResponse(
        status="ready",
        version=settings.app_version,
        environment=settings.environment,
    )
