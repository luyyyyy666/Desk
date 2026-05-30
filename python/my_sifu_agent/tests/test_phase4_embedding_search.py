from my_sifu_agent.embedding_gateway import EmbeddingGatewayResult, TextEmbedding
from my_sifu_agent.rag import (
    EmbeddingSourceType,
    EmbeddingVectorRecord,
    InMemoryEmbeddingIndex,
    KnowledgeLayer,
    RetrievalTrustTier,
)
from my_sifu_agent.rag_api import Phase4RagApi


class FakeQueryEmbeddingGateway:
    def __init__(self, vector: tuple[float, ...]) -> None:
        self.vector = vector
        self.calls = []

    def embed_texts(self, texts):
        self.calls.append(list(texts))
        return EmbeddingGatewayResult(
            model="text-embedding-v1",
            embeddings=(TextEmbedding(index=0, vector=self.vector),),
            usage={"total_tokens": len(texts[0])},
        )


def test_embedding_index_search_combines_metadata_filter_and_vector_similarity() -> None:
    index = InMemoryEmbeddingIndex()
    index.upsert(
        EmbeddingVectorRecord(
            id="vec_linear",
            source_type=EmbeddingSourceType.PUBLIC_KNOWLEDGE_CHUNK,
            source_id="source_curriculum_001:chunk_0",
            chunk_id="source_curriculum_001:chunk_0",
            embedding_model="text-embedding-v1",
            content_hash="sha256:linear",
            vector=(1.0, 0.0),
            metadata={
                "subject": "math",
                "gradeBand": "middle_school",
                "knowledgeLayer": "curriculum",
                "text": "一次函数的图像是一条直线。",
            },
        )
    )
    index.upsert(
        EmbeddingVectorRecord(
            id="vec_english",
            source_type=EmbeddingSourceType.PUBLIC_KNOWLEDGE_CHUNK,
            source_id="source_english_001:chunk_0",
            chunk_id="source_english_001:chunk_0",
            embedding_model="text-embedding-v1",
            content_hash="sha256:english",
            vector=(1.0, 0.0),
            metadata={"subject": "english", "knowledgeLayer": "curriculum"},
        )
    )
    index.upsert(
        EmbeddingVectorRecord(
            id="vec_quadratic",
            source_type=EmbeddingSourceType.PUBLIC_KNOWLEDGE_CHUNK,
            source_id="source_curriculum_002:chunk_0",
            chunk_id="source_curriculum_002:chunk_0",
            embedding_model="text-embedding-v1",
            content_hash="sha256:quadratic",
            vector=(0.0, 1.0),
            metadata={
                "subject": "math",
                "gradeBand": "middle_school",
                "knowledgeLayer": "curriculum",
            },
        )
    )

    results = index.search(
        query_vector=(1.0, 0.0),
        filters={"subject": "math", "knowledgeLayer": "curriculum"},
        limit=2,
    )

    assert [result.source_id for result in results] == [
        "source_curriculum_001:chunk_0",
        "source_curriculum_002:chunk_0",
    ]
    assert results[0].similarity_score == 1.0
    assert results[0].trust_score == 0.9
    assert results[0].trust_tier == RetrievalTrustTier.CURATED
    assert results[0].knowledge_layer == KnowledgeLayer.CURRICULUM
    assert results[0].text == "一次函数的图像是一条直线。"


def test_rag_api_executes_embedding_search_with_backend_gateway() -> None:
    gateway = FakeQueryEmbeddingGateway(vector=(1.0, 0.0))
    index = InMemoryEmbeddingIndex()
    index.upsert(
        EmbeddingVectorRecord(
            id="vec_linear",
            source_type=EmbeddingSourceType.PUBLIC_KNOWLEDGE_CHUNK,
            source_id="source_curriculum_001:chunk_0",
            chunk_id="source_curriculum_001:chunk_0",
            embedding_model="text-embedding-v1",
            content_hash="sha256:linear",
            vector=(1.0, 0.0),
            metadata={
                "subject": "math",
                "gradeBand": "middle_school",
                "knowledgeLayer": "curriculum",
                "text": "一次函数的图像是一条直线。",
            },
        )
    )
    api = Phase4RagApi.default_for_new_api(
        base_url="http://127.0.0.1:3000",
        model="text-embedding-v1",
        api_key_env_var=None,
        embedding_gateway=gateway,
        embedding_index=index,
    )

    response = api.embedding_search(
        {
            "query": "一次函数",
            "filters": {"subject": "math", "knowledgeLayer": "curriculum"},
            "limit": 3,
            "rerank": True,
        }
    )

    assert response["results"][0]["sourceId"] == "source_curriculum_001:chunk_0"
    assert response["results"][0]["similarityScore"] == 1.0
    assert response["results"][0]["trustScore"] == 0.9
    assert response["results"][0]["finalScore"] == 0.95
    assert response["executesVectorSearch"] is True
    assert gateway.calls == [["一次函数"]]
