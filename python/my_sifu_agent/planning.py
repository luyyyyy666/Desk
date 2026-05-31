from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import Any


class SkillCapability(StrEnum):
    LLM = "llm"
    RETRIEVAL = "retrieval"
    EXTERNAL_TOOL = "external_tool"
    EXPORT_JOB = "export_job"


class PlanStatus(StrEnum):
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PlanStepStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class SkillDefinition:
    skill_id: str
    display_name: str
    input_schema_ref: str
    output_schema_ref: str
    required_context: tuple[str, ...]
    capabilities: tuple[SkillCapability, ...]
    guardrails: tuple[str, ...]
    event_labels: tuple[str, ...]


@dataclass(frozen=True)
class SkillCatalog:
    skills: tuple[SkillDefinition, ...]

    @classmethod
    def seed(cls) -> SkillCatalog:
        return cls(
            skills=(
                SkillDefinition(
                    skill_id="generate_question_set",
                    display_name="生成题单",
                    input_schema_ref="contracts/skills/generate_question_set.schema.json",
                    output_schema_ref="contracts/skills/generate_question_set.schema.json#/output",
                    required_context=("memory", "rag_results"),
                    capabilities=(SkillCapability.LLM, SkillCapability.RETRIEVAL),
                    guardrails=(
                        "curriculum alignment",
                        "source grounding",
                        "answer correctness",
                        "age-appropriate content",
                    ),
                    event_labels=(
                        "generation_job_created",
                        "retrieval_context_ready",
                        "question_set_ready",
                    ),
                ),
                _skill(
                    "edit_question",
                    "编辑题目",
                    ("question_set",),
                    (SkillCapability.LLM,),
                    ("preserve answer correctness", "preserve source alignment"),
                    ("tool_call_started", "tool_call_completed"),
                ),
                _skill(
                    "explain_question",
                    "生成解析",
                    ("question_set", "memory", "rag_results"),
                    (SkillCapability.LLM, SkillCapability.RETRIEVAL),
                    ("mathematical correctness", "source consistency"),
                    ("tool_call_started", "tool_call_completed"),
                ),
                _skill(
                    "grade_answer",
                    "批改答案",
                    ("answer_attempt", "question_set"),
                    (SkillCapability.LLM,),
                    ("rubric consistency", "explainable grading result"),
                    ("tool_call_started", "evaluation_completed"),
                ),
                _skill(
                    "analyze_mistake",
                    "分析错因",
                    ("answer_attempt", "memory"),
                    (SkillCapability.LLM,),
                    ("observed facts before inferred causes",),
                    ("tool_call_started", "tool_call_completed"),
                ),
                _skill(
                    "recommend_next_practice",
                    "推荐下一练",
                    ("memory", "answer_attempt"),
                    (SkillCapability.LLM,),
                    ("keep recommendations explainable",),
                    ("tool_call_started", "tool_call_completed"),
                ),
                _skill(
                    "search_knowledge",
                    "检索知识",
                    ("memory",),
                    (SkillCapability.RETRIEVAL,),
                    ("source access control", "source attribution"),
                    ("retrieval_context_ready",),
                ),
                _skill(
                    "check_curriculum_alignment",
                    "课标对齐检查",
                    ("question_set", "rag_results"),
                    (SkillCapability.LLM, SkillCapability.RETRIEVAL),
                    ("block or flag off-scope generated content",),
                    ("tool_call_started", "tool_call_completed"),
                ),
                _skill(
                    "evaluate_question_quality",
                    "题目质量评估",
                    ("question_set",),
                    (SkillCapability.LLM,),
                    ("low-quality outputs cannot silently proceed",),
                    ("evaluation_completed",),
                ),
                _skill(
                    "export_paper",
                    "导出试卷",
                    ("question_set",),
                    (SkillCapability.EXPORT_JOB,),
                    ("only export quality-checked question sets",),
                    ("tool_call_started", "tool_call_completed"),
                ),
            )
        )

    @property
    def skill_ids(self) -> tuple[str, ...]:
        return tuple(skill.skill_id for skill in self.skills)

    def require(self, skill_id: str) -> SkillDefinition:
        for skill in self.skills:
            if skill.skill_id == skill_id:
                return skill
        raise ValueError(f"unknown skill: {skill_id}")


@dataclass(frozen=True)
class PlanStep:
    id: str
    skill_id: str
    title: str
    status: PlanStepStatus
    required_context: tuple[str, ...]


@dataclass(frozen=True)
class Plan:
    id: str
    agent_run_id: str
    user_goal: str
    task_type: str
    status: PlanStatus
    steps: tuple[PlanStep, ...]
    current_step_id: str

    def with_replaced_skill(self, *, step_id: str, skill_id: str) -> Plan:
        return replace(
            self,
            steps=tuple(
                replace(step, skill_id=skill_id) if step.id == step_id else step
                for step in self.steps
            ),
        )

    def with_step_order(self, step_ids: tuple[str, ...]) -> Plan:
        step_by_id = {step.id: step for step in self.steps}
        return replace(self, steps=tuple(step_by_id[step_id] for step_id in step_ids))


