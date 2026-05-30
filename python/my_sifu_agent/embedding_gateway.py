from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from my_sifu_agent.rag import EmbeddingProviderConfig


class EmbeddingGatewayError(RuntimeError):
    pass


@dataclass(frozen=True)
class EmbeddingHttpRequest:
    url: str
    authorization: str | None
    body: dict[str, Any]


@dataclass(frozen=True)
class EmbeddingHttpResponse:
    status_code: int
    body: dict[str, Any]


class EmbeddingTransport(Protocol):
    def send(self, request: EmbeddingHttpRequest) -> EmbeddingHttpResponse:
        pass


@dataclass(frozen=True)
class TextEmbedding:
    index: int
    vector: tuple[float, ...]


@dataclass(frozen=True)
class EmbeddingGatewayResult:
    model: str
    embeddings: tuple[TextEmbedding, ...]
    usage: dict[str, Any]


@dataclass
class OpenAICompatibleEmbeddingGateway:
    provider_config: EmbeddingProviderConfig
    read_env: Any
    transport: EmbeddingTransport
    max_attempts: int = 3

    def build_http_request(self, texts: list[str] | tuple[str, ...]) -> EmbeddingHttpRequest:
        if self.provider_config.base_url is None:
            raise EmbeddingGatewayError("embedding provider base url is not configured")
        if self.provider_config.model is None:
            raise EmbeddingGatewayError("embedding model is not configured")
        api_key = self._api_key()
        return EmbeddingHttpRequest(
            url=f"{self.provider_config.base_url.rstrip('/')}/v1/embeddings",
            authorization=f"Bearer {api_key}" if api_key is not None else None,
            body={
                "model": self.provider_config.model,
                "input": list(texts),
            },
        )

    def embed_texts(self, texts: list[str] | tuple[str, ...]) -> EmbeddingGatewayResult:
        if not texts:
            return EmbeddingGatewayResult(
                model=self.provider_config.model or "",
                embeddings=(),
                usage={},
            )

        request = self.build_http_request(texts)
        last_response: EmbeddingHttpResponse | None = None
        for _ in range(max(1, self.max_attempts)):
            response = self.transport.send(request)
            last_response = response
            if 200 <= response.status_code < 300:
                return self._parse_response(response)
            if not self._is_transient(response.status_code):
                break

        status_code = last_response.status_code if last_response is not None else "unknown"
        raise EmbeddingGatewayError(
            f"embedding provider failed after bounded attempts: {status_code}"
        )

    def _api_key(self) -> str | None:
        env_var = self.provider_config.api_key_env_var
        if env_var is None:
            return None
        value = self.read_env(env_var)
        if value is None or str(value).strip() == "":
            return None
        return str(value)

    def _parse_response(self, response: EmbeddingHttpResponse) -> EmbeddingGatewayResult:
        data = response.body.get("data")
        if not isinstance(data, list):
            raise EmbeddingGatewayError("embedding provider response is missing data")

        embeddings = []
        for item in data:
            index = int(item["index"])
            vector = tuple(float(value) for value in item["embedding"])
            embeddings.append(TextEmbedding(index=index, vector=vector))

        embeddings.sort(key=lambda embedding: embedding.index)
        return EmbeddingGatewayResult(
            model=str(response.body.get("model", self.provider_config.model or "")),
            embeddings=tuple(embeddings),
            usage=dict(response.body.get("usage", {})),
        )

    def _is_transient(self, status_code: int) -> bool:
        return status_code in {408, 409, 429} or 500 <= status_code <= 599
