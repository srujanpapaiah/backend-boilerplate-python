"""User CRUD endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query, status

from src.api.v1.schemas.common import APIResponse, PaginatedResponse
from src.api.v1.schemas.users import UserResponse, UserUpdate
from src.core.dependencies import CurrentUserId, DbSession
from src.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Get current authenticated user",
)
async def get_me(user_id: CurrentUserId, session: DbSession) -> APIResponse[UserResponse]:
    svc = UserService(session)
    user = await svc.get_user(user_id)
    return APIResponse(data=UserResponse.model_validate(user))


@router.patch(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Update current user profile",
)
async def update_me(
    body: UserUpdate,
    user_id: CurrentUserId,
    session: DbSession,
) -> APIResponse[UserResponse]:
    svc = UserService(session)
    update_data = body.model_dump(exclude_unset=True)
    user = await svc.update_user(user_id, **update_data)
    return APIResponse(data=UserResponse.model_validate(user), message="Profile updated")


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="List all users (admin)",
)
async def list_users(
    _user_id: CurrentUserId,
    session: DbSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[UserResponse]:
    svc = UserService(session)
    users = await svc.list_users(skip=skip, limit=limit)
    return PaginatedResponse(
        data=[UserResponse.model_validate(u) for u in users],
        total=len(users),
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{user_id}",
    response_model=APIResponse[UserResponse],
    summary="Get a user by ID",
)
async def get_user(
    user_id: int,
    _current_user_id: CurrentUserId,
    session: DbSession,
) -> APIResponse[UserResponse]:
    svc = UserService(session)
    user = await svc.get_user(user_id)
    return APIResponse(data=UserResponse.model_validate(user))


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user (admin)",
)
async def delete_user(
    user_id: int,
    _current_user_id: CurrentUserId,
    session: DbSession,
) -> None:
    svc = UserService(session)
    await svc.delete_user(user_id)
