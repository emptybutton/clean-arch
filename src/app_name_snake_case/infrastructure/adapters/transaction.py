from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager

from in_memory_db import InMemoryDb
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def in_postgres_transaction(session: AsyncSession) -> AsyncIterator[None]:
    async with session.begin():
        yield


@asynccontextmanager
async def in_memory_transaction(  # noqa: RUF029
    dbs: Sequence[InMemoryDb],
) -> AsyncIterator[None]:
    for db in dbs:
        db.begin()

    try:
        yield
    except Exception as error:
        for db in dbs:
            db.rollback()
        raise error from error
    else:
        for db in dbs:
            db.commit()
