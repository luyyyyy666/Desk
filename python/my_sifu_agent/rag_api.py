from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from my_sifu_agent.rag import (
    EmbeddingJob,
    EmbeddingJobSource,
    EmbeddingProviderConfig,
    EmbeddingSourceType,
)


@dataclass
class Phase4RagApi:
    provider_config: EmbeddingProviderConfig
    _embedding_jobs: dict[str, EmbeddingJob] = field(default_factory=dict)

    @classmethod
    def default_for_new_api(
        cls,
        *,
        base_url: str | None,
        model: str | None,
        api_key_env_var: str | None,
    ) -> Phase4RagApi:
        return cls(
            provider_config=EmbeddingProviderConfig(
                provider_id="new_api",
                base_url=base_url,
                model=model,
                api_key_env_var=api_key_env_var,
            )
        )

    def get_embedding_provider_status(self) -> dict[str, Any]:
        return {"provider": self.provider_config.public_status()}

    def create_embedding_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.provider_config.model is None:
            raise ValueError("embedding model is not configured")
        job = EmbeddingJob.queued(
            id=_required(payload, "id"),
            provider_id=self.provider_config.provider_id,
            embedding_model=self.provider_config.model,
            sources=[
                _embedding_job_source_from_json(item)
                for item in payload.get("sources", [])
            ],
            created_at=_parse_datetime(_required(payload, "createdAt")),
        )
        self._embedding_jobs[job.id] = job
        return {"job": _embedding_job_to_json(job)}

    def get_embedding_job(self, job_id: str) -> dict[str, Any]:
        try:
            job = self._embedding_jobs[job_id]
        except KeyError as exc:
            raise KeyError(f"unknown embedding job: {job_id}") from exc
        return {"job": _embedding_job_to_json(job)}

    def plan_embedding_search(self, payload: dict[str, Any]) -> dict[str, Any]:
        rerank = bool(payload.get("rerank", True))
        pipeline = ["structured_filter", "embedding_query", "vector_search"]
        if rerank:
            pipeline.append("rerank")
        return {
            "plan": {
                "query": _required(payload, "query"),
                "filters": dict(payload.get("filters", {})),
                "limit": int(payload.get("limit", 10)),
                "rerank": rerank,
                "pipeline": pipeline,
                "executesVectorSearch": False,
            }
        }


def _required(payload: dict[str, Any], key: str) -> Any:
    try:
        return payload[key]
    except KeyError as exc:
        raise ValueError(f"missing required field: {key}") from exc


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _embedding_job_source_from_json(payload: dict[str, Any]) -> EmbeddingJobSource:
    return EmbeddingJobSource(
        source_type=EmbeddingSourceType(_required(payload, "sourceType")),
        source_id=_required(payload, "sourceId"),
        content_hash=_required(payload, "contentHash"),
        text=_required(payload, "text"),
        metadata=dict(payload.get("metadata", {})),
    )


def _embedding_job_to_json(job: EmbeddingJob) -> dict[str, Any]:
    return {
        "id": job.id,
        "providerId": job.provider_id,
        "embeddingModel": job.embedding_model,
        "status": job.status.value,
        "sources": [_embedding_job_source_to_json(source) for source in job.sources],
        "sourceTypes": [source_type.value for source_type in job.source_types],
        "totalTexts": job.total_texts,
        "embeddedTexts": job.embedded_texts,
        "skippedTexts": job.skipped_texts,
        "failedTexts": job.failed_texts,
        "failureSummary": job.failure_summary,
        "createdAt": job.created_at.isoformat(),
        "startedAt": job.started_at.isoformat() if job.started_at is not None else None,
        "completedAt": (
            job.completed_at.isoformat() if job.completed_at is not None else None
        ),
        "callsProvider": False,
    }


def _embedding_job_source_to_json(source: EmbeddingJobSource) -> dict[str, Any]:
    return {
        "sourceType": source.source_type.value,
        "sourceId": source.source_id,
        "contentHash": source.content_hash,
        "text": source.text,
        "metadata": source.metadata,
    }
