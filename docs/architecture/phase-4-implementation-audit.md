# Phase 4 RAG / Knowledge Retrieval Implementation Audit

Date: 2026-05-30

This audit maps the current Phase 4 implementation back to
`docs/architecture/2026-05-13-full-stack-agent-phases.md`.

Phase 4 now has executable Python contracts for ingestion, embedding gateway request handling,
embedding jobs, in-memory vector indexing, and embedding search. It also has a PostgreSQL +
pgvector schema contract. Runtime PostgreSQL write/read adapters are not implemented yet, so the
database-backed exit criteria are not complete.

## Current Commits

- `585ff8e` Add phase 4 rag contracts
- `7893518` Add phase 4 embedding gateway
- `38c5d82` Add phase 4 knowledge ingestion
- `c2160eb` Add phase 4 embedding search
- `1150183` Add phase 4 pgvector schema
- `d43a7a9` Expose phase 4 rag status in frontend

## Implemented

| Requirement | Status | Evidence |
| --- | --- | --- |
| Knowledge layers for curriculum, textbook, question, pedagogy, rubric, and institution | Implemented in contract | `KnowledgeLayer` enum in `python/my_sifu_agent/rag.py`; OpenAPI enum in `KnowledgeSourceIngestRequest` |
| Plain text ingestion and chunking | Implemented | `InMemoryKnowledgeSourceRepository.ingest_plain_text()`; `/rag/ingest` OpenAPI contract; tests in `test_phase4_ingestion.py` |
| Embedding Gateway supports New API / OpenAI-compatible `/v1/embeddings` | Implemented behind injected transport | `OpenAICompatibleEmbeddingGateway.build_http_request()` and `embed_texts()`; tests verify URL, body, auth header, response parsing, retries |
| Provider keys stay out of frontend | Implemented in contract/UI boundary | `EmbeddingProviderConfig.public_status()` exposes status/env var only; frontend only shows static backend-owned status; tests assert no raw key field/value |
| Embedding job contract | Implemented | `EmbeddingJob`, `EmbeddingJobSource`, `Phase4RagApi.create_embedding_job()` |
| Batch texts for embedding | Implemented in gateway/job path | `embed_texts()` accepts multiple texts; `run_embedding_job()` passes all job source texts |
| Store `embedding_model`, `content_hash`, and source metadata with every vector | Implemented in in-memory index and pgvector schema | `EmbeddingVectorRecord`; `rag_embedding_vectors` table |
| Skip duplicate embedding work by source/model/hash | Implemented in in-memory index and pgvector schema | `InMemoryEmbeddingIndex.upsert()`; unique constraint on `(source_type, source_id, chunk_id, embedding_model, content_hash)` |
| Retry transient provider failures with bounded attempts | Implemented | `OpenAICompatibleEmbeddingGateway.embed_texts()` tests cover 503 retry and bounded failure |
| Retrieval request/result contract | Implemented | `Phase4RagApi.embedding_search()`; OpenAPI `EmbeddingSearchResponse` and `RetrievalResult` |
| Structured filters + vector similarity | Implemented in memory | `InMemoryEmbeddingIndex.search()` combines metadata filters and cosine similarity |
| Source ids and trust scores in results | Implemented | `RetrievalResult` contains `source_id`, `trust_score`, `final_score`, `trust_tier` |
| Frontend status surface | Implemented as static PC UI | Knowledge window shows Phase 4 RAG pipeline, backend key ownership, ingest/job/search status |

## Not Complete Yet

| Requirement | Current state | Needed next |
| --- | --- | --- |
| Embedding job stores vectors in PostgreSQL + pgvector | Schema exists, runtime adapter does not | Add Python or Rust repository that writes `rag_embedding_vectors` and reads search candidates from Postgres |
| Retrieval result persistence | Schema exists, runtime write path does not | Persist `Phase4RagApi.embedding_search()` results into `rag_retrieval_results` |
| Source access control | Not implemented | Add user/system access scope fields and enforce them in search filters |
| Integration with AgentRun | Not implemented | Connect retrieval results to generation/AgentRun context without frontend direct DB access |
| Real textbook chapter parser | Plain text only | Add parser only after supported source formats are specified |
| Real `/rag/rerank` service | Not implemented | Add deterministic or model-backed reranker contract after ranking policy is specified |

## Verification

Run after current Phase 4 changes:

```text
uv run pytest
uv run ruff check .
cargo test -p persistence --test postgres_persistence_contract
cd frontend; npm run test
cd frontend; npm run lint
cd frontend; npm run build
git diff --check
```

Latest observed results:

- Python tests: `64 passed`
- Python lint: passed
- Rust persistence contract: `3 passed`
- Frontend tests: `11 passed`
- Frontend lint: passed
- Frontend build: passed
- `git diff --check`: passed

## Boundary Checks

- No frontend provider calls were introduced.
- No raw provider API key is returned in public provider status.
- Phase 3 `/api/memory/hybrid-retrieval/plan` remains plan-only with `executesRetrieval: false`.
- Public knowledge curated content remains empty; Phase 4 only adds ingestion/index/search paths.
- Personal knowledge node/edge embeddings are still not required.
