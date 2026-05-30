from datetime import UTC, datetime

import pytest
from my_sifu_agent.rag import AccessScope, InMemoryKnowledgeSourceRepository, KnowledgeLayer
from my_sifu_agent.rag_api import Phase4RagApi


def test_ingestion_splits_plain_text_source_into_stable_chunks() -> None:
    repository = InMemoryKnowledgeSourceRepository()
    source = repository.ingest_plain_text(
        source_id="source_textbook_001",
        title="一次函数教材节选",
        knowledge_layer=KnowledgeLayer.TEXTBOOK,
        text="第一段讲一次函数的定义。\n\n第二段讲图像是一条直线。\n\n第三段讲应用题建模。",
        metadata={"subject": "math", "gradeBand": "middle_school"},
        created_at=datetime(2026, 5, 30, 12, 0, tzinfo=UTC),
    )

    chunks = repository.list_chunks(source.id)

    assert source.id == "source_textbook_001"
    assert source.knowledge_layer == KnowledgeLayer.TEXTBOOK
    assert source.chunk_count == 3
    assert [chunk.ordinal for chunk in chunks] == [0, 1, 2]
    assert chunks[0].text == "第一段讲一次函数的定义。"
    assert chunks[0].content_hash.startswith("sha256:")
    assert chunks[0].metadata == {"subject": "math", "gradeBand": "middle_school"}


def test_ingestion_reuses_existing_chunks_for_unchanged_source_text() -> None:
    repository = InMemoryKnowledgeSourceRepository()
    now = datetime(2026, 5, 30, 12, 30, tzinfo=UTC)
    first = repository.ingest_plain_text(
        source_id="source_textbook_001",
        title="一次函数教材节选",
        knowledge_layer=KnowledgeLayer.TEXTBOOK,
        text="第一段。\n\n第二段。",
        metadata={"subject": "math"},
        created_at=now,
    )
    first_chunks = repository.list_chunks(first.id)
    second = repository.ingest_plain_text(
        source_id="source_textbook_001",
        title="一次函数教材节选",
        knowledge_layer=KnowledgeLayer.TEXTBOOK,
        text="第一段。\n\n第二段。",
        metadata={"subject": "math"},
        created_at=now,
    )

    assert second.content_hash == first.content_hash
    assert repository.list_chunks(second.id) == first_chunks


def test_rag_api_ingests_plain_text_source_and_returns_embedding_sources() -> None:
    now = datetime(2026, 5, 30, 13, 0, tzinfo=UTC)
    api = Phase4RagApi.default_for_new_api(
        base_url="http://127.0.0.1:3000",
        model="text-embedding-v1",
        api_key_env_var=None,
    )

    response = api.ingest_plain_text(
        {
            "sourceId": "source_curriculum_001",
            "title": "一次函数课程标准",
            "knowledgeLayer": "curriculum",
            "sourceFormat": "plain_text",
            "text": "理解一次函数。\n\n会画一次函数图像。",
            "metadata": {"subject": "math", "examStage": "zhongkao"},
            "createdAt": now.isoformat(),
        }
    )

    assert response["source"]["id"] == "source_curriculum_001"
    assert response["source"]["knowledgeLayer"] == "curriculum"
    assert response["source"]["chunkCount"] == 2
    assert [chunk["ordinal"] for chunk in response["chunks"]] == [0, 1]
    assert response["embeddingSources"][0]["sourceType"] == "public_knowledge_chunk"
    assert response["embeddingSources"][0]["sourceId"] == "source_curriculum_001:chunk_0"
    assert response["embeddingSources"][0]["text"] == "理解一次函数。"
    assert response["embeddingSources"][0]["metadata"]["accessScope"] == AccessScope.PUBLIC.value


def test_rag_api_rejects_unknown_ingest_format() -> None:
    api = Phase4RagApi.default_for_new_api(
        base_url="http://127.0.0.1:3000",
        model="text-embedding-v1",
        api_key_env_var=None,
    )

    with pytest.raises(ValueError, match="plain_text"):
        api.ingest_plain_text(
            {
                "sourceId": "source_pdf_001",
                "title": "待解析 PDF",
                "knowledgeLayer": "textbook",
                "sourceFormat": "pdf",
                "text": "placeholder",
                "metadata": {},
                "createdAt": datetime(2026, 5, 30, 13, 30, tzinfo=UTC).isoformat(),
            }
        )
