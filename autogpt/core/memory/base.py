from __future__ import annotations

import abc
import uuid
from typing import TYPE_CHECKING , Any
from autogpt.core.configuration import Configurable, SystemConfiguration, SystemSettings
from autogpt.core.memory import BaseTable, JSONFileMemory
from logging import Logger
from pathlib import Path



if TYPE_CHECKING :
    from autogpt.core.memory.table.base import AgentsTable, MessagesTable, UsersTable


class NewMemory(Configurable):

    #TABLE_CLASS = BaseTable

    @abc.abstractmethod
    def __init__(self) :
        pass 

    @classmethod
    def get_adapter(cls, config : str  , logger = Logger , *kwargs ) -> "NewMemory":
        # TODO : Not yet integrated, For test purposes
        config = {'memory_adapter' : 'json_file' ,
                  'json_file_path' : '~/auto-gpt/data/'
        }

        if config.memory_adapter == "json_file":
            return JSONFileMemory(config = config , logger = logger)
        elif config.memory_adapter == "redis":
            raise NotImplementedError()
        else:
            raise ValueError("Invalid animal type")
    
    @classmethod
    def get_table(self, table_name : str, logger = Logger) -> BaseTable :

        if __class__ != NewMemory : 
            
            if table_name == 'agents':
                return AgentsTable(memory=__class__)
            elif table_name == 'messages_history':
                return MessagesTable(memory=__class__)
            elif table_name == 'users':
                return UsersTable(memory=__class__)
            else:
                raise ValueError(f'Unknown table: {table_name}')
            
    @abc.abstractmethod
    def connect(self, kwarg) :
        pass

    @abc.abstractmethod
    def get(self,  key, table_name: str):
        pass

    @abc.abstractmethod
    def add(self,  key : uuid, value : dict, table_name: str):
        pass

    @abc.abstractmethod
    def update(self,  key : uuid, value : dict, table_name: str):
        pass

    @abc.abstractmethod
    def delete(self,  key, table_name: str):
        pass

class Memory(abc.ABC) :
    pass

class MemoryItem(abc.ABC):
    pass


class MessageHistory(abc.ABC):
    pass
