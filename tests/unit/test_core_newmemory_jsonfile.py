import json
import uuid
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from autogpt.core.memory import JSONFileMemory


def test_json_file_memory_init():
    config = {"json_file_path": "~/auto-gpt/data/"}
    logger = MagicMock()
    memory = JSONFileMemory(config=config, logger=logger)
    assert memory._json_file_path == Path("~/auto-gpt/data/")
    assert memory._logger == logger


def test_json_file_memory_get_existing_key(tmp_path):
    data = {"key1": "value1", "key2": "value2"}
    table_name = "test_table"
    file_path = tmp_path / f"{table_name}.json"
    with file_path.open("w") as f:
        json.dump(data, f)

    config = {"json_file_path": tmp_path}
    logger = MagicMock()
    memory = JSONFileMemory(config=config, logger=logger)

    key = "key1"
    result = memory.get(key, table_name)
    assert result == "value1"


def test_json_file_memory_get_non_existing_key(tmp_path):
    data = {"key1": "value1", "key2": "value2"}
    table_name = "test_table"
    file_path = tmp_path / f"{table_name}.json"
    with file_path.open("w") as f:
        json.dump(data, f)

    config = {"json_file_path": tmp_path}
    logger = MagicMock()
    memory = JSONFileMemory(config=config, logger=logger)

    key = "key3"
    result = memory.get(key, table_name)
    assert result is None


def test_json_file_memory_add(tmp_path):
    data = {"key1": "value1", "key2": "value2"}
    table_name = "test_table"
    file_path = tmp_path / f"{table_name}.json"
    with file_path.open("w") as f:
        json.dump(data, f)

    config = {"json_file_path": tmp_path}
    logger = MagicMock()
    memory = JSONFileMemory(config=config, logger=logger)

    key = uuid.uuid4()
    value = {"new_key": "new_value"}
    memory.add(key, value, table_name)

    with file_path.open() as f:
        updated_data = json.load(f)
        assert updated_data[key.hex] == value


def test_json_file_memory_update_existing_key(tmp_path):
    data = {"key1": "value1", "key2": "value2"}
    table_name = "test_table"
    file_path = tmp_path / f"{table_name}.json"
    with file_path.open("w") as f:
        json.dump(data, f)

    config = {"json_file_path": tmp_path}
    logger = MagicMock()
    memory = JSONFileMemory(config=config, logger=logger)

    key = "key1"
    value = {"key1": "updated_value"}
    memory.update(key, value, table_name)

    with file_path.open() as f:
        updated_data = json.load(f)
        assert updated_data[key] == value[key]


def test_json_file_memory_update_non_existing_key(tmp_path):
    data = {"key1": "value1", "key2": "value2"}
    table_name = "test_table"
    file_path = tmp_path / f"{table_name}.json"
    with file_path.open("w") as f:
        json.dump(data, f)

    config = {"json_file_path": tmp_path}
    logger = MagicMock()
    memory = JSONFileMemory(config=config, logger=logger)

    key = "key3"
    value = {"key3": "new_value"}
    with pytest.raises(KeyError):
        memory.update(key, value, table_name)


def test_json_file_memory_delete_existing_key(tmp_path):
    data = {"key1": "value1", "key2": "value2"}
    table_name = "test_table"
    file_path = tmp_path / f"{table_name}.json"
    with file_path.open("w") as f:
        json.dump(data, f)

    config = {"json_file_path": tmp_path}
    logger = MagicMock()
    memory = JSONFileMemory(config=config, logger=logger)

    key = "key1"
    memory.delete(key, table_name)

    with file_path.open() as f:
        updated_data = json.load(f)
        assert key not in updated_data


def test_json_file_memory_delete_non_existing_key(tmp_path):
    data = {"key1": "value1", "key2": "value2"}
    table_name = "test_table"
    file_path = tmp_path / f"{table_name}.json"
    with file_path.open("w") as f:
        json.dump(data, f)

    config = {"json_file_path": tmp_path}
    logger = MagicMock()
    memory = JSONFileMemory(config=config, logger=logger)

    key = "key3"
    with pytest.raises(KeyError):
        memory.delete(key, table_name)


def test_json_file_memory_list_existing_data(tmp_path):
    data = {"key1": "value1", "key2": "value2"}
    table_name = "test_table"
    file_path = tmp_path / f"{table_name}.json"
    with file_path.open("w") as f:
        json.dump(data, f)

    config = {"json_file_path": tmp_path}
    logger = MagicMock()
    memory = JSONFileMemory(config=config, logger=logger)

    result = memory.list(table_name)
    assert result == data


def test_json_file_memory_list_empty_data(tmp_path):
    table_name = "test_table"
    file_path = tmp_path / f"{table_name}.json"
    file_path.touch()

    config = {"json_file_path": tmp_path}
    logger = MagicMock()
    memory = JSONFileMemory(config=config, logger=logger)

    result = memory.list(table_name)
    assert result == {}
