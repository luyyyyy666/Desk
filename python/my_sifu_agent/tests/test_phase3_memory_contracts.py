from datetime import UTC, datetime, timedelta

import pytest
from my_sifu_agent.memory import (
    DailyPracticeService,
    EvidenceType,
    FailedReasonType,
    GeneratedQuestion,
    GeneratedQuestionKnowledgeLink,
    GeneratedQuestionMode,
    GeneratedQuestionStatus,
    HybridRetrievalRequest,
    InMemoryGeneratedQuestionRepository,
    InMemoryPersonalKnowledgeRepository,
    InMemoryPracticeRepository,
    InMemoryPublicKnowledgeRepository,
    InMemoryReviewScheduleRepository,
    InMemoryWrongQuestionRepository,
    KnowledgeLinkRole,
    LinkSource,
    MasteryState,
    PersonalEdgeRelationType,
    PersonalKnowledgeBuild,
    PersonalKnowledgeBuildStatus,
    PersonalKnowledgeEdge,
    PersonalKnowledgeEvidence,
    PersonalKnowledgeNode,
    PracticeAttempt,
    PracticeAttemptAnalysis,
    PublicKnowledgeSeedData,
    QuestionGenerationService,
    QuestionVerificationReport,
    ReviewScheduleItem,
    ReviewScheduleStatus,
    TagLink,
    VerificationVerdict,
    WrongQuestion,
    WrongQuestionKnowledgeLink,
)


def test_public_knowledge_repository_starts_empty_and_accepts_empty_seed_only() -> None:
    repository = InMemoryPublicKnowledgeRepository()

    result = repository.import_seed(PublicKnowledgeSeedData.empty())

    assert result.knowledge_points == 0
    assert result.tags == 0
    assert result.edges == 0
    assert repository.list_knowledge_points() == []
    assert repository.list_tags() == []
    assert repository.list_edges() == []


def test_wrong_questions_are_raw_evidence_with_weighted_knowledge_and_tags() -> None:
    repository = InMemoryWrongQuestionRepository()
    wrong_question = WrongQuestion(
        id="wq_001",
        user_id="user_001",
        question_text="Solve a combined linear-function application problem.",
        correct_answer="y = 0.4x + 5",
        user_answer="y = 5x + 0.4",
        explanation="The fixed fee is the intercept and the per-page cost is the slope.",
        source="manual",
        subject="math",
        created_at=datetime(2026, 5, 19, 10, 0, tzinfo=UTC),
    )
    knowledge_link = WrongQuestionKnowledgeLink(
        wrong_question_id="wq_001",
        knowledge_point_id="kp_linear_modeling",
        role=KnowledgeLinkRole.PRIMARY,
        content_weight=0.7,
        source=LinkSource.LLM,
        confidence=0.83,
    )
    tag_link = TagLink(
        target_id="wq_001",
        tag_id="tag_slope_intercept_confusion",
        source=LinkSource.LLM,
        confidence=0.81,
    )

    repository.add_wrong_question(
        wrong_question,
        knowledge_links=[knowledge_link],
        tag_links=[tag_link],
    )

    assert repository.list_wrong_questions("user_001") == [wrong_question]
    assert repository.list_knowledge_links("wq_001") == [knowledge_link]
    assert repository.list_tag_links("wq_001") == [tag_link]


