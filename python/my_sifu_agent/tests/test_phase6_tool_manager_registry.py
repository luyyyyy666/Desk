import pytest
from my_sifu_agent.planning import SkillCatalog
from my_sifu_agent.tool_manager import ToolPermission, ToolRegistry


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
