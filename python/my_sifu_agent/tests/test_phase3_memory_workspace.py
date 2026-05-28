from datetime import UTC, datetime, timedelta

import pytest
from my_sifu_agent.memory import (
    EvidenceType,
    FailedReasonType,
    GeneratedQuestion,
    GeneratedQuestionKnowledgeLink,
    GeneratedQuestionMode,
    GeneratedQuestionStatus,
    KnowledgeLinkRole,
    LinkSource,
    MasteryState,
    PersonalEdgeRelationType,
    PersonalKnowledgeBuild,
    PersonalKnowledgeBuildStatus,
    PersonalKnowledgeEdge,
    PersonalKnowledgeEvidence,
    PersonalKnowledgeNode,
    Phase3MemoryWorkspace,
    PracticeAttempt,
    PracticeAttemptAnalysis,
    PublicKnowledgeSeedData,
    QuestionVerificationReport,
    ReviewScheduleItem,
    ReviewScheduleStatus,
    TagLink,
    UserKnowledgeFeedback,
    UserKnowledgeFeedbackType,
    VerificationVerdict,
    WrongQuestion,
    WrongQuestionKnowledgeLink,
)


def test_workspace_keeps_public_kb_empty_and_wrong_questions_out_of_personal_kb() -> None:
    now = datetime(2026, 5, 23, 8, 0, tzinfo=UTC)
    workspace = Phase3MemoryWorkspace.empty()

    import_result = workspace.bootstrap_public_knowledge(PublicKnowledgeSeedData.empty())
    workspace.record_wrong_question(
        WrongQuestion(
            id="wq_001",
            user_id="user_001",
            question_text="A raw wrong question.",
            correct_answer="correct",
            user_answer="wrong",
            explanation="A raw explanation.",
            source="manual",
            subject="math",
            created_at=now,
        ),
        knowledge_links=[
            WrongQuestionKnowledgeLink(
                wrong_question_id="wq_001",
                knowledge_point_id="kp_linear_modeling",
                role=KnowledgeLinkRole.PRIMARY,
                content_weight=0.8,
                source=LinkSource.LLM,
                confidence=0.82,
            )
        ],
        tag_links=[
            TagLink(
                target_id="wq_001",
                tag_id="tag_modeling_error",
                source=LinkSource.LLM,
                confidence=0.8,
            )
        ],
    )

    snapshot = workspace.snapshot("user_001", now=now)

    assert import_result.knowledge_points == 0
    assert snapshot.public_knowledge.is_empty is True
    assert snapshot.public_knowledge.knowledge_points == 0
    assert snapshot.wrong_question_count == 1
    assert snapshot.active_personal_build is None
    assert snapshot.personal_node_count == 0