def test_personal_knowledge_builds_nodes_edges_and_evidence_are_versioned() -> None:
    repository = InMemoryPersonalKnowledgeRepository()
    first_build = repository.create_build(
        PersonalKnowledgeBuild(
            id="pkb_001",
            user_id="user_001",
            build_version=1,
            model="manual-test",
            prompt_version="phase3-test",
            public_kb_version="empty-v0",
            status=PersonalKnowledgeBuildStatus.BUILDING,
            created_at=datetime(2026, 5, 19, 10, 0, tzinfo=UTC),
        )
    )
    repository.activate_build(first_build.id)

    second_build = repository.create_build(
        PersonalKnowledgeBuild(
            id="pkb_002",
            user_id="user_001",
            build_version=2,
            model="manual-test",
            prompt_version="phase3-test",
            public_kb_version="empty-v0",
            status=PersonalKnowledgeBuildStatus.BUILDING,
            created_at=datetime(2026, 5, 20, 10, 0, tzinfo=UTC),
        )
    )
    repository.activate_build(second_build.id)

    node = repository.add_node(
        PersonalKnowledgeNode(
            id="pkn_001",
            build_id=second_build.id,
            user_id="user_001",
            knowledge_point_id="kp_linear_modeling",
            mastery_state=MasteryState.WEAK,
            mastery_score=0.22,
            weakness_score=0.78,
            confidence=0.76,
            evidence_count=1,
            summary="Confuses slope and intercept in application problems.",
            summary_for_embedding="slope intercept confusion linear modeling",
            created_at=datetime(2026, 5, 20, 10, 5, tzinfo=UTC),
            updated_at=datetime(2026, 5, 20, 10, 5, tzinfo=UTC),
        )
    )
    edge = repository.add_edge(
        PersonalKnowledgeEdge(
            id="pke_001",
            build_id=second_build.id,
            user_id="user_001",
            source_knowledge_point_id="kp_linear_modeling",
            target_knowledge_point_id="kp_coordinate_intersections",
            relation_type=PersonalEdgeRelationType.CO_FAILED,
            weight=0.64,
            confidence=0.7,
            evidence_count=1,
            summary="The two weak points appeared in the same wrong question.",
            summary_for_embedding="linear modeling coordinate intersections co failed",
            created_at=datetime(2026, 5, 20, 10, 6, tzinfo=UTC),
            updated_at=datetime(2026, 5, 20, 10, 6, tzinfo=UTC),
        )
    )
    evidence = repository.add_evidence(
        PersonalKnowledgeEvidence(
            id="pkev_001",
            build_id=second_build.id,
            user_id="user_001",
            target_type="node",
            target_id=node.id,
            evidence_type=EvidenceType.WRONG_QUESTION,
            evidence_id="wq_001",
            analysis_summary="Wrong question shows slope/intercept confusion.",
            created_at=datetime(2026, 5, 20, 10, 7, tzinfo=UTC),
        )
    )

    assert repository.get_build(first_build.id).status == PersonalKnowledgeBuildStatus.SUPERSEDED
    assert repository.get_active_build("user_001").id == second_build.id
    assert repository.list_nodes("user_001", second_build.id) == [node]
    assert repository.list_edges("user_001", second_build.id) == [edge]
    assert repository.list_evidence_for_target(node.id) == [evidence]


