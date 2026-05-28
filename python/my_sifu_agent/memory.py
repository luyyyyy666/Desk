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


class UserKnowledgeFeedbackType(StrEnum):
    CONFIRM_WEAKNESS = "confirm_weakness"
    DENY_WEAKNESS = "deny_weakness"
    PAUSE_PRACTICE = "pause_practice"
    RESUME_PRACTICE = "resume_practice"
    MARK_MASTERED = "mark_mastered"


class ReviewScheduleStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    MASTERED_PENDING_CONFIRM = "mastered_pending_confirm"
    MASTERED = "mastered"


class DailyPracticePlanMode(StrEnum):
    DEFAULT = "default"
    ENHANCED = "enhanced"


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
class PublicKnowledgeSnapshot:
    knowledge_points: int
    tags: int
    edges: int

    @property
    def is_empty(self) -> bool:
        return self.knowledge_points == 0 and self.tags == 0 and self.edges == 0


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
    feedback_type: UserKnowledgeFeedbackType
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
class GeneratedQuestionKnowledgeLink:
    knowledge_point_id: str
    content_weight: float
    role: KnowledgeLinkRole


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
    knowledge_point_links: tuple[GeneratedQuestionKnowledgeLink, ...]
    expected_error_traps: tuple[str, ...]
    grading_rubric: str
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


@dataclass(frozen=True)
class PracticeGenerationPlan:
    mode: DailyPracticePlanMode
    target_knowledge_point_ids: tuple[str, ...]
    total_question_count: int
    llm_generated_question_count: int

    @classmethod
    def for_mode(
        cls,
        mode: DailyPracticePlanMode,
        *,
        target_knowledge_point_ids: list[str] | tuple[str, ...],
    ) -> PracticeGenerationPlan:
        if mode == DailyPracticePlanMode.DEFAULT:
            llm_generated_question_count = 1
        else:
            llm_generated_question_count = 3
        return cls(
            mode=mode,
            target_knowledge_point_ids=tuple(target_knowledge_point_ids),
            total_question_count=3,
            llm_generated_question_count=llm_generated_question_count,
        )

    @property
    def stable_bank_question_count(self) -> int:
        return self.total_question_count - self.llm_generated_question_count

    @property
    def generation_modes(self) -> tuple[GeneratedQuestionMode, ...]:
        modes: list[GeneratedQuestionMode] = []
        if self.stable_bank_question_count > 0:
            modes.append(GeneratedQuestionMode.STABLE_BANK)
        if self.llm_generated_question_count > 0:
            modes.append(GeneratedQuestionMode.LLM_TOOL_GENERATED)
        return tuple(modes)


@dataclass(frozen=True)
class ActivePersonalKnowledgeBuildSnapshot:
    build_id: str
    build_version: int
    status: PersonalKnowledgeBuildStatus
    public_kb_version: str


@dataclass(frozen=True)
class Phase3MemorySnapshot:
    user_id: str
    public_knowledge: PublicKnowledgeSnapshot
    wrong_question_count: int
    active_personal_build: ActivePersonalKnowledgeBuildSnapshot | None
    personal_node_count: int
    personal_edge_count: int
    personal_evidence_count: int
    user_knowledge_note_count: int
    user_knowledge_feedback_count: int
    due_review_count: int
    practice_attempt_count: int
    practice_analysis_count: int
    generated_question_count: int
    approved_generated_question_count: int


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

    def snapshot(self) -> PublicKnowledgeSnapshot:
        return PublicKnowledgeSnapshot(
            knowledge_points=len(self._knowledge_points),
            tags=len(self._tags),
            edges=len(self._edges),
        )


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

    def update_node(self, node: PersonalKnowledgeNode) -> PersonalKnowledgeNode:
        if node.id not in self._nodes:
            raise KeyError(f"unknown personal knowledge node: {node.id}")
        self._nodes[node.id] = node
        return node

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

    def list_evidence(self, user_id: str, build_id: str) -> list[PersonalKnowledgeEvidence]:
        return [
            evidence
            for evidence in self._evidence.values()
            if evidence.user_id == user_id and evidence.build_id == build_id
        ]


