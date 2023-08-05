from __future__ import annotations

import abc
import uuid
from typing import TYPE_CHECKING

from autogpt.core.configuration import Configurable
from autogpt.core.memory.base import (
    Memory,
    MemoryAdapterType,
    MemorySettings,
    NewMemoryConfig,
)

if TYPE_CHECKING:
    from autogpt.core.memory.table.base import BaseTable



class NoSQLMemory(Memory, Configurable):
    default_settings = MemorySettings(
        name="new_memory",
        description="NewMemory is an abstract memory adapter design to interact with NoSQL back-end ",
        configuration= NewMemoryConfig(memory_adapter=MemoryAdapterType.JSON_FILE, json_file_path='path/to/json'),
    )

    """
    Abstract class representing a memory storage system for storing and retrieving data.

    To use a specific memory adapter, create a configuration dict specifying the desired
    memory_adapter. Currently, "json_file" and "redis" adapters are available.

    Example:
        config = {"memory_adapter": "json_file", "json_file_path": "~/auto-gpt/data/"}
        memory = NewMemory.get_adapter(config)

    After getting the memory adapter, you can connect to it using the `connect` method
    with any required parameters.

    After connecting, you can access individual tables using the `get_table` method,
    passing the desired table name as an argument.

    Example:
        # Assuming we have connected to the memory using `memory` variable
        agents_table = memory.get_table("agents")
        messages_table = memory.get_table("messages_history")
        users_table = memory.get_table("users")

    Note:
        The `NewMemory` class is an abstract class, and you should use one of its concrete
        subclasses like `JSONFileMemory` or `RedisMemory` for actual implementations.
    """

    # TABLE_CLASS = BaseTable


    def get_table(self, table_name: str) -> BaseTable:
        """
        Get an instance of the table with the specified table_name.

        Parameters:
            table_name (str): The name of the table to retrieve.

        Returns:
            BaseTable: An instance of the table with the specified table_name.

        Raises:
            ValueError: If the provided table_name is not recognized.

        Example:
            # Assuming we have connected to the memory using `memory` variable
            agents_table = memory.get_table("agents")
            messages_table = memory.get_table("messages_history")
            users_table = memory.get_table("users")
        """

        if self.__class__ == NoSQLMemory:
            raise TypeError(
                "get_table method cannot be called on NewMemory class directly"
            )

        if table_name == "agents":
            from autogpt.core.memory.table.base import AgentsTable
            returnvalue  = AgentsTable(memory=self)
            return AgentsTable(memory=self)
        elif table_name == "messages_history":
            from autogpt.core.memory.table.base import MessagesTable
            return MessagesTable(memory=self)
        elif table_name == "users_informations":
            from autogpt.core.memory.table.base import UsersInformationsTable
            return UsersInformationsTable(memory=self)
        # elif table_name == "users_agents":
        #     return UsersAgentsTable(memory=self)
        else:
            raise ValueError(f"Unknown table: {table_name}")

    @abc.abstractmethod
    def connect(self, *args, **kwargs):
        """
        Connect to the memory storage system.

        Implement this method to establish a connection to the desired memory storage system
        using any required parameters.

        Parameters:
            kwarg: Any required parameters for connecting to the memory storage system.

        Example:
            # Example implementation for JSONFileMemory
            def connect(self, json_file_path):
                # Implementation for connecting to JSON file memory storage
                pass
        """
        pass

    @abc.abstractmethod
    def get(self, key, table_name: str):
        pass

    @abc.abstractmethod
    def add(self, key: uuid, value: dict, table_name: str):
        pass

    @abc.abstractmethod
    def update(self, key: uuid, value: dict, table_name: str):
        pass

    @abc.abstractmethod
    def delete(self, key, table_name: str):
        pass

    @abc.abstractmethod
    def list(self, table_name: str) -> dict:
        pass
