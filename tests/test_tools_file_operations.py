import hashlib
import os
import re
from io import TextIOWrapper
from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from .dataset.plan_familly_dinner import task_ready_no_predecessors_or_subtasks , Task

from langchain_core.embeddings import Embeddings
import AFAAS.core.tools.builtins.file_operations as file_ops
from AFAAS.interfaces.agent.main import BaseAgent
from AFAAS.lib.sdk.errors import DuplicateOperationError
#from AFAAS.configs.config import Config
from AFAAS.core.workspace import AbstractFileWorkspace
#from autogpt.memory.vector.memory_item import MemoryItem


@pytest.fixture()
def file_content():
    return "This is a test file.\n"


# @pytest.fixture()
# def mock_MemoryItem_from_text(
#     mocker: MockerFixture, mock_embedding: Embeddings, config: Config
# ):
#     mocker.patch.object(
#         file_ops.MemoryItemFactory,
#         "from_text",
#         new=lambda content, source_type, config, metadata: MemoryItem(
#             raw_content=content,
#             summary= f"Summary of content '{content}'",
#             chunk_summaries=[f"Summary of content '{content}'"],
#             chunks=[content],
#             e_summary=mock_embedding,
#             e_chunks=[mock_embedding],
#             metadata=metadata | {"source_type": source_type},
#         ),
#     )


@pytest.fixture()
def test_file_name():
    return Path("test_file.txt")


@pytest.fixture
def test_file_path(test_file_name: Path, local_workspace : AbstractFileWorkspace):
    return local_workspace. get_path(test_file_name)


@pytest.fixture()
def test_file(test_file_path: Path):
    file = open(test_file_path, "w")
    yield file
    if not file.closed:
        file.close()


@pytest.fixture()
def test_file_with_content_path(task_ready_no_predecessors_or_subtasks : Task,  test_file: TextIOWrapper, file_content, agent: BaseAgent):
    test_file.write(file_content)
    test_file.close()
    file_ops.log_operation( 
       operation= "write", file_path=Path(test_file.name), agent= agent, checksum= file_ops.text_checksum(text= file_content , task=task_ready_no_predecessors_or_subtasks) , task=task_ready_no_predecessors_or_subtasks
    )
    return Path(test_file.name)


@pytest.fixture()
def test_directory( local_workspace : AbstractFileWorkspace):
    return local_workspace.get_path("test_directory")


@pytest.fixture()
def test_nested_file( local_workspace : AbstractFileWorkspace):
    return local_workspace.get_path("nested/test_file.txt")


def test_file_operations_log(task_ready_no_predecessors_or_subtasks : Task, test_file: TextIOWrapper):
    log_file_content = (
        "File Operation Logger\n"
        "write: path/to/file1.txt #checksum1\n"
        "write: path/to/file2.txt #checksum2\n"
        "write: path/to/file3.txt #checksum3\n"
        "append: path/to/file2.txt #checksum4\n"
        "delete: path/to/file3.txt\n"
    )
    test_file.write(log_file_content)
    test_file.close()

    expected = [
        ("write", "path/to/file1.txt", "checksum1"),
        ("write", "path/to/file2.txt", "checksum2"),
        ("write", "path/to/file3.txt", "checksum3"),
        ("append", "path/to/file2.txt", "checksum4"),
        ("delete", "path/to/file3.txt", None),
    ]
    assert list(file_ops.operations_from_log(log_path=test_file.name), task=task_ready_no_predecessors_or_subtasks) == expected


def test_file_operations_state(task_ready_no_predecessors_or_subtasks : Task, test_file: TextIOWrapper):
    # Prepare a fake log file
    log_file_content = (
        "File Operation Logger\n"
        "write: path/to/file1.txt #checksum1\n"
        "write: path/to/file2.txt #checksum2\n"
        "write: path/to/file3.txt #checksum3\n"
        "append: path/to/file2.txt #checksum4\n"
        "delete: path/to/file3.txt\n"
    )
    test_file.write(log_file_content)
    test_file.close()

    # Call the function and check the returned dictionary
    expected_state = {
        "path/to/file1.txt": "checksum1",
        "path/to/file2.txt": "checksum4",
    }
    assert file_ops.file_operations_state(log_path=test_file.name, task=task_ready_no_predecessors_or_subtasks) == expected_state


# def test_is_duplicate_operation(task_ready_no_predecessors_or_subtasks : Task , agent: BaseAgent, mocker: MockerFixture):
#     # Prepare a fake state dictionary for the function to use
#     state = {
#         "path/to/file1.txt": "checksum1",
#         "path/to/file2.txt": "checksum2",
#     }
#     mocker.patch.object(file_ops, "file_operations_state", lambda _: state)

