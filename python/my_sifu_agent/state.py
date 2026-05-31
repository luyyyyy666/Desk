from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class StateTransitionKind(StrEnum):
    PHASE_CHANGED = "phase_changed"
    PLAN_STEP_ACTIVATED = "plan_step_activated"
    TOOL_CALL_RECORDED = "tool_call_recorded"
    ARTIFACT_RECORDED = "artifact_recorded"
    USER_CONFIRMATION_RECORDED = "user_confirmation_recorded"
    RETRY_COUNT_CHANGED = "retry_count_changed"
    FINAL_RESPONSE_STATUS_CHANGED = "final_response_status_changed"


@dataclass(frozen=True)
class StateTransition:
    id: str
    agent_run_id: str
    sequence: int
    kind: StateTransitionKind
    payload: dict[str, Any]
    created_at: str


@dataclass
class AgentRunStateStore:
    _transitions: dict[str, list[StateTransition]] = field(default_factory=dict)

    def append_transition(
        self,
        *,
        agent_run_id: str,
        kind: StateTransitionKind,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        transitions = self._transitions.setdefault(agent_run_id, [])
        sequence = len(transitions) + 1
        transition = StateTransition(
            id=f"state_transition_{agent_run_id}_{sequence:03}",
            agent_run_id=agent_run_id,
            sequence=sequence,
            kind=kind,
            payload=payload,
            created_at=_STATE_TIMESTAMP,
        )
        transitions.append(transition)
        return _transition_to_json(transition)

    def transitions_for(self, agent_run_id: str) -> list[dict[str, Any]]:
        return [
            _transition_to_json(transition)
            for transition in self._transitions.get(agent_run_id, [])
        ]

    def snapshot(self, agent_run_id: str) -> dict[str, Any]:
        snapshot: dict[str, Any] = {
            "agentRunId": agent_run_id,
            "currentPhase": "created",
            "activePlanStepId": None,
            "generatedArtifacts": [],
            "toolCalls": [],
            "userConfirmations": [],
            "retryCount": 0,
            "finalResponseStatus": "pending",
            "transitionCount": 0,
            "updatedAt": None,
        }
        for transition in self._transitions.get(agent_run_id, []):
            _apply_transition(snapshot, transition)
            snapshot["transitionCount"] = transition.sequence
            snapshot["updatedAt"] = transition.created_at
        return snapshot


_STATE_TIMESTAMP = "2026-05-31T00:00:00Z"


def _apply_transition(snapshot: dict[str, Any], transition: StateTransition) -> None:
    payload = transition.payload
    match transition.kind:
        case StateTransitionKind.PHASE_CHANGED:
            snapshot["currentPhase"] = payload["phase"]
        case StateTransitionKind.PLAN_STEP_ACTIVATED:
            snapshot["activePlanStepId"] = payload["planStepId"]
        case StateTransitionKind.TOOL_CALL_RECORDED:
            snapshot["toolCalls"].append(
                {
                    "toolCallId": payload["toolCallId"],
                    "status": payload["status"],
                }
            )
        case StateTransitionKind.ARTIFACT_RECORDED:
            snapshot["generatedArtifacts"].append(
                {
                    "artifactId": payload["artifactId"],
                    "artifactType": payload["artifactType"],
                }
            )
        case StateTransitionKind.USER_CONFIRMATION_RECORDED:
            snapshot["userConfirmations"].append(
                {
                    "confirmationId": payload["confirmationId"],
                    "status": payload["status"],
                }
            )
        case StateTransitionKind.RETRY_COUNT_CHANGED:
            snapshot["retryCount"] = payload["retryCount"]
        case StateTransitionKind.FINAL_RESPONSE_STATUS_CHANGED:
            snapshot["finalResponseStatus"] = payload["finalResponseStatus"]


def _transition_to_json(transition: StateTransition) -> dict[str, Any]:
    return {
        "id": transition.id,
        "agentRunId": transition.agent_run_id,
        "sequence": transition.sequence,
        "kind": transition.kind.value,
        "payload": transition.payload,
        "createdAt": transition.created_at,
    }