def test_workspace_requires_evidence_for_personal_kb_activation() -> None:
    now = datetime(2026, 5, 24, 9, 0, tzinfo=UTC)
    workspace = Phase3MemoryWorkspace.empty()
    workspace.activate_personal_knowledge_build(
        PersonalKnowledgeBuild(
            id="pkb_001",
            user_id="user_001",
            build_version=1,
            model="manual-test",
            prompt_version="phase3-test",
            public_kb_version="empty-v0",
            status=PersonalKnowledgeBuildStatus.BUILDING,
            created_at=now,
        ),
        nodes=[
            PersonalKnowledgeNode(
                id="node_001",
                build_id="pkb_001",
                user_id="user_001",
                knowledge_point_id="kp_linear_modeling",
                mastery_state=MasteryState.WEAK,
                mastery_score=0.2,
                weakness_score=0.8,
                confidence=0.75,
                evidence_count=1,
                summary="Weak on linear modeling.",
                summary_for_embedding="weak linear modeling",
                created_at=now,
                updated_at=now,
            )
        ],
        edges=[],
        evidence=[
            PersonalKnowledgeEvidence(
                id="ev_001",
                build_id="pkb_001",
                user_id="user_001",
                target_type="node",
                target_id="node_001",
                evidence_type=EvidenceType.WRONG_QUESTION,
                evidence_id="wq_001",
                analysis_summary="Wrong question evidence.",
                created_at=now,
            )
        ],
    )

    with pytest.raises(ValueError, match="cite evidence"):
        workspace.activate_personal_knowledge_build(
            PersonalKnowledgeBuild(
                id="pkb_002",
                user_id="user_001",
                build_version=2,
                model="manual-test",
                prompt_version="phase3-test",
                public_kb_version="empty-v0",
                status=PersonalKnowledgeBuildStatus.BUILDING,
                created_at=now + timedelta(hours=1),
            ),
            nodes=[
                PersonalKnowledgeNode(
                    id="node_002",
                    build_id="pkb_002",
                    user_id="user_001",
                    knowledge_point_id="kp_coordinate_intersections",
                    mastery_state=MasteryState.REVIEWING,
                    mastery_score=0.4,
                    weakness_score=0.6,
                    confidence=0.7,
                    evidence_count=1,
                    summary="Needs review but has no evidence citation.",
                    summary_for_embedding="needs review no citation",
                    created_at=now,
                    updated_at=now,
                )
            ],
            edges=[],
            evidence=[],
        )

    second_build = workspace.activate_personal_knowledge_build(
        PersonalKnowledgeBuild(
            id="pkb_002",
            user_id="user_001",
            build_version=2,
            model="manual-test",
            prompt_version="phase3-test",
            public_kb_version="empty-v0",
            status=PersonalKnowledgeBuildStatus.BUILDING,
            created_at=now + timedelta(hours=1),
        ),
        nodes=[
            PersonalKnowledgeNode(
                id="node_002",
                build_id="pkb_002",
                user_id="user_001",
                knowledge_point_id="kp_coordinate_intersections",
                mastery_state=MasteryState.REVIEWING,
                mastery_score=0.4,
                weakness_score=0.6,
                confidence=0.7,
                evidence_count=1,
                summary="Needs review with evidence.",
                summary_for_embedding="needs review with evidence",
                created_at=now,
                updated_at=now,
            )
        ],
        edges=[
            PersonalKnowledgeEdge(
                id="edge_001",
                build_id="pkb_002",
                user_id="user_001",
                source_knowledge_point_id="kp_linear_modeling",
                target_knowledge_point_id="kp_coordinate_intersections",
                relation_type=PersonalEdgeRelationType.CO_FAILED,
                weight=0.55,
                confidence=0.72,
                evidence_count=1,
                summary="Two knowledge points co-failed.",
                summary_for_embedding="co failed linear coordinate",
                created_at=now,
                updated_at=now,
            )
        ],
        evidence=[
            PersonalKnowledgeEvidence(
                id="ev_002",
                build_id="pkb_002",
                user_id="user_001",
                target_type="node",
                target_id="node_002",
                evidence_type=EvidenceType.WRONG_QUESTION,
                evidence_id="wq_001",
                analysis_summary="Node evidence.",
                created_at=now,
            ),
            PersonalKnowledgeEvidence(
                id="ev_003",
                build_id="pkb_002",
                user_id="user_001",
                target_type="edge",
                target_id="edge_001",
                evidence_type=EvidenceType.WRONG_QUESTION,
                evidence_id="wq_001",
                analysis_summary="Edge evidence.",
                created_at=now,
            ),
        ],
    )

    snapshot = workspace.snapshot("user_001", now=now)

    assert second_build.status == PersonalKnowledgeBuildStatus.ACTIVE
    assert snapshot.active_personal_build is not None
    assert snapshot.active_personal_build.build_id == "pkb_002"
    assert snapshot.active_personal_build.build_version == 2
    assert snapshot.personal_node_count == 1
    assert snapshot.personal_edge_count == 1
    assert snapshot.personal_evidence_count == 2


