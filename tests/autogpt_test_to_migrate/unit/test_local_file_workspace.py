from pathlib import Path

from AFAAS.lib.task.task import Task
import pytest
from AFAAS.core.workspace.local import AGPTLocalFileWorkspace, AGPTLocalFileWorkspaceConfiguration

_WORKSPACE_ROOT = Path("home/users/monty/auto_gpt_workspace")

_ACCESSIBLE_PATHS = [
    Path("."),
    Path("test_file.txt"),
    Path("test_folder"),
    Path("test_folder/test_file.txt"),
    Path("test_folder/.."),
    Path("test_folder/../test_file.txt"),
    Path("test_folder/../test_folder"),
    Path("test_folder/../test_folder/test_file.txt"),
]

_INACCESSIBLE_PATHS = (
    [
        # Takes us out of the workspace
        Path(".."),
        Path("../test_file.txt"),
        Path("../not_auto_gpt_workspace"),
        Path("../not_auto_gpt_workspace/test_file.txt"),
        Path("test_folder/../.."),
        Path("test_folder/../../test_file.txt"),
        Path("test_folder/../../not_auto_gpt_workspace"),
        Path("test_folder/../../not_auto_gpt_workspace/test_file.txt"),
    ]
    + [
        # Contains null byte
        Path("\0"),
        Path("\0test_file.txt"),
        Path("test_folder/\0"),
        Path("test_folder/\0test_file.txt"),
    ]
    + [
        # Absolute paths
        Path("/"),
        Path("/test_file.txt"),
        Path("/home"),
    ]
)


@pytest.fixture()
def workspace_root(tmp_path):
    return tmp_path / _WORKSPACE_ROOT


@pytest.fixture(params=_ACCESSIBLE_PATHS)
def accessible_path(request):
    return request.param


@pytest.fixture(params=_INACCESSIBLE_PATHS)
def inaccessible_path(request):
    return request.param


def test_sanitize_path_accessible(accessible_path, workspace_root):
    full_path = AGPTLocalFileWorkspace._sanitize_path(
        accessible_path,
        root=workspace_root,
        restrict_to_root=True,
    )
    assert full_path.is_absolute()
    assert full_path.is_relative_to(workspace_root)


def test_sanitize_path_inaccessible(inaccessible_path, workspace_root):
    with pytest.raises(ValueError):
        AGPTLocalFileWorkspace._sanitize_path(
            inaccessible_path,
            root=workspace_root,
            restrict_to_root=True,
        )


def test_get_path_accessible(accessible_path, workspace_root):
    workspace = AGPTLocalFileWorkspace(AGPTLocalFileWorkspaceConfiguration(root=workspace_root))
    full_path = workspace.get_path(accessible_path)
    assert full_path.is_absolute()
    assert full_path.is_relative_to(workspace_root)


def test_get_path_inaccessible(inaccessible_path, workspace_root):
    workspace = AGPTLocalFileWorkspace(AGPTLocalFileWorkspaceConfiguration(root=workspace_root))
    with pytest.raises(ValueError):
        workspace.get_path(inaccessible_path)
