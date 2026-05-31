from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from my_sifu_agent.planning import SkillCapability, SkillCatalog


class ToolPermission(StrEnum):
    LLM_CALL = "llm_call"
    RETRIEVAL_READ = "retrieval_read"
    EXTERNAL_TOOL_CALL = "external_tool_call"
    EXPORT_WRITE = "export_write"


class ToolCallStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


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


@dataclass(frozen=True)
class ToolCallRecord:
    id: str
    agent_run_id: str
    tool_name: str
    skill_id: str
    status: ToolCallStatus
    input: dict[str, Any]
    output: dict[str, Any] | None
    error: str | None
    started_at: str
    finished_at: str | None


@dataclass
class InMemoryToolCallRepository:
    _calls: dict[str, ToolCallRecord] = field(default_factory=dict)

    def save(self, call: ToolCallRecord) -> None:
        self._calls[call.id] = call

    def get(self, call_id: str) -> ToolCallRecord:
        try:
            return self._calls[call_id]
        except KeyError as exc:
            raise KeyError(f"unknown tool call: {call_id}") from exc


@dataclass(frozen=True)
class MockToolExecutor:
    failures: dict[str, str] = field(default_factory=dict)

    @classmethod
    def fail_for(cls, failures: dict[str, str]) -> MockToolExecutor:
        return cls(failures=failures)

    def execute(self, tool: ToolDefinition, input_payload: dict[str, Any]) -> dict[str, Any]:
        if tool.name in self.failures:
            raise ToolExecutionError(self.failures[tool.name])
        return {
            "toolName": tool.name,
            "mode": "mock",
            "acceptedInputKeys": sorted(input_payload.keys()),
        }


class ToolExecutionError(Exception):
    pass


@dataclass
class Phase6ToolManagerApi:
    registry: ToolRegistry
    executor: MockToolExecutor = field(default_factory=MockToolExecutor)
    call_repository: InMemoryToolCallRepository = field(
        default_factory=InMemoryToolCallRepository
    )
    _next_call_index: int = 1

    @classmethod
    def default(cls) -> Phase6ToolManagerApi:
        return cls(registry=ToolRegistry.from_skill_catalog(SkillCatalog.seed()))

    def call_tool(self, payload: dict[str, Any]) -> dict[str, Any]:
        agent_run_id = _required(payload, "agentRunId")
        tool_name = _required(payload, "toolName")
        input_payload = dict(_required(payload, "input"))
        sequence_start = int(_required(payload, "sequenceStart"))
        tool = self.registry.require(tool_name)
        call_id = f"tool_call_{agent_run_id}_{self._next_call_index:03}"
        self._next_call_index += 1

        started_event = _tool_call_event(
            agent_run_id=agent_run_id,
            sequence=sequence_start,
            kind="tool_call_started",
            tool_call_id=call_id,
            tool=tool,
        )
        try:
            output = self.executor.execute(tool, input_payload)
        except ToolExecutionError as exc:
            call = ToolCallRecord(
                id=call_id,
                agent_run_id=agent_run_id,
                tool_name=tool.name,
                skill_id=tool.skill_id,
                status=ToolCallStatus.FAILED,
                input=input_payload,
                output=None,
                error=str(exc),
                started_at=_STARTED_AT,
                finished_at=_FINISHED_AT,
            )
            self.call_repository.save(call)
            failed_event = _tool_call_event(
                agent_run_id=agent_run_id,
                sequence=sequence_start + 1,
                kind="tool_call_failed",
                tool_call_id=call_id,
                tool=tool,
                status=ToolCallStatus.FAILED.value,
                error=str(exc),
            )
            return {
                "toolCall": _tool_call_to_json(call),
                "agentRunEvents": [started_event, failed_event],
            }

        call = ToolCallRecord(
            id=call_id,
            agent_run_id=agent_run_id,
            tool_name=tool.name,
            skill_id=tool.skill_id,
            status=ToolCallStatus.SUCCEEDED,
            input=input_payload,
            output=output,
            error=None,
            started_at=_STARTED_AT,
            finished_at=_FINISHED_AT,
        )
        self.call_repository.save(call)
        completed_event = _tool_call_event(
            agent_run_id=agent_run_id,
            sequence=sequence_start + 1,
            kind="tool_call_completed",
            tool_call_id=call_id,
            tool=tool,
            status=ToolCallStatus.SUCCEEDED.value,
        )
        return {
            "toolCall": _tool_call_to_json(call),
            "agentRunEvents": [started_event, completed_event],
        }

    def get_tool_call(self, call_id: str) -> dict[str, Any]:
        return {"toolCall": _tool_call_to_json(self.call_repository.get(call_id))}


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


_STARTED_AT = "2026-05-31T00:00:00Z"
_FINISHED_AT = "2026-05-31T00:00:01Z"


def _required(payload: dict[str, Any], key: str) -> Any:
    try:
        return payload[key]
    except KeyError as exc:
        raise ValueError(f"missing required field: {key}") from exc


def _tool_call_to_json(call: ToolCallRecord) -> dict[str, Any]:
    return {
        "id": call.id,
        "agentRunId": call.agent_run_id,
        "toolName": call.tool_name,
        "skillId": call.skill_id,
        "status": call.status.value,
        "input": call.input,
        "output": call.output,
        "error": call.error,
        "startedAt": call.started_at,
        "finishedAt": call.finished_at,
    }


def _tool_call_event(
    *,
    agent_run_id: str,
    sequence: int,
    kind: str,
    tool_call_id: str,
    tool: ToolDefinition,
    status: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "toolCallId": tool_call_id,
        "toolName": tool.name,
        "skillId": tool.skill_id,
    }
    if status is not None:
        payload["status"] = status
    if error is not None:
        payload["error"] = error
    return {
        "id": f"event_{agent_run_id}_{sequence}",
        "agentRunId": agent_run_id,
        "sequence": sequence,
        "kind": kind,
        "payload": payload,
    }
