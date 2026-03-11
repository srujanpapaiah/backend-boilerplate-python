"""Integration tests for health-check endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = pytest.mark.integration


class TestHealthEndpoints:
    async def test_health_returns_200(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "healthy"
        assert "version" in body

    async def test_readiness_returns_200(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/ready")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] in ("ready", "not_ready")
