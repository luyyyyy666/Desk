from datetime import UTC, datetime

from my_sifu_agent.rag import (
    EmbeddingJob,
    EmbeddingJobSource,
    EmbeddingJobStatus,
    EmbeddingProviderConfig,
    EmbeddingSourceType,
    EmbeddingVectorRecord,
    InMemoryEmbeddingIndex,
    KnowledgeLayer,
    RetrievalResult,
    RetrievalTrustTier,
    VectorUpsertStatus,
)


def test_embedding_provider_status_never_exposes_api_key_material() -> None:
    config = EmbeddingProviderConfig(
        provider_id="new_api",
        base_url="https://new-api.example/v1",
        model="text-embedding-v1",
        api_key_env_var="NEW_API_KEY",
    )

    public_status = config.public_status()

    assert public_status == {
        "providerId": "new_api",
        "baseUrlConfigured": True,
        "modelConfigured": True,
        "apiKeyConfigured": True,
        "apiKeyEnvVar": "NEW_API_KEY",
    }
    assert "apiKey" not in public_status
    assert "secret" not in public_status


def test_embedding_job_contract_tracks_backend_owned_batch_work() -> None:
    now = datetime(2026, 5, 30, 9, 0, tzinfo=UTC)
    job = EmbeddingJob.queued(
        id="emb_job_001",
        provider_id="new_api",
        embedding_model="text-embedding-v1",
        sources=[
            EmbeddingJobSource(
                source_type=EmbeddingSourceType.WRONG_QUESTION_ANALYSIS,
                source_id="wq_001",
                content_hash="sha256:wrong-question",
                text="一次函数应用题中斜率和截距混淆。",
                metadata={"subject": "math"},
            ),
            EmbeddingJobSource(
                source_type=EmbeddingSourceType.PUBLIC_QUESTION_TEMPLATE,
                source_id="template_001",
                content_hash="sha256:template",
                text="一次函数应用题模板。",
                metadata={"questionType": "application"},
            ),
        ],
        created_at=now,
    )

    assert job.status == EmbeddingJobStatus.QUEUED
    assert job.total_texts == 2
    assert job.embedded_texts == 0
    assert job.skipped_texts == 0
    assert job.failed_texts == 0
    assert job.source_types == (
        EmbeddingSourceType.WRONG_QUESTION_ANALYSIS,
        EmbeddingSourceType.PUBLIC_QUESTION_TEMPLATE,
    )


def test_embedding_index_skips_duplicate_content_hash_and_model() -> None:
    index = InMemoryEmbeddingIndex()
    record = EmbeddingVectorRecord(
        id="vec_001",
        source_type=EmbeddingSourceType.WRONG_QUESTION_ANALYSIS,
        source_id="wq_001",
        chunk_id="chunk_001",
        embedding_model="text-embedding-v1",
        content_hash="sha256:wrong-question",
        vector=(0.1, 0.2, 0.3),
        metadata={"subject": "math"},
    )

    first_result = index.upsert(record)
    second_result = index.upsert(record)
    changed_result = index.upsert(
        EmbeddingVectorRecord(
            id="vec_002",
            source_type=EmbeddingSourceType.WRONG_QUESTION_ANALYSIS,
            source_id="wq_001",
            chunk_id="chunk_001",
            embedding_model="text-embedding-v2",
            content_hash="sha256:wrong-question",
            vector=(0.4, 0.5, 0.6),
            metadata={"subject": "math"},
        )
    )

    assert first_result == VectorUpsertStatus.UPSERTED
    assert second_result == VectorUpsertStatus.SKIPPED_DUPLICATE
    assert changed_result == VectorUpsertStatus.UPSERTED
    assert len(index.list_records()) == 2


def test_retrieval_result_contract_includes_source_ids_scores_and_trust_tier() -> None:
    result = RetrievalResult(
        source_type=EmbeddingSourceType.PUBLIC_KNOWLEDGE_CHUNK,
        source_id="source_001",
        chunk_id="chunk_001",
        knowledge_layer=KnowledgeLayer.CURRICULUM,
        text="一次函数的图像是一条直线。",
        similarity_score=0.82,
        trust_score=0.9,
        final_score=0.86,
        trust_tier=RetrievalTrustTier.CURATED,
        metadata={"subject": "math", "gradeBand": "middle_school"},
    )

    assert result.source_type == EmbeddingSourceType.PUBLIC_KNOWLEDGE_CHUNK
    assert result.source_id == "source_001"
    assert result.trust_tier == RetrievalTrustTier.CURATED
    assert result.metadata["subject"] == "math"
