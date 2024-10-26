import autogpt.memory.vector.memory_item as vector_memory_item
import autogpt.memory.vector.providers.base as memory_provider_base
import numpy
import pytest
from autogpt.config.config import Config
from autogpt.core.resource.model_providers import OPEN_AI_EMBEDDING_MODELS
from langchain import Embeddings
from pytest_mock import MockerFixture

from AFAAS.lib.task.task import Task


@pytest.fixture
def embedding_dimension(config: Config):
    return OPEN_AI_EMBEDDING_MODELS[config.embedding_model].embedding_dimensions


@pytest.fixture
def mock_embedding(embedding_dimension: int) -> Embeddings:
    return numpy.full((1, embedding_dimension), 0.0255, numpy.float32)[0]


@pytest.fixture
def mock_get_embedding(mocker: MockerFixture, mock_embedding: Embeddings):
    mocker.patch.object(
        vector_memory_item,
        "get_embedding",
        return_value=mock_embedding,
    )
    mocker.patch.object(
        memory_provider_base,
        "get_embedding",
        return_value=mock_embedding,
    )


@pytest.fixture
def memory_none(agent_test_config: Config, mock_get_embedding):
    was_memory_backend = agent_test_config.memory_backend

    agent_test_config.memory_backend = "no_memory"
    yield get_memory(agent_test_config)

    agent_test_config.memory_backend = was_memory_backend
