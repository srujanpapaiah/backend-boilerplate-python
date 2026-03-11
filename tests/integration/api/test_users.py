"""Integration tests for user endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.factories.user import create_test_user

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = pytest.mark.integration


class TestUserEndpoints:
    async def test_get_me_unauthenticated(self, client: AsyncClient) -> None:
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401

    async def test_get_me(self, client: AsyncClient, db_session, make_auth_headers) -> None:
        user = await create_test_user(db_session, email="me@example.com")
        headers = make_auth_headers(user.id)
        response = await client.get("/api/v1/users/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["data"]["email"] == "me@example.com"

    async def test_update_me(self, client: AsyncClient, db_session, make_auth_headers) -> None:
        user = await create_test_user(db_session, email="update_me@example.com")
        headers = make_auth_headers(user.id)
        response = await client.patch(
            "/api/v1/users/me",
            json={"full_name": "Updated Name"},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["data"]["full_name"] == "Updated Name"

    async def test_list_users(self, client: AsyncClient, db_session, make_auth_headers) -> None:
        user = await create_test_user(db_session, email="listuser@example.com")
        headers = make_auth_headers(user.id)
        response = await client.get("/api/v1/users", headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert "data" in body
        assert isinstance(body["data"], list)