#     # Test cases with write operations
#     assert (
#         file_ops.is_duplicate_operation(
#             "write", Path("path/to/file1.txt"),  "checksum1", agent=agent, task=task_ready_no_predecessors_or_subtasks)
#         )
#         is True
#     )
#     assert (
#         file_ops.is_duplicate_operation(
#             "write", Path("path/to/file1.txt"), "checksum2", agent=agent, task=task_ready_no_predecessors_or_subtasks)
#         )
#         is False
#     )
#     assert (
#         file_ops.is_duplicate_operation(
#             "write", Path("path/to/file3.txt"), "checksum3", agent=agent, task=task_ready_no_predecessors_or_subtasks)
#         )
#         is False
#     )
#     # Test cases with append operations
#     assert (
#         file_ops.is_duplicate_operation(
#             "append", Path("path/to/file1.txt"),  "checksum1", agent=agent, task=task_ready_no_predecessors_or_subtasks)
#         )
#         is False
#     )
#     # Test cases with delete operations
#     assert (
#         file_ops.is_duplicate_operation("delete", Path("path/to/file1.txt"), agent=agent, task=task_ready_no_predecessors_or_subtasks)
#         is False
#     )
#     assert (
#         file_ops.is_duplicate_operation("delete", Path("path/to/file3.txt"), agent=agent, task=task_ready_no_predecessors_or_subtasks)
#         is True
#     )


# # Test logging a file operation
# def test_log_operation(task_ready_no_predecessors_or_subtasks : Task,agent: BaseAgent):
#     file_ops.log_operation("log_test", Path("path/to/test"), agent=agent, task=task_ready_no_predecessors_or_subtasks)
#     with open(agent.file_manager.file_ops_log_path, "r", encoding="utf-8") as f:
#         content = f.read()
#     assert "log_test: path/to/test\n" in content


def test_text_checksum( task_ready_no_predecessors_or_subtasks : Task, file_content: str):
    checksum = file_ops.text_checksum(text= file_content, task=task_ready_no_predecessors_or_subtasks)
    different_checksum = file_ops.text_checksum(text="other content", task=task_ready_no_predecessors_or_subtasks)
    assert re.match(r"^[a-fA-F0-9]+$", checksum) is not None
    assert checksum != different_checksum

#FIXME:
# def test_log_operation_with_checksum(agent: BaseAgent):
#     file_ops.log_operation(
#         "log_test", Path("path/to/test"), agent=agent, checksum="ABCDEF"
#     )
#     with open(agent.file_manager.file_ops_log_path, "r", encoding="utf-8") as f:
#         content = f.read()
#     assert "log_test: path/to/test #ABCDEF\n" in content


def test_read_file(
    task_ready_no_predecessors_or_subtasks : Task,
    test_file_with_content_path: Path,
    file_content,
    agent: BaseAgent,
):
    content = file_ops.read_file(filename=test_file_with_content_path, agent=agent, task=task_ready_no_predecessors_or_subtasks)

    assert content.replace("\r", "") == file_content


def test_read_file_not_found(task_ready_no_predecessors_or_subtasks : Task, agent: BaseAgent):
    filename = "does_not_exist.txt"
    with pytest.raises(FileNotFoundError):
        file_ops.read_file(filename= filename, agent=agent, task=task_ready_no_predecessors_or_subtasks)


@pytest.mark.asyncio
async def test_write_to_file_relative_path(task_ready_no_predecessors_or_subtasks : Task, test_file_name: Path, agent: BaseAgent):
    new_content = "This is new content.\n"
    await file_ops.write_to_file(filename = test_file_name, contents=new_content, agent=agent, task=task_ready_no_predecessors_or_subtasks)
    with open(agent.workspace.get_path(test_file_name), "r", encoding="utf-8") as f:
        content = f.read()
    assert content == new_content