@dataclass
class InMemoryPlanRepository:
    _plans: dict[str, Plan] = field(default_factory=dict)

    def save(self, plan: Plan) -> None:
        self._plans[plan.id] = plan

    def get(self, plan_id: str) -> Plan:
        try:
            return self._plans[plan_id]
        except KeyError as exc:
            raise KeyError(f"unknown plan: {plan_id}") from exc


@dataclass
class Phase5PlanningApi:
    skill_catalog: SkillCatalog
    plan_repository: InMemoryPlanRepository

    @classmethod
    def default(cls) -> Phase5PlanningApi:
        return cls(
            skill_catalog=SkillCatalog.seed(),
            plan_repository=InMemoryPlanRepository(),
        )

    def generate_plan(self, payload: dict[str, Any]) -> dict[str, Any]:
        task_type = _required(payload, "taskType")
        if task_type != "question_generation":
            raise ValueError(f"unsupported task type: {task_type}")

        plan = self.generate_question_generation_plan(
            agent_run_id=_required(payload, "agentRunId"),
            user_goal=_required(payload, "userGoal"),
            subject=_required(payload, "subject"),
            knowledge_point_ids=tuple(payload.get("knowledgePointIds", ())),
            question_count=int(_required(payload, "questionCount")),
        )
        self.validate_plan(plan)
        self.plan_repository.save(plan)
        return {
            "plan": _plan_to_json(plan),
            "agentRunEvent": _plan_created_event(plan, sequence=1),
        }

    def get_plan(self, plan_id: str) -> dict[str, Any]:
        return {"plan": _plan_to_json(self.plan_repository.get(plan_id))}

    def generate_question_generation_plan(
        self,
        *,
        agent_run_id: str,
        user_goal: str,
        subject: str,
        knowledge_point_ids: tuple[str, ...],
        question_count: int,
    ) -> Plan:
        _ = subject, knowledge_point_ids, question_count
        steps = tuple(
            self._step(index, skill_id)
            for index, skill_id in enumerate(_QUESTION_GENERATION_SKILL_ORDER, start=1)
        )
        return Plan(
            id=f"plan_{agent_run_id}",
            agent_run_id=agent_run_id,
            user_goal=user_goal,
            task_type="question_generation",
            status=PlanStatus.READY,
            steps=steps,
            current_step_id=steps[0].id,
        )

    def validate_plan(self, plan: Plan) -> None:
        for step in plan.steps:
            self.skill_catalog.require(step.skill_id)

        skill_order = tuple(step.skill_id for step in plan.steps)
        if skill_order != _QUESTION_GENERATION_SKILL_ORDER:
            raise ValueError("question generation plan must start with search_knowledge")

    def _step(self, index: int, skill_id: str) -> PlanStep:
        skill = self.skill_catalog.require(skill_id)
        return PlanStep(
            id=f"step_{index:02}_{skill_id}",
            skill_id=skill.skill_id,
            title=skill.display_name,
            status=PlanStepStatus.PENDING,
            required_context=skill.required_context,
        )


_QUESTION_GENERATION_SKILL_ORDER = (
    "search_knowledge",
    "generate_question_set",
    "check_curriculum_alignment",
    "evaluate_question_quality",
)


def _skill(
    skill_id: str,
    display_name: str,
    required_context: tuple[str, ...],
    capabilities: tuple[SkillCapability, ...],
    guardrails: tuple[str, ...],
    event_labels: tuple[str, ...],
) -> SkillDefinition:
    schema_path = f"contracts/skills/{skill_id}.schema.json"
    return SkillDefinition(
        skill_id=skill_id,
        display_name=display_name,
        input_schema_ref=schema_path,
        output_schema_ref=f"{schema_path}#/output",
        required_context=required_context,
        capabilities=capabilities,
        guardrails=guardrails,
        event_labels=event_labels,
    )


def _required(payload: dict[str, Any], key: str) -> Any:
    try:
        return payload[key]
    except KeyError as exc:
        raise ValueError(f"missing required field: {key}") from exc


def _plan_to_json(plan: Plan) -> dict[str, Any]:
    return {
        "id": plan.id,
        "agentRunId": plan.agent_run_id,
        "userGoal": plan.user_goal,
        "taskType": plan.task_type,
        "status": plan.status.value,
        "currentStepId": plan.current_step_id,
        "steps": [
            {
                "id": step.id,
                "skillId": step.skill_id,
                "title": step.title,
                "status": step.status.value,
                "requiredContext": list(step.required_context),
            }
            for step in plan.steps
        ],
    }


def _plan_created_event(plan: Plan, *, sequence: int) -> dict[str, Any]:
    return {
        "id": f"event_{plan.agent_run_id}_{sequence}",
        "agentRunId": plan.agent_run_id,
        "sequence": sequence,
        "kind": "plan_created",
        "payload": {
            "planId": plan.id,
            "status": plan.status.value,
            "stepIds": [step.id for step in plan.steps],
            "skillIds": [step.skill_id for step in plan.steps],
        },
    }
