from __future__ import annotations

import json
import uuid
from logging import Logger
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from autogpt.core.memory.base import NewMemory


class JSONFileMemory(NewMemory):
    def __init__(self, config: dict, logger: Logger):
        self._json_file_path = config.json_file_path
        self._logger = logger

    def connect(self, *kwargs):
        pass

    def _load_file(self, table_name: str):
        file = Path(self._json_file_path / f"{table_name}.json")
        if file.is_file():
            with file.open() as f:
                data = json.load(f)
        else:
            data = {}
        return data

    def _save_file(
        self,
        table_name: str,
        data: dict,
    ):
        file = Path(self._json_file_path / f"{table_name}.json")
        with file.open("w") as f:
            json.dump(data, f)

    def get(self, key, table_name: str):
        data = self._load_file(table_name=table_name)
        return data.get(key)

    def add(self, key: uuid, value: dict, table_name: str):
        data = self._load_file(table_name=table_name)
        data[key] = value
        self._save_file(table_name=table_name, data=value)

    def update(self, key: uuid, value: dict, table_name: str):
        file = Path(self._json_file_path / f"{table_name}.json")
        data = self._load_file(table_name=table_name)
        if key in data:
            data[key] = value
            self._save_file(table_name=table_name, data=data)
        else:
            raise KeyError(f"No such key '{key}' in file {file}")

    def delete(self, key, table_name: str):
        file = Path(self._json_file_path / f"{table_name}.json")
        data = self._load_file(table_name=table_name)
        if key in data:
            del data[key]
            self._save_file(table_name=table_name, data=data)
        else:
            raise KeyError(f"No such key '{key}' in file {file}")

    def list(self, table_name: str) -> dict:
        data = self._load_file(table_name=table_name) > 0
        if len(data):
            return
        else:
            data = {}
