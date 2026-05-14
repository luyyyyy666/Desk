# Local Development Setup

Date: 2026-05-14

## Phase 0 Scope

Phase 0 establishes the repository and engineering foundation. It does not implement Agent
business logic yet.

Current layout:

```text
frontend/              # existing Next.js 15 static Learning OS prototype
apps/api/              # Rust API/BFF skeleton
crates/agent-core/     # Rust runtime foundation contracts
crates/domain/         # shared Rust domain types
crates/tool-runtime/   # future tool registry boundary
crates/persistence/    # future database/event-store boundary
python/ai_services/    # future Python LLM/RAG/evaluation workspace
tests/                 # root repository structure checks
```

The existing frontend remains in `frontend/` for now to avoid destabilizing the current PC web
prototype. A later migration to `apps/web/` should be treated as a separate phase because it changes
paths, scripts, and deployment assumptions.

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

Start the Rust API skeleton:

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
GET  /api/tasks/current
POST /api/generation-jobs
GET  /api/generation-jobs/job_fixture_linear_function_001
GET  /api/generation-jobs/job_fixture_linear_function_001/events
GET  /api/questions/qs_fixture_linear_function_001
GET  /api/mistakes
GET  /api/knowledge/search?query=一次函数
GET  /api/reports/current
```

Start the Next.js desktop prototype:

```powershell
just dev-web
```

## Phase 0 Exit Criteria Mapping

- Rust workspace exists at the repository root.
- Python workspace exists at the repository root.
- `frontend/` keeps its existing Next.js scripts.
- Root `justfile` provides one-command checks.
- `.env.example` documents local service and cache conventions.
- This document records the local development commands.
