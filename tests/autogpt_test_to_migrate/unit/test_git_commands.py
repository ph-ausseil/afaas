import pytest
from git.exc import GitCommandError
from git.repo.base import Repo

from AFAAS.core.tools.untested.git_operations import clone_repository
from AFAAS.interfaces.agent.main import BaseAgent
from AFAAS.lib.sdk.errors import ToolExecutionError
from AFAAS.lib.task.task import Task


@pytest.fixture
def mock_clone_from(mocker):
    return mocker.patch.object(Repo, "clone_from")


def test_clone_auto_gpt_repository(workspace, mock_clone_from, agent: BaseAgent):
    mock_clone_from.return_value = None

    repo = "github.com/Significant-Gravitas/Auto-GPT.git"
    scheme = "https://"
    url = scheme + repo
    clone_path = workspace.get_path("auto-gpt-repo")

    expected_output = f"Cloned {url} to {clone_path}"

    clone_result = clone_repository(
        url=url,
        clone_path=clone_path,
        agent=default_task.agent,
    )

    assert clone_result == expected_output
    mock_clone_from.assert_called_once_with(
        url=f"{scheme}{agent.legacy_config.github_username}:{agent.legacy_config.github_api_key}@{repo}",  # noqa: E501
        to_path=clone_path,
    )


def test_clone_repository_error(workspace, mock_clone_from, agent: BaseAgent):
    url = "https://github.com/this-repository/does-not-exist.git"
    clone_path = workspace.get_path("does-not-exist")

    mock_clone_from.side_effect = GitCommandError(
        "clone", "fatal: repository not found", ""
    )

    with pytest.raises(ToolExecutionError):
        clone_repository(
            url=url,
            clone_path=clone_path,
            agent=default_task.agent,
        )
