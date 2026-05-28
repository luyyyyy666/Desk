from datetime import UTC, datetime, timedelta

import pytest
from my_sifu_agent.memory import (
    DailyPracticePlanMode,
    EvidenceType,
    GeneratedQuestionMode,
    GeneratedQuestionStatus,
    MasteryState,
    PersonalKnowledgeBuildStatus,
    ReviewScheduleStatus,
)
from my_sifu_agent.memory_api import Phase3MemoryApi


def test_memory_api_bootstraps_empty_public_kb_and_returns_snapshot_json() -> None:
    now = datetime(2026, 5, 28, 8, 0, tzinfo=UTC)
    api = Phase3MemoryApi.empty()

    import_response = api.import_empty_public_knowledge()
    snapshot = api.get_memory_snapshot("user_001", now=now)

    assert import_response == {
        "imported": {
            "knowledgePoints": 0,
            "tags": 0,
            "pointTags": 0,
            "edges": 0,
        },
        "publicKnowledge": {
            "knowledgePoints": 0,
            "tags": 0,
            "edges": 0,
            "isEmpty": True,
        },
    }
    assert snapshot["userId"] == "user_001"
    assert snapshot["publicKnowledge"]["isEmpty"] is True
    assert snapshot["wrongQuestionCount"] == 0
    assert snapshot["activePersonalBuild"] is None


def test_memory_api_records_wrong_question_without_promoting_it_to_personal_nodes() -> None:
    now = datetime(2026, 5, 28, 9, 0, tzinfo=UTC)
    api = Phase3MemoryApi.empty()

    api.record_wrong_question(
        {
            "id": "wq_001",
            "userId": "user_001",
            "questionText": "A raw wrong question.",
            "correctAnswer": "correct",
            "userAnswer": "wrong",
            "explanation": "raw explanation",
            "source": "manual",
            "subject": "math",
            "createdAt": now.isoformat(),
            "knowledgeLinks": [
                {
                    "knowledgePointId": "kp_linear_modeling",
                    "role": "primary",
                    "contentWeight": 0.8,
                    "source": "llm",
                    "confidence": 0.82,
                }
            ],
            "tagLinks": [
                {
                    "tagId": "tag_modeling_error",
                    "source": "llm",
                    "confidence": 0.8,
                }
            ],
        }
    )
    snapshot = api.get_memory_snapshot("user_001", now=now)

    assert snapshot["wrongQuestionCount"] == 1
    assert snapshot["personalNodeCount"] == 0


def test_memory_api_activates_personal_build_and_selects_due_targets() -> None:
    now = datetime(2026, 5, 28, 10, 0, tzinfo=UTC)
    api = Phase3MemoryApi.empty()

    build_response = api.activate_personal_knowledge_build(
        {
            "build": {
                "id": "pkb_001",
                "userId": "user_001",
                "buildVersion": 1,
                "model": "manual-test",
                "promptVersion": "phase3-test",
                "publicKbVersion": "empty-v0",
                "status": PersonalKnowledgeBuildStatus.BUILDING.value,
                "createdAt": now.isoformat(),
            },
            "nodes": [
                {
                    "id": "node_due",
                    "buildId": "pkb_001",
                    "userId": "user_001",
                    "knowledgePointId": "kp_due",
                    "masteryState": MasteryState.REVIEWING.value,
                    "masteryScore": 0.4,
                    "weaknessScore": 0.6,
                    "confidence": 0.8,
                    "evidenceCount": 1,
                    "summary": "Due for review.",
                    "summaryForEmbedding": "due review",
                    "createdAt": now.isoformat(),
                    "updatedAt": now.isoformat(),
                }
            ],
            "edges": [],
            "evidence": [
                {
                    "id": "ev_due",
                    "buildId": "pkb_001",
                    "userId": "user_001",
                    "targetType": "node",
                    "targetId": "node_due",
                    "evidenceType": EvidenceType.WRONG_QUESTION.value,
                    "evidenceId": "wq_001",
                    "analysisSummary": "Wrong question evidence.",
                    "createdAt": now.isoformat(),
                }
            ],
        }
    )
    api.schedule_review(
        {
            "id": "review_due",
            "userId": "user_001",
            "knowledgePointId": "kp_due",
            "nextReviewAt": (now - timedelta(hours=1)).isoformat(),
            "intervalDays": 2,
            "easeFactor": 2.0,
            "consecutiveSuccesses": 0,
            "status": ReviewScheduleStatus.ACTIVE.value,
            "createdAt": now.isoformat(),
            "updatedAt": now.isoformat(),
        }
    )

    targets = api.get_daily_practice_targets("user_001", now=now, limit=3)
    snapshot = api.get_memory_snapshot("user_001", now=now)

    assert build_response["build"]["id"] == "pkb_001"
    assert build_response["build"]["status"] == PersonalKnowledgeBuildStatus.ACTIVE.value
    assert targets["targets"][0]["knowledgePointId"] == "kp_due"
    assert snapshot["dueReviewCount"] == 1


