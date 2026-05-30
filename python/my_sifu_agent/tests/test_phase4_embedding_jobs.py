from datetime import UTC, datetime

from my_sifu_agent.embedding_gateway import EmbeddingGatewayResult, TextEmbedding
from my_sifu_agent.rag import InMemoryEmbeddingIndex, VectorUpsertStatus
from my_sifu_agent.rag_api import Phase4RagApi


class FakeEmbeddingGateway:
    def __init__(self) -> None:
        self.calls = []

    def embed_texts(self, texts):
        self.calls.append(list(texts))
        return EmbeddingGatewayResult(
            model="text-embedding-v1",
            embeddings=tuple(
                TextEmbedding(index=index, vector=(float(index), float(index + 1)))
                for index, _ in enumerate(texts)
            ),
            usage={"total_tokens": len(texts) * 2},
        )


def test_rag_api_runs_embedding_job_and_stores_vectors_in_index() -> None:
    now = datetime(2026, 5, 30, 11, 0, tzinfo=UTC)
    gateway = FakeEmbeddingGateway()
    index = InMemoryEmbeddingIndex()
    api = Phase4RagApi.default_for_new_api(
        base_url="http://127.0.0.1:3000",
        model="text-embedding-v1",
        api_key_env_var="MY_SIFU_EMBEDDING_GATEWAY_API_KEY",
        embedding_gateway=gateway,
        embedding_index=index,
    )
    api.create_embedding_job(
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

    response = api.run_embedding_job("emb_job_001", now=now)

    assert response["job"]["status"] == "completed"
    assert response["job"]["embeddedTexts"] == 1
    assert response["job"]["skippedTexts"] == 0
    assert response["job"]["failedTexts"] == 0
    assert response["upserts"] == [{"sourceId": "wq_001", "status": VectorUpsertStatus.UPSERTED}]
    assert gateway.calls == [["一次函数应用题中斜率和截距混淆。"]]
    records = index.list_records()
    assert len(records) == 1
    assert records[0].source_id == "wq_001"
    assert records[0].embedding_model == "text-embedding-v1"
    assert records[0].content_hash == "sha256:wrong-question"
    assert records[0].vector == (0.0, 1.0)


def test_rag_api_run_embedding_job_skips_duplicate_vectors() -> None:
    now = datetime(2026, 5, 30, 11, 30, tzinfo=UTC)
    gateway = FakeEmbeddingGateway()
    index = InMemoryEmbeddingIndex()
    api = Phase4RagApi.default_for_new_api(
        base_url="http://127.0.0.1:3000",
        model="text-embedding-v1",
        api_key_env_var=None,
        embedding_gateway=gateway,
        embedding_index=index,
    )
    payload = {
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
    api.create_embedding_job(payload)
    api.run_embedding_job("emb_job_001", now=now)
    api.create_embedding_job({**payload, "id": "emb_job_002"})

    response = api.run_embedding_job("emb_job_002", now=now)

    assert response["job"]["status"] == "completed"
    assert response["job"]["embeddedTexts"] == 0
    assert response["job"]["skippedTexts"] == 1
    assert len(index.list_records()) == 1
