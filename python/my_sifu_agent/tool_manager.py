from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from my_sifu_agent.planning import SkillCapability, SkillCatalog


class ToolPermission(StrEnum):
    LLM_CALL = "llm_call"
    RETRIEVAL_READ = "retrieval_read"
    EXTERNAL_TOOL_CALL = "external_tool_call"
    EXPORT_WRITE = "export_write"


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    skill_id: str
    input_schema_ref: str
    output_schema_ref: str
    required_context: tuple[str, ...]
    permissions: tuple[ToolPermission, ...]
    timeout_seconds: int
    max_retries: int
    is_skill_backed: bool = True


@dataclass(frozen=True)
class ToolRegistry:
    tools: tuple[ToolDefinition, ...]

    @classmethod
    def from_skill_catalog(cls, catalog: SkillCatalog) -> ToolRegistry:
        return cls(
            tools=tuple(
                ToolDefinition(
                    name=skill.skill_id,
                    skill_id=skill.skill_id,
                    input_schema_ref=skill.input_schema_ref,
                    output_schema_ref=skill.output_schema_ref,
                    required_context=skill.required_context,
                    permissions=_permissions_for(skill.capabilities),
                    timeout_seconds=60,
                    max_retries=1,
                )
                for skill in catalog.skills
            )
        )

    @property
    def tool_names(self) -> tuple[str, ...]:
        return tuple(tool.name for tool in self.tools)

    def require(self, tool_name: str) -> ToolDefinition:
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        raise ValueError(f"unknown tool: {tool_name}")


def _permissions_for(
    capabilities: tuple[SkillCapability, ...],
) -> tuple[ToolPermission, ...]:
    permission_by_capability = {
        SkillCapability.LLM: ToolPermission.LLM_CALL,
        SkillCapability.RETRIEVAL: ToolPermission.RETRIEVAL_READ,
        SkillCapability.EXTERNAL_TOOL: ToolPermission.EXTERNAL_TOOL_CALL,
        SkillCapability.EXPORT_JOB: ToolPermission.EXPORT_WRITE,
    }
    return tuple(permission_by_capability[capability] for capability in capabilities)
