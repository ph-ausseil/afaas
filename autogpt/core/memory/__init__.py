"""The memory subsystem manages the Agent's long-term memory."""
from autogpt.core.memory.base import Memory
from autogpt.core.memory.simple import MemorySettings, SimpleMemory
from autogpt.core.memory.jsonfile import JSONFileMemory


from autogpt.core.memory.table import BaseTable
