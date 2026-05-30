from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum
from typing import Any


class KnowledgeLayer(StrEnum):
    CURRICULUM = "curriculum"
    TEXTBOOK = "textbook"
    QUESTION = "question"
    PEDAGOGY = "pedagogy"
    RUBRIC = "rubric"
    INSTITUTION = "institution"


class EmbeddingSourceType(StrEnum):
    PUBLIC_KNOWLEDGE_CHUNK = "public_knowledge_chunk"
    PUBLIC_QUESTION_TEMPLATE = "public_question_template"
    PUBLIC_QUESTION = "public_question"
    WRONG_QUESTION_ANALYSIS = "wrong_question_analysis"


class EmbeddingJobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL_FAILED = "partial_failed"
    FAILED = "failed"


class VectorUpsertStatus(StrEnum):
    UPSERTED = "upserted"
    SKIPPED_DUPLICATE = "skipped_duplicate"


class RetrievalTrustTier(StrEnum):
    CURATED = "curated"
    VERIFIED = "verified"
    GENERATED = "generated"
    USER_EVIDENCE = "user_evidence"


@dataclass(frozen=True)
class EmbeddingProviderConfig:
    provider_id: str
    base_url: str | None
    model: str | None
    api_key_env_var: str | None

    def public_status(self) -> dict[str, Any]:
        return {
            "providerId": self.provider_id,
            "baseUrlConfigured": self.base_url is not None,
            "modelConfigured": self.model is not None,
            "apiKeyConfigured": self.api_key_env_var is not None,
            "apiKeyEnvVar": self.api_key_env_var,
        }


@dataclass(frozen=True)
class EmbeddingJobSource:
    source_type: EmbeddingSourceType
    source_id: str
    content_hash: str
    text: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class EmbeddingJob:
    id: str
    provider_id: str
    embedding_model: str
    status: EmbeddingJobStatus
    sources: tuple[EmbeddingJobSource, ...]
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    embedded_texts: int = 0
    skipped_texts: int = 0
    failed_texts: int = 0
    failure_summary: str | None = None

    @classmethod
    def queued(
        cls,
        *,
        id: str,
        provider_id: str,
        embedding_model: str,
        sources: list[EmbeddingJobSource] | tuple[EmbeddingJobSource, ...],
        created_at: datetime,
    ) -> EmbeddingJob:
        return cls(
            id=id,
            provider_id=provider_id,
            embedding_model=embedding_model,
            status=EmbeddingJobStatus.QUEUED,
            sources=tuple(sources),
            created_at=created_at,
        )

    @property
    def total_texts(self) -> int:
        return len(self.sources)

    @property
    def source_types(self) -> tuple[EmbeddingSourceType, ...]:
        return tuple(dict.fromkeys(source.source_type for source in self.sources))

    def running(self, *, started_at: datetime) -> EmbeddingJob:
        return replace(
            self,
            status=EmbeddingJobStatus.RUNNING,
            started_at=started_at,
        )

    def completed(
        self,
        *,
        completed_at: datetime,
        embedded_texts: int,
        skipped_texts: int,
        failed_texts: int = 0,
        failure_summary: str | None = None,
    ) -> EmbeddingJob:
        status = EmbeddingJobStatus.COMPLETED
        if failed_texts > 0 and embedded_texts + skipped_texts > 0:
            status = EmbeddingJobStatus.PARTIAL_FAILED
        elif failed_texts > 0:
            status = EmbeddingJobStatus.FAILED
        return replace(
            self,
            status=status,
            completed_at=completed_at,
            embedded_texts=embedded_texts,
            skipped_texts=skipped_texts,
            failed_texts=failed_texts,
            failure_summary=failure_summary,
        )


@dataclass(frozen=True)
class EmbeddingVectorRecord:
    id: str
    source_type: EmbeddingSourceType
    source_id: str
    chunk_id: str
    embedding_model: str
    content_hash: str
    vector: tuple[float, ...]
    metadata: dict[str, Any]


@dataclass
class InMemoryEmbeddingIndex:
    _records: dict[tuple[EmbeddingSourceType, str, str, str, str], EmbeddingVectorRecord] = field(
        default_factory=dict
    )

    def upsert(self, record: EmbeddingVectorRecord) -> VectorUpsertStatus:
        key = self._record_key(record)
        if key in self._records:
            return VectorUpsertStatus.SKIPPED_DUPLICATE
        self._records[key] = record
        return VectorUpsertStatus.UPSERTED

    def list_records(self) -> list[EmbeddingVectorRecord]:
        return list(self._records.values())

    def _record_key(
        self,
        record: EmbeddingVectorRecord,
    ) -> tuple[EmbeddingSourceType, str, str, str, str]:
        return (
            record.source_type,
            record.source_id,
            record.chunk_id,
            record.embedding_model,
            record.content_hash,
        )


@dataclass(frozen=True)
class RetrievalResult:
    source_type: EmbeddingSourceType
    source_id: str
    chunk_id: str
    knowledge_layer: KnowledgeLayer
    text: str
    similarity_score: float
    trust_score: float
    final_score: float
    trust_tier: RetrievalTrustTier
    metadata: dict[str, Any]
