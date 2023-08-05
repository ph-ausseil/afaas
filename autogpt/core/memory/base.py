from __future__ import annotations

import abc
from enum import Enum
from logging import Logger
from typing import TYPE_CHECKING

from pydantic import Field

from autogpt.core.configuration import SystemConfiguration, SystemSettings

if TYPE_CHECKING:
    pass


class MemoryAdapterType(Enum):
    JSON_FILE = "json_file"
    DYNAMODB = "dynamodb"
    COSMOSDB = "cosmosdb"
    MONGODB = "mongodb"


class NewMemoryConfig(SystemConfiguration):
    """
    Configuration class representing the parameters for creating a NewMemory adapter.

    Attributes:
        memory_adapter (MemoryAdapterType): The type of memory adapter to use.
        json_file_path (str): The file path for the JSON file when using the JSONFileMemory adapter.
        # Add other parameters for different memory adapters as needed.
    """
    pass

    memory_adapter: MemoryAdapterType = Field(
        ..., description="The type of memory adapter to use."
    )
    json_file_path: str = Field(
        ...,
        description="The file path for the JSON file when using the JSONFileMemory adapter.",
    )
    # Add other parameters for different memory adapters as needed.

class MemorySettings(SystemSettings) : 
    configuration: NewMemoryConfig

class Memory(abc.ABC):
    
    @abc.abstractmethod
    def __init__(self):
        pass

    @classmethod
    def get_adapter(
        cls, config: NewMemoryConfig, logger=Logger, *args, **kwargs
    ) -> "Memory":
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

        if config.memory_adapter == "json_file":
            
            from autogpt.core.memory.nosql.jsonfile import NewJSONFileMemory
            return NewJSONFileMemory(config=config, logger=logger)
        
        elif config.memory_adapter == "dynamodb":
            raise NotImplementedError("DynamoDBMemory")

        elif config.memory_adapter == "cosmosdb":
            raise NotImplementedError("CosmosDBMemory")

        elif config.memory_adapter == "mongodb":
            raise NotImplementedError("MongoDBMemory")

        else:
            raise ValueError("Invalid memory_adapter type")



class MemoryItem(abc.ABC):
    pass


class MessageHistory(abc.ABC):
    pass
