"""User CRUD endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Query, status

from src.api.v1.schemas.common import APIResponse, PaginatedResponse
from src.api.v1.schemas.users import UserResponse, UserUpdate
from src.core.dependencies import CurrentUserId, DbSession, SuperuserId
from src.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Get current authenticated user",
)
async def get_me(user_id: CurrentUserId, session: DbSession) -> APIResponse[UserResponse]:
    """Return the profile of the currently authenticated user."""
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
    """Update the profile of the currently authenticated user."""
    svc = UserService(session)
    update_data = body.model_dump(exclude_unset=True)
    user = await svc.update_user(user_id, **update_data)
    return APIResponse(data=UserResponse.model_validate(user), message="Profile updated")


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="List all users (superuser only)",
)
async def list_users(
    _admin_id: SuperuserId,
    session: DbSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[UserResponse]:
    """List all users. Requires superuser privileges."""
    svc = UserService(session)
    users = await svc.list_users(skip=skip, limit=limit)
    total = await svc.count_users()
    return PaginatedResponse(
        data=[UserResponse.model_validate(u) for u in users],
        total=total,
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
    """Get a specific user by ID. Requires authentication."""
    svc = UserService(session)
    user = await svc.get_user(user_id)
    return APIResponse(data=UserResponse.model_validate(user))


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user (superuser only)",
)
async def delete_user(
    user_id: int,
    _admin_id: SuperuserId,
    session: DbSession,
) -> None:
    """Delete a user account. Requires superuser privileges."""
    svc = UserService(session)
    await svc.delete_user(user_id)
