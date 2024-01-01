# import json
#

# from AFAAS.configs.schema import Configurable, SystemConfiguration, SystemSettings
# from AFAAS.interfaces.db import Memory
# from AFAAS.interfaces.workspace import Workspace


# class MemoryConfiguration(SystemConfiguration):
#     pass


# class Memory.SystemSettings(SystemSettings):
#     configuration: MemoryConfiguration


# class MessageHistory:
#     def __init__(self, previous_message_history: list[str]):
#         self._message_history = previous_message_history


# class SimpleMemory(Memory, Configurable):
#     default_settings = Memory.SystemSettings(
#         name="simple_memory",
#         description="A simple memory.",
#         configuration=MemoryConfiguration(),
#     )

#     def __init__(
#         self,
#         settings: Memory.SystemSettings,
#
#         workspace: Workspace,
#     ):
#         self._configuration = settings.configuration
#         LOG = logger
#         self._message_history = self._load_message_history(workspace)

#     @staticmethod
#     def _load_message_history(workspace: Workspace):
#         message_history_path = workspace.get_path("message_history.json")
#         if message_history_path.exists():
#             with message_history_path.open("r") as f:
#                 message_history = json.load(f)
#         else:
#             message_history = []
#         return MessageHistory(message_history)
