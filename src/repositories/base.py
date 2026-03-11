"""Generic async repository implementing common CRUD operations.

Inherit from this class and specify the SQLAlchemy model to get free
create / get / list / update / delete operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from sqlalchemy import select

from src.models.base import Base

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository[ModelT: Base]:
    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    async def get_by_id(self, obj_id: int) -> ModelT | None:
        return await self.session.get(self.model, obj_id)

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> Sequence[ModelT]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, **kwargs: Any) -> ModelT:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, obj_id: int, **kwargs: Any) -> ModelT | None:
        instance = await self.get_by_id(obj_id)
        if instance is None:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, obj_id: int) -> bool:
        instance = await self.get_by_id(obj_id)
        if instance is None:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True
