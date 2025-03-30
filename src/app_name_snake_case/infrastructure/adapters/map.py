from dataclasses import dataclass

from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app_name_snake_case.application.ports.map import (
    Map,
    MappableEntityLifeCycle,
    NotUniqueUserNameError,
)


@dataclass(kw_only=True, frozen=True, slots=True)
class MapToPostgres(Map):
    session: AsyncSession

    async def __call__(
        self,
        effect: MappableEntityLifeCycle,
    ) -> None:
        """
        :raises app_name_snake_case.application.ports.map.NotUniqueUserNameError:
        """  # noqa: E501

        self.session.add_all(effect.new_values)
        self.session.add_all(effect.translated_values)

        for mutated_value in effect.mutated_values:
            await self.session.merge(mutated_value, load=False)

        for dead_value in effect.dead_values:
            await self.session.delete(dead_value)

        try:
            await self.session.flush()
        except IntegrityError as error:
            self._handle_integrity_error(error)
            raise error from error

    def _handle_integrity_error(self, error: IntegrityError) -> None:
        if isinstance(error.orig, UniqueViolation):
            table_name = error.orig.diag.table_name
            column_name = error.orig.diag.column_name

            if table_name == "user_table" and column_name == "name":
                raise NotUniqueUserNameError from error
