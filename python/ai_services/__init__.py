"""Python AI service workspace for future LLM, RAG, and evaluation code."""

__all__ = ["phase0_status"]


def phase0_status() -> dict[str, str]:
    return {
        "service": "ai-services",
        "status": "not_started_yet",
        "phase": "phase0-foundation",
    }
