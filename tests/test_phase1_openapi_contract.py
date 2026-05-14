from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_learning_os_openapi_contract_declares_phase1_paths() -> None:
    contract = ROOT / "contracts" / "openapi" / "learning-os.yaml"

    assert contract.exists()
    content = contract.read_text(encoding="utf-8")

    for path in [
        "/health:",
        "/api/tasks/current:",
        "/api/generation-jobs:",
        "/api/generation-jobs/{job_id}:",
        "/api/generation-jobs/{job_id}/events:",
        "/api/questions/{question_set_id}:",
        "/api/mistakes:",
        "/api/knowledge/search:",
        "/api/model-gateway/status:",
        "/api/reports/current:",
    ]:
        assert path in content

    assert "ApiError" in content
    assert "ModelGatewayStatus" in content
    assert "text/event-stream" in content
