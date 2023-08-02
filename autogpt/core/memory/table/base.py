from __future__ import annotations

import abc
import uuid
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from autogpt.core.memory.base import NewMemory


class BaseTable(abc.ABC):
    def __init__(self, memory=NewMemory):
        self.memory = memory

    def add(self, value: dict) -> uuid:
        id = uuid.uuid4()
        value["id"] = id
        self.memory.save(key=id, value=value)
        return id

    def get(self, id: uuid) -> Any:
        return self.memory.data[id]

    def update(self, id: uuid, value: dict):
        self.memory.data[id] = value
        self.memory.save(key=id, value=value)

    def delete(self, id: uuid):
        del self.memorydata[id]
        self.memory.delete(id)


class AgentsTable(BaseTable):
    def update(self, agent):
        # NOTE : overwrite parent update # Perform any custom logic needed for adding an agent
        super().add(agent)


class MessagesTable(BaseTable):
    pass


class UsersTable(BaseTable):
    pass
