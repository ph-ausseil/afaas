

import pytest
import re
from io import TextIOWrapper
from pathlib import Path
import pytest_asyncio
import AFAAS.core.tools.builtins.file_operations as file_ops
from AFAAS.core.tools.builtins.file_operations_helpers import operations_from_log, text_checksum, file_operations_state , append_to_file, log_operation
from AFAAS.interfaces.agent.main import BaseAgent
from AFAAS.lib.sdk.errors import DuplicateOperationError
from tests.dataset.test_tools_file import test_file_name, test_file_path, test_file_with_content_path, test_nested_file, test_directory, test_file, file_content
from tests.dataset.plan_familly_dinner import task_ready_no_predecessors_or_subtasks , Task  , plan_step_0 , plan_familly_dinner


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
    assert list(operations_from_log(log_path=test_file.name)) == expected


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
    assert file_operations_state(log_path=test_file.name) == expected_state

# FIXME:NOT NotImplementedError
async def test_append_to_file(task_ready_no_predecessors_or_subtasks : Task, test_nested_file: Path, agent: BaseAgent):
    append_text = "This is appended text.\n"
    await file_ops.write_to_file(filename=test_nested_file, contents=append_text, agent=agent, task=task_ready_no_predecessors_or_subtasks)

    append_to_file(filename=test_nested_file, text= append_text, agent=agent)

    with open(test_nested_file, "r") as f:
        content_after = f.read()

    assert content_after == append_text + append_text

# FIXME:NOT NotImplementedError
@pytest.mark.asyncio
async def test_write_file_fails_if_content_exists(
    task_ready_no_predecessors_or_subtasks : Task, test_file_name: Path, agent: BaseAgent):
    new_content = "This is new content.\n"
    log_operation(
         "write",
         test_file_name,
         agent=agent,
         checksum= text_checksum(new_content)
     )
    with pytest.raises(DuplicateOperationError):
        await file_ops.write_to_file(filename=test_file_name, contents = new_content, agent=agent, task=task_ready_no_predecessors_or_subtasks)


#from autogpt.memory.vector.memory_item import MemoryItem


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
#             "write", Path("path/to/file1.txt"),  "checksum1", agent=agent)
#         )
#         is True
#     )
#     assert (
#         file_ops.is_duplicate_operation(
#             "write", Path("path/to/file1.txt"), "checksum2", agent=agent)
#         )
#         is False
#     )
#     assert (
#         file_ops.is_duplicate_operation(
#             "write", Path("path/to/file3.txt"), "checksum3", agent=agent)
#         )
#         is False
#     )
#     # Test cases with append operations
#     assert (
#         file_ops.is_duplicate_operation(
#             "append", Path("path/to/file1.txt"),  "checksum1", agent=agent)
#         )
#         is False
#     )
#     # Test cases with delete operations
#     assert (
#         file_ops.is_duplicate_operation("delete", Path("path/to/file1.txt"), agent=agent)
#         is False
#     )
#     assert (
#         file_ops.is_duplicate_operation("delete", Path("path/to/file3.txt"), agent=agent)
#         is True
#     )


# Test logging a file operation
def test_log_operation(task_ready_no_predecessors_or_subtasks : Task, agent: BaseAgent):

    #FIXMEv0.0.2 : Set as AgentSetting
    LOG_FILE_OPERATION = Path(__file__).parent.parent / 'logs' / (f"{agent.agent_id}_file_operation")

    file_ops.log_operation("log_test", Path("path/to/test"), agent=agent)
    with open(LOG_FILE_OPERATION, "r", encoding="utf-8") as f:
        content = f.read()
    assert "log_test: path/to/test\n" in content


def test_text_checksum( task_ready_no_predecessors_or_subtasks : Task, file_content: str):
    checksum = text_checksum(text= file_content)
    different_checksum = text_checksum(text="other content")
    assert re.match(r"^[a-fA-F0-9]+$", checksum) is not None
    assert checksum != different_checksum



# FIXME:
# @pytest.mark.asyncio
# async def test_write_file_logs_checksum(test_file_name: Path, agent: BaseAgent):
#     new_content = "This is new content.\n"
#     new_checksum = file_ops.text_checksum(new_content)
#     await file_ops.write_to_file(test_file_name, new_content, agent=agent)
#     with open(agent.file_manager.file_ops_log_path, "r", encoding="utf-8") as f:
#         log_entry = f.read()
#     assert log_entry == f"write: {test_file_name} #{new_checksum}\n"

#FIXME:
# def test_append_to_file_uses_checksum_from_appended_file(
#     task_ready_no_predecessors_or_subtasks : Task,
#     test_file_name: Path, agent: BaseAgent
# ):
#     append_text = "This is appended text.\n"
#     file_ops.append_to_file(
#         agent.workspace.get_path(test_file_name),
#         append_text,
#         agent=agent)
#     file_ops.append_to_file(
#         agent.workspace.get_path(test_file_name),
#         append_text,
#         agent=agent,)
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
