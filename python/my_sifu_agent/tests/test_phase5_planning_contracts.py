from pathlib import Path

import pytest
from my_sifu_agent.planning import (
    InMemoryPlanRepository,
    Phase5PlanningApi,
    PlanStatus,
    PlanStepStatus,
    SkillCapability,
    SkillCatalog,
)

ROOT = Path(__file__).resolve().parents[3]


def test_skill_catalog_seed_contains_stable_backend_skill_ids() -> None:
    catalog = SkillCatalog.seed()

    assert catalog.skill_ids == (
        "generate_question_set",
        "edit_question",
        "explain_question",
        "grade_answer",
        "analyze_mistake",
        "recommend_next_practice",
        "search_knowledge",
        "check_curriculum_alignment",
        "evaluate_question_quality",
        "export_paper",
    )
    generate_question_set = catalog.require("generate_question_set")
    assert generate_question_set.display_name == "生成题单"
    assert (
        generate_question_set.input_schema_ref
        == "contracts/skills/generate_question_set.schema.json"
    )
    assert (
        generate_question_set.output_schema_ref
        == "contracts/skills/generate_question_set.schema.json#/output"
    )
    assert generate_question_set.required_context == ("memory", "rag_results")
    assert generate_question_set.capabilities == (
        SkillCapability.LLM,
        SkillCapability.RETRIEVAL,
    )
    assert "answer correctness" in generate_question_set.guardrails
    assert generate_question_set.event_labels == (
        "generation_job_created",
        "retrieval_context_ready",
        "question_set_ready",
    )


def test_phase55_skill_schema_deliverables_exist_for_seed_catalog() -> None:
    catalog = SkillCatalog.seed()

    assert (ROOT / "contracts" / "skills" / "skill-catalog.schema.json").is_file()
    for skill in catalog.skills:
        schema_path = ROOT / skill.input_schema_ref
        assert schema_path.is_file(), f"missing schema for {skill.skill_id}: {schema_path}"


def test_planner_generates_question_generation_plan_with_catalog_skill_ids() -> None:
    api = Phase5PlanningApi.default()

    response = api.generate_plan(
        {
            "agentRunId": "run_plan_001",
            "userGoal": "围绕一次函数生成 8 道中等难度题",
            "taskType": "question_generation",
            "subject": "math",
            "knowledgePointIds": ["kp_linear_function"],
            "questionCount": 8,
        }
    )

    plan = response["plan"]
    assert plan["id"] == "plan_run_plan_001"
    assert plan["agentRunId"] == "run_plan_001"
    assert plan["status"] == PlanStatus.READY.value
    assert [step["skillId"] for step in plan["steps"]] == [
        "search_knowledge",
        "generate_question_set",
        "check_curriculum_alignment",
        "evaluate_question_quality",
    ]
    assert [step["status"] for step in plan["steps"]] == [
        PlanStepStatus.PENDING.value,
        PlanStepStatus.PENDING.value,
        PlanStepStatus.PENDING.value,
        PlanStepStatus.PENDING.value,
    ]
    assert plan["currentStepId"] == "step_01_search_knowledge"
    assert response["agentRunEvent"] == {
        "id": "event_run_plan_001_1",
        "agentRunId": "run_plan_001",
        "sequence": 1,
        "kind": "plan_created",
        "payload": {
            "planId": "plan_run_plan_001",
            "status": "ready",
            "stepIds": [
                "step_01_search_knowledge",
                "step_02_generate_question_set",
                "step_03_check_curriculum_alignment",
                "step_04_evaluate_question_quality",
            ],
            "skillIds": [
                "search_knowledge",
                "generate_question_set",
                "check_curriculum_alignment",
                "evaluate_question_quality",
            ],
        },
    }

    persisted = api.get_plan("plan_run_plan_001")
    assert persisted["plan"]["id"] == "plan_run_plan_001"
    assert persisted["plan"]["currentStepId"] == "step_01_search_knowledge"


def test_planner_rejects_unknown_skill_id_and_invalid_step_order() -> None:
    catalog = SkillCatalog.seed()
    api = Phase5PlanningApi(
        skill_catalog=catalog,
        plan_repository=InMemoryPlanRepository(),
    )
    plan = api.generate_question_generation_plan(
        agent_run_id="run_plan_002",
        user_goal="生成一次函数题",
        subject="math",
        knowledge_point_ids=("kp_linear_function",),
        question_count=8,
    )

    invalid_unknown_skill = plan.with_replaced_skill(
        step_id="step_02_generate_question_set",
        skill_id="free_form_tool_name",
    )
    with pytest.raises(ValueError, match="unknown skill"):
        api.validate_plan(invalid_unknown_skill)

    invalid_order = plan.with_step_order(
        (
            "step_02_generate_question_set",
            "step_01_search_knowledge",
            "step_03_check_curriculum_alignment",
            "step_04_evaluate_question_quality",
        )
    )
    with pytest.raises(ValueError, match="search_knowledge"):
        api.validate_plan(invalid_order)
