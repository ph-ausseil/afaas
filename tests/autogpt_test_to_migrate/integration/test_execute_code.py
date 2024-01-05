import random
import string
import tempfile
from pathlib import Path

from AFAAS.lib.task.task import Task
import pytest
from autogpt.agents.agent import PlannerAgent

import AFAAS.core.tools.execute_code as sut  # system under testing
from AFAAS.lib.sdk.errors import InvalidArgumentError, OperationNotAllowedError


@pytest.fixture
def random_code(random_string) -> str:
    return f"print('Hello {random_string}!')"


@pytest.fixture
def python_test_file(agent: PlannerAgent, random_code: str):
    temp_file = tempfile.NamedTemporaryFile(dir=agent.workspace.root, suffix=".py")
    temp_file.write(str.encode(random_code))
    temp_file.flush()

    yield Path(temp_file.name)
    temp_file.close()


@pytest.fixture
def python_test_args_file(agent: PlannerAgent):
    temp_file = tempfile.NamedTemporaryFile(dir=agent.workspace.root, suffix=".py")
    temp_file.write(str.encode("import sys\nprint(sys.argv[1], sys.argv[2])"))
    temp_file.flush()

    yield Path(temp_file.name)
    temp_file.close()


@pytest.fixture
def random_string():
    return "".join(random.choice(string.ascii_lowercase) for _ in range(10))


def test_execute_python_file(
    python_test_file: Path, random_string: str, agent: PlannerAgent
):
    result: str = sut.execute_python_file(
        python_test_file, agent=default_task.agent
    )
    assert result.replace("\r", "") == f"Hello {random_string}!\n"


def test_execute_python_file_args(
    python_test_args_file: Path, random_string: str, agent: PlannerAgent
):
    random_args = [random_string] * 2
    random_args_string = " ".join(random_args)
    result = sut.execute_python_file(
        python_test_args_file,
        args=random_args,
        agent=default_task.agent,
    )
    assert result == f"{random_args_string}\n"


def test_execute_python_code(random_code: str, random_string: str, agent: PlannerAgent):
    result: str = sut.execute_python_code(
        random_code, agent=default_task.agent
    )
    assert result.replace("\r", "") == f"Hello {random_string}!\n"


def test_execute_python_file_invalid(agent: PlannerAgent):
    with pytest.raises(InvalidArgumentError):
        sut.execute_python_file(Path("not_python.txt"), agent)


def test_execute_python_file_not_found(agent: PlannerAgent):
    with pytest.raises(
        FileNotFoundError,
        match=r"python: can't open file '([a-zA-Z]:)?[/\\\-\w]*notexist.py': "
        r"\[Errno 2\] No such file or directory",
    ):
        sut.execute_python_file(Path("notexist.py"), agent)


def test_execute_shell(random_string: str, agent: PlannerAgent):
    result = sut.execute_shell(f"echo 'Hello {random_string}!'", agent)
    assert f"Hello {random_string}!" in result


def test_execute_shell_local_commands_not_allowed(
    random_string: str, agent: PlannerAgent
):
    result = sut.execute_shell(f"echo 'Hello {random_string}!'", agent)
    assert f"Hello {random_string}!" in result


def test_execute_shell_denylist_should_deny(agent: PlannerAgent, random_string: str):
    agent.legacy_config.shell_denylist = ["echo"]

    with pytest.raises(OperationNotAllowedError, match="not allowed"):
        sut.execute_shell(f"echo 'Hello {random_string}!'", agent)


def test_execute_shell_denylist_should_allow(agent: PlannerAgent, random_string: str):
    agent.legacy_config.shell_denylist = ["cat"]

    result = sut.execute_shell(f"echo 'Hello {random_string}!'", agent)
    assert "Hello" in result and random_string in result


def test_execute_shell_allowlist_should_deny(agent: PlannerAgent, random_string: str):
    agent.legacy_config.shell_command_control = sut.ALLOWLIST_CONTROL
    agent.legacy_config.shell_allowlist = ["cat"]

    with pytest.raises(OperationNotAllowedError, match="not allowed"):
        sut.execute_shell(f"echo 'Hello {random_string}!'", agent)


def test_execute_shell_allowlist_should_allow(agent: PlannerAgent, random_string: str):
    agent.legacy_config.shell_command_control = sut.ALLOWLIST_CONTROL
    agent.legacy_config.shell_allowlist = ["echo"]

    result = sut.execute_shell(f"echo 'Hello {random_string}!'", agent)
    assert "Hello" in result and random_string in result
