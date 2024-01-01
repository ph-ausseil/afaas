from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from AFAAS.interfaces.agent.main import BaseAgent

from AFAAS.lib.utils.json_schema import JSONSchema
from AFAAS.core.tools.tools import Tool
from AFAAS.interfaces.tools.tool_parameters import ToolParameter
from AFAAS.core.tools.simple import SimpleToolRegistry

PARAMETERS = [
    ToolParameter(
        "arg1",
        spec=JSONSchema(
            type=JSONSchema.Type.INTEGER,
            description="Argument 1",
            required=True,
        ),
    ),
    ToolParameter(
        "arg2",
        spec=JSONSchema(
            type=JSONSchema.Type.STRING,
            description="Argument 2",
            required=False,
        ),
    ),
]


def example_tool_method(arg1: int, arg2: str, agent: BaseAgent) -> str:
    """Example function for testing the Command class."""
    # This function is static because it is not used by any other test cases.
    return f"{arg1} - {arg2}"


def test_tool_creation():
    """Test that a Command object can be created with the correct attributes."""
    cmd = Tool(
        name="example",
        description="Example command",
        method=example_tool_method,
        parameters=PARAMETERS,
    )

    assert cmd.name == "example"
    assert cmd.description == "Example command"
    assert cmd.method == example_tool_method
    assert (
        str(cmd)
        == "example: Example command. Params: (arg1: integer, arg2: Optional[string])"
    )


@pytest.fixture
def example_tool():
    yield Tool(
        name="example",
        description="Example command",
        method=example_tool_method,
        parameters=PARAMETERS,
    )


def test_tool_call(example_command: Tool, agent: BaseAgent):
    """Test that Tool(*args) calls and returns the result of method(*args)."""
    result = example_tool(arg1=1, arg2="test", agent=agent)
    assert result == "1 - test"


def test_tool_call_with_invalid_arguments(example_command: Tool, agent: BaseAgent):
    """Test that calling a Command object with invalid arguments raises a TypeError."""
    with pytest.raises(TypeError):
        example_tool(arg1="invalid", does_not_exist="test", agent=agent)


def test_register_tool(example_command: Tool):
    """Test that a command can be registered to the registry."""
    registry = SimpleToolRegistry()

    registry.register(example_command)

    assert registry.get_tool(example_command.name) == example_command
    assert len(registry.commands) == 1


def test_unregister_tool(example_command: Tool):
    """Test that a command can be unregistered from the registry."""
    registry = SimpleToolRegistry()

    registry.register(example_command)
    registry.unregister(example_command)

    assert len(registry.commands) == 0
    assert example_command.name not in registry


@pytest.fixture
def example_tool_with_aliases(example_command: Tool):
    example_command.aliases = ["example_alias", "example_alias_2"]
    return example_command


def test_register_tool_aliases(example_tool_with_aliases: Tool):
    """Test that a command can be registered to the registry."""
    registry = SimpleToolRegistry()
    command = example_tool_with_aliases

    registry.register(command)

    assert command.name in registry
    assert registry.get_tool(command.name) == command
    for alias in command.aliases:
        assert registry.get_tool(alias) == command
    assert len(registry.commands) == 1


def test_unregister_tool_aliases(example_tool_with_aliases: Tool):
    """Test that a command can be unregistered from the registry."""
    registry = SimpleToolRegistry()
    command = example_tool_with_aliases

    registry.register(command)
    registry.unregister(command)

    assert len(registry.commands) == 0
    assert command.name not in registry
    for alias in command.aliases:
        assert alias not in registry


def test_tool_in_registry(example_tool_with_aliases: Tool):
    """Test that `command_name in registry` works."""
    registry = SimpleToolRegistry()
    command = example_tool_with_aliases

    assert command.name not in registry
    assert "nonexistent_command" not in registry

    registry.register(command)

    assert command.name in registry
    assert "nonexistent_command" not in registry
    for alias in command.aliases:
        assert alias in registry


def test_get_tool(example_command: Tool):
    """Test that a command can be retrieved from the registry."""
    registry = SimpleToolRegistry()

    registry.register(example_command)
    retrieved_cmd = registry.get_tool(example_command.name)

    assert retrieved_cmd == example_command


def test_get_nonexistent_tool():
    """Test that attempting to get a nonexistent command raises a KeyError."""
    registry = SimpleToolRegistry()

    assert registry.get_tool("nonexistent_command") is None
    assert "nonexistent_command" not in registry


def test_call_tool(agent: BaseAgent):
    """Test that a command can be called through the registry."""
    registry = SimpleToolRegistry()
    cmd = Tool(
        name="example",
        description="Example command",
        method=example_tool_method,
        parameters=PARAMETERS,
    )

    registry.register(cmd)
    result = registry.call("example", arg1=1, arg2="test", agent=agent)

    assert result == "1 - test"


def test_call_nonexistent_tool(agent: BaseAgent):
    """Test that attempting to call a nonexistent command raises a KeyError."""
    registry = SimpleToolRegistry()

    with pytest.raises(KeyError):
        registry.call("nonexistent_command", arg1=1, arg2="test", agent=agent)


def test_import_mock_commands_module():
    """Test that the registry can import a module with mock command plugins."""
    registry = SimpleToolRegistry()
    mock_commands_module = "tests.mocks.mock_commands"

    registry.import_tool_module(mock_commands_module)

    assert "function_based_cmd" in registry
    assert registry.tools["function_based_cmd"].name == "function_based_cmd"
    assert (
        registry.tools["function_based_cmd"].description
        == "Function-based test command"
    )


def test_import_temp_tool_file_module(tmp_path: Path):
    """
    Test that the registry can import a command plugins module from a temp file.
    Args:
        tmp_path (pathlib.Path): Path to a temporary directory.
    """
    registry = SimpleToolRegistry()

    # Create a temp command file
    src = Path(os.getcwd()) / "tests/mocks/mock_commands.py"
    temp_commands_file = tmp_path / "mock_commands.py"
    shutil.copyfile(src, temp_commands_file)

    # Add the temp directory to sys.path to make the module importable
    sys.path.append(str(tmp_path))

    temp_commands_module = "mock_commands"
    registry.import_tool_module(temp_commands_module)

    # Remove the temp directory from sys.path
    sys.path.remove(str(tmp_path))

    assert "function_based_cmd" in registry
    assert registry.tools["function_based_cmd"].name == "function_based_cmd"
    assert (
        registry.tools["function_based_cmd"].description
        == "Function-based test command"
    )
