"""Generic async repository implementing common CRUD operations.

Inherit from this class and specify the SQLAlchemy model to get free
create / get / list / update / delete operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from sqlalchemy import func, select

from src.models.base import Base

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository[ModelT: Base]:
    """Base CRUD repository with deterministic pagination."""

    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, obj_id: int) -> ModelT | None:
        """Fetch a single record by primary key."""
        return await self.session.get(self.model, obj_id)

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> Sequence[ModelT]:
        """Fetch a page of records, ordered by ID for stable pagination."""
        stmt = select(self.model).order_by(self.model.id).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self) -> int:
        """Return the total number of records."""
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def create(self, **kwargs: Any) -> ModelT:
        """Insert a new record and return it with DB-generated fields."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, obj_id: int, **kwargs: Any) -> ModelT | None:
        """Update a record by ID and return the updated instance."""
        instance = await self.get_by_id(obj_id)
        if instance is None:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, obj_id: int) -> bool:
        """Delete a record by ID. Returns True if deleted, False if not found."""
        instance = await self.get_by_id(obj_id)
        if instance is None:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True