def test_memory_api_returns_daily_practice_generation_plan_defaults() -> None:
    api = Phase3MemoryApi.empty()

    default_plan = api.get_daily_practice_generation_plan(
        "default",
        ["kp_linear_modeling", "kp_due"],
    )
    enhanced_plan = api.get_daily_practice_generation_plan(
        DailyPracticePlanMode.ENHANCED.value,
        ["kp_linear_modeling"],
    )

    assert default_plan["plan"]["totalQuestionCount"] == 3
    assert default_plan["plan"]["llmGeneratedQuestionCount"] == 1
    assert default_plan["plan"]["stableBankQuestionCount"] == 2
    assert default_plan["plan"]["generationModes"] == ["stable_bank", "llm_tool_generated"]
    assert enhanced_plan["plan"]["llmGeneratedQuestionCount"] == 3


def test_memory_api_returns_hybrid_retrieval_plan_without_running_rag() -> None:
    api = Phase3MemoryApi.empty()

    response = api.plan_hybrid_retrieval(
        {
            "query": "一次函数",
            "subject": "math",
            "gradeBand": "middle_school",
            "examStage": "zhongkao",
            "knowledgePointIds": ["kp_linear_function"],
            "tagIds": ["tag_application_problem"],
            "includePublicGraph": True,
            "includePersonalGraph": True,
            "vectorQueryText": "一次函数应用题错因",
            "rerank": True,
            "embeddingJobId": None,
        }
    )

    assert response["plan"]["pipeline"] == [
        "structured_filter",
        "graph_expansion",
        "vector_search",
        "rerank",
    ]
    assert response["plan"]["embeddingJobId"] is None
    assert response["plan"]["executesRetrieval"] is False


def test_memory_api_records_practice_analysis_with_error_weight() -> None:
    now = datetime(2026, 5, 28, 11, 0, tzinfo=UTC)
    api = Phase3MemoryApi.empty()

    response = api.record_practice_attempt_analysis(
        {
            "attempt": {
                "id": "attempt_001",
                "userId": "user_001",
                "questionId": "question_001",
                "userAnswer": "wrong",
                "isCorrect": False,
                "difficulty": "medium",
                "timeSpentSeconds": 120,
                "hintUsed": True,
                "reviewedExplanation": True,
                "createdAt": now.isoformat(),
            },
            "analysis": {
                "id": "analysis_001",
                "attemptId": "attempt_001",
                "model": "manual-test",
                "promptVersion": "phase3-test",
                "analysisSummary": "Main error responsibility.",
                "masteryDelta": -0.06,
                "weaknessDelta": 0.1,
                "confidence": 0.83,
                "createdAt": now.isoformat(),
            },
            "errorLinks": [
                {
                    "knowledgePointId": "kp_due",
                    "errorWeight": 0.9,
                    "tagId": "tag_error",
                    "evidenceSummary": "Main error responsibility.",
                    "confidence": 0.84,
                }
            ],
        }
    )
    snapshot = api.get_memory_snapshot("user_001", now=now)

    assert response["analysis"]["id"] == "analysis_001"
    assert response["errorLinks"][0]["errorWeight"] == 0.9
    assert snapshot["practiceAttemptCount"] == 1
    assert snapshot["practiceAnalysisCount"] == 1


