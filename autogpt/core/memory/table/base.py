from __future__ import annotations

import abc
import uuid
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from autogpt.core.memory.base import NewMemory


# TODO : Adopt Configurable ?
class BaseTable(abc.ABC, BaseModel):
    table_name: str = Field(default_factory=lambda: "")
    memory: NewMemory

    def __init__(self, memory=NewMemory):
        self.memory = memory

    def add(self, value: dict) -> uuid:
        id = uuid.uuid4()
        value["id"] = id
        self.memory.add(key=id, value=value, table_name=self.table_name)
        return id

    def get(self, id: uuid) -> Any:
        return self.memory.get(key=id, table_name=self.table_name)

    def update(self, id: uuid, value: dict):
        self.memory.update(key=id, value=value, table_name=self.table_name)

    def delete(self, id: uuid):
        self.memory.delete(id, table_name=self.table_name)


class AgentsTable(BaseTable):
    table_name = "agents"

    def update(self, id : uuid, value :  dict ):
        # NOTE : overwrite parent update 
        # # Perform any custom logic needed for updating an agent
        super().update( id =  id , value = value )


class MessagesTable(BaseTable):
    table_name = "messages_history"


class UsersTable(BaseTable):
    table_name = "users"
