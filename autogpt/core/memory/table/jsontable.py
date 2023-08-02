from __future__ import annotations
from typing import TYPE_CHECKING
import json
from pathlib import Path

if TYPE_CHECKING : 
        from autogpt.core.memory.table.base import BaseTable

class JSONTable(BaseTable) : 
    def __init__(self, filepath: Path):
        super().__init__()
        self.filepath = filepath
        self._load()
