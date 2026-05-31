# Phase 4 RAG / Knowledge Retrieval Implementation Audit

Date: 2026-05-31

This audit maps the current Phase 4 implementation back to
`docs/architecture/2026-05-13-full-stack-agent-phases.md`.

Phase 4 now has executable Python contracts for ingestion, embedding gateway request handling,
embedding jobs, in-memory vector indexing, access-scoped embedding search, and generation retrieval
context handoff. It also has a PostgreSQL + pgvector schema and a Rust/sqlx persistence adapter for
vector upsert, filtered vector search, and retrieval result persistence.
The generation retrieval context handoff now emits a replayable AgentRun event when an AgentRun id
and event sequence are supplied.

## Current Commits

- `585ff8e` Add phase 4 rag contracts
- `7893518` Add phase 4 embedding gateway
- `38c5d82` Add phase 4 knowledge ingestion
- `c2160eb` Add phase 4 embedding search
- `1150183` Add phase 4 pgvector schema
- `d43a7a9` Expose phase 4 rag status in frontend
- `2600c7b` Document phase 4 implementation audit
- `1a8b0c9` Use pgvector postgres runtime
- `f0d0c85` Add phase 4 pgvector repository
- `cf2c56f` Add phase 4 generation retrieval context
- `e1c9741` Add phase 4 source access control
- `d7f87db` Add rag retrieval agent run events

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
| PostgreSQL + pgvector runtime storage/search | Implemented in Rust persistence | `PostgresLearningRepository.upsert_embedding_vector()` and `search_embedding_vectors()`; `postgres_persistence_contract.rs` |
| Retry transient provider failures with bounded attempts | Implemented | `OpenAICompatibleEmbeddingGateway.embed_texts()` tests cover 503 retry and bounded failure |
| Retrieval request/result contract | Implemented | `Phase4RagApi.embedding_search()`; OpenAPI `EmbeddingSearchResponse` and `RetrievalResult` |
| Retrieval result persistence | Implemented in Rust persistence | `PostgresLearningRepository.persist_retrieval_results()` and `retrieval_results_for_query()` |
| Generation phase can consume retrieval results without direct DB coupling | Implemented as backend contract | `Phase4RagApi.build_generation_retrieval_context()`; OpenAPI `/api/generation/retrieval-context`; `directDatabaseAccess: false` |
| Structured filters + vector similarity | Implemented in memory and pgvector adapter | `InMemoryEmbeddingIndex.search()` combines metadata filters and cosine similarity; `PostgresLearningRepository.search_embedding_vectors()` applies subject, knowledge layer, and access scope filters |
| Source access control | Implemented as explicit search metadata | `AccessScope` enum; public knowledge ingestion writes `accessScope: public`; `Phase4RagApi.embedding_search()` defaults to public access; pgvector search supports `RagSearchFilters.access_scope` |
| Source ids and trust scores in results | Implemented | `RetrievalResult` contains `source_id`, `trust_score`, `final_score`, `trust_tier` |
| AgentRun event integration | Implemented | `Phase4RagApi.build_generation_retrieval_context()` returns `retrieval_context_ready` when called with `agentRunId` and `sequence`; Rust `AgentRunEventKind::RetrievalContextReady` maps to DB value `retrieval_context_ready` |
| Frontend status surface | Implemented as static PC UI | Knowledge window shows Phase 4 RAG pipeline, backend key ownership, ingest/job/search status |

## Not Complete Yet

| Requirement | Current state | Needed next |
| --- | --- | --- |
| Real textbook chapter parser | Plain text only | Add parser only after supported source formats are specified |
| Real `/rag/rerank` service | Not implemented | Add deterministic or model-backed reranker contract after ranking policy is specified |

## Verification

Run after current Phase 4 changes:

```text
uv run pytest
uv run ruff check .
cargo fmt --all --check
cargo test -p persistence --test postgres_persistence_contract
cargo clippy -p persistence --all-targets -- -D warnings
cd frontend; npm run test
cd frontend; npm run lint
cd frontend; npm run build
just docker-config
git diff --check
```

Latest observed results:

- Python tests: `74 passed`
- Python lint: passed
- Rust format: passed
- Rust domain model contract: `6 passed`
- Rust persistence contracts: `2 passed` and `5 passed`
- Rust clippy: passed
- Frontend tests: `13 passed`
- Frontend lint: passed
- Frontend build: passed
- Docker compose config: passed; PostgreSQL image resolves to `pgvector/pgvector:pg17`
- `git diff --check`: passed

## Boundary Checks

- No frontend provider calls were introduced.
- No raw provider API key is returned in public provider status.
- Phase 3 `/api/memory/hybrid-retrieval/plan` remains plan-only with `executesRetrieval: false`.
- Public knowledge curated content remains empty; Phase 4 only adds ingestion/index/search paths.
- Personal knowledge node/edge embeddings are still not required.
- Default embedding search is access-scoped to public knowledge unless a backend caller explicitly supplies another `accessScope`.
