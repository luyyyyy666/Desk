from ai_services import phase0_status


def test_phase0_status_declares_python_workspace_boundary() -> None:
    assert phase0_status() == {
        "service": "ai-services",
        "status": "not_started_yet",
        "phase": "phase0-foundation",
    }
