from my_sifu_agent.state import (
    AgentRunStateStore,
    StateTransitionKind,
)


def test_state_store_builds_snapshot_from_append_only_transitions() -> None:
    store = AgentRunStateStore()

    store.append_transition(
        agent_run_id="run_state_001",
        kind=StateTransitionKind.PHASE_CHANGED,
        payload={"phase": "planning"},
    )
    store.append_transition(
        agent_run_id="run_state_001",
        kind=StateTransitionKind.PLAN_STEP_ACTIVATED,
        payload={"planStepId": "step_01_search_knowledge"},
    )
    store.append_transition(
        agent_run_id="run_state_001",
        kind=StateTransitionKind.TOOL_CALL_RECORDED,
        payload={"toolCallId": "tool_call_run_state_001_001", "status": "succeeded"},
    )
    store.append_transition(
        agent_run_id="run_state_001",
        kind=StateTransitionKind.ARTIFACT_RECORDED,
        payload={"artifactId": "question_set_state_001", "artifactType": "question_set"},
    )
    store.append_transition(
        agent_run_id="run_state_001",
        kind=StateTransitionKind.USER_CONFIRMATION_RECORDED,
        payload={"confirmationId": "confirm_state_001", "status": "approved"},
    )
    store.append_transition(
        agent_run_id="run_state_001",
        kind=StateTransitionKind.RETRY_COUNT_CHANGED,
        payload={"retryCount": 1},
    )
    store.append_transition(
        agent_run_id="run_state_001",
        kind=StateTransitionKind.FINAL_RESPONSE_STATUS_CHANGED,
        payload={"finalResponseStatus": "waiting_for_user"},
    )

    snapshot = store.snapshot("run_state_001")

    assert snapshot == {
        "agentRunId": "run_state_001",
        "currentPhase": "planning",
        "activePlanStepId": "step_01_search_knowledge",
        "generatedArtifacts": [
            {"artifactId": "question_set_state_001", "artifactType": "question_set"}
        ],
        "toolCalls": [
            {"toolCallId": "tool_call_run_state_001_001", "status": "succeeded"}
        ],
        "userConfirmations": [
            {"confirmationId": "confirm_state_001", "status": "approved"}
        ],
        "retryCount": 1,
        "finalResponseStatus": "waiting_for_user",
        "transitionCount": 7,
        "updatedAt": "2026-05-31T00:00:00Z",
    }

    transitions = store.transitions_for("run_state_001")
    assert [transition["sequence"] for transition in transitions] == list(range(1, 8))
    assert transitions[0]["kind"] == "phase_changed"


def test_idempotent_request_replays_first_response_without_duplicate_transitions() -> None:
    store = AgentRunStateStore()

    first = store.record_idempotent_request(
        agent_run_id="run_state_002",
        idempotency_key="client_request_001",
        operation="activate_plan_step",
        response={"accepted": True, "planStepId": "step_01_search_knowledge"},
        transitions=(
            (
                StateTransitionKind.PLAN_STEP_ACTIVATED,
                {"planStepId": "step_01_search_knowledge"},
            ),
        ),
    )
    duplicate = store.record_idempotent_request(
        agent_run_id="run_state_002",
        idempotency_key="client_request_001",
        operation="activate_plan_step",
        response={"accepted": True, "planStepId": "step_02_generate_question_set"},
        transitions=(
            (
                StateTransitionKind.PLAN_STEP_ACTIVATED,
                {"planStepId": "step_02_generate_question_set"},
            ),
        ),
    )

    assert first["status"] == "created"
    assert duplicate["status"] == "replayed"
    assert duplicate["response"] == first["response"]
    assert duplicate["response"]["planStepId"] == "step_01_search_knowledge"
    assert store.snapshot("run_state_002")["activePlanStepId"] == (
        "step_01_search_knowledge"
    )
    assert store.snapshot("run_state_002")["transitionCount"] == 1


def test_idempotent_key_cannot_be_reused_for_different_operation() -> None:
    store = AgentRunStateStore()
    store.record_idempotent_request(
        agent_run_id="run_state_003",
        idempotency_key="client_request_001",
        operation="activate_plan_step",
        response={"accepted": True},
        transitions=(),
    )

    try:
        store.record_idempotent_request(
            agent_run_id="run_state_003",
            idempotency_key="client_request_001",
            operation="record_tool_call",
            response={"accepted": True},
            transitions=(),
        )
    except ValueError as exc:
        assert str(exc) == (
            "idempotency key client_request_001 was already used for "
            "activate_plan_step"
        )
    else:
        raise AssertionError("expected idempotency key reuse to fail")