def test_daily_practice_selects_due_targets_and_records_attempt_analysis() -> None:
    now = datetime(2026, 5, 21, 8, 0, tzinfo=UTC)
    personal_repository = InMemoryPersonalKnowledgeRepository()
    schedule_repository = InMemoryReviewScheduleRepository()
    practice_repository = InMemoryPracticeRepository()
    build = personal_repository.create_build(
        PersonalKnowledgeBuild(
            id="pkb_001",
            user_id="user_001",
            build_version=1,
            model="manual-test",
            prompt_version="phase3-test",
            public_kb_version="empty-v0",
            status=PersonalKnowledgeBuildStatus.ACTIVE,
            created_at=now,
        )
    )
    personal_repository.add_node(
        PersonalKnowledgeNode(
            id="pkn_due",
            build_id=build.id,
            user_id="user_001",
            knowledge_point_id="kp_due",
            mastery_state=MasteryState.REVIEWING,
            mastery_score=0.44,
            weakness_score=0.56,
            confidence=0.8,
            evidence_count=2,
            summary="Due for review.",
            summary_for_embedding="due review",
            created_at=now,
            updated_at=now,
        )
    )
    personal_repository.add_node(
        PersonalKnowledgeNode(
            id="pkn_future",
            build_id=build.id,
            user_id="user_001",
            knowledge_point_id="kp_future",
            mastery_state=MasteryState.WEAK,
            mastery_score=0.2,
            weakness_score=0.8,
            confidence=0.7,
            evidence_count=1,
            summary="Not due yet.",
            summary_for_embedding="future review",
            created_at=now,
            updated_at=now,
        )
    )
    schedule_repository.add_item(
        ReviewScheduleItem(
            id="rsi_due",
            user_id="user_001",
            knowledge_point_id="kp_due",
            next_review_at=now - timedelta(days=1),
            interval_days=2,
            ease_factor=2.1,
            consecutive_successes=0,
            status=ReviewScheduleStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
    )
    schedule_repository.add_item(
        ReviewScheduleItem(
            id="rsi_future",
            user_id="user_001",
            knowledge_point_id="kp_future",
            next_review_at=now + timedelta(days=1),
            interval_days=2,
            ease_factor=2.1,
            consecutive_successes=0,
            status=ReviewScheduleStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
    )

    service = DailyPracticeService(personal_repository, schedule_repository, practice_repository)
    targets = service.select_due_targets("user_001", now=now, limit=3)

    assert [target.knowledge_point_id for target in targets] == ["kp_due"]

    attempt = practice_repository.add_attempt(
        PracticeAttempt(
            id="attempt_001",
            user_id="user_001",
            question_id="question_001",
            user_answer="wrong",
            is_correct=False,
            difficulty="medium",
            time_spent_seconds=180,
            hint_used=True,
            reviewed_explanation=True,
            created_at=now,
        )
    )
    analysis = practice_repository.add_analysis(
        PracticeAttemptAnalysis(
            id="analysis_001",
            attempt_id=attempt.id,
            model="manual-test",
            prompt_version="phase3-test",
            analysis_summary="Error responsibility is mainly on linear modeling.",
            mastery_delta=-0.08,
            weakness_delta=0.12,
            confidence=0.82,
            created_at=now,
        ),
        error_links=[
            {
                "knowledge_point_id": "kp_due",
                "error_weight": 0.9,
                "tag_id": "tag_modeling_error",
                "evidence_summary": "Used page cost as intercept.",
                "confidence": 0.84,
            }
        ],
    )

    assert practice_repository.list_attempts("user_001") == [attempt]
    assert practice_repository.get_analysis(attempt.id) == analysis
    assert practice_repository.list_error_links(attempt.id)[0].error_weight == 0.9


def test_generated_questions_require_verifier_approval_before_practice() -> None:
    now = datetime(2026, 5, 22, 8, 0, tzinfo=UTC)
    repository = InMemoryGeneratedQuestionRepository()
    service = QuestionGenerationService(repository)
    question = repository.add_question(
        GeneratedQuestion(
            id="gq_001",
            user_id="user_001",
            generation_request_id="request_001",
            generation_attempt=1,
            mode=GeneratedQuestionMode.LLM_TOOL_GENERATED,
            status=GeneratedQuestionStatus.DRAFT_GENERATED,
            stem="A generated linear-function question.",
            answer="42",
            explanation="A checked explanation.",
            knowledge_point_links=(
                GeneratedQuestionKnowledgeLink(
                    knowledge_point_id="kp_due",
                    content_weight=1.0,
                    role=KnowledgeLinkRole.PRIMARY,
                ),
            ),
            expected_error_traps=(),
            grading_rubric="",
            difficulty="medium",
            question_type="open_response",
            model="generator-model",
            prompt_version="phase3-test",
            public_kb_version="empty-v0",
            personal_knowledge_build_id="pkb_001",
            created_at=now,
        )
    )

    service.start_verification(question.id)
    failed_report = QuestionVerificationReport(
        id="qvr_001",
        question_id=question.id,
        verifier_agent_id="verifier_001",
        verdict=VerificationVerdict.FAILED,
        verifier_answer="not 42",
        issue_summary="Answer mismatch.",
        failed_reason_type=FailedReasonType.ANSWER_MISMATCH,
        confidence=0.9,
        created_at=now,
    )
    service.record_verification_report(failed_report)

    assert repository.get_question(question.id).status == GeneratedQuestionStatus.REGENERATED_ONCE
    with pytest.raises(ValueError, match="verification"):
        service.approve_for_practice(question.id)

    regenerated = service.start_regenerated_attempt(question.id)
    service.start_verification(regenerated.id)
    second_failed_report = QuestionVerificationReport(
        id="qvr_002",
        question_id=regenerated.id,
        verifier_agent_id="verifier_001",
        verdict=VerificationVerdict.FAILED,
        verifier_answer="still invalid",
        issue_summary="Question remains ambiguous.",
        failed_reason_type=FailedReasonType.AMBIGUOUS_CONDITION,
        confidence=0.88,
        created_at=now,
    )
    service.record_verification_report(second_failed_report)

    assert (
        repository.get_question(regenerated.id).status
        == GeneratedQuestionStatus.NEEDS_HUMAN_REVIEW
    )


def test_hybrid_retrieval_request_is_a_phase4_contract_without_embedding_execution() -> None:
    request = HybridRetrievalRequest(
        query="一次函数",
        subject="math",
        grade_band="middle_school",
        exam_stage="zhongkao",
        knowledge_point_ids=["kp_linear_function"],
        tag_ids=["tag_application_problem"],
        include_public_graph=True,
        include_personal_graph=True,
        vector_query_text="一次函数应用题错因",
        rerank=True,
    )

    assert request.pipeline == (
        "structured_filter",
        "graph_expansion",
        "vector_search",
        "rerank",
    )
    assert request.embedding_job_id is None
