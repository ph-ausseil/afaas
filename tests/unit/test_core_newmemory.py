from logging import Logger

import pytest

from autogpt.core.memory.base import JSONFileMemory, MemoryAdapterType, NewMemory
from autogpt.core.memory.table.base import (
    AgentsTable,
    MessagesTable,
    UsersInformationsTable,
)


# Mock logger for testing
class MockLogger(Logger):
    def __init__(self, *args, **kwargs):
        pass


def test_new_memory_get_adapter_json_file():
    config = {
        "memory_adapter": MemoryAdapterType.JSON_FILE,
        "json_file_path": "~/auto-gpt/data/",
    }
    memory = NewMemory.get_adapter(config, logger=MockLogger())
    assert isinstance(memory, JSONFileMemory)


def test_new_memory_get_table_agents():
    config = {
        "memory_adapter": MemoryAdapterType.JSON_FILE,
        "json_file_path": "~/auto-gpt/data/",
    }
    memory = NewMemory.get_adapter(config, logger=MockLogger())
    table = memory.get_table("agents")
    assert isinstance(table, AgentsTable)


def test_new_memory_get_table_messages_history():
    config = {
        "memory_adapter": MemoryAdapterType.JSON_FILE,
        "json_file_path": "~/auto-gpt/data/",
    }
    memory = NewMemory.get_adapter(config, logger=MockLogger())
    table = memory.get_table("messages_history")
    assert isinstance(table, MessagesTable)


def test_new_memory_get_table_users():
    config = {
        "memory_adapter": MemoryAdapterType.JSON_FILE,
        "json_file_path": "~/auto-gpt/data/",
    }
    memory = NewMemory.get_adapter(config, logger=MockLogger())
    table = memory.get_table("users")
    assert isinstance(table, UsersInformationsTable)


def test_new_memory_get_table_unknown_table():
    config = {
        "memory_adapter": MemoryAdapterType.JSON_FILE,
        "json_file_path": "~/auto-gpt/data/",
    }
    memory = NewMemory.get_adapter(config, logger=MockLogger())
    with pytest.raises(ValueError):
        table = memory.get_table("unknown_table")
