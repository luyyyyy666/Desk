import pytest
from my_sifu_agent.planning import SkillCatalog
from my_sifu_agent.tool_manager import (
    MockToolExecutor,
    Phase6ToolManagerApi,
    ToolPermission,
    ToolRegistry,
)


def test_tool_registry_derives_skill_backed_tools_from_phase55_catalog() -> None:
    catalog = SkillCatalog.seed()

    registry = ToolRegistry.from_skill_catalog(catalog)

    assert registry.tool_names == catalog.skill_ids

    generate_question_set = registry.require("generate_question_set")
    assert generate_question_set.skill_id == "generate_question_set"
    assert (
        generate_question_set.input_schema_ref
        == "contracts/skills/generate_question_set.schema.json"
    )
    assert (
        generate_question_set.output_schema_ref
        == "contracts/skills/generate_question_set.schema.json#/output"
    )
    assert generate_question_set.required_context == ("memory", "rag_results")
    assert generate_question_set.permissions == (
        ToolPermission.LLM_CALL,
        ToolPermission.RETRIEVAL_READ,
    )
    assert generate_question_set.timeout_seconds == 60
    assert generate_question_set.max_retries == 1
    assert generate_question_set.is_skill_backed is True


def test_tool_registry_rejects_unknown_tool_names() -> None:
    registry = ToolRegistry.from_skill_catalog(SkillCatalog.seed())

    with pytest.raises(ValueError, match="unknown tool"):
        registry.require("free_form_tool_name")


def test_tool_manager_records_auditable_mock_tool_call_events() -> None:
    api = Phase6ToolManagerApi.default()

    response = api.call_tool(
        {
            "agentRunId": "run_tool_001",
            "toolName": "search_knowledge",
            "input": {"query": "一次函数", "desiredResultCount": 3},
            "sequenceStart": 10,
        }
    )

    call = response["toolCall"]
    assert call["id"] == "tool_call_run_tool_001_001"
    assert call["agentRunId"] == "run_tool_001"
    assert call["toolName"] == "search_knowledge"
    assert call["skillId"] == "search_knowledge"
    assert call["status"] == "succeeded"
    assert call["input"] == {"query": "一次函数", "desiredResultCount": 3}
    assert call["output"] == {
        "toolName": "search_knowledge",
        "mode": "mock",
        "acceptedInputKeys": ["desiredResultCount", "query"],
    }
    assert call["error"] is None
    assert call["startedAt"] == "2026-05-31T00:00:00Z"
    assert call["finishedAt"] == "2026-05-31T00:00:01Z"

    assert response["agentRunEvents"] == [
        {
            "id": "event_run_tool_001_10",
            "agentRunId": "run_tool_001",
            "sequence": 10,
            "kind": "tool_call_started",
            "payload": {
                "toolCallId": "tool_call_run_tool_001_001",
                "toolName": "search_knowledge",
                "skillId": "search_knowledge",
            },
        },
        {
            "id": "event_run_tool_001_11",
            "agentRunId": "run_tool_001",
            "sequence": 11,
            "kind": "tool_call_completed",
            "payload": {
                "toolCallId": "tool_call_run_tool_001_001",
                "toolName": "search_knowledge",
                "skillId": "search_knowledge",
                "status": "succeeded",
            },
        },
    ]

    persisted = api.get_tool_call("tool_call_run_tool_001_001")
    assert persisted["toolCall"] == call


def test_failed_tool_call_is_audited_without_completed_success_event() -> None:
    api = Phase6ToolManagerApi(
        registry=ToolRegistry.from_skill_catalog(SkillCatalog.seed()),
        executor=MockToolExecutor.fail_for({"generate_question_set": "mock failure"}),
    )

    response = api.call_tool(
        {
            "agentRunId": "run_tool_002",
            "toolName": "generate_question_set",
            "input": {"learningGoal": "一次函数", "subject": "math", "questionCount": 3},
            "sequenceStart": 20,
        }
    )

    call = response["toolCall"]
    assert call["status"] == "failed"
    assert call["output"] is None
    assert call["error"] == "mock failure"
    assert [event["kind"] for event in response["agentRunEvents"]] == [
        "tool_call_started",
        "tool_call_failed",
    ]
    assert response["agentRunEvents"][1]["payload"]["status"] == "failed"
