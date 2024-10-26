from __future__ import annotations

from typing import TYPE_CHECKING

from AFAAS.interfaces.db.db import AbstractMemory

if TYPE_CHECKING:
    from AFAAS.interfaces.db.db_table import AbstractTable


class NoSQLMemory(AbstractMemory):
    async def get_table(self, table_name: str) -> AbstractTable:
        if self.__class__ == NoSQLMemory:
            raise TypeError(
                "get_table method cannot be called on NoSQLMemory class directly"
            )
        return await super().get_table(table_name)
