from my_sifu_agent.rag_api import Phase4RagApi


def test_generation_context_consumes_retrieval_results_without_database_coupling() -> None:
    api = Phase4RagApi.default_for_new_api(
        base_url="http://127.0.0.1:3000",
        model="text-embedding-v1",
        api_key_env_var=None,
    )

    response = api.build_generation_retrieval_context(
        {
            "query": "一次函数",
            "results": [
                {
                    "sourceType": "public_knowledge_chunk",
                    "sourceId": "source_curriculum_001:chunk_0",
                    "chunkId": "source_curriculum_001:chunk_0",
                    "knowledgeLayer": "curriculum",
                    "text": "一次函数的图像是一条直线。",
                    "similarityScore": 1.0,
                    "trustScore": 0.9,
                    "finalScore": 0.95,
                    "trustTier": "curated",
                    "metadata": {"subject": "math"},
                }
            ],
        }
    )

    assert response == {
        "context": {
            "query": "一次函数",
            "sourceReferences": [
                {
                    "sourceId": "source_curriculum_001:chunk_0",
                    "chunkId": "source_curriculum_001:chunk_0",
                    "trustScore": 0.9,
                    "trustTier": "curated",
                }
            ],
            "groundingText": "一次函数的图像是一条直线。",
            "directDatabaseAccess": False,
        }
    }


def test_generation_context_can_emit_agent_run_event_for_replay() -> None:
    api = Phase4RagApi.default_for_new_api(
        base_url="http://127.0.0.1:3000",
        model="text-embedding-v1",
        api_key_env_var=None,
    )

    response = api.build_generation_retrieval_context(
        {
            "agentRunId": "run_001",
            "sequence": 3,
            "query": "一次函数",
            "results": [
                {
                    "sourceType": "public_knowledge_chunk",
                    "sourceId": "source_curriculum_001:chunk_0",
                    "chunkId": "source_curriculum_001:chunk_0",
                    "knowledgeLayer": "curriculum",
                    "text": "一次函数的图像是一条直线。",
                    "similarityScore": 1.0,
                    "trustScore": 0.9,
                    "finalScore": 0.95,
                    "trustTier": "curated",
                    "metadata": {"subject": "math"},
                }
            ],
        }
    )

    assert response["agentRunEvent"] == {
        "id": "event_run_001_3",
        "agentRunId": "run_001",
        "sequence": 3,
        "kind": "retrieval_context_ready",
        "payload": {
            "query": "一次函数",
            "sourceReferences": [
                {
                    "sourceId": "source_curriculum_001:chunk_0",
                    "chunkId": "source_curriculum_001:chunk_0",
                    "trustScore": 0.9,
                    "trustTier": "curated",
                }
            ],
            "directDatabaseAccess": False,
        },
    }