def test_workspace_daily_practice_records_attempt_analysis_and_uses_due_personal_targets() -> None:
    now = datetime(2026, 5, 25, 7, 30, tzinfo=UTC)
    workspace = Phase3MemoryWorkspace.empty()
    workspace.activate_personal_knowledge_build(
        PersonalKnowledgeBuild(
            id="pkb_001",
            user_id="user_001",
            build_version=1,
            model="manual-test",
            prompt_version="phase3-test",
            public_kb_version="empty-v0",
            status=PersonalKnowledgeBuildStatus.BUILDING,
            created_at=now,
        ),
        nodes=[
            PersonalKnowledgeNode(
                id="node_due",
                build_id="pkb_001",
                user_id="user_001",
                knowledge_point_id="kp_due",
                mastery_state=MasteryState.REVIEWING,
                mastery_score=0.45,
                weakness_score=0.55,
                confidence=0.81,
                evidence_count=1,
                summary="Due review.",
                summary_for_embedding="due review",
                created_at=now,
                updated_at=now,
            )
        ],
        edges=[],
        evidence=[
            PersonalKnowledgeEvidence(
                id="ev_due",
                build_id="pkb_001",
                user_id="user_001",
                target_type="node",
                target_id="node_due",
                evidence_type=EvidenceType.WRONG_QUESTION,
                evidence_id="wq_001",
                analysis_summary="Due node evidence.",
                created_at=now,
            )
        ],
    )
    workspace.schedule_review(
        ReviewScheduleItem(
            id="review_due",
            user_id="user_001",
            knowledge_point_id="kp_due",
            next_review_at=now - timedelta(hours=1),
            interval_days=2,
            ease_factor=2.0,
            consecutive_successes=0,
            status=ReviewScheduleStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
    )
    workspace.record_practice_attempt_analysis(
        PracticeAttempt(
            id="attempt_001",
            user_id="user_001",
            question_id="question_001",
            user_answer="wrong",
            is_correct=False,
            difficulty="medium",
            time_spent_seconds=120,
            hint_used=True,
            reviewed_explanation=True,
            created_at=now,
        ),
        PracticeAttemptAnalysis(
            id="analysis_001",
            attempt_id="attempt_001",
            model="manual-test",
            prompt_version="phase3-test",
            analysis_summary="Error is mostly on the due knowledge point.",
            mastery_delta=-0.06,
            weakness_delta=0.1,
            confidence=0.83,
            created_at=now,
        ),
        error_links=[
            {
                "knowledge_point_id": "kp_due",
                "error_weight": 0.9,
                "tag_id": "tag_error",
                "evidence_summary": "Main error responsibility.",
                "confidence": 0.84,
            }
        ],
    )

    targets = workspace.select_daily_practice_targets("user_001", now=now, limit=3)
    snapshot = workspace.snapshot("user_001", now=now)

    assert [target.knowledge_point_id for target in targets] == ["kp_due"]
    assert snapshot.due_review_count == 1
    assert snapshot.practice_attempt_count == 1
    assert snapshot.practice_analysis_count == 1


def test_workspace_daily_practice_moves_mastery_to_pending_until_user_confirms() -> None:
    now = datetime(2026, 5, 25, 9, 0, tzinfo=UTC)
    workspace = Phase3MemoryWorkspace.empty()
    workspace.activate_personal_knowledge_build(
        PersonalKnowledgeBuild(
            id="pkb_001",
            user_id="user_001",
            build_version=1,
            model="manual-test",
            prompt_version="phase3-test",
            public_kb_version="empty-v0",
            status=PersonalKnowledgeBuildStatus.BUILDING,
            created_at=now,
        ),
        nodes=[
            PersonalKnowledgeNode(
                id="node_due",
                build_id="pkb_001",
                user_id="user_001",
                knowledge_point_id="kp_due",
                mastery_state=MasteryState.REVIEWING,
                mastery_score=0.86,
                weakness_score=0.14,
                confidence=0.84,
                evidence_count=1,
                summary="Almost mastered but still needs confirmation.",
                summary_for_embedding="almost mastered",
                created_at=now,
                updated_at=now,
            )
        ],
        edges=[],
        evidence=[
            PersonalKnowledgeEvidence(
                id="ev_due",
                build_id="pkb_001",
                user_id="user_001",
                target_type="node",
                target_id="node_due",
                evidence_type=EvidenceType.WRONG_QUESTION,
                evidence_id="wq_001",
                analysis_summary="Prior weak-point evidence.",
                created_at=now,
            )
        ],
    )
    workspace.schedule_review(
        ReviewScheduleItem(
            id="review_due",
            user_id="user_001",
            knowledge_point_id="kp_due",
            next_review_at=now - timedelta(hours=1),
            interval_days=2,
            ease_factor=2.0,
            consecutive_successes=2,
            status=ReviewScheduleStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
    )
    question = workspace.submit_generated_question(
        GeneratedQuestion(
            id="question_due",
            user_id="user_001",
            generation_request_id="request_001",
            generation_attempt=1,
            mode=GeneratedQuestionMode.LLM_TOOL_GENERATED,
            status=GeneratedQuestionStatus.APPROVED_FOR_PRACTICE,
            stem="Correct practice question.",
            answer="A",
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
    workspace.mark_generated_question_used_in_daily_practice(question.id)

    workspace.record_practice_attempt_analysis(
        PracticeAttempt(
            id="attempt_correct",
            user_id="user_001",
            question_id="question_due",
            user_answer="A",
            is_correct=True,
            difficulty="medium",
            time_spent_seconds=90,
            hint_used=False,
            reviewed_explanation=True,
            created_at=now,
        ),
        PracticeAttemptAnalysis(
            id="analysis_correct",
            attempt_id="attempt_correct",
            model="manual-test",
            prompt_version="phase3-test",
            analysis_summary="Correct answer confirms mastery improvement.",
            mastery_delta=0.08,
            weakness_delta=-0.08,
            confidence=0.9,
            created_at=now,
        ),
        error_links=[],
    )

    pending_node = workspace.get_active_personal_knowledge_node("user_001", "kp_due")
    pending_review = workspace.get_review_schedule_item("user_001", "kp_due")

    assert pending_node.mastery_state == MasteryState.MASTERED_PENDING_CONFIRM
    assert pending_node.mastery_score == 0.94
    assert pending_node.weakness_score == 0.06
    assert pending_review.status == ReviewScheduleStatus.MASTERED_PENDING_CONFIRM
    assert workspace.select_daily_practice_targets("user_001", now=now, limit=3) == []

    workspace.record_user_knowledge_feedback(
        UserKnowledgeFeedback(
            id="feedback_mastered",
            user_id="user_001",
            knowledge_point_id="kp_due",
            feedback_type=UserKnowledgeFeedbackType.MARK_MASTERED,
            comment="确认掌握，暂时不用再推这类题。",
            created_at=now,
        )
    )

    mastered_node = workspace.get_active_personal_knowledge_node("user_001", "kp_due")
    mastered_review = workspace.get_review_schedule_item("user_001", "kp_due")

    assert mastered_node.mastery_state == MasteryState.MASTERED
    assert mastered_review.status == ReviewScheduleStatus.MASTERED


def test_workspace_verifier_gate_blocks_unverified_questions() -> None:
    now = datetime(2026, 5, 26, 8, 0, tzinfo=UTC)
    workspace = Phase3MemoryWorkspace.empty()
    question = workspace.submit_generated_question(
        GeneratedQuestion(
            id="gq_001",
            user_id="user_001",
            generation_request_id="request_001",
            generation_attempt=1,
            mode=GeneratedQuestionMode.LLM_TOOL_GENERATED,
            status=GeneratedQuestionStatus.DRAFT_GENERATED,
            stem="Generated question.",
            answer="A",
            explanation="Verified explanation.",
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

    with pytest.raises(ValueError, match="verification"):
        workspace.approve_generated_question_for_practice(question.id)

    workspace.start_question_verification(question.id)
    workspace.record_question_verification(
        QuestionVerificationReport(
            id="report_001",
            question_id=question.id,
            verifier_agent_id="verifier_001",
            verdict=VerificationVerdict.PASSED,
            verifier_answer="A",
            issue_summary="No issue.",
            failed_reason_type=None,
            confidence=0.92,
            created_at=now,
        )
    )
    approved = workspace.approve_generated_question_for_practice(question.id)
    snapshot = workspace.snapshot("user_001", now=now)

    assert approved.status == GeneratedQuestionStatus.APPROVED_FOR_PRACTICE
    assert snapshot.generated_question_count == 1
    assert snapshot.approved_generated_question_count == 1


def test_workspace_failed_verifier_path_regenerates_once_then_needs_human_review() -> None:
    now = datetime(2026, 5, 27, 8, 0, tzinfo=UTC)
    workspace = Phase3MemoryWorkspace.empty()
    question = workspace.submit_generated_question(
        GeneratedQuestion(
            id="gq_bad",
            user_id="user_001",
            generation_request_id="request_001",
            generation_attempt=1,
            mode=GeneratedQuestionMode.LLM_TOOL_GENERATED,
            status=GeneratedQuestionStatus.DRAFT_GENERATED,
            stem="Bad generated question.",
            answer="A",
            explanation="Bad explanation.",
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
    workspace.start_question_verification(question.id)
    workspace.record_question_verification(
        QuestionVerificationReport(
            id="report_bad_001",
            question_id=question.id,
            verifier_agent_id="verifier_001",
            verdict=VerificationVerdict.FAILED,
            verifier_answer="B",
            issue_summary="Answer mismatch.",
            failed_reason_type=FailedReasonType.ANSWER_MISMATCH,
            confidence=0.9,
            created_at=now,
        )
    )
    assert workspace.get_generated_question(question.id).status == (
        GeneratedQuestionStatus.VERIFICATION_FAILED
    )
    regenerated = workspace.start_regenerated_question_attempt(question.id)
    workspace.start_question_verification(regenerated.id)
    workspace.record_question_verification(
        QuestionVerificationReport(
            id="report_bad_002",
            question_id=regenerated.id,
            verifier_agent_id="verifier_001",
            verdict=VerificationVerdict.FAILED,
            verifier_answer="Still invalid",
            issue_summary="Ambiguous condition.",
            failed_reason_type=FailedReasonType.AMBIGUOUS_CONDITION,
            confidence=0.88,
            created_at=now,
        )
    )

    assert workspace.get_generated_question(regenerated.id).status == (
        GeneratedQuestionStatus.NEEDS_HUMAN_REVIEW
    )


def test_workspace_marks_approved_generated_question_used_in_daily_practice() -> None:
    now = datetime(2026, 5, 27, 10, 0, tzinfo=UTC)
    workspace = Phase3MemoryWorkspace.empty()
    question = workspace.submit_generated_question(
        GeneratedQuestion(
            id="gq_approved",
            user_id="user_001",
            generation_request_id="request_001",
            generation_attempt=1,
            mode=GeneratedQuestionMode.LLM_TOOL_GENERATED,
            status=GeneratedQuestionStatus.DRAFT_GENERATED,
            stem="Generated question.",
            answer="A",
            explanation="Verified explanation.",
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

    with pytest.raises(ValueError, match="approved"):
        workspace.mark_generated_question_used_in_daily_practice(question.id)

    workspace.start_question_verification(question.id)
    workspace.record_question_verification(
        QuestionVerificationReport(
            id="report_passed",
            question_id=question.id,
            verifier_agent_id="verifier_001",
            verdict=VerificationVerdict.PASSED,
            verifier_answer="A",
            issue_summary="No issue.",
            failed_reason_type=None,
            confidence=0.92,
            created_at=now,
        )
    )
    workspace.approve_generated_question_for_practice(question.id)
    used = workspace.mark_generated_question_used_in_daily_practice(question.id)

    assert used.status == GeneratedQuestionStatus.USED_IN_DAILY_PRACTICE


def test_workspace_blocks_practice_analysis_from_unverified_generated_question() -> None:
    now = datetime(2026, 5, 27, 11, 0, tzinfo=UTC)
    workspace = Phase3MemoryWorkspace.empty()
    workspace.activate_personal_knowledge_build(
        PersonalKnowledgeBuild(
            id="pkb_001",
            user_id="user_001",
            build_version=1,
            model="manual-test",
            prompt_version="phase3-test",
            public_kb_version="empty-v0",
            status=PersonalKnowledgeBuildStatus.BUILDING,
            created_at=now,
        ),
        nodes=[
            PersonalKnowledgeNode(
                id="node_due",
                build_id="pkb_001",
                user_id="user_001",
                knowledge_point_id="kp_due",
                mastery_state=MasteryState.REVIEWING,
                mastery_score=0.5,
                weakness_score=0.5,
                confidence=0.8,
                evidence_count=1,
                summary="Review target.",
                summary_for_embedding="review target",
                created_at=now,
                updated_at=now,
            )
        ],
        edges=[],
        evidence=[
            PersonalKnowledgeEvidence(
                id="ev_due",
                build_id="pkb_001",
                user_id="user_001",
                target_type="node",
                target_id="node_due",
                evidence_type=EvidenceType.WRONG_QUESTION,
                evidence_id="wq_001",
                analysis_summary="Prior evidence.",
                created_at=now,
            )
        ],
    )
    workspace.submit_generated_question(
        GeneratedQuestion(
            id="gq_unverified",
            user_id="user_001",
            generation_request_id="request_001",
            generation_attempt=1,
            mode=GeneratedQuestionMode.LLM_TOOL_GENERATED,
            status=GeneratedQuestionStatus.DRAFT_GENERATED,
            stem="Unverified generated question.",
            answer="A",
            explanation="Unchecked explanation.",
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

    with pytest.raises(ValueError, match="approved generated question"):
        workspace.record_practice_attempt_analysis(
            PracticeAttempt(
                id="attempt_unverified",
                user_id="user_001",
                question_id="gq_unverified",
                user_answer="A",
                is_correct=True,
                difficulty="medium",
                time_spent_seconds=60,
                hint_used=False,
                reviewed_explanation=False,
                created_at=now,
            ),
            PracticeAttemptAnalysis(
                id="analysis_unverified",
                attempt_id="attempt_unverified",
                model="manual-test",
                prompt_version="phase3-test",
                analysis_summary="Should not update mastery from unverified generated content.",
                mastery_delta=0.2,
                weakness_delta=-0.2,
                confidence=0.9,
                created_at=now,
            ),
            error_links=[],
        )

    node = workspace.get_active_personal_knowledge_node("user_001", "kp_due")
    snapshot = workspace.snapshot("user_001", now=now)

    assert node.mastery_score == 0.5
    assert node.weakness_score == 0.5
    assert snapshot.practice_attempt_count == 0
    assert snapshot.practice_analysis_count == 0
