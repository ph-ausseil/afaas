"""Tools to search the web with"""

from __future__ import annotations

TOOL_CATEGORY = "web_search"
TOOL_CATEGORY_TITLE = "Web Search"

import json
import time
from itertools import islice

from duckduckgo_search import DDGS

from AFAAS.core.tools.tool_decorator import SAFE_MODE, tool
from AFAAS.interfaces.agent.main import BaseAgent
from AFAAS.interfaces.task.task import AbstractTask
from AFAAS.lib.sdk.errors import ConfigurationError
from AFAAS.lib.utils.json_schema import JSONSchema

COMMAND_CATEGORY = "web_search"
COMMAND_CATEGORY_TITLE = "Web Search"


DUCKDUCKGO_MAX_ATTEMPTS = 3


@tool(
    name="web_search",
    description="Searches the web",
    parameters={
        "query": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="Search the web for recent information.",
            required=True,
        )
    },
    aliases=["search"],
)
def web_search(
    query: str, agent: BaseAgent, task: AbstractTask, num_results: int = 8
) -> str:
    """Return the results of a Google search

    Args:
        query (str): The search query.
        num_results (int): The number of results to return.

    Returns:
        str: The results of the search.
    """
    print(
        """TODO : Merge with query language model in a 4 steps tools : 
        1. query_llm
        2. check llm retult sanity
        3. if not sane search_web
        4. send results to LLM to formal with original extra arguments"""
    )
    search_results = []
    attempts = 0

    while attempts < DUCKDUCKGO_MAX_ATTEMPTS:
        if not query:
            return json.dumps(search_results)

        results = DDGS().text(query)
        search_results = list(islice(results, num_results))

        if search_results:
            break

        time.sleep(1)
        attempts += 1

    search_results = [
        {
            "title": r["title"],
            "url": r["href"],
            **({"exerpt": r["body"]} if r.get("body") else {}),
        }
        for r in search_results
    ]

    results = (
        "## Search results\n"
        # "Read these results carefully."
        # " Extract the information you need for your task from the list of results"
        # " if possible. Otherwise, choose a webpage from the list to read entirely."
        # "\n\n"
    ) + "\n\n".join(
        f"### \"{r['title']}\"\n"
        f"**URL:** {r['url']}  \n"
        "**Excerpt:** " + (f'"{exerpt}"' if (exerpt := r.get("exerpt")) else "N/A")
        for r in search_results
    )
    return safe_google_results(results)


@tool(
    "google",
    "Google Search",
    {
        "query": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The search query",
            required=True,
        )
    },
    lambda config: bool(config.google_api_key)
    and bool(config.google_custom_search_engine_id),
    "Configure google_api_key and custom_search_engine_id.",
    aliases=["search"],
)
def google(
    query: str, agent: BaseAgent, task: AbstractTask, num_results: int = 8
) -> str | list[str]:
    """Return the results of a Google search using the official Google API

    Args:
        query (str): The search query.
        num_results (int): The number of results to return.

    Returns:
        str: The results of the search.
    """

    print(
        """TODO : Merge with query language model in a 4 steps tools : 
        1. query_llm
        2. check llm retult sanity
        3. if not sane search_web
        4. send results to LLM to formal with original extra arguments"""
    )
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    try:
        # Get the Google API key and Custom Search Engine ID from the config file
        api_key = agent.legacy_config.google_api_key
        custom_search_engine_id = agent.legacy_config.google_custom_search_engine_id

        # Initialize the Custom Search API service
        service = build("customsearch", "v1", developerKey=api_key)

        # Send the search query and retrieve the results
        result = (
            service.cse()
            .list(q=query, cx=custom_search_engine_id, num=num_results)
            .execute()
        )

        # Extract the search result items from the response
        search_results = result.get("items", [])

        # Create a list of only the URLs from the search results
        search_results_links = [item["link"] for item in search_results]

    except HttpError as e:
        # Handle errors in the API call
        error_details = json.loads(e.content.decode())

        # Check if the error is related to an invalid or missing API key
        if error_details.get("error", {}).get(
            "code"
        ) == 403 and "invalid API key" in error_details.get("error", {}).get(
            "message", ""
        ):
            raise ConfigurationError(
                "The provided Google API key is invalid or missing."
            )
        raise
    # google_result can be a list or a string depending on the search results

    # Return the list of search result URLs
    return safe_google_results(search_results_links)


def safe_google_results(results: str | list) -> str:
    """
        Return the results of a Google search in a safe format.

    Args:
        results (str | list): The search results.

    Returns:
        str: The results of the search.
    """

    print(
        """TODO : Merge with query language model in a 4 steps tools : 
        1. query_llm
        2. check llm retult sanity
        3. if not sane search_web
        4. send results to LLM to formal with original extra arguments"""
    )
    if isinstance(results, list):
        safe_message = json.dumps(
            [result.encode("utf-8", "ignore").decode("utf-8") for result in results]
        )
    else:
        safe_message = results.encode("utf-8", "ignore").decode("utf-8")
    return safe_message
