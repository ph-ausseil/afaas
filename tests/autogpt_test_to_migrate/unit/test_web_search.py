import json

import pytest
from googleapiclient.errors import HttpError

from AFAAS.core.tools.untested.web_search import google, safe_google_results, web_search
from AFAAS.interfaces.agent.main import BaseAgent
from AFAAS.lib.sdk.errors import ConfigurationError
from AFAAS.lib.task.task import Task


@pytest.mark.parametrize(
    "query, expected_output",
    [("test", "test"), (["test1", "test2"], '["test1", "test2"]')],
)
def test_safe_google_results(query, expected_output):
    result = safe_google_results(query)
    assert isinstance(result, str)
    assert result == expected_output


def test_safe_google_results_invalid_input():
    with pytest.raises(AttributeError):
        safe_google_results(123)


@pytest.mark.parametrize(
    "query, num_results, expected_output_parts, return_value",
    [
        (
            "test",
            1,
            ("Result 1", "https://example.com/result1"),
            [{"title": "Result 1", "href": "https://example.com/result1"}],
        ),
        ("", 1, (), []),
        ("no results", 1, (), []),
    ],
)
def test_google_search(
    default_task: Task,
    query,
    num_results,
    expected_output_parts,
    return_value,
    mocker,
    agent: BaseAgent,
):
    mock_ddg = mocker.Mock()
    mock_ddg.return_value = return_value

    mocker.patch("AFAAS.core.tools.web_search.DDGS.text", mock_ddg)
    actual_output = web_search(
        query,
        agent=default_task.agent,
        num_results=num_results,
    )
    for o in expected_output_parts:
        assert o in actual_output


@pytest.fixture
def mock_googleapiclient(mocker):
    mock_build = mocker.patch("googleapiclient.discovery.build")
    mock_service = mocker.Mock()
    mock_build.return_value = mock_service
    return mock_service.cse().list().execute().get


@pytest.mark.parametrize(
    "query, num_results, search_results, expected_output",
    [
        (
            "test",
            3,
            [
                {"link": "http://example.com/result1"},
                {"link": "http://example.com/result2"},
                {"link": "http://example.com/result3"},
            ],
            [
                "http://example.com/result1",
                "http://example.com/result2",
                "http://example.com/result3",
            ],
        ),
        ("", 3, [], []),
    ],
)
def test_google_official_search(
    default_task: Task,
    query,
    num_results,
    expected_output,
    search_results,
    mock_googleapiclient,
    agent: BaseAgent,
):
    mock_googleapiclient.return_value = search_results
    actual_output = google(
        query,
        agent=default_task.agent,
        num_results=num_results,
    )
    assert actual_output == safe_google_results(expected_output)


@pytest.mark.parametrize(
    "query, num_results, expected_error_type, http_code, error_msg",
    [
        (
            "invalid query",
            3,
            HttpError,
            400,
            "Invalid Value",
        ),
        (
            "invalid API key",
            3,
            ConfigurationError,
            403,
            "invalid API key",
        ),
    ],
)
def test_google_official_search_errors(
    default_task: Task,
    query,
    num_results,
    expected_error_type,
    mock_googleapiclient,
    http_code,
    error_msg,
    agent: BaseAgent,
):
    class resp:
        def __init__(self, _status, _reason):
            self.status = _status
            self.reason = _reason

    response_content = {
        "error": {"code": http_code, "message": error_msg, "reason": "backendError"}
    }
    error = HttpError(
        resp=resp(http_code, error_msg),
        content=str.encode(json.dumps(response_content)),
        uri="https://www.googleapis.com/customsearch/v1?q=invalid+query&cx",
    )

    mock_googleapiclient.side_effect = error
    with pytest.raises(expected_error_type):
        google(
            query,
            agent=default_task.agent,
            num_results=num_results,
        )
