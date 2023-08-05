from __future__ import annotations


from autogpt.core.configuration import Configurable
from autogpt.core.memory.base import (
    Memory,
)


class NoSQLMemory(Memory, Configurable):
   pass