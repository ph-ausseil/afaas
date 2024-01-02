import hashlib
import os
from AFAAS.core.tools.builtins.decorators import sanitize_path_arg

from AFAAS.core.tools.builtins.file_operations import LOG, Operation
from pathlib import Path
from typing import Iterator, Literal

from AFAAS.interfaces.agent.main import BaseAgent


def text_checksum(text: str) -> str:
    """Get the hex checksum for the given text."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def operations_from_log(
    log_path: str | Path,
) -> Iterator[
    tuple[Literal["write", "append"], str, str] | tuple[Literal["delete"], str, None]
]:
    """Parse the file operations log and return a tuple containing the log entries"""
    try:
        log = open(log_path, "r", encoding="utf-8")
    except FileNotFoundError:
        return

    for line in log:
        line = line.replace("File Operation Logger", "").strip()
        if not line:
            continue
        operation, tail = line.split(": ", maxsplit=1)
        operation = operation.strip()
        if operation in ("write", "append"):
            try:
                path, checksum = (x.strip() for x in tail.rsplit(" #", maxsplit=1))
            except ValueError:
                LOG.warn(f"File log entry lacks checksum: '{line}'")
                path, checksum = tail.strip(), None
            yield (operation, path, checksum)
        elif operation == "delete":
            yield (operation, tail.strip(), None)

    log.close()


def file_operations_state(log_path: str | Path) -> dict[str, str]:
    """Iterates over the operations log and returns the expected state.

    Parses a log file at file_manager.file_ops_log_path to construct a dictionary
    that maps each file path written or appended to its checksum. Deleted files are
    removed from the dictionary.

    Returns:
        A dictionary mapping file paths to their checksums.

    Raises:
        FileNotFoundError: If file_manager.file_ops_log_path is not found.
        ValueError: If the log file content is not in the expected format.
    """
    state = {}
    for operation, path, checksum in operations_from_log(log_path):
        if operation in ("write", "append"):
            state[path] = checksum
        elif operation == "delete":
            del state[path]
    return state


@sanitize_path_arg("file_path", make_relative=True)
def is_duplicate_operation(
    operation: Operation, file_path: Path, agent: BaseAgent, checksum: str | None = None
) -> bool:
    """Check if the operation has already been performed

    Args:
        operation: The operation to check for
        file_path: The name of the file to check for
        agent: The agent
        checksum: The checksum of the contents to be written

    Returns:
        True if the operation has already been performed on the file
    """
    state = file_operations_state(agent._setting.Config.file_logger_path)
    if operation == "delete" and file_path not in state:
        return True
    if operation == "write" and state.get(str(file_path)) == checksum:
        return True
    return False


@sanitize_path_arg("file_path", make_relative=True)
def log_operation(
    operation: Operation,
    file_path: str | Path,
    agent: BaseAgent,
    checksum: str | None = None,
) -> None:
    raise NotImplementedError("Not implemented error")
    """Log the file operation to the file_LOG.log

    Args:
        operation: The operation to log
        file_path: The name of the file the operation was performed on
        checksum: The checksum of the contents to be written
    """
    log_entry = f"{operation}: {file_path}"
    if checksum is not None:
        log_entry += f" #{checksum}"
    LOG.trace(f"Logging file operation: {log_entry}")
    append_to_file(
        agent._setting.Config.file_logger_path,
        f"{log_entry}\n",
        agent,
        should_log=False,
    )


def append_to_file(
    filename: Path, text: str, agent: BaseAgent, should_log: bool = True
) -> None:
    """Append text to a file

    Args:
        filename (Path): The name of the file to append to
        text (str): The text to append to the file
        should_log (bool): Should log output
    """
    directory = os.path.dirname(filename)
    os.makedirs(directory, exist_ok=True)
    with open(filename, "a") as f:
        f.write(text)

    if should_log:
        with open(filename, "r") as f:
            checksum = text_checksum(f.read())
        log_operation("append", filename, agent, checksum=checksum)
