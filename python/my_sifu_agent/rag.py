from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
from math import sqrt
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
class KnowledgeSource:
    id: str
    title: str
    knowledge_layer: KnowledgeLayer
    content_hash: str
    metadata: dict[str, Any]
    chunk_count: int
    created_at: datetime


@dataclass(frozen=True)
class KnowledgeChunk:
    id: str
    source_id: str
    ordinal: int
    text: str
    content_hash: str
    metadata: dict[str, Any]
    created_at: datetime


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

    def search(
        self,
        *,
        query_vector: tuple[float, ...],
        filters: dict[str, Any],
        limit: int,
    ) -> list[RetrievalResult]:
        results = []
        for record in self._records.values():
            if not _metadata_matches(record.metadata, filters):
                continue
            similarity_score = _cosine_similarity(query_vector, record.vector)
            trust_score = _trust_score_for(record)
            final_score = round((similarity_score + trust_score) / 2, 4)
            knowledge_layer = KnowledgeLayer(
                record.metadata.get("knowledgeLayer", KnowledgeLayer.QUESTION.value)
            )
            results.append(
                RetrievalResult(
                    source_type=record.source_type,
                    source_id=record.source_id,
                    chunk_id=record.chunk_id,
                    knowledge_layer=knowledge_layer,
                    text=str(record.metadata.get("text", "")),
                    similarity_score=similarity_score,
                    trust_score=trust_score,
                    final_score=final_score,
                    trust_tier=_trust_tier_for(record),
                    metadata=record.metadata,
                )
            )
        results.sort(key=lambda result: (-result.final_score, result.source_id))
        return results[:limit]

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


@dataclass
class InMemoryKnowledgeSourceRepository:
    _sources: dict[str, KnowledgeSource] = field(default_factory=dict)
    _chunks: dict[str, tuple[KnowledgeChunk, ...]] = field(default_factory=dict)

    def ingest_plain_text(
        self,
        *,
        source_id: str,
        title: str,
        knowledge_layer: KnowledgeLayer,
        text: str,
        metadata: dict[str, Any],
        created_at: datetime,
    ) -> KnowledgeSource:
        content_hash = _content_hash(text)
        existing = self._sources.get(source_id)
        if existing is not None and existing.content_hash == content_hash:
            return existing

        chunk_texts = _split_plain_text_chunks(text)
        chunks = tuple(
            KnowledgeChunk(
                id=f"{source_id}:chunk_{index}",
                source_id=source_id,
                ordinal=index,
                text=chunk_text,
                content_hash=_content_hash(chunk_text),
                metadata=dict(metadata),
                created_at=created_at,
            )
            for index, chunk_text in enumerate(chunk_texts)
        )
        source = KnowledgeSource(
            id=source_id,
            title=title,
            knowledge_layer=knowledge_layer,
            content_hash=content_hash,
            metadata=dict(metadata),
            chunk_count=len(chunks),
            created_at=created_at,
        )
        self._sources[source_id] = source
        self._chunks[source_id] = chunks
        return source

    def list_chunks(self, source_id: str) -> list[KnowledgeChunk]:
        return list(self._chunks.get(source_id, ()))


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


def _content_hash(text: str) -> str:
    return f"sha256:{sha256(text.encode('utf-8')).hexdigest()}"


def _split_plain_text_chunks(text: str) -> list[str]:
    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    if chunks:
        return chunks
    stripped = text.strip()
    return [stripped] if stripped else []


def _metadata_matches(metadata: dict[str, Any], filters: dict[str, Any]) -> bool:
    return all(metadata.get(key) == value for key, value in filters.items())


def _cosine_similarity(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if len(left) != len(right) or not left or not right:
        return 0.0
    dot_product = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return round(dot_product / (left_norm * right_norm), 4)


def _trust_tier_for(record: EmbeddingVectorRecord) -> RetrievalTrustTier:
    if record.source_type == EmbeddingSourceType.PUBLIC_KNOWLEDGE_CHUNK:
        return RetrievalTrustTier.CURATED
    if record.source_type in {
        EmbeddingSourceType.PUBLIC_QUESTION,
        EmbeddingSourceType.PUBLIC_QUESTION_TEMPLATE,
    }:
        return RetrievalTrustTier.VERIFIED
    return RetrievalTrustTier.USER_EVIDENCE


def _trust_score_for(record: EmbeddingVectorRecord) -> float:
    trust_tier = _trust_tier_for(record)
    if trust_tier == RetrievalTrustTier.CURATED:
        return 0.9
    if trust_tier == RetrievalTrustTier.VERIFIED:
        return 0.82
    return 0.72
