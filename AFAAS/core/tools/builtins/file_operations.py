"""Tools to perform operations on files"""

from __future__ import annotations

import contextlib
import os
import os.path
from pathlib import Path
from typing import Generator

from langchain_community.tools.file_management.file_search import FileSearchTool
from langchain_core.vectorstores import VectorStore
from AFAAS.core.tools.builtins.file_operations_helpers import is_duplicate_operation, log_operation, text_checksum
from AFAAS.core.tools.builtins.file_operations_utils import decode_textual_file #FIXME: replace with Langchain
from AFAAS.core.tools.tool_decorator import tool
from AFAAS.core.tools.tools import Tool
from AFAAS.interfaces.agent.main import BaseAgent
from AFAAS.lib.sdk.errors import DuplicateOperationError
from AFAAS.lib.sdk.logger import AFAASLogger
from AFAAS.lib.task.task import Task
from AFAAS.lib.utils.json_schema import JSONSchema

TOOL_CATEGORY = "file_operations"
TOOL_CATEGORY_TITLE = "File Operations"


LOG = AFAASLogger(name=__name__)

@tool(
    "read_file",
    "Read an existing file",
    {
        "filename": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The path of the file to read",
            required=True,
        )
    },
)
def read_file(filename:  str | Path, task: Task, agent: BaseAgent) -> str:
    """Read a file and return the contents

    Args:
        filename (Path): The name of the file to read

    Returns:
        str: The contents of the file
    """
    file = agent.workspace.open_file(filename, binary=True)
    content = decode_textual_file(file, os.path.splitext(filename)[1])



@tool(
    "write_file",
    "Write a file, creating it if necessary. If the file exists, it is overwritten.",
    {
        "filename": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The name of the file to write to",
            required=True,
        ),
        "contents": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The contents to write to the file",
            required=True,
        ),
    },
    aliases=["write_file", "create_file"],
)
async def write_to_file(
    filename: Path, contents: str, task: Task, agent: BaseAgent
) -> str:
    """Write contents to a file

    Args:
        filename (Path): The name of the file to write to
        contents (str): The contents to write to the file

    Returns:
        str: A message indicating success or failure
    """
    checksum = text_checksum(contents)
    if is_duplicate_operation("write", Path(filename), agent, checksum):
        raise DuplicateOperationError(f"File {filename} has already been updated.")

    if directory := os.path.dirname(filename):
        agent.workspace.get_path(directory).mkdir(exist_ok=True)
    await agent.workspace.write_file(filename, contents)
    log_operation("write", filename, agent, checksum)
    return f"File {filename} has been written successfully."


    # TODO: invalidate/update memory when file is edited
    # file_memory = MemoryItem.from_text_file(content, str(filename), agent.config)
    # if len(file_memory.chunks) > 1:
    #     return file_memory.summary

    #cf : ingest_file
    agent.vectorstore.adelete(id=str(filename))
    agent.vectorstore.aadd_texts(texts=[content],
                                #  ids=[str(filename)],
                                #  lang="en",
                                #  title=str(filename),
                                #  description="",
                                #  tags=[],
                                #  metadata={},
                                #  source="",
                                #  author="",
                                #  date="",
                                #  license="",
                                #  url="",
                                #  chunk_size=100,
                                #  chunk_overlap=0,
                                #  chunking_strategy="fixed",
                                #  chunking_strategy_args={},
                                #  chunking_strategy_kwargs={},
    )

    return content


def ingest_file(
    filename: str,
    vectorstore: VectorStore,
) -> None:
    """
    Ingest a file by reading its content, splitting it into chunks with a specified
    maximum length and overlap, and adding the chunks to the memory storage.

    Args:
        filename: The name of the file to ingest
        memory: An object with an add() method to store the chunks in memory
    """
    try:
        LOG.info(f"Ingesting file {filename}")
        content = read_file(filename)

        # TODO: Move to langchain
        raise ("Not implemented error")

        file_memory = MemoryItemFactory.from_text_file(content, filename)
        LOG.trace(f"Created memory: {file_memory.dump(True)}")
        vectorstore.add(file_memory)

        LOG.info(f"Ingested {len(file_memory.e_chunks)} chunks from {filename}")
    except Exception as err:
        LOG.warn(f"Error while ingesting file '{filename}': {err}")


@tool(
    "list_folder",
    "List the items in a folder",
    {
        "folder": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The folder to list files in",
            required=True,
        )
    },
)
def list_folder(folder: Path, task: Task, agent: BaseAgent) -> list[str]:
    """Lists files in a folder recursively

    Args:
        folder (Path): The folder to search in

    Returns:
        list[str]: A list of files found in the folder
    """
    return [str(p) for p in agent.workspace.list(folder)]



def file_search_args(input_args: dict[str, any], agent: BaseAgent):
    # Force only searching in the workspace root
    input_args["dir_path"] = str(agent.workspace.get_path(input_args["dir_path"]))
    return input_args


file_search = Tool.generate_from_langchain_tool(
    tool=FileSearchTool(), arg_converter=file_search_args
)
