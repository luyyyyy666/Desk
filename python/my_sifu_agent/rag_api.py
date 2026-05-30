from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from my_sifu_agent.rag import (
    EmbeddingJob,
    EmbeddingJobSource,
    EmbeddingProviderConfig,
    EmbeddingSourceType,
    EmbeddingVectorRecord,
    InMemoryEmbeddingIndex,
    InMemoryKnowledgeSourceRepository,
    KnowledgeChunk,
    KnowledgeLayer,
    KnowledgeSource,
    VectorUpsertStatus,
)


@dataclass
class Phase4RagApi:
    provider_config: EmbeddingProviderConfig
    embedding_gateway: Any | None = None
    embedding_index: InMemoryEmbeddingIndex = field(default_factory=InMemoryEmbeddingIndex)
    knowledge_source_repository: InMemoryKnowledgeSourceRepository = field(
        default_factory=InMemoryKnowledgeSourceRepository
    )
    _embedding_jobs: dict[str, EmbeddingJob] = field(default_factory=dict)

    @classmethod
    def default_for_new_api(
        cls,
        *,
        base_url: str | None,
        model: str | None,
        api_key_env_var: str | None,
        embedding_gateway: Any | None = None,
        embedding_index: InMemoryEmbeddingIndex | None = None,
        knowledge_source_repository: InMemoryKnowledgeSourceRepository | None = None,
    ) -> Phase4RagApi:
        return cls(
            provider_config=EmbeddingProviderConfig(
                provider_id="new_api",
                base_url=base_url,
                model=model,
                api_key_env_var=api_key_env_var,
            ),
            embedding_gateway=embedding_gateway,
            embedding_index=embedding_index or InMemoryEmbeddingIndex(),
            knowledge_source_repository=(
                knowledge_source_repository or InMemoryKnowledgeSourceRepository()
            ),
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

    def run_embedding_job(self, job_id: str, *, now: datetime) -> dict[str, Any]:
        if self.embedding_gateway is None:
            raise ValueError("embedding gateway is not configured")
        job = self._get_embedding_job(job_id).running(started_at=now)
        self._embedding_jobs[job.id] = job

        gateway_result = self.embedding_gateway.embed_texts(
            [source.text for source in job.sources]
        )
        embedded_texts = 0
        skipped_texts = 0
        upserts: list[dict[str, Any]] = []
        for embedding in gateway_result.embeddings:
            source = job.sources[embedding.index]
            status = self.embedding_index.upsert(
                EmbeddingVectorRecord(
                    id=f"{job.id}_{source.source_type.value}_{source.source_id}_{embedding.index}",
                    source_type=source.source_type,
                    source_id=source.source_id,
                    chunk_id=f"{source.source_id}:{embedding.index}",
                    embedding_model=gateway_result.model,
                    content_hash=source.content_hash,
                    vector=embedding.vector,
                    metadata=source.metadata,
                )
            )
            if status == VectorUpsertStatus.UPSERTED:
                embedded_texts += 1
            else:
                skipped_texts += 1
            upserts.append({"sourceId": source.source_id, "status": status})

        completed = job.completed(
            completed_at=now,
            embedded_texts=embedded_texts,
            skipped_texts=skipped_texts,
        )
        self._embedding_jobs[completed.id] = completed
        return {
            "job": _embedding_job_to_json(completed),
            "upserts": upserts,
            "usage": gateway_result.usage,
        }

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

    def ingest_plain_text(self, payload: dict[str, Any]) -> dict[str, Any]:
        source_format = _required(payload, "sourceFormat")
        if source_format != "plain_text":
            raise ValueError("phase 4 ingestion currently supports plain_text only")
        source = self.knowledge_source_repository.ingest_plain_text(
            source_id=_required(payload, "sourceId"),
            title=_required(payload, "title"),
            knowledge_layer=KnowledgeLayer(_required(payload, "knowledgeLayer")),
            text=_required(payload, "text"),
            metadata=dict(payload.get("metadata", {})),
            created_at=_parse_datetime(_required(payload, "createdAt")),
        )
        chunks = self.knowledge_source_repository.list_chunks(source.id)
        embedding_sources = [
            EmbeddingJobSource(
                source_type=EmbeddingSourceType.PUBLIC_KNOWLEDGE_CHUNK,
                source_id=chunk.id,
                content_hash=chunk.content_hash,
                text=chunk.text,
                metadata={
                    **chunk.metadata,
                    "knowledgeLayer": source.knowledge_layer.value,
                    "sourceTitle": source.title,
                },
            )
            for chunk in chunks
        ]
        return {
            "source": _knowledge_source_to_json(source),
            "chunks": [_knowledge_chunk_to_json(chunk) for chunk in chunks],
            "embeddingSources": [
                _embedding_job_source_to_json(embedding_source)
                for embedding_source in embedding_sources
            ],
        }

    def _get_embedding_job(self, job_id: str) -> EmbeddingJob:
        try:
            return self._embedding_jobs[job_id]
        except KeyError as exc:
            raise KeyError(f"unknown embedding job: {job_id}") from exc


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
        "providerCallsOwnedByBackend": True,
    }


def _embedding_job_source_to_json(source: EmbeddingJobSource) -> dict[str, Any]:
    return {
        "sourceType": source.source_type.value,
        "sourceId": source.source_id,
        "contentHash": source.content_hash,
        "text": source.text,
        "metadata": source.metadata,
    }


def _knowledge_source_to_json(source: KnowledgeSource) -> dict[str, Any]:
    return {
        "id": source.id,
        "title": source.title,
        "knowledgeLayer": source.knowledge_layer.value,
        "contentHash": source.content_hash,
        "metadata": source.metadata,
        "chunkCount": source.chunk_count,
        "createdAt": source.created_at.isoformat(),
    }


def _knowledge_chunk_to_json(chunk: KnowledgeChunk) -> dict[str, Any]:
    return {
        "id": chunk.id,
        "sourceId": chunk.source_id,
        "ordinal": chunk.ordinal,
        "text": chunk.text,
        "contentHash": chunk.content_hash,
        "metadata": chunk.metadata,
        "createdAt": chunk.created_at.isoformat(),
    }
