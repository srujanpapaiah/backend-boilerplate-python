"""Aggregate all v1 endpoint routers."""

from __future__ import annotations

from fastapi import APIRouter

from src.api.v1.endpoints import auth, health, users

api_v1_router = APIRouter()

api_v1_router.include_router(health.router)
api_v1_router.include_router(auth.router)
api_v1_router.include_router(users.router)
