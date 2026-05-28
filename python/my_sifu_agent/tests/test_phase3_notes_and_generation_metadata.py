from datetime import UTC, datetime

from my_sifu_agent.memory import (
    GeneratedQuestion,
    GeneratedQuestionKnowledgeLink,
    GeneratedQuestionMode,
    GeneratedQuestionStatus,
    KnowledgeLinkRole,
    Phase3MemoryWorkspace,
    UserKnowledgeFeedback,
    UserKnowledgeFeedbackType,
    UserKnowledgeNote,
)
from my_sifu_agent.memory_api import Phase3MemoryApi


def test_workspace_keeps_user_notes_and_feedback_separate_from_calculated_state() -> None:
    now = datetime(2026, 5, 28, 13, 0, tzinfo=UTC)
    workspace = Phase3MemoryWorkspace.empty()
    note = UserKnowledgeNote(
        id="note_001",
        user_id="user_001",
        knowledge_point_id="kp_linear_modeling",
        note="我总是把固定费用和单价写反。",
        custom_tags=("易错", "建模"),
        created_at=now,
        updated_at=now,
    )
    feedback = UserKnowledgeFeedback(
        id="feedback_001",
        user_id="user_001",
        knowledge_point_id="kp_linear_modeling",
        feedback_type=UserKnowledgeFeedbackType.CONFIRM_WEAKNESS,
        comment="确实需要继续练。",
        created_at=now,
    )

    workspace.upsert_user_knowledge_note(note)
    workspace.record_user_knowledge_feedback(feedback)
    snapshot = workspace.snapshot("user_001", now=now)

    assert workspace.list_user_knowledge_notes("user_001", "kp_linear_modeling") == [note]
    assert workspace.list_user_knowledge_feedback("user_001", "kp_linear_modeling") == [feedback]
    assert snapshot.user_knowledge_note_count == 1
    assert snapshot.user_knowledge_feedback_count == 1
    assert snapshot.personal_node_count == 0
    assert snapshot.personal_evidence_count == 0


def test_memory_api_round_trips_user_notes_and_feedback() -> None:
    now = datetime(2026, 5, 28, 14, 0, tzinfo=UTC)
    api = Phase3MemoryApi.empty()

    note_response = api.upsert_user_knowledge_note(
        {
            "id": "note_001",
            "userId": "user_001",
            "knowledgePointId": "kp_linear_modeling",
            "note": "用自己的话解释截距。",
            "customTags": ["手写笔记", "复习"],
            "createdAt": now.isoformat(),
            "updatedAt": now.isoformat(),
        }
    )
    feedback_response = api.record_user_knowledge_feedback(
        {
            "id": "feedback_001",
            "userId": "user_001",
            "knowledgePointId": "kp_linear_modeling",
            "feedbackType": UserKnowledgeFeedbackType.MARK_MASTERED.value,
            "comment": "这类题我已经掌握，先暂停推荐。",
            "createdAt": now.isoformat(),
        }
    )
    list_response = api.get_user_knowledge_notes_and_feedback(
        "user_001",
        "kp_linear_modeling",
    )

    assert note_response["note"]["customTags"] == ["手写笔记", "复习"]
    assert feedback_response["feedback"]["feedbackType"] == "mark_mastered"
    assert list_response["notes"][0]["note"] == "用自己的话解释截距。"
    assert list_response["feedback"][0]["comment"] == "这类题我已经掌握，先暂停推荐。"


def test_generated_question_keeps_structured_metadata_for_verifier_and_practice() -> None:
    now = datetime(2026, 5, 28, 15, 0, tzinfo=UTC)
    workspace = Phase3MemoryWorkspace.empty()
    question = workspace.submit_generated_question(
        GeneratedQuestion(
            id="gq_001",
            user_id="user_001",
            generation_request_id="request_001",
            generation_attempt=1,
            mode=GeneratedQuestionMode.LLM_TOOL_GENERATED,
            status=GeneratedQuestionStatus.DRAFT_GENERATED,
            stem="A linear function application problem.",
            answer="y = 0.4x + 5",
            explanation="The fixed fee is the intercept.",
            knowledge_point_links=(
                GeneratedQuestionKnowledgeLink(
                    knowledge_point_id="kp_linear_modeling",
                    content_weight=0.75,
                    role=KnowledgeLinkRole.PRIMARY,
                ),
            ),
            expected_error_traps=("slope_intercept_confusion",),
            grading_rubric="Check expression, substitution, and final amount.",
            difficulty="medium",
            question_type="open_response",
            model="generator-model",
            prompt_version="phase3-test",
            public_kb_version="empty-v0",
            personal_knowledge_build_id="pkb_001",
            created_at=now,
        )
    )

    assert question.knowledge_point_links[0].content_weight == 0.75
    assert question.expected_error_traps == ("slope_intercept_confusion",)
    assert "substitution" in question.grading_rubric


def test_memory_api_preserves_generated_question_structured_metadata() -> None:
    now = datetime(2026, 5, 28, 16, 0, tzinfo=UTC)
    api = Phase3MemoryApi.empty()

    response = api.submit_generated_question(
        {
            "id": "gq_001",
            "userId": "user_001",
            "generationRequestId": "request_001",
            "generationAttempt": 1,
            "mode": GeneratedQuestionMode.LLM_TOOL_GENERATED.value,
            "status": GeneratedQuestionStatus.DRAFT_GENERATED.value,
            "stem": "A generated problem.",
            "answer": "42",
            "explanation": "Checked explanation.",
            "knowledgePointLinks": [
                {
                    "knowledgePointId": "kp_linear_modeling",
                    "contentWeight": 0.75,
                    "role": "primary",
                }
            ],
            "expectedErrorTraps": ["slope_intercept_confusion"],
            "gradingRubric": "Expression, substitution, final answer.",
            "difficulty": "medium",
            "questionType": "open_response",
            "model": "generator-model",
            "promptVersion": "phase3-test",
            "publicKbVersion": "empty-v0",
            "personalKnowledgeBuildId": "pkb_001",
            "createdAt": now.isoformat(),
        }
    )

    assert response["question"]["knowledgePointLinks"][0]["contentWeight"] == 0.75
    assert response["question"]["expectedErrorTraps"] == ["slope_intercept_confusion"]
    assert response["question"]["gradingRubric"] == "Expression, substitution, final answer."
