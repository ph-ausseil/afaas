from __future__ import annotations

import abc
import base64
import json
import uuid
from enum import Enum
from logging import Logger
from pathlib import Path
from typing import TYPE_CHECKING
from autogpt.core.configuration import Configurable

from pydantic import Field

from autogpt.core.configuration import SystemConfiguration, SystemSettings

if TYPE_CHECKING:
    from autogpt.core.memory.table.base import BaseTable

class MemoryAdapterType(Enum):
    SQLLIKE_JSON_FILE = "json_file"
    NOSQL_JSON_FILE = "nosqljson_file"
    DYNAMODB = "dynamodb"
    COSMOSDB = "cosmosdb"
    MONGODB = "mongodb"


class MemoryConfig(SystemConfiguration):
    """
    Configuration class representing the parameters for creating a Memory adapter.

    Attributes:
        memory_adapter (MemoryAdapterType): The type of memory adapter to use.
        json_file_path (str): The file path for the JSON file when using the JSONFileMemory adapter.
        # Add other parameters for different memory adapters as needed.
    """

    memory_adapter: MemoryAdapterType = Field(
        MemoryAdapterType.NOSQL_JSON_FILE,
        description="The type of memory adapter to use.",
    )
    json_file_path: str = Field(
        str(Path("~/auto-gpt/data/").expanduser().resolve()),
        description="The file path for the JSON file when using the JSONFileMemory adapter.",
    )
    # sqllikejson_file_path=str(Path("~/auto-gpt/sqlikejsondata/").expanduser().resolve()),
    # cosmos_endpoint=None, 
    # cosmos_key=None, 
    # cosmos_database_name=None,
    # aws_access_key_id=None, 
    # aws_secret_access_key,
    # dynamodb_region_name=None, 
    # mongodb_connection_string='connection_string',
    # mongodb_database_name='database_name',
    # mongo_uri=None, 
    # mongo_db_name=None

class MemorySettings(SystemSettings) : 
    configuration: MemoryConfig
    name : str ="Memory"
    description : str ="Memory is an abstract memory adapter"

    class Config(SystemSettings.Config):
        extra = "allow"

class Memory(Configurable, abc.ABC):

    default_settings = MemorySettings(
            name="new_memory",
            description="Memory is an abstract memory adapter",
            configuration= MemoryConfig(
                                        memory_adapter=MemoryAdapterType.NOSQL_JSON_FILE, 
                                        json_file_path=str(Path("~/auto-gpt/data/").expanduser().resolve()),
                                        # sqllikejson_file_path=str(Path("~/auto-gpt/sqlikejsondata/").expanduser().resolve()),
                                        # cosmos_endpoint=None, 
                                        # cosmos_key=None, 
                                        # cosmos_database_name=None,
                                        # aws_access_key_id=None, 
                                        # aws_secret_access_key,
                                        # dynamodb_region_name=None, 
                                        # mongodb_connection_string='connection_string',
                                        # mongodb_database_name='database_name',
                                        # mongo_uri=None, 
                                        # mongo_db_name=None
                                        ),
        )
    _instances = {}

    """
    Abstract class representing a memory storage system for storing and retrieving data.

    To use a specific memory adapter, create a configuration dict specifying the desired
    memory_adapter. Currently, "json_file" and "redis" adapters are available.

    Example:
        config = {"memory_adapter": "json_file", "json_file_path": "~/auto-gpt/data/"}
        memory = Memory.get_adapter(config)

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
        The `Memory` class is an abstract class, and you should use one of its concrete
        subclasses like `JSONFileMemory` or `RedisMemory` for actual implementations.
    """
    
    @abc.abstractmethod
    def __init__(self,
                 settings: MemorySettings,
                logger: Logger,):
        Memory._instances = {}
        super().__init__(settings, logger)
        # self._configuration = settings.configuration
        # self._logger = logger
        

    @classmethod
    def get_adapter(
        cls, memory_settings: MemorySettings, logger=Logger, *args, **kwargs
    ) -> "Memory":
        """
        Get an instance of a memory adapter based on the provided configuration.

        Parameters:
            config (dict): Configuration dict specifying the memory_adapter type and
                           any required parameters for that adapter.
            logger (Logger, optional): The logger instance to use for logging messages.
                                       Default: Logger.

        Returns:
            Memory: An instance of the memory adapter based on the provided configuration.

        Raises:
            ValueError: If an invalid memory_adapter type is provided in the configuration.

        Example:
            config = {"memory_adapter": "json_file", "json_file_path": "~/auto-gpt/data/"}
            memory = Memory.get_adapter(config)
        """
        adapter_type = memory_settings.configuration.memory_adapter
        config_key = base64.b64encode(json.dumps(memory_settings.configuration.dict()).encode()).decode()

        if config_key in Memory._instances:
            return Memory._instances[config_key]
        
        if adapter_type == MemoryAdapterType.NOSQL_JSON_FILE:
            
            from autogpt.core.memory.nosql.jsonfile import JSONFileMemory
            instance=  JSONFileMemory(settings=memory_settings, logger=logger)
        
        elif adapter_type == MemoryAdapterType.SQLLIKE_JSON_FILE:
            raise NotImplementedError("SQLLikeJSONFileMemory") 
               
        elif adapter_type == MemoryAdapterType.DYNAMODB:
            raise NotImplementedError("DynamoDBMemory")

        elif adapter_type == MemoryAdapterType.COSMOSDB:
            raise NotImplementedError("CosmosDBMemory")

        elif adapter_type == MemoryAdapterType.MONGODB:
            raise NotImplementedError("MongoDBMemory")

        else:
            raise ValueError("Invalid memory_adapter type")
        
        Memory._instances[config_key] = instance # Store the newly created instance
        return instance

    abc.abstractmethod
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

        if self.__class__ == Memory:
            raise TypeError(
                "get_table method cannot be called on Memory class directly"
            )

        if table_name == "agents":
            from autogpt.core.memory.table.base import AgentsTable
            returnvalue  = AgentsTable(memory=self)
            return returnvalue
        elif table_name == "messages_history":
            from autogpt.core.memory.table.base import MessagesTable
            return MessagesTable(memory=self)
        elif table_name == "users_informations":
            from autogpt.core.memory.table.base import UsersInformationsTable
            return UsersInformationsTable(memory=self)
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
    def get(self, key: uuid.UUID, table_name: str):
        pass

    @abc.abstractmethod
    def add(self, key: uuid.UUID, value: dict, table_name: str):
        pass

    @abc.abstractmethod
    def update(self, key: uuid.UUID, value: dict, table_name: str):
        pass

    @abc.abstractmethod
    def delete(self, key: uuid.UUID, table_name: str):
        pass

    @abc.abstractmethod
    def list(self, table_name: str) -> dict:
        pass


class MemoryItem(abc.ABC):
    pass


class MessageHistory(abc.ABC):
    pass
