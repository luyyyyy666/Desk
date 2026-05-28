from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from my_sifu_agent.memory import (
    ActivePersonalKnowledgeBuildSnapshot,
    AttemptErrorLink,
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
    Phase3MemorySnapshot,
    Phase3MemoryWorkspace,
    PracticeAttempt,
    PracticeAttemptAnalysis,
    PublicKnowledgeImportResult,
    PublicKnowledgeSeedData,
    PublicKnowledgeSnapshot,
    QuestionVerificationReport,
    ReviewScheduleItem,
    ReviewScheduleStatus,
    TagLink,
    UserKnowledgeFeedback,
    UserKnowledgeFeedbackType,
    UserKnowledgeNote,
    VerificationVerdict,
    WrongQuestion,
    WrongQuestionKnowledgeLink,
)


@dataclass
class Phase3MemoryApi:
    workspace: Phase3MemoryWorkspace

    @classmethod
    def empty(cls) -> Phase3MemoryApi:
        return cls(workspace=Phase3MemoryWorkspace.empty())

    def import_empty_public_knowledge(self) -> dict[str, Any]:
        imported = self.workspace.bootstrap_public_knowledge(PublicKnowledgeSeedData.empty())
        return {
            "imported": _public_knowledge_import_result_to_json(imported),
            "publicKnowledge": _public_knowledge_snapshot_to_json(
                self.workspace.public_knowledge_repository.snapshot()
            ),
        }

    def get_memory_snapshot(self, user_id: str, *, now: datetime) -> dict[str, Any]:
        return _snapshot_to_json(self.workspace.snapshot(user_id, now=now))

    def record_wrong_question(self, payload: dict[str, Any]) -> dict[str, Any]:
        wrong_question = _wrong_question_from_json(payload)
        knowledge_links = [
            _wrong_question_knowledge_link_from_json(wrong_question.id, item)
            for item in payload.get("knowledgeLinks", [])
        ]
        tag_links = [
            _tag_link_from_json(wrong_question.id, item)
            for item in payload.get("tagLinks", [])
        ]
        stored = self.workspace.record_wrong_question(
            wrong_question,
            knowledge_links=knowledge_links,
            tag_links=tag_links,
        )
        return {"wrongQuestion": _wrong_question_to_json(stored)}

    def upsert_user_knowledge_note(self, payload: dict[str, Any]) -> dict[str, Any]:
        note = self.workspace.upsert_user_knowledge_note(
            _user_knowledge_note_from_json(payload)
        )
        return {"note": _user_knowledge_note_to_json(note)}

    def record_user_knowledge_feedback(self, payload: dict[str, Any]) -> dict[str, Any]:
        feedback = self.workspace.record_user_knowledge_feedback(
            _user_knowledge_feedback_from_json(payload)
        )
        return {"feedback": _user_knowledge_feedback_to_json(feedback)}

    def get_user_knowledge_notes_and_feedback(
        self,
        user_id: str,
        knowledge_point_id: str,
    ) -> dict[str, Any]:
        return {
            "notes": [
                _user_knowledge_note_to_json(note)
                for note in self.workspace.list_user_knowledge_notes(
                    user_id,
                    knowledge_point_id,
                )
            ],
            "feedback": [
                _user_knowledge_feedback_to_json(feedback)
                for feedback in self.workspace.list_user_knowledge_feedback(
                    user_id,
                    knowledge_point_id,
                )
            ],
        }

    def activate_personal_knowledge_build(self, payload: dict[str, Any]) -> dict[str, Any]:
        build = _personal_knowledge_build_from_json(_required(payload, "build"))
        nodes = [
            _personal_knowledge_node_from_json(item)
            for item in payload.get("nodes", [])
        ]
        edges = [
            _personal_knowledge_edge_from_json(item)
            for item in payload.get("edges", [])
        ]
        evidence = [
            _personal_knowledge_evidence_from_json(item)
            for item in payload.get("evidence", [])
        ]
        activated = self.workspace.activate_personal_knowledge_build(
            build,
            nodes=nodes,
            edges=edges,
            evidence=evidence,
        )
        return {"build": _personal_knowledge_build_to_json(activated)}

    def schedule_review(self, payload: dict[str, Any]) -> dict[str, Any]:
        item = self.workspace.schedule_review(_review_schedule_item_from_json(payload))
        return {"item": _review_schedule_item_to_json(item)}

    def get_daily_practice_targets(
        self,
        user_id: str,
        *,
        now: datetime,
        limit: int,
    ) -> dict[str, Any]:
        targets = self.workspace.select_daily_practice_targets(user_id, now=now, limit=limit)
        return {"targets": [_personal_knowledge_node_to_json(target) for target in targets]}

    def get_user_knowledge_state(
        self,
        user_id: str,
        knowledge_point_id: str,
    ) -> dict[str, Any]:
        node = self.workspace.get_active_personal_knowledge_node(user_id, knowledge_point_id)
        review = self.workspace.get_review_schedule_item(user_id, knowledge_point_id)
        return {
            "node": _personal_knowledge_node_to_json(node),
            "reviewSchedule": _review_schedule_item_to_json(review),
        }

    def record_practice_attempt_analysis(self, payload: dict[str, Any]) -> dict[str, Any]:
        attempt = _practice_attempt_from_json(_required(payload, "attempt"))
        analysis = _practice_attempt_analysis_from_json(_required(payload, "analysis"))
        error_links = [
            _attempt_error_link_payload_from_json(item)
            for item in payload.get("errorLinks", [])
        ]
        stored_analysis = self.workspace.record_practice_attempt_analysis(
            attempt,
            analysis,
            error_links=error_links,
        )
        return {
            "attempt": _practice_attempt_to_json(attempt),
            "analysis": _practice_attempt_analysis_to_json(stored_analysis),
            "errorLinks": [_attempt_error_link_to_json(link) for link in error_links],
        }

    def submit_generated_question(self, payload: dict[str, Any]) -> dict[str, Any]:
        question = self.workspace.submit_generated_question(_generated_question_from_json(payload))
        return {"question": _generated_question_to_json(question)}

    def start_question_verification(self, question_id: str) -> dict[str, Any]:
        question = self.workspace.start_question_verification(question_id)
        return {"question": _generated_question_to_json(question)}

    def record_question_verification(self, payload: dict[str, Any]) -> dict[str, Any]:
        report = self.workspace.record_question_verification(
            _question_verification_report_from_json(payload)
        )
        return {"report": _question_verification_report_to_json(report)}

    def approve_generated_question_for_practice(self, question_id: str) -> dict[str, Any]:
        question = self.workspace.approve_generated_question_for_practice(question_id)
        return {"question": _generated_question_to_json(question)}


def _required(payload: dict[str, Any], key: str) -> Any:
    try:
        return payload[key]
    except KeyError as exc:
        raise ValueError(f"missing required field: {key}") from exc


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _enum(enum_type: type[StrEnum], value: str) -> StrEnum:
    return enum_type(value)


def _public_knowledge_import_result_to_json(result: PublicKnowledgeImportResult) -> dict[str, Any]:
    return {
        "knowledgePoints": result.knowledge_points,
        "tags": result.tags,
        "pointTags": result.point_tags,
        "edges": result.edges,
    }


def _public_knowledge_snapshot_to_json(snapshot: PublicKnowledgeSnapshot) -> dict[str, Any]:
    return {
        "knowledgePoints": snapshot.knowledge_points,
        "tags": snapshot.tags,
        "edges": snapshot.edges,
        "isEmpty": snapshot.is_empty,
    }


def _active_build_snapshot_to_json(
    snapshot: ActivePersonalKnowledgeBuildSnapshot | None,
) -> dict[str, Any] | None:
    if snapshot is None:
        return None
    return {
        "buildId": snapshot.build_id,
        "buildVersion": snapshot.build_version,
        "status": snapshot.status.value,
        "publicKbVersion": snapshot.public_kb_version,
    }


def _snapshot_to_json(snapshot: Phase3MemorySnapshot) -> dict[str, Any]:
    return {
        "userId": snapshot.user_id,
        "publicKnowledge": _public_knowledge_snapshot_to_json(snapshot.public_knowledge),
        "wrongQuestionCount": snapshot.wrong_question_count,
        "activePersonalBuild": _active_build_snapshot_to_json(snapshot.active_personal_build),
        "personalNodeCount": snapshot.personal_node_count,
        "personalEdgeCount": snapshot.personal_edge_count,
        "personalEvidenceCount": snapshot.personal_evidence_count,
        "userKnowledgeNoteCount": snapshot.user_knowledge_note_count,
        "userKnowledgeFeedbackCount": snapshot.user_knowledge_feedback_count,
        "dueReviewCount": snapshot.due_review_count,
        "practiceAttemptCount": snapshot.practice_attempt_count,
        "practiceAnalysisCount": snapshot.practice_analysis_count,
        "generatedQuestionCount": snapshot.generated_question_count,
        "approvedGeneratedQuestionCount": snapshot.approved_generated_question_count,
    }


def _wrong_question_from_json(payload: dict[str, Any]) -> WrongQuestion:
    return WrongQuestion(
        id=_required(payload, "id"),
        user_id=_required(payload, "userId"),
        question_text=_required(payload, "questionText"),
        correct_answer=_required(payload, "correctAnswer"),
        user_answer=_required(payload, "userAnswer"),
        explanation=_required(payload, "explanation"),
        source=_required(payload, "source"),
        subject=_required(payload, "subject"),
        created_at=_parse_datetime(_required(payload, "createdAt")),
    )


def _wrong_question_to_json(wrong_question: WrongQuestion) -> dict[str, Any]:
    return {
        "id": wrong_question.id,
        "userId": wrong_question.user_id,
        "questionText": wrong_question.question_text,
        "correctAnswer": wrong_question.correct_answer,
        "userAnswer": wrong_question.user_answer,
        "explanation": wrong_question.explanation,
        "source": wrong_question.source,
        "subject": wrong_question.subject,
        "createdAt": wrong_question.created_at.isoformat(),
    }


def _wrong_question_knowledge_link_from_json(
    wrong_question_id: str,
    payload: dict[str, Any],
) -> WrongQuestionKnowledgeLink:
    return WrongQuestionKnowledgeLink(
        wrong_question_id=wrong_question_id,
        knowledge_point_id=_required(payload, "knowledgePointId"),
        role=KnowledgeLinkRole(_required(payload, "role")),
        content_weight=float(_required(payload, "contentWeight")),
        source=LinkSource(_required(payload, "source")),
        confidence=float(_required(payload, "confidence")),
    )


def _tag_link_from_json(target_id: str, payload: dict[str, Any]) -> TagLink:
    return TagLink(
        target_id=target_id,
        tag_id=_required(payload, "tagId"),
        source=LinkSource(_required(payload, "source")),
        confidence=float(_required(payload, "confidence")),
    )


def _user_knowledge_note_from_json(payload: dict[str, Any]) -> UserKnowledgeNote:
    return UserKnowledgeNote(
        id=_required(payload, "id"),
        user_id=_required(payload, "userId"),
        knowledge_point_id=_required(payload, "knowledgePointId"),
        note=_required(payload, "note"),
        custom_tags=tuple(payload.get("customTags", [])),
        created_at=_parse_datetime(_required(payload, "createdAt")),
        updated_at=_parse_datetime(_required(payload, "updatedAt")),
    )


def _user_knowledge_note_to_json(note: UserKnowledgeNote) -> dict[str, Any]:
    return {
        "id": note.id,
        "userId": note.user_id,
        "knowledgePointId": note.knowledge_point_id,
        "note": note.note,
        "customTags": list(note.custom_tags),
        "createdAt": note.created_at.isoformat(),
        "updatedAt": note.updated_at.isoformat(),
    }


def _user_knowledge_feedback_from_json(payload: dict[str, Any]) -> UserKnowledgeFeedback:
    return UserKnowledgeFeedback(
        id=_required(payload, "id"),
        user_id=_required(payload, "userId"),
        knowledge_point_id=_required(payload, "knowledgePointId"),
        feedback_type=UserKnowledgeFeedbackType(_required(payload, "feedbackType")),
        comment=_required(payload, "comment"),
        created_at=_parse_datetime(_required(payload, "createdAt")),
    )


def _user_knowledge_feedback_to_json(
    feedback: UserKnowledgeFeedback,
) -> dict[str, Any]:
    return {
        "id": feedback.id,
        "userId": feedback.user_id,
        "knowledgePointId": feedback.knowledge_point_id,
        "feedbackType": feedback.feedback_type.value,
        "comment": feedback.comment,
        "createdAt": feedback.created_at.isoformat(),
    }


def _personal_knowledge_build_from_json(payload: dict[str, Any]) -> PersonalKnowledgeBuild:
    return PersonalKnowledgeBuild(
        id=_required(payload, "id"),
        user_id=_required(payload, "userId"),
        build_version=int(_required(payload, "buildVersion")),
        model=_required(payload, "model"),
        prompt_version=_required(payload, "promptVersion"),
        public_kb_version=_required(payload, "publicKbVersion"),
        status=PersonalKnowledgeBuildStatus(_required(payload, "status")),
        created_at=_parse_datetime(_required(payload, "createdAt")),
    )


def _personal_knowledge_build_to_json(build: PersonalKnowledgeBuild) -> dict[str, Any]:
    return {
        "id": build.id,
        "userId": build.user_id,
        "buildVersion": build.build_version,
        "model": build.model,
        "promptVersion": build.prompt_version,
        "publicKbVersion": build.public_kb_version,
        "status": build.status.value,
        "createdAt": build.created_at.isoformat(),
    }


def _personal_knowledge_node_from_json(payload: dict[str, Any]) -> PersonalKnowledgeNode:
    return PersonalKnowledgeNode(
        id=_required(payload, "id"),
        build_id=_required(payload, "buildId"),
        user_id=_required(payload, "userId"),
        knowledge_point_id=_required(payload, "knowledgePointId"),
        mastery_state=MasteryState(_required(payload, "masteryState")),
        mastery_score=float(_required(payload, "masteryScore")),
        weakness_score=float(_required(payload, "weaknessScore")),
        confidence=float(_required(payload, "confidence")),
        evidence_count=int(_required(payload, "evidenceCount")),
        summary=_required(payload, "summary"),
        summary_for_embedding=_required(payload, "summaryForEmbedding"),
        created_at=_parse_datetime(_required(payload, "createdAt")),
        updated_at=_parse_datetime(_required(payload, "updatedAt")),
    )


def _personal_knowledge_node_to_json(node: PersonalKnowledgeNode) -> dict[str, Any]:
    return {
        "id": node.id,
        "buildId": node.build_id,
        "userId": node.user_id,
        "knowledgePointId": node.knowledge_point_id,
        "masteryState": node.mastery_state.value,
        "masteryScore": node.mastery_score,
        "weaknessScore": node.weakness_score,
        "confidence": node.confidence,
        "evidenceCount": node.evidence_count,
        "summary": node.summary,
        "summaryForEmbedding": node.summary_for_embedding,
        "createdAt": node.created_at.isoformat(),
        "updatedAt": node.updated_at.isoformat(),
    }


def _personal_knowledge_edge_from_json(payload: dict[str, Any]) -> PersonalKnowledgeEdge:
    return PersonalKnowledgeEdge(
        id=_required(payload, "id"),
        build_id=_required(payload, "buildId"),
        user_id=_required(payload, "userId"),
        source_knowledge_point_id=_required(payload, "sourceKnowledgePointId"),
        target_knowledge_point_id=_required(payload, "targetKnowledgePointId"),
        relation_type=PersonalEdgeRelationType(_required(payload, "relationType")),
        weight=float(_required(payload, "weight")),
        confidence=float(_required(payload, "confidence")),
        evidence_count=int(_required(payload, "evidenceCount")),
        summary=_required(payload, "summary"),
        summary_for_embedding=_required(payload, "summaryForEmbedding"),
        created_at=_parse_datetime(_required(payload, "createdAt")),
        updated_at=_parse_datetime(_required(payload, "updatedAt")),
    )


def _personal_knowledge_evidence_from_json(payload: dict[str, Any]) -> PersonalKnowledgeEvidence:
    return PersonalKnowledgeEvidence(
        id=_required(payload, "id"),
        build_id=_required(payload, "buildId"),
        user_id=_required(payload, "userId"),
        target_type=_required(payload, "targetType"),
        target_id=_required(payload, "targetId"),
        evidence_type=EvidenceType(_required(payload, "evidenceType")),
        evidence_id=_required(payload, "evidenceId"),
        analysis_summary=_required(payload, "analysisSummary"),
        created_at=_parse_datetime(_required(payload, "createdAt")),
    )


def _review_schedule_item_from_json(payload: dict[str, Any]) -> ReviewScheduleItem:
    return ReviewScheduleItem(
        id=_required(payload, "id"),
        user_id=_required(payload, "userId"),
        knowledge_point_id=_required(payload, "knowledgePointId"),
        next_review_at=_parse_datetime(_required(payload, "nextReviewAt")),
        interval_days=int(_required(payload, "intervalDays")),
        ease_factor=float(_required(payload, "easeFactor")),
        consecutive_successes=int(_required(payload, "consecutiveSuccesses")),
        status=ReviewScheduleStatus(_required(payload, "status")),
        created_at=_parse_datetime(_required(payload, "createdAt")),
        updated_at=_parse_datetime(_required(payload, "updatedAt")),
    )


def _review_schedule_item_to_json(item: ReviewScheduleItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "userId": item.user_id,
        "knowledgePointId": item.knowledge_point_id,
        "nextReviewAt": item.next_review_at.isoformat(),
        "intervalDays": item.interval_days,
        "easeFactor": item.ease_factor,
        "consecutiveSuccesses": item.consecutive_successes,
        "status": item.status.value,
        "createdAt": item.created_at.isoformat(),
        "updatedAt": item.updated_at.isoformat(),
    }


def _practice_attempt_from_json(payload: dict[str, Any]) -> PracticeAttempt:
    return PracticeAttempt(
        id=_required(payload, "id"),
        user_id=_required(payload, "userId"),
        question_id=_required(payload, "questionId"),
        user_answer=_required(payload, "userAnswer"),
        is_correct=bool(_required(payload, "isCorrect")),
        difficulty=_required(payload, "difficulty"),
        time_spent_seconds=payload.get("timeSpentSeconds"),
        hint_used=bool(_required(payload, "hintUsed")),
        reviewed_explanation=bool(_required(payload, "reviewedExplanation")),
        created_at=_parse_datetime(_required(payload, "createdAt")),
    )


def _practice_attempt_to_json(attempt: PracticeAttempt) -> dict[str, Any]:
    return {
        "id": attempt.id,
        "userId": attempt.user_id,
        "questionId": attempt.question_id,
        "userAnswer": attempt.user_answer,
        "isCorrect": attempt.is_correct,
        "difficulty": attempt.difficulty,
        "timeSpentSeconds": attempt.time_spent_seconds,
        "hintUsed": attempt.hint_used,
        "reviewedExplanation": attempt.reviewed_explanation,
        "createdAt": attempt.created_at.isoformat(),
    }


def _practice_attempt_analysis_from_json(payload: dict[str, Any]) -> PracticeAttemptAnalysis:
    return PracticeAttemptAnalysis(
        id=_required(payload, "id"),
        attempt_id=_required(payload, "attemptId"),
        model=_required(payload, "model"),
        prompt_version=_required(payload, "promptVersion"),
        analysis_summary=_required(payload, "analysisSummary"),
        mastery_delta=float(_required(payload, "masteryDelta")),
        weakness_delta=float(_required(payload, "weaknessDelta")),
        confidence=float(_required(payload, "confidence")),
        created_at=_parse_datetime(_required(payload, "createdAt")),
    )


def _practice_attempt_analysis_to_json(analysis: PracticeAttemptAnalysis) -> dict[str, Any]:
    return {
        "id": analysis.id,
        "attemptId": analysis.attempt_id,
        "model": analysis.model,
        "promptVersion": analysis.prompt_version,
        "analysisSummary": analysis.analysis_summary,
        "masteryDelta": analysis.mastery_delta,
        "weaknessDelta": analysis.weakness_delta,
        "confidence": analysis.confidence,
        "createdAt": analysis.created_at.isoformat(),
    }


def _attempt_error_link_payload_from_json(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "knowledge_point_id": _required(payload, "knowledgePointId"),
        "error_weight": float(_required(payload, "errorWeight")),
        "tag_id": _required(payload, "tagId"),
        "evidence_summary": _required(payload, "evidenceSummary"),
        "confidence": float(_required(payload, "confidence")),
    }


def _attempt_error_link_to_json(link: dict[str, Any] | AttemptErrorLink) -> dict[str, Any]:
    if isinstance(link, AttemptErrorLink):
        return {
            "knowledgePointId": link.knowledge_point_id,
            "errorWeight": link.error_weight,
            "tagId": link.tag_id,
            "evidenceSummary": link.evidence_summary,
            "confidence": link.confidence,
        }
    return {
        "knowledgePointId": link["knowledge_point_id"],
        "errorWeight": link["error_weight"],
        "tagId": link["tag_id"],
        "evidenceSummary": link["evidence_summary"],
        "confidence": link["confidence"],
    }


def _generated_question_from_json(payload: dict[str, Any]) -> GeneratedQuestion:
    return GeneratedQuestion(
        id=_required(payload, "id"),
        user_id=_required(payload, "userId"),
        generation_request_id=_required(payload, "generationRequestId"),
        generation_attempt=int(_required(payload, "generationAttempt")),
        mode=GeneratedQuestionMode(_required(payload, "mode")),
        status=GeneratedQuestionStatus(_required(payload, "status")),
        stem=_required(payload, "stem"),
        answer=_required(payload, "answer"),
        explanation=_required(payload, "explanation"),
        knowledge_point_links=tuple(
            _generated_question_knowledge_link_from_json(item)
            for item in _required(payload, "knowledgePointLinks")
        ),
        expected_error_traps=tuple(_required(payload, "expectedErrorTraps")),
        grading_rubric=_required(payload, "gradingRubric"),
        difficulty=_required(payload, "difficulty"),
        question_type=_required(payload, "questionType"),
        model=_required(payload, "model"),
        prompt_version=_required(payload, "promptVersion"),
        public_kb_version=_required(payload, "publicKbVersion"),
        personal_knowledge_build_id=_required(payload, "personalKnowledgeBuildId"),
        created_at=_parse_datetime(_required(payload, "createdAt")),
    )


def _generated_question_knowledge_link_from_json(
    payload: dict[str, Any],
) -> GeneratedQuestionKnowledgeLink:
    return GeneratedQuestionKnowledgeLink(
        knowledge_point_id=_required(payload, "knowledgePointId"),
        content_weight=float(_required(payload, "contentWeight")),
        role=KnowledgeLinkRole(_required(payload, "role")),
    )


def _generated_question_knowledge_link_to_json(
    link: GeneratedQuestionKnowledgeLink,
) -> dict[str, Any]:
    return {
        "knowledgePointId": link.knowledge_point_id,
        "contentWeight": link.content_weight,
        "role": link.role.value,
    }


def _generated_question_to_json(question: GeneratedQuestion) -> dict[str, Any]:
    return {
        "id": question.id,
        "userId": question.user_id,
        "generationRequestId": question.generation_request_id,
        "generationAttempt": question.generation_attempt,
        "mode": question.mode.value,
        "status": question.status.value,
        "stem": question.stem,
        "answer": question.answer,
        "explanation": question.explanation,
        "knowledgePointLinks": [
            _generated_question_knowledge_link_to_json(link)
            for link in question.knowledge_point_links
        ],
        "expectedErrorTraps": list(question.expected_error_traps),
        "gradingRubric": question.grading_rubric,
        "difficulty": question.difficulty,
        "questionType": question.question_type,
        "model": question.model,
        "promptVersion": question.prompt_version,
        "publicKbVersion": question.public_kb_version,
        "personalKnowledgeBuildId": question.personal_knowledge_build_id,
        "createdAt": question.created_at.isoformat(),
    }


def _question_verification_report_from_json(payload: dict[str, Any]) -> QuestionVerificationReport:
    failed_reason_type = payload.get("failedReasonType")
    return QuestionVerificationReport(
        id=_required(payload, "id"),
        question_id=_required(payload, "questionId"),
        verifier_agent_id=_required(payload, "verifierAgentId"),
        verdict=VerificationVerdict(_required(payload, "verdict")),
        verifier_answer=_required(payload, "verifierAnswer"),
        issue_summary=_required(payload, "issueSummary"),
        failed_reason_type=(
            FailedReasonType(failed_reason_type) if failed_reason_type is not None else None
        ),
        confidence=float(_required(payload, "confidence")),
        created_at=_parse_datetime(_required(payload, "createdAt")),
    )


def _question_verification_report_to_json(report: QuestionVerificationReport) -> dict[str, Any]:
    return {
        "id": report.id,
        "questionId": report.question_id,
        "verifierAgentId": report.verifier_agent_id,
        "verdict": report.verdict.value,
        "verifierAnswer": report.verifier_answer,
        "issueSummary": report.issue_summary,
        "failedReasonType": (
            report.failed_reason_type.value if report.failed_reason_type is not None else None
        ),
        "confidence": report.confidence,
        "createdAt": report.created_at.isoformat(),
    }
