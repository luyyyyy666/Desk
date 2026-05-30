from datetime import UTC, datetime

import pytest
from my_sifu_agent.rag import EmbeddingJobStatus
from my_sifu_agent.rag_api import Phase4RagApi


def test_rag_api_exposes_embedding_provider_status_without_secret_values() -> None:
    api = Phase4RagApi.default_for_new_api(
        base_url="https://new-api.example/v1",
        model="text-embedding-v1",
        api_key_env_var="NEW_API_KEY",
    )

    response = api.get_embedding_provider_status()

    assert response == {
        "provider": {
            "providerId": "new_api",
            "baseUrlConfigured": True,
            "modelConfigured": True,
            "apiKeyConfigured": True,
            "apiKeyEnvVar": "NEW_API_KEY",
        }
    }
    assert "apiKey" not in response["provider"]
    assert "sk-" not in str(response)


def test_rag_api_creates_queued_embedding_job_without_calling_provider() -> None:
    now = datetime(2026, 5, 30, 10, 0, tzinfo=UTC)
    api = Phase4RagApi.default_for_new_api(
        base_url="https://new-api.example/v1",
        model="text-embedding-v1",
        api_key_env_var="NEW_API_KEY",
    )

    response = api.create_embedding_job(
        {
            "id": "emb_job_001",
            "sources": [
                {
                    "sourceType": "wrong_question_analysis",
                    "sourceId": "wq_001",
                    "contentHash": "sha256:wrong-question",
                    "text": "一次函数应用题中斜率和截距混淆。",
                    "metadata": {"subject": "math"},
                }
            ],
            "createdAt": now.isoformat(),
        }
    )

    job = response["job"]
    assert job["id"] == "emb_job_001"
    assert job["providerId"] == "new_api"
    assert job["embeddingModel"] == "text-embedding-v1"
    assert job["status"] == EmbeddingJobStatus.QUEUED.value
    assert job["totalTexts"] == 1
    assert job["embeddedTexts"] == 0
    assert job["skippedTexts"] == 0
    assert job["failedTexts"] == 0
    assert job["providerCallsOwnedByBackend"] is True
    assert api.get_embedding_job("emb_job_001")["job"] == job


def test_rag_api_requires_configured_embedding_model_before_creating_job() -> None:
    api = Phase4RagApi.default_for_new_api(
        base_url="https://new-api.example/v1",
        model=None,
        api_key_env_var="NEW_API_KEY",
    )

    with pytest.raises(ValueError, match="embedding model"):
        api.create_embedding_job(
            {
                "id": "emb_job_001",
                "sources": [],
                "createdAt": datetime(2026, 5, 30, 10, 0, tzinfo=UTC).isoformat(),
            }
        )


def test_rag_api_returns_embedding_search_contract_without_vector_execution() -> None:
    api = Phase4RagApi.default_for_new_api(
        base_url="https://new-api.example/v1",
        model="text-embedding-v1",
        api_key_env_var="NEW_API_KEY",
    )

    response = api.plan_embedding_search(
        {
            "query": "一次函数",
            "filters": {
                "subject": "math",
                "gradeBand": "middle_school",
                "knowledgeLayer": "curriculum",
            },
            "limit": 5,
            "rerank": True,
        }
    )

    assert response["plan"] == {
        "query": "一次函数",
        "filters": {
            "subject": "math",
            "gradeBand": "middle_school",
            "knowledgeLayer": "curriculum",
        },
        "limit": 5,
        "rerank": True,
        "pipeline": ["structured_filter", "embedding_query", "vector_search", "rerank"],
        "executesVectorSearch": False,
    }