@dataclass
class InMemoryUserKnowledgeRepository:
    _notes: dict[tuple[str, str, str], UserKnowledgeNote] = field(default_factory=dict)
    _feedback: dict[tuple[str, str, str], UserKnowledgeFeedback] = field(default_factory=dict)

    def upsert_note(self, note: UserKnowledgeNote) -> UserKnowledgeNote:
        self._notes[(note.user_id, note.knowledge_point_id, note.id)] = note
        return note

    def record_feedback(self, feedback: UserKnowledgeFeedback) -> UserKnowledgeFeedback:
        self._feedback[(feedback.user_id, feedback.knowledge_point_id, feedback.id)] = feedback
        return feedback

    def list_notes(self, user_id: str, knowledge_point_id: str) -> list[UserKnowledgeNote]:
        return [
            note
            for (stored_user_id, stored_knowledge_point_id, _), note in self._notes.items()
            if stored_user_id == user_id and stored_knowledge_point_id == knowledge_point_id
        ]

    def list_feedback(
        self,
        user_id: str,
        knowledge_point_id: str,
    ) -> list[UserKnowledgeFeedback]:
        return [
            feedback
            for (
                stored_user_id,
                stored_knowledge_point_id,
                _,
            ), feedback in self._feedback.items()
            if stored_user_id == user_id and stored_knowledge_point_id == knowledge_point_id
        ]

    def count_notes(self, user_id: str) -> int:
        return sum(1 for stored_user_id, _, _ in self._notes if stored_user_id == user_id)

    def count_feedback(self, user_id: str) -> int:
        return sum(1 for stored_user_id, _, _ in self._feedback if stored_user_id == user_id)


@dataclass
class InMemoryReviewScheduleRepository:
    _items: dict[str, ReviewScheduleItem] = field(default_factory=dict)

    def add_item(self, item: ReviewScheduleItem) -> ReviewScheduleItem:
        self._items[item.id] = item
        return item

    def get_item(self, user_id: str, knowledge_point_id: str) -> ReviewScheduleItem:
        matching_items = [
            item
            for item in self._items.values()
            if item.user_id == user_id and item.knowledge_point_id == knowledge_point_id
        ]
        if not matching_items:
            raise KeyError(
                f"unknown review schedule item: {user_id}/{knowledge_point_id}"
            )
        return max(matching_items, key=lambda item: item.updated_at)

    def update_item(self, item: ReviewScheduleItem) -> ReviewScheduleItem:
        if item.id not in self._items:
            raise KeyError(f"unknown review schedule item: {item.id}")
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

    def list_analyses(self) -> list[PracticeAttemptAnalysis]:
        return list(self._analysis_by_attempt.values())


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

    def list_questions(self, user_id: str) -> list[GeneratedQuestion]:
        return [
            question
            for question in self._questions.values()
            if question.user_id == user_id
        ]


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
                GeneratedQuestionStatus.VERIFICATION_FAILED,
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

    def mark_used_in_daily_practice(self, question_id: str) -> GeneratedQuestion:
        question = self.repository.get_question(question_id)
        if question.status != GeneratedQuestionStatus.APPROVED_FOR_PRACTICE:
            raise ValueError("generated question must be approved before daily practice use")
        return self.repository.update_question_status(
            question_id,
            GeneratedQuestionStatus.USED_IN_DAILY_PRACTICE,
        )

    def start_regenerated_attempt(self, question_id: str) -> GeneratedQuestion:
        previous = self.repository.get_question(question_id)
        if previous.status != GeneratedQuestionStatus.VERIFICATION_FAILED:
            raise ValueError("question is not eligible for a regenerated attempt")
        regenerated = replace(
            previous,
            id=f"{previous.id}_retry_2",
            generation_attempt=previous.generation_attempt + 1,
            status=GeneratedQuestionStatus.REGENERATED_ONCE,
        )
        return self.repository.add_question(regenerated)


