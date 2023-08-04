from __future__ import annotations

import abc
import uuid
from logging import Logger
from typing import TYPE_CHECKING, Enum

from pydantic import BaseModel, Field

from autogpt.core.configuration import Configurable
from autogpt.core.memory import BaseTable, JSONFileMemory

if TYPE_CHECKING:
    from autogpt.core.memory.table.base import (
        AgentsTable,
        MessagesTable,
        UsersInformationsTable,
    )


class MemoryAdapterType(Enum):
    JSON_FILE = "json_file"
    REDIS = "redis"


class NewMemoryConfig(BaseModel):
    """
    Configuration class representing the parameters for creating a NewMemory adapter.

    Attributes:
        memory_adapter (MemoryAdapterType): The type of memory adapter to use.
        json_file_path (str): The file path for the JSON file when using the JSONFileMemory adapter.
        # Add other parameters for different memory adapters as needed.
    """

    memory_adapter: MemoryAdapterType = Field(
        ..., description="The type of memory adapter to use."
    )
    json_file_path: str = Field(
        ...,
        description="The file path for the JSON file when using the JSONFileMemory adapter.",
    )
    # Add other parameters for different memory adapters as needed.


class NewMemory(Configurable):

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

    @abc.abstractmethod
    def __init__(self):
        pass

    @classmethod
    def get_adapter(
        cls, config: NewMemoryConfig, logger=Logger, *args, **kwargs
    ) -> "NewMemory":
        """
        Get an instance of a memory adapter based on the provided configuration.

        Parameters:
            config (dict): Configuration dict specifying the memory_adapter type and
                           any required parameters for that adapter.
            logger (Logger, optional): The logger instance to use for logging messages.
                                       Default: Logger.

        Returns:
            NewMemory: An instance of the memory adapter based on the provided configuration.

        Raises:
            ValueError: If an invalid memory_adapter type is provided in the configuration.

        Example:
            config = {"memory_adapter": "json_file", "json_file_path": "~/auto-gpt/data/"}
            memory = NewMemory.get_adapter(config)
        """

        # TODO : Not yet integrated, For test purposes
        config = NewMemoryConfig(
            memory_adapter=MemoryAdapterType.JSON_FILE,
            json_file_path="~/auto-gpt/data/",
        )

        if config.memory_adapter == "json_file":
            return JSONFileMemory(config=config, logger=logger)
        elif config.memory_adapter == "redis":
            raise NotImplementedError()
        else:
            raise ValueError("Invalid animal type")

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
        if isinstance(self, NewMemory):
            raise TypeError(
                "get_table method cannot be called on NewMemory class directly"
            )

        if table_name == "agents":
            return AgentsTable(memory=self)
        if table_name == "agents":
            return AgentsTable(memory=self)
        elif table_name == "messages_history":
            return MessagesTable(memory=self)
        elif table_name == "users_informations":
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


class Memory(abc.ABC):
    pass


class MemoryItem(abc.ABC):
    pass


class MessageHistory(abc.ABC):
    pass
