"""Authentication endpoints — login, register, refresh."""

from __future__ import annotations

from fastapi import APIRouter, status

from src.api.v1.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from src.api.v1.schemas.common import APIResponse
from src.api.v1.schemas.users import UserCreate, UserResponse
from src.core.dependencies import DbSession
from src.services.auth import AuthService
from src.services.user import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(body: UserCreate, session: DbSession) -> APIResponse[UserResponse]:
    svc = UserService(session)
    user = await svc.create_user(email=body.email, password=body.password, full_name=body.full_name)
    return APIResponse(data=UserResponse.model_validate(user), message="User created successfully")


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Obtain access and refresh tokens",
)
async def login(body: LoginRequest, session: DbSession) -> TokenResponse:
    svc = AuthService(session)
    tokens = await svc.login(body.email, body.password)
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh an access token",
)
async def refresh_token(body: RefreshRequest, session: DbSession) -> TokenResponse:
    svc = AuthService(session)
    tokens = await svc.refresh(body.refresh_token)
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )
