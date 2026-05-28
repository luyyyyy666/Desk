from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum
from typing import Any


class KnowledgeLinkRole(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    PREREQUISITE = "prerequisite"
    TRAP = "trap"


class LinkSource(StrEnum):
    PUBLIC_KB = "public_kb"
    LLM = "llm"
    MANUAL = "manual"


class PublicTagType(StrEnum):
    ERROR_TYPE = "error_type"
    QUESTION_TYPE = "question_type"
    DIFFICULTY = "difficulty"
    BEHAVIOR = "behavior"
    EXAM_PATTERN = "exam_pattern"


class PublicKnowledgeEdgeRelationType(StrEnum):
    PREREQUISITE = "prerequisite"
    SAME_TOPIC = "same_topic"
    OFTEN_COMBINED = "often_combined"
    EXAM_PATTERN = "exam_pattern"


class PersonalKnowledgeBuildStatus(StrEnum):
    BUILDING = "building"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    FAILED = "failed"


class MasteryState(StrEnum):
    WEAK = "weak"
    LEARNING = "learning"
    REVIEWING = "reviewing"
    MASTERED_PENDING_CONFIRM = "mastered_pending_confirm"
    MASTERED = "mastered"


class PersonalEdgeRelationType(StrEnum):
    CO_FAILED = "co_failed"
    CO_PRACTICED = "co_practiced"
    CONFUSED_WITH = "confused_with"
    PREREQUISITE_GAP = "prerequisite_gap"
    IMPROVES_WITH = "improves_with"


class EvidenceType(StrEnum):
    WRONG_QUESTION = "wrong_question"
    PRACTICE_ATTEMPT = "practice_attempt"
    EXPLICIT_FEEDBACK = "explicit_feedback"
    MANUAL_CONFIRMATION = "manual_confirmation"


class ReviewScheduleStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    MASTERED_PENDING_CONFIRM = "mastered_pending_confirm"
    MASTERED = "mastered"


class GeneratedQuestionMode(StrEnum):
    STABLE_BANK = "stable_bank"
    LLM_TOOL_GENERATED = "llm_tool_generated"


class GeneratedQuestionStatus(StrEnum):
    DRAFT_GENERATED = "draft_generated"
    VERIFICATION_RUNNING = "verification_running"
    VERIFICATION_PASSED = "verification_passed"
    APPROVED_FOR_PRACTICE = "approved_for_practice"
    USED_IN_DAILY_PRACTICE = "used_in_daily_practice"
    VERIFICATION_FAILED = "verification_failed"
    REGENERATED_ONCE = "regenerated_once"
    NEEDS_HUMAN_REVIEW = "needs_human_review"


class VerificationVerdict(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class FailedReasonType(StrEnum):
    NO_VALID_ANSWER = "no_valid_answer"
    ANSWER_MISMATCH = "answer_mismatch"
    AMBIGUOUS_CONDITION = "ambiguous_condition"
    EXPLANATION_ERROR = "explanation_error"
    KNOWLEDGE_TAG_MISMATCH = "knowledge_tag_mismatch"
    DIFFICULTY_MISMATCH = "difficulty_mismatch"


@dataclass(frozen=True)
class PublicKnowledgePoint:
    id: str
    subject: str
    grade_band: str
    exam_stage: str
    parent_id: str | None
    name: str
    aliases: tuple[str, ...]
    difficulty_band: str
    exam_frequency: str
    description: str


@dataclass(frozen=True)
class PublicTag:
    id: str
    tag_type: PublicTagType
    name: str
    description: str


@dataclass(frozen=True)
class PublicKnowledgePointTag:
    knowledge_point_id: str
    tag_id: str


@dataclass(frozen=True)
class PublicKnowledgePointEdge:
    source_knowledge_point_id: str
    target_knowledge_point_id: str
    relation_type: PublicKnowledgeEdgeRelationType
    weight: float
    source: str


@dataclass(frozen=True)
class PublicKnowledgeSeedData:
    knowledge_points: tuple[PublicKnowledgePoint, ...] = ()
    tags: tuple[PublicTag, ...] = ()
    point_tags: tuple[PublicKnowledgePointTag, ...] = ()
    edges: tuple[PublicKnowledgePointEdge, ...] = ()

    @classmethod
    def empty(cls) -> PublicKnowledgeSeedData:
        return cls()


@dataclass(frozen=True)
class PublicKnowledgeImportResult:
    knowledge_points: int
    tags: int
    point_tags: int
    edges: int


@dataclass(frozen=True)
class WrongQuestion:
    id: str
    user_id: str
    question_text: str
    correct_answer: str
    user_answer: str
    explanation: str
    source: str
    subject: str
    created_at: datetime


@dataclass(frozen=True)
class WrongQuestionKnowledgeLink:
    wrong_question_id: str
    knowledge_point_id: str
    role: KnowledgeLinkRole
    content_weight: float
    source: LinkSource
    confidence: float


@dataclass(frozen=True)
class TagLink:
    target_id: str
    tag_id: str
    source: LinkSource
    confidence: float


@dataclass(frozen=True)
class PersonalKnowledgeBuild:
    id: str
    user_id: str
    build_version: int
    model: str
    prompt_version: str
    public_kb_version: str
    status: PersonalKnowledgeBuildStatus
    created_at: datetime


@dataclass(frozen=True)
class PersonalKnowledgeNode:
    id: str
    build_id: str
    user_id: str
    knowledge_point_id: str
    mastery_state: MasteryState
    mastery_score: float
    weakness_score: float
    confidence: float
    evidence_count: int
    summary: str
    summary_for_embedding: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class PersonalKnowledgeEdge:
    id: str
    build_id: str
    user_id: str
    source_knowledge_point_id: str
    target_knowledge_point_id: str
    relation_type: PersonalEdgeRelationType
    weight: float
    confidence: float
    evidence_count: int
    summary: str
    summary_for_embedding: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class PersonalKnowledgeEvidence:
    id: str
    build_id: str
    user_id: str
    target_type: str
    target_id: str
    evidence_type: EvidenceType
    evidence_id: str
    analysis_summary: str
    created_at: datetime


@dataclass(frozen=True)
class UserKnowledgeNote:
    id: str
    user_id: str
    knowledge_point_id: str
    note: str
    custom_tags: tuple[str, ...]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class UserKnowledgeFeedback:
    id: str
    user_id: str
    knowledge_point_id: str
    feedback_type: str
    comment: str
    created_at: datetime


@dataclass(frozen=True)
class ReviewScheduleItem:
    id: str
    user_id: str
    knowledge_point_id: str
    next_review_at: datetime
    interval_days: int
    ease_factor: float
    consecutive_successes: int
    status: ReviewScheduleStatus
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class PracticeAttempt:
    id: str
    user_id: str
    question_id: str
    user_answer: str
    is_correct: bool
    difficulty: str
    time_spent_seconds: int | None
    hint_used: bool
    reviewed_explanation: bool
    created_at: datetime


@dataclass(frozen=True)
class PracticeAttemptAnalysis:
    id: str
    attempt_id: str
    model: str
    prompt_version: str
    analysis_summary: str
    mastery_delta: float
    weakness_delta: float
    confidence: float
    created_at: datetime


@dataclass(frozen=True)
class AttemptErrorLink:
    attempt_id: str
    knowledge_point_id: str
    error_weight: float
    tag_id: str
    evidence_summary: str
    confidence: float


@dataclass(frozen=True)
class GeneratedQuestion:
    id: str
    user_id: str
    generation_request_id: str
    generation_attempt: int
    mode: GeneratedQuestionMode
    status: GeneratedQuestionStatus
    stem: str
    answer: str
    explanation: str
    difficulty: str
    question_type: str
    model: str
    prompt_version: str
    public_kb_version: str
    personal_knowledge_build_id: str
    created_at: datetime


@dataclass(frozen=True)
class QuestionVerificationReport:
    id: str
    question_id: str
    verifier_agent_id: str
    verdict: VerificationVerdict
    verifier_answer: str
    issue_summary: str
    failed_reason_type: FailedReasonType | None
    confidence: float
    created_at: datetime


@dataclass(frozen=True)
class HybridRetrievalRequest:
    query: str
    subject: str
    grade_band: str
    exam_stage: str
    knowledge_point_ids: list[str]
    tag_ids: list[str]
    include_public_graph: bool
    include_personal_graph: bool
    vector_query_text: str | None = None
    rerank: bool = True
    embedding_job_id: str | None = None

    @property
    def pipeline(self) -> tuple[str, ...]:
        steps = ["structured_filter"]
        if self.include_public_graph or self.include_personal_graph:
            steps.append("graph_expansion")
        if self.vector_query_text is not None:
            steps.append("vector_search")
        if self.rerank:
            steps.append("rerank")
        return tuple(steps)


@dataclass
class InMemoryPublicKnowledgeRepository:
    _knowledge_points: dict[str, PublicKnowledgePoint] = field(default_factory=dict)
    _tags: dict[str, PublicTag] = field(default_factory=dict)
    _point_tags: list[PublicKnowledgePointTag] = field(default_factory=list)
    _edges: list[PublicKnowledgePointEdge] = field(default_factory=list)

    def import_seed(self, seed: PublicKnowledgeSeedData) -> PublicKnowledgeImportResult:
        for knowledge_point in seed.knowledge_points:
            self._knowledge_points[knowledge_point.id] = knowledge_point
        for tag in seed.tags:
            self._tags[tag.id] = tag
        self._point_tags.extend(seed.point_tags)
        self._edges.extend(seed.edges)

        return PublicKnowledgeImportResult(
            knowledge_points=len(seed.knowledge_points),
            tags=len(seed.tags),
            point_tags=len(seed.point_tags),
            edges=len(seed.edges),
        )

    def list_knowledge_points(self) -> list[PublicKnowledgePoint]:
        return list(self._knowledge_points.values())

    def list_tags(self) -> list[PublicTag]:
        return list(self._tags.values())

    def list_edges(self) -> list[PublicKnowledgePointEdge]:
        return list(self._edges)


@dataclass
class InMemoryWrongQuestionRepository:
    _wrong_questions: dict[str, WrongQuestion] = field(default_factory=dict)
    _knowledge_links: dict[str, list[WrongQuestionKnowledgeLink]] = field(default_factory=dict)
    _tag_links: dict[str, list[TagLink]] = field(default_factory=dict)

    def add_wrong_question(
        self,
        wrong_question: WrongQuestion,
        *,
        knowledge_links: list[WrongQuestionKnowledgeLink] | None = None,
        tag_links: list[TagLink] | None = None,
    ) -> WrongQuestion:
        self._wrong_questions[wrong_question.id] = wrong_question
        self._knowledge_links[wrong_question.id] = list(knowledge_links or [])
        self._tag_links[wrong_question.id] = list(tag_links or [])
        return wrong_question

    def list_wrong_questions(self, user_id: str) -> list[WrongQuestion]:
        return [
            wrong_question
            for wrong_question in self._wrong_questions.values()
            if wrong_question.user_id == user_id
        ]

    def list_knowledge_links(self, wrong_question_id: str) -> list[WrongQuestionKnowledgeLink]:
        return list(self._knowledge_links.get(wrong_question_id, []))

    def list_tag_links(self, wrong_question_id: str) -> list[TagLink]:
        return list(self._tag_links.get(wrong_question_id, []))


@dataclass
class InMemoryPersonalKnowledgeRepository:
    _builds: dict[str, PersonalKnowledgeBuild] = field(default_factory=dict)
    _nodes: dict[str, PersonalKnowledgeNode] = field(default_factory=dict)
    _edges: dict[str, PersonalKnowledgeEdge] = field(default_factory=dict)
    _evidence: dict[str, PersonalKnowledgeEvidence] = field(default_factory=dict)

    def create_build(self, build: PersonalKnowledgeBuild) -> PersonalKnowledgeBuild:
        self._builds[build.id] = build
        return build

    def activate_build(self, build_id: str) -> PersonalKnowledgeBuild:
        build = self.get_build(build_id)
        for candidate in list(self._builds.values()):
            if (
                candidate.user_id == build.user_id
                and candidate.status == PersonalKnowledgeBuildStatus.ACTIVE
                and candidate.id != build_id
            ):
                self._builds[candidate.id] = replace(
                    candidate,
                    status=PersonalKnowledgeBuildStatus.SUPERSEDED,
                )
        active_build = replace(build, status=PersonalKnowledgeBuildStatus.ACTIVE)
        self._builds[build_id] = active_build
        return active_build

    def get_build(self, build_id: str) -> PersonalKnowledgeBuild:
        try:
            return self._builds[build_id]
        except KeyError as exc:
            raise KeyError(f"unknown personal knowledge build: {build_id}") from exc

    def get_active_build(self, user_id: str) -> PersonalKnowledgeBuild:
        active_builds = [
            build
            for build in self._builds.values()
            if build.user_id == user_id and build.status == PersonalKnowledgeBuildStatus.ACTIVE
        ]
        if not active_builds:
            raise LookupError(f"no active personal knowledge build for user: {user_id}")
        return max(active_builds, key=lambda build: build.build_version)

    def add_node(self, node: PersonalKnowledgeNode) -> PersonalKnowledgeNode:
        self._nodes[node.id] = node
        return node

    def list_nodes(self, user_id: str, build_id: str) -> list[PersonalKnowledgeNode]:
        return [
            node
            for node in self._nodes.values()
            if node.user_id == user_id and node.build_id == build_id
        ]

    def add_edge(self, edge: PersonalKnowledgeEdge) -> PersonalKnowledgeEdge:
        self._edges[edge.id] = edge
        return edge

    def list_edges(self, user_id: str, build_id: str) -> list[PersonalKnowledgeEdge]:
        return [
            edge
            for edge in self._edges.values()
            if edge.user_id == user_id and edge.build_id == build_id
        ]

    def add_evidence(self, evidence: PersonalKnowledgeEvidence) -> PersonalKnowledgeEvidence:
        self._evidence[evidence.id] = evidence
        return evidence

    def list_evidence_for_target(self, target_id: str) -> list[PersonalKnowledgeEvidence]:
        return [
            evidence
            for evidence in self._evidence.values()
            if evidence.target_id == target_id
        ]


@dataclass
class InMemoryReviewScheduleRepository:
    _items: dict[str, ReviewScheduleItem] = field(default_factory=dict)

    def add_item(self, item: ReviewScheduleItem) -> ReviewScheduleItem:
        self._items[item.id] = item
        return item

    def list_due_items(self, user_id: str, *, now: datetime) -> list[ReviewScheduleItem]:
        return [
            item
            for item in self._items.values()
            if item.user_id == user_id
            and item.status == ReviewScheduleStatus.ACTIVE
            and item.next_review_at <= now
        ]


@dataclass
class InMemoryPracticeRepository:
    _attempts: dict[str, PracticeAttempt] = field(default_factory=dict)
    _analysis_by_attempt: dict[str, PracticeAttemptAnalysis] = field(default_factory=dict)
    _error_links_by_attempt: dict[str, list[AttemptErrorLink]] = field(default_factory=dict)

    def add_attempt(self, attempt: PracticeAttempt) -> PracticeAttempt:
        self._attempts[attempt.id] = attempt
        return attempt

    def list_attempts(self, user_id: str) -> list[PracticeAttempt]:
        return [
            attempt
            for attempt in self._attempts.values()
            if attempt.user_id == user_id
        ]

    def add_analysis(
        self,
        analysis: PracticeAttemptAnalysis,
        *,
        error_links: list[dict[str, Any]] | list[AttemptErrorLink] | None = None,
    ) -> PracticeAttemptAnalysis:
        self._analysis_by_attempt[analysis.attempt_id] = analysis
        normalized_links: list[AttemptErrorLink] = []
        for link in error_links or []:
            if isinstance(link, AttemptErrorLink):
                normalized_links.append(link)
            else:
                normalized_links.append(AttemptErrorLink(attempt_id=analysis.attempt_id, **link))
        self._error_links_by_attempt[analysis.attempt_id] = normalized_links
        return analysis

    def get_analysis(self, attempt_id: str) -> PracticeAttemptAnalysis:
        try:
            return self._analysis_by_attempt[attempt_id]
        except KeyError as exc:
            raise KeyError(f"unknown practice attempt analysis: {attempt_id}") from exc

    def list_error_links(self, attempt_id: str) -> list[AttemptErrorLink]:
        return list(self._error_links_by_attempt.get(attempt_id, []))


@dataclass
class DailyPracticeService:
    personal_repository: InMemoryPersonalKnowledgeRepository
    schedule_repository: InMemoryReviewScheduleRepository
    practice_repository: InMemoryPracticeRepository

    def select_due_targets(
        self,
        user_id: str,
        *,
        now: datetime,
        limit: int,
    ) -> list[PersonalKnowledgeNode]:
        active_build = self.personal_repository.get_active_build(user_id)
        due_items = self.schedule_repository.list_due_items(user_id, now=now)
        due_ids = {item.knowledge_point_id for item in due_items}
        nodes = self.personal_repository.list_nodes(user_id, active_build.id)
        due_nodes = [node for node in nodes if node.knowledge_point_id in due_ids]
        due_nodes.sort(key=lambda node: (-node.weakness_score, node.knowledge_point_id))
        return due_nodes[:limit]


@dataclass
class InMemoryGeneratedQuestionRepository:
    _questions: dict[str, GeneratedQuestion] = field(default_factory=dict)
    _reports: dict[str, list[QuestionVerificationReport]] = field(default_factory=dict)

    def add_question(self, question: GeneratedQuestion) -> GeneratedQuestion:
        self._questions[question.id] = question
        return question

    def update_question_status(
        self,
        question_id: str,
        status: GeneratedQuestionStatus,
    ) -> GeneratedQuestion:
        question = self.get_question(question_id)
        updated = replace(question, status=status)
        self._questions[question_id] = updated
        return updated

    def get_question(self, question_id: str) -> GeneratedQuestion:
        try:
            return self._questions[question_id]
        except KeyError as exc:
            raise KeyError(f"unknown generated question: {question_id}") from exc

    def add_report(self, report: QuestionVerificationReport) -> QuestionVerificationReport:
        self._reports.setdefault(report.question_id, []).append(report)
        return report

    def list_reports(self, question_id: str) -> list[QuestionVerificationReport]:
        return list(self._reports.get(question_id, []))


@dataclass
class QuestionGenerationService:
    repository: InMemoryGeneratedQuestionRepository

    def start_verification(self, question_id: str) -> GeneratedQuestion:
        return self.repository.update_question_status(
            question_id,
            GeneratedQuestionStatus.VERIFICATION_RUNNING,
        )

    def record_verification_report(
        self,
        report: QuestionVerificationReport,
    ) -> QuestionVerificationReport:
        self.repository.add_report(report)
        question = self.repository.get_question(report.question_id)

        if report.verdict == VerificationVerdict.PASSED:
            self.repository.update_question_status(
                report.question_id,
                GeneratedQuestionStatus.VERIFICATION_PASSED,
            )
        elif question.generation_attempt <= 1:
            self.repository.update_question_status(
                report.question_id,
                GeneratedQuestionStatus.REGENERATED_ONCE,
            )
        else:
            self.repository.update_question_status(
                report.question_id,
                GeneratedQuestionStatus.NEEDS_HUMAN_REVIEW,
            )
        return report

    def approve_for_practice(self, question_id: str) -> GeneratedQuestion:
        question = self.repository.get_question(question_id)
        if question.status != GeneratedQuestionStatus.VERIFICATION_PASSED:
            raise ValueError("generated question must pass verification before practice")
        return self.repository.update_question_status(
            question_id,
            GeneratedQuestionStatus.APPROVED_FOR_PRACTICE,
        )

    def start_regenerated_attempt(self, question_id: str) -> GeneratedQuestion:
        previous = self.repository.get_question(question_id)
        if previous.status != GeneratedQuestionStatus.REGENERATED_ONCE:
            raise ValueError("question is not eligible for a regenerated attempt")
        regenerated = replace(
            previous,
            id=f"{previous.id}_retry_2",
            generation_attempt=previous.generation_attempt + 1,
            status=GeneratedQuestionStatus.DRAFT_GENERATED,
        )
        return self.repository.add_question(regenerated)