@dataclass
class Phase3MemoryWorkspace:
    public_knowledge_repository: InMemoryPublicKnowledgeRepository
    wrong_question_repository: InMemoryWrongQuestionRepository
    personal_knowledge_repository: InMemoryPersonalKnowledgeRepository
    user_knowledge_repository: InMemoryUserKnowledgeRepository
    review_schedule_repository: InMemoryReviewScheduleRepository
    practice_repository: InMemoryPracticeRepository
    generated_question_repository: InMemoryGeneratedQuestionRepository

    @classmethod
    def empty(cls) -> Phase3MemoryWorkspace:
        return cls(
            public_knowledge_repository=InMemoryPublicKnowledgeRepository(),
            wrong_question_repository=InMemoryWrongQuestionRepository(),
            personal_knowledge_repository=InMemoryPersonalKnowledgeRepository(),
            user_knowledge_repository=InMemoryUserKnowledgeRepository(),
            review_schedule_repository=InMemoryReviewScheduleRepository(),
            practice_repository=InMemoryPracticeRepository(),
            generated_question_repository=InMemoryGeneratedQuestionRepository(),
        )

    def bootstrap_public_knowledge(
        self,
        seed: PublicKnowledgeSeedData,
    ) -> PublicKnowledgeImportResult:
        return self.public_knowledge_repository.import_seed(seed)

    def record_wrong_question(
        self,
        wrong_question: WrongQuestion,
        *,
        knowledge_links: list[WrongQuestionKnowledgeLink] | None = None,
        tag_links: list[TagLink] | None = None,
    ) -> WrongQuestion:
        return self.wrong_question_repository.add_wrong_question(
            wrong_question,
            knowledge_links=knowledge_links,
            tag_links=tag_links,
        )

    def activate_personal_knowledge_build(
        self,
        build: PersonalKnowledgeBuild,
        *,
        nodes: list[PersonalKnowledgeNode],
        edges: list[PersonalKnowledgeEdge],
        evidence: list[PersonalKnowledgeEvidence],
    ) -> PersonalKnowledgeBuild:
        self._validate_personal_knowledge_evidence(
            nodes=nodes,
            edges=edges,
            evidence=evidence,
        )
        self.personal_knowledge_repository.create_build(build)
        for node in nodes:
            self.personal_knowledge_repository.add_node(node)
        for edge in edges:
            self.personal_knowledge_repository.add_edge(edge)
        for evidence_item in evidence:
            self.personal_knowledge_repository.add_evidence(evidence_item)
        return self.personal_knowledge_repository.activate_build(build.id)

    def upsert_user_knowledge_note(self, note: UserKnowledgeNote) -> UserKnowledgeNote:
        return self.user_knowledge_repository.upsert_note(note)

    def record_user_knowledge_feedback(
        self,
        feedback: UserKnowledgeFeedback,
    ) -> UserKnowledgeFeedback:
        stored = self.user_knowledge_repository.record_feedback(feedback)
        if feedback.feedback_type == UserKnowledgeFeedbackType.MARK_MASTERED:
            self._confirm_mastery(feedback)
        return stored

    def list_user_knowledge_notes(
        self,
        user_id: str,
        knowledge_point_id: str,
    ) -> list[UserKnowledgeNote]:
        return self.user_knowledge_repository.list_notes(user_id, knowledge_point_id)

    def list_user_knowledge_feedback(
        self,
        user_id: str,
        knowledge_point_id: str,
    ) -> list[UserKnowledgeFeedback]:
        return self.user_knowledge_repository.list_feedback(user_id, knowledge_point_id)

    def schedule_review(self, item: ReviewScheduleItem) -> ReviewScheduleItem:
        return self.review_schedule_repository.add_item(item)

    def get_review_schedule_item(
        self,
        user_id: str,
        knowledge_point_id: str,
    ) -> ReviewScheduleItem:
        return self.review_schedule_repository.get_item(user_id, knowledge_point_id)

    def get_active_personal_knowledge_node(
        self,
        user_id: str,
        knowledge_point_id: str,
    ) -> PersonalKnowledgeNode:
        active_build = self.personal_knowledge_repository.get_active_build(user_id)
        matching_nodes = [
            node
            for node in self.personal_knowledge_repository.list_nodes(user_id, active_build.id)
            if node.knowledge_point_id == knowledge_point_id
        ]
        if not matching_nodes:
            raise KeyError(
                f"unknown active personal knowledge node: {user_id}/{knowledge_point_id}"
            )
        return matching_nodes[0]

    def select_daily_practice_targets(
        self,
        user_id: str,
        *,
        now: datetime,
        limit: int,
    ) -> list[PersonalKnowledgeNode]:
        service = DailyPracticeService(
            personal_repository=self.personal_knowledge_repository,
            schedule_repository=self.review_schedule_repository,
            practice_repository=self.practice_repository,
        )
        return service.select_due_targets(user_id, now=now, limit=limit)

    def record_practice_attempt_analysis(
        self,
        attempt: PracticeAttempt,
        analysis: PracticeAttemptAnalysis,
        *,
        error_links: list[dict[str, Any]] | list[AttemptErrorLink] | None = None,
    ) -> PracticeAttemptAnalysis:
        self._validate_practice_attempt_question_can_update_memory(attempt)
        self.practice_repository.add_attempt(attempt)
        stored_analysis = self.practice_repository.add_analysis(
            analysis,
            error_links=error_links,
        )
        self._apply_practice_analysis_to_mastery(attempt, stored_analysis)
        return stored_analysis

    def submit_generated_question(self, question: GeneratedQuestion) -> GeneratedQuestion:
        return self.generated_question_repository.add_question(question)

    def start_question_verification(self, question_id: str) -> GeneratedQuestion:
        return self._question_generation_service().start_verification(question_id)

    def record_question_verification(
        self,
        report: QuestionVerificationReport,
    ) -> QuestionVerificationReport:
        return self._question_generation_service().record_verification_report(report)

    def approve_generated_question_for_practice(self, question_id: str) -> GeneratedQuestion:
        return self._question_generation_service().approve_for_practice(question_id)

    def mark_generated_question_used_in_daily_practice(
        self,
        question_id: str,
    ) -> GeneratedQuestion:
        return self._question_generation_service().mark_used_in_daily_practice(question_id)

    def start_regenerated_question_attempt(self, question_id: str) -> GeneratedQuestion:
        return self._question_generation_service().start_regenerated_attempt(question_id)

    def get_generated_question(self, question_id: str) -> GeneratedQuestion:
        return self.generated_question_repository.get_question(question_id)

    def snapshot(self, user_id: str, *, now: datetime) -> Phase3MemorySnapshot:
        active_build = self._active_build_or_none(user_id)
        if active_build is None:
            personal_nodes: list[PersonalKnowledgeNode] = []
            personal_edges: list[PersonalKnowledgeEdge] = []
            personal_evidence: list[PersonalKnowledgeEvidence] = []
            active_build_snapshot = None
        else:
            personal_nodes = self.personal_knowledge_repository.list_nodes(user_id, active_build.id)
            personal_edges = self.personal_knowledge_repository.list_edges(user_id, active_build.id)
            personal_evidence = self.personal_knowledge_repository.list_evidence(
                user_id,
                active_build.id,
            )
            active_build_snapshot = ActivePersonalKnowledgeBuildSnapshot(
                build_id=active_build.id,
                build_version=active_build.build_version,
                status=active_build.status,
                public_kb_version=active_build.public_kb_version,
            )

        attempts = self.practice_repository.list_attempts(user_id)
        attempt_ids = {attempt.id for attempt in attempts}
        analyses = [
            analysis
            for analysis in self.practice_repository.list_analyses()
            if analysis.attempt_id in attempt_ids
        ]
        generated_questions = self.generated_question_repository.list_questions(user_id)

        return Phase3MemorySnapshot(
            user_id=user_id,
            public_knowledge=self.public_knowledge_repository.snapshot(),
            wrong_question_count=len(self.wrong_question_repository.list_wrong_questions(user_id)),
            active_personal_build=active_build_snapshot,
            personal_node_count=len(personal_nodes),
            personal_edge_count=len(personal_edges),
            personal_evidence_count=len(personal_evidence),
            user_knowledge_note_count=self.user_knowledge_repository.count_notes(user_id),
            user_knowledge_feedback_count=self.user_knowledge_repository.count_feedback(user_id),
            due_review_count=len(
                self.review_schedule_repository.list_due_items(user_id, now=now)
            ),
            practice_attempt_count=len(attempts),
            practice_analysis_count=len(analyses),
            generated_question_count=len(generated_questions),
            approved_generated_question_count=len(
                [
                    question
                    for question in generated_questions
                    if question.status == GeneratedQuestionStatus.APPROVED_FOR_PRACTICE
                ]
            ),
        )

    def _question_generation_service(self) -> QuestionGenerationService:
        return QuestionGenerationService(self.generated_question_repository)

    def _validate_practice_attempt_question_can_update_memory(
        self,
        attempt: PracticeAttempt,
    ) -> None:
        try:
            question = self.generated_question_repository.get_question(attempt.question_id)
        except KeyError:
            return
        if question.status != GeneratedQuestionStatus.USED_IN_DAILY_PRACTICE:
            raise ValueError(
                "practice analysis from a generated question requires an approved generated "
                "question used in daily practice"
            )

    def _active_build_or_none(self, user_id: str) -> PersonalKnowledgeBuild | None:
        try:
            return self.personal_knowledge_repository.get_active_build(user_id)
        except LookupError:
            return None

    def _apply_practice_analysis_to_mastery(
        self,
        attempt: PracticeAttempt,
        analysis: PracticeAttemptAnalysis,
    ) -> None:
        target_knowledge_ids = self._practice_attempt_target_knowledge_ids(attempt, analysis)
        for knowledge_point_id in target_knowledge_ids:
            try:
                node = self.get_active_personal_knowledge_node(
                    attempt.user_id,
                    knowledge_point_id,
                )
            except (KeyError, LookupError):
                continue
            mastery_score = _clamp_score(node.mastery_score + analysis.mastery_delta)
            weakness_score = _clamp_score(node.weakness_score + analysis.weakness_delta)
            mastery_state = node.mastery_state
            if mastery_score >= 0.9:
                mastery_state = MasteryState.MASTERED_PENDING_CONFIRM
                self._set_review_status(
                    attempt.user_id,
                    knowledge_point_id,
                    ReviewScheduleStatus.MASTERED_PENDING_CONFIRM,
                    analysis.created_at,
                )
            elif attempt.is_correct and mastery_state == MasteryState.WEAK:
                mastery_state = MasteryState.LEARNING
            elif not attempt.is_correct:
                mastery_state = MasteryState.WEAK

            self.personal_knowledge_repository.update_node(
                replace(
                    node,
                    mastery_state=mastery_state,
                    mastery_score=mastery_score,
                    weakness_score=weakness_score,
                    updated_at=analysis.created_at,
                )
            )

    def _practice_attempt_target_knowledge_ids(
        self,
        attempt: PracticeAttempt,
        analysis: PracticeAttemptAnalysis,
    ) -> list[str]:
        error_links = self.practice_repository.list_error_links(attempt.id)
        if error_links:
            return [link.knowledge_point_id for link in error_links]
        try:
            question = self.generated_question_repository.get_question(attempt.question_id)
        except KeyError:
            return []
        return [link.knowledge_point_id for link in question.knowledge_point_links]

    def _confirm_mastery(self, feedback: UserKnowledgeFeedback) -> None:
        try:
            node = self.get_active_personal_knowledge_node(
                feedback.user_id,
                feedback.knowledge_point_id,
            )
        except (KeyError, LookupError):
            return
        if node.mastery_state != MasteryState.MASTERED_PENDING_CONFIRM:
            return
        self.personal_knowledge_repository.update_node(
            replace(
                node,
                mastery_state=MasteryState.MASTERED,
                updated_at=feedback.created_at,
            )
        )
        self._set_review_status(
            feedback.user_id,
            feedback.knowledge_point_id,
            ReviewScheduleStatus.MASTERED,
            feedback.created_at,
        )

    def _set_review_status(
        self,
        user_id: str,
        knowledge_point_id: str,
        status: ReviewScheduleStatus,
        updated_at: datetime,
    ) -> None:
        item = self.review_schedule_repository.get_item(user_id, knowledge_point_id)
        self.review_schedule_repository.update_item(
            replace(item, status=status, updated_at=updated_at)
        )

    def _validate_personal_knowledge_evidence(
        self,
        *,
        nodes: list[PersonalKnowledgeNode],
        edges: list[PersonalKnowledgeEdge],
        evidence: list[PersonalKnowledgeEvidence],
    ) -> None:
        cited_targets = {(item.target_type, item.target_id) for item in evidence}
        missing_node_ids = [
            node.id
            for node in nodes
            if node.evidence_count > 0 and ("node", node.id) not in cited_targets
        ]
        missing_edge_ids = [
            edge.id
            for edge in edges
            if edge.evidence_count > 0 and ("edge", edge.id) not in cited_targets
        ]
        if missing_node_ids or missing_edge_ids:
            missing = [*missing_node_ids, *missing_edge_ids]
            raise ValueError(f"personal knowledge targets must cite evidence: {missing}")


def _clamp_score(value: float) -> float:
    return round(min(1.0, max(0.0, value)), 4)
