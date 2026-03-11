"""Integration tests for authentication endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.factories.user import create_test_user

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = pytest.mark.integration


class TestAuthEndpoints:
    async def test_register(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "register@example.com",
                "password": "securepassword123",
                "full_name": "New User",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["data"]["email"] == "register@example.com"
        assert body["message"] == "User created successfully"

    async def test_register_duplicate_email(self, client: AsyncClient, db_session) -> None:
        await create_test_user(db_session, email="dup_auth@example.com")
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "dup_auth@example.com", "password": "securepassword123"},
        )
        assert response.status_code == 409

    async def test_login(self, client: AsyncClient, db_session) -> None:
        await create_test_user(db_session, email="login@example.com", password="testpassword")
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "testpassword"},
        )
        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

    async def test_login_invalid_credentials(self, client: AsyncClient) -> None:
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
