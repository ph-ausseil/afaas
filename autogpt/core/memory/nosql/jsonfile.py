from __future__ import annotations

import json
import uuid
from logging import Logger
from pathlib import Path
from typing import List

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


class NewJSONFileMemory(NewMemory):
    def __init__(self, config: dict, logger: Logger):
        self._json_file_path = config.json_file_path
        self._logger = logger

    def connect(self, *kwargs):
        pass

    def _load_file(self, key: dict, table_name: str):
        file = self._get_file_path(key, table_name)
        if file.is_file():
            with file.open() as f:
                data = json.load(f)
        else:
            data = {}
        return data

    def _save_file(self, key: dict, table_name: str, data: dict):
        file = self._get_file_path(key, table_name)
        file.parent.mkdir(parents=True, exist_ok=True)
        with file.open("w") as f:
            json.dump(data, f)

    def get(self, key: dict, table_name: str):
        return self._load_file(key, table_name)

    def add(self, key: dict, value: dict, table_name: str):
        data = self._load_file(key, table_name)
        data.update(value)
        self._save_file(key, table_name, data)

    def update(self, key: dict, value: dict, table_name: str):
        data = self._load_file(key, table_name)
        if data:
            data.update(value)
            self._save_file(key, table_name, data)
        else:
            raise KeyError(f"No such key '{key}' in table {table_name}")

    def delete(self, key: dict, table_name: str):
        file = self._get_file_path(key, table_name)
        if file.is_file():
            file.unlink()
        else:
            raise KeyError(f"No such key '{key}' in table {table_name}")

    def list(self, table_name: str) -> List[dict]:
        table_path = Path(self._json_file_path, table_name)
        data = []
        for json_file in table_path.glob("**/*.json"):
            with json_file.open() as f:
                data.append(json.load(f))
        return data

    def _get_file_path(self, key: dict, table_name: str) -> Path:
        file_path = Path(self._json_file_path, table_name, str(key["primary_key"]))
        if "secondary_key" in key:
            file_path = file_path / str(key["secondary_key"])
        file_path = file_path.with_suffix(".json")
        return file_path
