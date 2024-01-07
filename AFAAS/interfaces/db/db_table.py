from __future__ import annotations

import abc
import uuid
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, TypedDict, Union

if TYPE_CHECKING:
    from AFAAS.interfaces.db.db import AbstractMemory


class AbstractTable(abc.ABC):
    class Operators(Enum):
        GREATER_THAN = lambda x, y: x > y
        LESS_THAN = lambda x, y: x < y
        EQUAL_TO = lambda x, y: x == y
        GREATER_THAN_OR_EQUAL = lambda x, y: x >= y
        IN_LIST = lambda x, y: x in y
        NOT_IN_LIST = lambda x, y: x not in y
        LESS_THAN_OR_EQUAL = lambda x, y: x <= y
        NOT_EQUAL_TO = lambda x, y: x != y

    class ComparisonOperator(Callable[[Any, Any], bool]):
        pass

    class FilterItem(TypedDict):
        value: Any
        operator: Union[AbstractTable.ComparisonOperator, AbstractTable.Operators]

    # NOTE : Change str as key as value from an enum of column provided by the model class provided by the table class (headache :))
    # BaseModel to require a column description Enum
    # CustomTable to reference the Enum/Model
    # FilterDict probably to be defined in the CustomTable class (Enforce via abc or pydantic)
    class FilterDict(dict[str, list[FilterItem]]):
        pass

    table_name: str
    db: AbstractMemory
    primary_key: str

    def __init__(self, db: AbstractMemory) -> None:
        self.db = db

    @abc.abstractmethod
    async def add(self, value: dict) -> uuid.UUID:
        ...

    @abc.abstractmethod
    async def get(self, key: Any) -> Any:
        ...

    @abc.abstractmethod
    async def update(self, id: uuid, value: dict):
        ...

    @abc.abstractmethod
    async def delete(self, id: uuid):
        ...

    @abc.abstractmethod
    async def list(
        self,
        filter: AbstractTable.FilterDict = {},
        order_column: Optional[str] = "modified_at",
        order_direction: Literal["asc", "desc"] = "desc",
    ) -> list[dict[str, Any]]:
        ...
