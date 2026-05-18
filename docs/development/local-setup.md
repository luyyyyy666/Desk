# Local Development Setup

Date: 2026-05-14

## Phase 0 Scope

Phase 0 establishes the repository and engineering foundation. It does not implement Agent
business logic yet.

Current layout:

```text
frontend/              # existing Next.js 15 static Learning OS prototype
apps/api/              # existing Rust API/BFF reference skeleton
crates/agent-core/     # existing Rust runtime foundation contracts
crates/domain/         # existing Rust domain reference types
crates/tool-runtime/   # existing Rust tool registry boundary
crates/persistence/    # existing Rust database/event-store reference
python/ai_services/    # Python LLM/RAG/evaluation workspace
tests/                 # root repository structure checks
```

The existing frontend remains in `frontend/` for now to avoid destabilizing the current PC web
prototype. A later migration to `apps/web/` should be treated as a separate phase because it changes
paths, scripts, and deployment assumptions.

## Language Direction

The current committed backend foundation is Rust-based because Phase 1, Phase 1.5, and Phase 2 were
started that way. The forward implementation direction is now Python + TypeScript first:

```text
TypeScript / Next.js   # PC web UI and generated API client types
Python / FastAPI       # primary BFF, Agent runtime, Memory, RAG, tools, guardrails, evaluation
PostgreSQL             # durable relational and AgentRun event state
New API                # local OpenAI-compatible model gateway behind the backend
Rust                   # keep existing code as reference; add new Rust only when performance,
                       # native sandboxing, packaging, or concurrency pressure justifies it
```

Do not delete the existing Rust code only because the preferred language changed. Future work should
add Python parity behind the same OpenAPI contracts, then decide whether a Rust crate remains useful
as a compatibility shim, reference test target, or optional optimized service.

## Environment

Copy `.env.example` when a local `.env` is needed. Machine-local caches and developer homes should
stay under `E:\DevData` when tools allow it.

Important defaults:

```text
PLAYWRIGHT_BROWSERS_PATH=E:\DevData\ms-playwright
UV_CACHE_DIR=E:\DevData\uv\cache
CARGO_HOME=E:\DevData\cargo
```

## Commands

Run all Phase 0 checks:

```powershell
just check
```

Run Rust checks only:

```powershell
just rust-check
```

Run Python checks only:

```powershell
just python-check
```

Run frontend checks only:

```powershell
just frontend-check
```

Start the current Rust API reference skeleton:

```powershell
just dev-api
```

The Phase 1 OpenAPI contract is stored at:

```text
contracts/openapi/learning-os.yaml
```

The API currently returns fixture-backed Learning OS data. Useful endpoints:

```text
GET  /health
GET  /api/model-gateway/status
GET  /api/tasks/current
POST /api/generation-jobs
GET  /api/generation-jobs/job_fixture_linear_function_001
GET  /api/generation-jobs/job_fixture_linear_function_001/events
GET  /api/questions/qs_fixture_linear_function_001
GET  /api/mistakes
GET  /api/knowledge/search?query=一次函数
GET  /api/reports/current
```

## New API Model Gateway

The backend is prepared to use New API as an OpenAI-compatible model gateway.

Recommended request path:

```text
Next.js UI
  -> Python FastAPI BFF / Agent Runtime
    -> New API gateway
      -> upstream model providers
```

The frontend should not call New API directly. The backend owns model selection, key handling,
audit, rate limits, AgentRun state, and future tool permissions. The current Rust model gateway is a
working reference; the forward path is a Python model gateway module with the same public contract.

Local environment variables:

```text
MY_SIFU_LLM_GATEWAY_PROVIDER=new-api
MY_SIFU_LLM_GATEWAY_BASE_URL=http://127.0.0.1:3000
MY_SIFU_LLM_GATEWAY_API_KEY=
MY_SIFU_DEFAULT_MODEL=gpt-4o-mini
```

Current implementation status:

```text
crates/model-gateway/      # New API/OpenAI-compatible request shape and public config status
GET /api/model-gateway/status
```

This phase does not send real LLM requests yet. It only establishes the adapter boundary and
non-sensitive status endpoint.

## In-Memory Persistence

Phase 2a currently adds Rust domain models and an in-memory repository boundary. The Python-first
follow-up should add equivalent Pydantic models and repository protocols before moving new Agent
features forward.

Current behavior:

```text
Rust API route
  -> LearningRepository trait
    -> InMemoryLearningRepository::with_fixture_data()
```

This keeps the Phase 1 API contract stable while preparing the codebase for PostgreSQL in Phase 2b.
No database is required for Phase 2a checks.

Forward Python parity target:

```text
Python FastAPI route
  -> LearningRepository protocol
    -> InMemoryLearningRepository.with_fixture_data()
```

## PostgreSQL Persistence

Phase 2b currently adds PostgreSQL migrations and a `PostgresLearningRepository` for durable
AgentRun event storage. The Python-first follow-up should reuse the same database shape where it is
still appropriate, while implementing the main runtime repository in Python.

Migration file:

```text
crates/persistence/migrations/0001_phase2_core.sql
```

Current PostgreSQL-backed scope:

```text
DatabaseConfig
PostgresLearningRepository::connect()
PostgresLearningRepository::run_migrations()
AgentRun create/read/status update
AgentRunEvent append/replay
```

The default `just check` compiles the PostgreSQL repository and validates the migration contract. It
does not require a running database. To run the real database integration path, set
`MY_SIFU_DATABASE_URL` and run:

```powershell
just postgres-check
```

Example:

```powershell
$env:MY_SIFU_DATABASE_URL='postgres://my_sifu:my_sifu@127.0.0.1:5432/my_sifu'
just postgres-check
```

## Docker Runtime

Phase 2.5 adds a local Docker Compose runtime for development dependencies.

Services:

```text
postgres    # Phase 2b database checks and future durable runtime data
new-api     # local model gateway service
redis       # future queue/cache/rate-limit dependency
minio       # future uploads, exports, and artifacts
```

Files:

```text
docker-compose.yml
.env.docker.example
docker/README.md
```

Commands:

```powershell
just docker-config
just docker-up
just docker-down
just docker-logs
just docker-ps
just docker-clean
just postgres-check-docker
just new-api-status
```

Phase 2.5 should keep the Python API, current Rust reference API, Next.js frontend, and Python
workspaces running on the host. It only containerizes local dependencies first.

`just docker-clean` is destructive because it removes local named Docker volumes. Use it only when
local dependency data can be discarded.

Start the Next.js desktop prototype:

```powershell
just dev-web
```

## Phase 0 Exit Criteria Mapping

- Rust reference workspace exists at the repository root.
- Python workspace exists at the repository root and is the forward implementation target.
- `frontend/` keeps its existing Next.js scripts.
- Root `justfile` provides one-command checks.
- `.env.example` documents local service and cache conventions.
- This document records the local development commands.
