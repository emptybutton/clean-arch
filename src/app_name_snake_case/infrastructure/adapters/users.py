from dataclasses import dataclass
from uuid import UUID

from in_memory_db import InMemoryDb
from sqlalchemy.ext.asyncio import AsyncSession

from app_name_snake_case.application.ports.users import Users
from app_name_snake_case.entities.core.user import User
from app_name_snake_case.infrastructure.sqlalchemy import orm  # noqa: F401


@dataclass(frozen=True)
class InMemoryUsers(Users):
    db: InMemoryDb

    async def user_with_id(self, id_: UUID) -> User | None:
        return self.db.subset(User).select_one(lambda user: user.id == id_)


@dataclass(frozen=True)
class InPostgresUsers(Users):
    session: AsyncSession

    async def user_with_id(self, id_: UUID) -> User | None:
        return await self.session.get(User, id_)