def test_memory_api_exposes_mastery_pending_confirmation_and_user_confirmation() -> None:
    now = datetime(2026, 5, 28, 11, 30, tzinfo=UTC)
    api = Phase3MemoryApi.empty()
    api.activate_personal_knowledge_build(
        {
            "build": {
                "id": "pkb_001",
                "userId": "user_001",
                "buildVersion": 1,
                "model": "manual-test",
                "promptVersion": "phase3-test",
                "publicKbVersion": "empty-v0",
                "status": PersonalKnowledgeBuildStatus.BUILDING.value,
                "createdAt": now.isoformat(),
            },
            "nodes": [
                {
                    "id": "node_due",
                    "buildId": "pkb_001",
                    "userId": "user_001",
                    "knowledgePointId": "kp_due",
                    "masteryState": MasteryState.REVIEWING.value,
                    "masteryScore": 0.86,
                    "weaknessScore": 0.14,
                    "confidence": 0.84,
                    "evidenceCount": 1,
                    "summary": "Almost mastered.",
                    "summaryForEmbedding": "almost mastered",
                    "createdAt": now.isoformat(),
                    "updatedAt": now.isoformat(),
                }
            ],
            "edges": [],
            "evidence": [
                {
                    "id": "ev_due",
                    "buildId": "pkb_001",
                    "userId": "user_001",
                    "targetType": "node",
                    "targetId": "node_due",
                    "evidenceType": EvidenceType.WRONG_QUESTION.value,
                    "evidenceId": "wq_001",
                    "analysisSummary": "Prior evidence.",
                    "createdAt": now.isoformat(),
                }
            ],
        }
    )
    api.schedule_review(
        {
            "id": "review_due",
            "userId": "user_001",
            "knowledgePointId": "kp_due",
            "nextReviewAt": (now - timedelta(hours=1)).isoformat(),
            "intervalDays": 2,
            "easeFactor": 2.0,
            "consecutiveSuccesses": 2,
            "status": ReviewScheduleStatus.ACTIVE.value,
            "createdAt": now.isoformat(),
            "updatedAt": now.isoformat(),
        }
    )
    api.submit_generated_question(
        {
            "id": "question_due",
            "userId": "user_001",
            "generationRequestId": "request_001",
            "generationAttempt": 1,
            "mode": GeneratedQuestionMode.LLM_TOOL_GENERATED.value,
            "status": GeneratedQuestionStatus.APPROVED_FOR_PRACTICE.value,
            "stem": "Correct practice question.",
            "answer": "A",
            "explanation": "Explanation.",
            "knowledgePointLinks": [
                {
                    "knowledgePointId": "kp_due",
                    "contentWeight": 1.0,
                    "role": "primary",
                }
            ],
            "expectedErrorTraps": [],
            "gradingRubric": "",
            "difficulty": "medium",
            "questionType": "open_response",
            "model": "generator-model",
            "promptVersion": "phase3-test",
            "publicKbVersion": "empty-v0",
            "personalKnowledgeBuildId": "pkb_001",
            "createdAt": now.isoformat(),
        }
    )

    api.record_practice_attempt_analysis(
        {
            "attempt": {
                "id": "attempt_correct",
                "userId": "user_001",
                "questionId": "question_due",
                "userAnswer": "A",
                "isCorrect": True,
                "difficulty": "medium",
                "timeSpentSeconds": 90,
                "hintUsed": False,
                "reviewedExplanation": True,
                "createdAt": now.isoformat(),
            },
            "analysis": {
                "id": "analysis_correct",
                "attemptId": "attempt_correct",
                "model": "manual-test",
                "promptVersion": "phase3-test",
                "analysisSummary": "Correct answer confirms mastery improvement.",
                "masteryDelta": 0.08,
                "weaknessDelta": -0.08,
                "confidence": 0.9,
                "createdAt": now.isoformat(),
            },
            "errorLinks": [],
        }
    )

    pending = api.get_user_knowledge_state("user_001", "kp_due")
    assert pending["node"]["masteryState"] == MasteryState.MASTERED_PENDING_CONFIRM.value
    assert pending["reviewSchedule"]["status"] == (
        ReviewScheduleStatus.MASTERED_PENDING_CONFIRM.value
    )

    api.record_user_knowledge_feedback(
        {
            "id": "feedback_mastered",
            "userId": "user_001",
            "knowledgePointId": "kp_due",
            "feedbackType": "mark_mastered",
            "comment": "确认掌握。",
            "createdAt": now.isoformat(),
        }
    )

    mastered = api.get_user_knowledge_state("user_001", "kp_due")
    assert mastered["node"]["masteryState"] == MasteryState.MASTERED.value
    assert mastered["reviewSchedule"]["status"] == ReviewScheduleStatus.MASTERED.value


def test_memory_api_enforces_verifier_gate_for_generated_questions() -> None:
    now = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)
    api = Phase3MemoryApi.empty()
    api.submit_generated_question(
        {
            "id": "gq_001",
            "userId": "user_001",
            "generationRequestId": "request_001",
            "generationAttempt": 1,
            "mode": GeneratedQuestionMode.LLM_TOOL_GENERATED.value,
            "status": GeneratedQuestionStatus.DRAFT_GENERATED.value,
            "stem": "Generated question.",
            "answer": "A",
            "explanation": "Explanation.",
            "knowledgePointLinks": [],
            "expectedErrorTraps": [],
            "gradingRubric": "",
            "difficulty": "medium",
            "questionType": "open_response",
            "model": "generator-model",
            "promptVersion": "phase3-test",
            "publicKbVersion": "empty-v0",
            "personalKnowledgeBuildId": "pkb_001",
            "createdAt": now.isoformat(),
        }
    )

    with pytest.raises(ValueError, match="verification"):
        api.approve_generated_question_for_practice("gq_001")

    api.start_question_verification("gq_001")
    api.record_question_verification(
        {
            "id": "report_001",
            "questionId": "gq_001",
            "verifierAgentId": "verifier_001",
            "verdict": "passed",
            "verifierAnswer": "A",
            "issueSummary": "No issue.",
            "failedReasonType": None,
            "confidence": 0.92,
            "createdAt": now.isoformat(),
        }
    )
    approved = api.approve_generated_question_for_practice("gq_001")

    assert approved["question"]["status"] == GeneratedQuestionStatus.APPROVED_FOR_PRACTICE.value
    used = api.mark_generated_question_used_in_daily_practice("gq_001")

    assert used["question"]["status"] == GeneratedQuestionStatus.USED_IN_DAILY_PRACTICE.value
