import pytest
from my_sifu_agent.embedding_gateway import (
    EmbeddingGatewayError,
    EmbeddingHttpResponse,
    OpenAICompatibleEmbeddingGateway,
)
from my_sifu_agent.rag import EmbeddingProviderConfig


class FakeEmbeddingTransport:
    def __init__(self, responses: list[EmbeddingHttpResponse]) -> None:
        self._responses = list(responses)
        self.requests = []

    def send(self, request):
        self.requests.append(request)
        if not self._responses:
            raise AssertionError("no fake embedding response configured")
        return self._responses.pop(0)


def test_embedding_gateway_builds_openai_compatible_new_api_request() -> None:
    gateway = OpenAICompatibleEmbeddingGateway(
        provider_config=EmbeddingProviderConfig(
            provider_id="new_api",
            base_url="http://127.0.0.1:3000/",
            model="text-embedding-v1",
            api_key_env_var="MY_SIFU_EMBEDDING_GATEWAY_API_KEY",
        ),
        read_env=lambda key: {"MY_SIFU_EMBEDDING_GATEWAY_API_KEY": "local-token"}.get(key),
        transport=FakeEmbeddingTransport([]),
    )

    request = gateway.build_http_request(["一次函数", "二次函数"])

    assert request.url == "http://127.0.0.1:3000/v1/embeddings"
    assert request.authorization == "Bearer local-token"
    assert request.body == {
        "model": "text-embedding-v1",
        "input": ["一次函数", "二次函数"],
    }


def test_embedding_gateway_parses_openai_compatible_response_in_input_order() -> None:
    transport = FakeEmbeddingTransport(
        [
            EmbeddingHttpResponse(
                status_code=200,
                body={
                    "model": "text-embedding-v1",
                    "data": [
                        {"index": 1, "embedding": [0.3, 0.4]},
                        {"index": 0, "embedding": [0.1, 0.2]},
                    ],
                    "usage": {"prompt_tokens": 8, "total_tokens": 8},
                },
            )
        ]
    )
    gateway = OpenAICompatibleEmbeddingGateway(
        provider_config=EmbeddingProviderConfig(
            provider_id="new_api",
            base_url="http://127.0.0.1:3000",
            model="text-embedding-v1",
            api_key_env_var=None,
        ),
        read_env=lambda key: None,
        transport=transport,
    )

    result = gateway.embed_texts(["一次函数", "二次函数"])

    assert [embedding.index for embedding in result.embeddings] == [0, 1]
    assert result.embeddings[0].vector == (0.1, 0.2)
    assert result.embeddings[1].vector == (0.3, 0.4)
    assert result.model == "text-embedding-v1"
    assert result.usage == {"prompt_tokens": 8, "total_tokens": 8}
    assert len(transport.requests) == 1


def test_embedding_gateway_retries_transient_provider_failure_once() -> None:
    transport = FakeEmbeddingTransport(
        [
            EmbeddingHttpResponse(status_code=503, body={"error": "temporarily unavailable"}),
            EmbeddingHttpResponse(
                status_code=200,
                body={
                    "model": "text-embedding-v1",
                    "data": [{"index": 0, "embedding": [0.1]}],
                    "usage": {"total_tokens": 2},
                },
            ),
        ]
    )
    gateway = OpenAICompatibleEmbeddingGateway(
        provider_config=EmbeddingProviderConfig(
            provider_id="new_api",
            base_url="http://127.0.0.1:3000",
            model="text-embedding-v1",
            api_key_env_var=None,
        ),
        read_env=lambda key: None,
        transport=transport,
        max_attempts=2,
    )

    result = gateway.embed_texts(["一次函数"])

    assert result.embeddings[0].vector == (0.1,)
    assert len(transport.requests) == 2


def test_embedding_gateway_reports_provider_failure_after_bounded_attempts() -> None:
    transport = FakeEmbeddingTransport(
        [
            EmbeddingHttpResponse(status_code=503, body={"error": "first failure"}),
            EmbeddingHttpResponse(status_code=503, body={"error": "second failure"}),
        ]
    )
    gateway = OpenAICompatibleEmbeddingGateway(
        provider_config=EmbeddingProviderConfig(
            provider_id="new_api",
            base_url="http://127.0.0.1:3000",
            model="text-embedding-v1",
            api_key_env_var=None,
        ),
        read_env=lambda key: None,
        transport=transport,
        max_attempts=2,
    )

    with pytest.raises(EmbeddingGatewayError, match="embedding provider failed"):
        gateway.embed_texts(["一次函数"])

    assert len(transport.requests) == 2