@pytest.mark.asyncio
async def test_write_to_file_absolute_path(test_file_path: Path, agent: BaseAgent, task_ready_no_predecessors_or_subtasks : Task):
    new_content = "This is new content.\n"
    await file_ops.write_to_file(filename=test_file_path, contents=new_content, agent=agent, task=task_ready_no_predecessors_or_subtasks)
    with open(test_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == new_content


# FIXME:
# @pytest.mark.asyncio
# async def test_write_file_logs_checksum(test_file_name: Path, agent: BaseAgent):
#     new_content = "This is new content.\n"
#     new_checksum = file_ops.text_checksum(new_content)
#     await file_ops.write_to_file(test_file_name, new_content, agent=agent)
#     with open(agent.file_manager.file_ops_log_path, "r", encoding="utf-8") as f:
#         log_entry = f.read()
#     assert log_entry == f"write: {test_file_name} #{new_checksum}\n"

@pytest.mark.asyncio
async def test_write_file_fails_if_content_exists(
    task_ready_no_predecessors_or_subtasks : Task, test_file_name: Path, agent: BaseAgent):
    new_content = "This is new content.\n"
    file_ops.log_operation(
        "write",
        test_file_name,
        agent=agent,
        checksum= file_ops.text_checksum(new_content), task=task_ready_no_predecessors_or_subtasks
    )
    with pytest.raises(DuplicateOperationError):
        await file_ops.write_to_file(filename=test_file_name, content = new_content, agent=agent, task=task_ready_no_predecessors_or_subtasks)


@pytest.mark.asyncio
async def test_write_file_succeeds_if_content_different(
    task_ready_no_predecessors_or_subtasks : Task, test_file_with_content_path: Path, agent: BaseAgent
):
    new_content = "This is different content.\n"
    await file_ops.write_to_file(test_file_with_content_path, new_content, agent=agent, task=task_ready_no_predecessors_or_subtasks)


@pytest.mark.asyncio
async def test_append_to_file(task_ready_no_predecessors_or_subtasks : Task, test_nested_file: Path, agent: BaseAgent):
    append_text = "This is appended text.\n"
    await file_ops.write_to_file(filename=test_nested_file, contents=append_text, agent=agent, task=task_ready_no_predecessors_or_subtasks)

    file_ops.append_to_file(filename=test_nested_file, text= append_text, agent=agent, task=task_ready_no_predecessors_or_subtasks)

    with open(test_nested_file, "r") as f:
        content_after = f.read()

    assert content_after == append_text + append_text

#FIXME:
# def test_append_to_file_uses_checksum_from_appended_file(
#     task_ready_no_predecessors_or_subtasks : Task,
#     test_file_name: Path, agent: BaseAgent
# ):
#     append_text = "This is appended text.\n"
#     file_ops.append_to_file(
#         agent.workspace.get_path(test_file_name),
#         append_text,
#         agent=agent,
#      task=task_ready_no_predecessors_or_subtasks)
#     file_ops.append_to_file(
#         agent.workspace.get_path(test_file_name),
#         append_text,
#         agent=agent,
#      task=task_ready_no_predecessors_or_subtasks)
#     with open(agent.file_manager.file_ops_log_path, "r", encoding="utf-8") as f:
#         log_contents = f.read()

#     digest = hashlib.md5()
#     digest.update(append_text.encode("utf-8"))
#     checksum1 = digest.hexdigest()
#     digest.update(append_text.encode("utf-8"))
#     checksum2 = digest.hexdigest()
#     assert log_contents == (
#         f"append: {test_file_name} #{checksum1}\n"
#         f"append: {test_file_name} #{checksum2}\n"
#     )


def test_list_files(task_ready_no_predecessors_or_subtasks : Task, local_workspace : AbstractFileWorkspace, test_directory: Path, agent: BaseAgent):
    # Case 1: Create files A and B, search for A, and ensure we don't return A and B
    file_a = local_workspace. get_path("file_a.txt")
    file_b = local_workspace. get_path("file_b.txt")

    with open(file_a, "w") as f:
        f.write("This is file A.")

    with open(file_b, "w") as f:
        f.write("This is file B.")

    # Create a subdirectory and place a copy of file_a in it
    if not os.path.exists(test_directory):
        os.makedirs(test_directory)

    with open(os.path.join(test_directory, file_a.name), "w") as f:
        f.write("This is file A in the subdirectory.")

    files = file_ops.list_folder(folder=str(local_workspace.root), agent=agent, task=task_ready_no_predecessors_or_subtasks)
    assert file_a.name in files
    assert file_b.name in files
    assert os.path.join(Path(test_directory).name, file_a.name) in files

    # Clean up
    os.remove(file_a)
    os.remove(file_b)
    os.remove(os.path.join(test_directory, file_a.name))
    os.rmdir(test_directory)

    # Case 2: Search for a file that does not exist and make sure we don't throw
    non_existent_file = "non_existent_file.txt"
    files = file_ops.list_folder(folder="", agent=agent, task=task_ready_no_predecessors_or_subtasks)
    assert non_existent_file not in files
