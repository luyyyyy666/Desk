from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_learning_os_openapi_contract_declares_phase3_memory_paths() -> None:
    content = (ROOT / "contracts" / "openapi" / "learning-os.yaml").read_text(
        encoding="utf-8"
    )

    for path in [
        "/api/memory/public-knowledge/status:",
        "/api/memory/public-knowledge/import-empty-seed:",
        "/api/memory/snapshot/{user_id}:",
        "/api/memory/wrong-questions:",
        "/api/memory/user-knowledge-notes:",
        "/api/memory/user-knowledge-feedback:",
        "/api/memory/user-knowledge/{knowledge_point_id}:",
        "/api/memory/user-knowledge/{knowledge_point_id}/state:",
        "/api/memory/personal-knowledge/builds:",
        "/api/memory/daily-practice/targets:",
        "/api/memory/daily-practice/generation-plan:",
        "/api/memory/hybrid-retrieval/plan:",
        "/api/memory/practice-attempts/analysis:",
        "/api/memory/generated-questions:",
        "/api/memory/generated-questions/{question_id}/verification/start:",
        "/api/memory/generated-questions/{question_id}/verification-reports:",
        "/api/memory/generated-questions/{question_id}/approve-for-practice:",
        "/api/memory/generated-questions/{question_id}/used-in-daily-practice:",
    ]:
        assert path in content


def test_learning_os_openapi_contract_declares_phase3_memory_schemas() -> None:
    content = (ROOT / "contracts" / "openapi" / "learning-os.yaml").read_text(
        encoding="utf-8"
    )

    for schema in [
        "Phase3MemorySnapshot:",
        "PublicKnowledgeStatus:",
        "PublicKnowledgeImportResponse:",
        "WrongQuestionCreateRequest:",
        "UserKnowledgeNoteRequest:",
        "UserKnowledgeFeedbackRequest:",
        "UserKnowledgeNotesAndFeedbackResponse:",
        "UserKnowledgeStateResponse:",
        "ReviewScheduleItem:",
        "PersonalKnowledgeBuildActivateRequest:",
        "DailyPracticeTargetsResponse:",
        "DailyPracticeGenerationPlanResponse:",
        "HybridRetrievalPlanRequest:",
        "HybridRetrievalPlanResponse:",
        "PracticeAttemptAnalysisRequest:",
        "GeneratedQuestionRequest:",
        "GeneratedQuestionKnowledgeLink:",
        "QuestionVerificationReportRequest:",
    ]:
        assert schema in content

    assert "curated public knowledge content is intentionally empty" in content
    assert "knowledgePointLinks" in content
    assert "expectedErrorTraps" in content
    assert "gradingRubric" in content
    assert "teacher" not in content.lower()
    assert "student" not in content.lower()
    assert "classroom" not in content.lower()
    assert "school" not in content.lower()
    assert "tenant" not in content.lower()


def test_learning_os_openapi_contract_declares_phase4_rag_paths() -> None:
    content = (ROOT / "contracts" / "openapi" / "learning-os.yaml").read_text(
        encoding="utf-8"
    )

    for path in [
        "/api/embeddings/provider-status:",
        "/api/embeddings/jobs:",
        "/api/embeddings/jobs/{job_id}:",
        "/api/knowledge/embedding-search:",
    ]:
        assert path in content


def test_learning_os_openapi_contract_declares_phase4_rag_schemas() -> None:
    content = (ROOT / "contracts" / "openapi" / "learning-os.yaml").read_text(
        encoding="utf-8"
    )

    for schema in [
        "EmbeddingProviderStatusResponse:",
        "EmbeddingJobCreateRequest:",
        "EmbeddingJobResponse:",
        "EmbeddingJobSource:",
        "EmbeddingSearchPlanRequest:",
        "EmbeddingSearchPlanResponse:",
    ]:
        assert schema in content

    assert "Raw API keys are never returned" in content
    assert "executesVectorSearch" in content
