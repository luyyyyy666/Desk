# 我的师傅 Full-Stack Agent Framework Phases

Date: 2026-05-13

## Purpose

This document breaks the future frontend and backend foundation into phased work. Each phase is intentionally narrow enough to become its own spec, implementation plan, and testable milestone.

The product direction is a unified learning and question-generation workspace. It should support:

- generating questions and papers
- editing generated questions
- practicing directly
- reviewing explanations
- collecting mistakes and weak points
- using memory and retrieval to improve the next generation round

The initial UI prototype is static. The phases below describe the path from static prototype to a real Agent system.

## Recommended Language Split

Use Python + TypeScript as the main implementation path first. Keep Rust as a later optional hardening or acceleration layer instead of the default language for new Agent features.

TypeScript should own product UI and frontend contracts:

- PC web Learning OS interface
- static and interactive windows
- user workflows
- generated API client types from OpenAPI
- frontend loading, empty, error, and success states
- Playwright coverage for the main UI loop

Python should own the primary backend and Agent implementation:

- FastAPI API / BFF edge for frontend-facing contracts
- Agent runtime orchestration
- state machine and workflow execution
- tool execution boundary
- typed domain models with Pydantic
- persistence adapters and migrations
- audit logs and AgentRun event records
- guardrail enforcement points
- model gateway adapters for New API and other OpenAI-compatible providers
- LLM provider adapters
- prompt and response parsing
- RAG ingestion and retrieval pipelines
- embeddings and reranking
- question quality evaluation
- offline evaluation datasets
- data cleaning and document processing
- experimentation notebooks or scripts

Rust should be deferred until there is concrete pressure that justifies it:

- high-concurrency streaming that Python cannot handle cleanly
- a sandboxed native tool executor
- performance-sensitive retrieval, parsing, or reranking components
- a packaged local runtime service where a small native binary is valuable
- strict event-replay or workflow execution needs that benefit from Rust types

Avoid putting Agent decision logic in the frontend. The frontend should never call New API or upstream model providers directly. Model keys, provider routing, memory writes, tool permissions, guardrails, and AgentRun state should stay behind the backend.

Existing Rust Phase 1, Phase 1.5, and Phase 2 code should be treated as a working foundation and reference implementation. Do not delete it only because the language direction changed. Future code should add Python parity behind the same OpenAPI contracts, then decide whether to keep the Rust pieces as compatibility shims, tests, or optional optimized services.

## Suggested Repository Shape

```text
apps/
  web/                         # Next.js 15 frontend
  api/                         # Python FastAPI API / BFF target
python/
  my_sifu_agent/               # Agent runtime, domain, persistence, memory, tools
  ai_services/                 # LLM, RAG, evaluation, and worker modules
  rag_pipeline/                # ingestion, chunking, embedding, indexing jobs
  evals/                       # datasets, rubrics, scoring scripts
contracts/
  openapi/                     # API schemas
  skills/                      # skill input/output schemas
  events/                      # event contracts
crates/                        # existing Rust foundation; optional/deferred
  model-gateway/               # current New API/OpenAI-compatible reference
  domain/                      # current Rust domain reference
  persistence/                 # current Rust persistence reference
docs/
  architecture/
  superpowers/
```

This structure can be simplified at the start, but the ownership boundaries should stay clear. The key rule is contract stability: frontend code should depend on OpenAPI and typed client code, not on whether the backend implementation is currently Python or Rust.

## Phase 0: Repo And Engineering Foundation

Goal: make the repo ready for multi-language development.

Scope:

- choose package layout
- keep the existing Rust workspace as a reference foundation
- add and prioritize the Python workspace
- move current Next prototype into `apps/web` or decide to keep `frontend/`
- add shared formatting, linting, testing commands
- define local environment conventions under `E:\DevData`
- add `.env.example`
- add CI-equivalent local scripts

Deliverables:

- `Cargo.toml` workspace for current Rust reference code
- Python project config, preferably `pyproject.toml`
- frontend package scripts
- root `justfile`, `makefile`, or task runner
- documented local dev commands

Recommended tools:

- Python: `uv`, `ruff`, `pytest`, `mypy` or `pyright`, `fastapi`, `pydantic`, `sqlalchemy` or `sqlmodel`, `alembic`
- Frontend: Next.js 15, TypeScript, Tailwind, Playwright
- Rust reference: `cargo`, `clippy`, `rustfmt`, `axum`, `tokio`, `serde`, `sqlx`

Exit criteria:

- one command runs backend checks
- one command runs Python checks
- one command runs frontend checks
- root docs explain how to start all services locally

## Phase 1: API Contract And BFF Skeleton

Goal: define how the frontend talks to the backend before implementing Agent intelligence.

Scope:

- design REST or RPC endpoints for Learning OS workflows
- create Python FastAPI BFF/API service
- return static or fixture-backed responses matching the current UI
- define streaming endpoint shape for future Agent progress
- define OpenAPI contract

Core endpoints:

```text
GET  /health
GET  /api/tasks/current
POST /api/generation-jobs
GET  /api/generation-jobs/{job_id}
GET  /api/generation-jobs/{job_id}/events
GET  /api/questions/{question_set_id}
GET  /api/mistakes
GET  /api/knowledge/search
GET  /api/reports/current
```

Python ownership:

- request validation
- response contracts
- job ids
- frontend-facing errors
- typed DTOs with Pydantic

Existing Rust reference status:

- keep existing Rust fixture API as a reference implementation until Python parity exists

Exit criteria:

- frontend can replace mock data with API responses without changing UI structure
- OpenAPI contract exists
- API tests cover success and error responses

## Phase 1.5: Model Gateway Foundation

Goal: prepare the backend to call different model providers through New API or another
OpenAI-compatible gateway without exposing model keys to the frontend.

Recommended request path:

```text
Next.js frontend
  -> Python FastAPI BFF / Agent Runtime
    -> Model Gateway adapter
      -> New API
        -> upstream model providers
```

Scope:

- add a Python model gateway module
- define gateway config from environment variables
- default to New API-compatible `/v1/chat/completions`
- build typed OpenAI-compatible chat completion request JSON
- expose only non-sensitive gateway status through the Python BFF
- keep API keys and provider routing outside the frontend

Environment variables:

```text
MY_SIFU_LLM_GATEWAY_PROVIDER=new-api
MY_SIFU_LLM_GATEWAY_BASE_URL=http://127.0.0.1:3000
MY_SIFU_LLM_GATEWAY_API_KEY=
MY_SIFU_DEFAULT_MODEL=gpt-4o-mini
```

Python ownership:

- model gateway adapter boundary
- model config loading
- API key handling
- frontend-safe status reporting
- later: model capability registry, retry policy, timeout policy, request audit

Existing Rust reference status:

- keep the existing `crates/model-gateway` implementation as a reference for request shape and status redaction

Exit criteria:

- Python model gateway module exists
- tests cover default config, environment override config, and OpenAI-compatible request shape
- Python BFF exposes `GET /api/model-gateway/status`
- status endpoint never returns raw API keys
- frontend still does not call New API directly

## Phase 2: Domain Model And Persistence Foundation

Goal: define durable entities before building Agent behavior.

Core entities:

- User
- LearningProfile
- Task
- QuestionSet
- Question
- AnswerAttempt
- Mistake
- KnowledgeSource
- RetrievalResult
- AgentRun
- ToolCall
- EvaluationResult
- MemoryItem

Recommended storage:

- PostgreSQL for primary relational data
- pgvector or a vector database for embeddings
- object storage for uploaded documents and generated exports
- append-only event table for Agent run history

Python ownership:

- migrations
- repository traits
- transaction boundaries
- typed persistence models
- event store

Existing Rust reference status:

- keep current Phase 2 Rust persistence as a reference and compatibility target until Python persistence reaches parity
- optional later extraction if a Rust event-store service becomes justified

Exit criteria:

- migrations can create a clean database
- core repositories have integration tests
- AgentRun and event records can be persisted and replayed

### Phase 2a: Domain Models And In-Memory Persistence

Goal: establish stable Python domain models and repository contracts before introducing PostgreSQL.

Scope:

- define core Python domain entities
- define repository traits for Learning OS read models and AgentRun persistence
- add an in-memory repository for tests and fixture-backed API responses
- support append/read replay for AgentRun events
- keep API response contracts unchanged

Entities covered in this step:

```text
User
LearningProfile
Task
QuestionSet / Question response contracts
AnswerAttempt
Mistake
KnowledgeSource
RetrievalResult
AgentRun
AgentRunEvent
ToolCall
EvaluationResult
MemoryItem
```

Out of scope:

- PostgreSQL migrations
- sqlx repositories
- authentication
- real Memory service
- real RAG ingestion or vector search
- real model calls

Exit criteria:

- domain model serialization tests pass
- in-memory repository tests pass
- AgentRun events can be appended and replayed in sequence order
- Python BFF can read fixture-backed data through the repository boundary

### Phase 2b: PostgreSQL Persistence

Goal: replace or complement the in-memory repository with real database-backed persistence.

Scope:

- add PostgreSQL migrations
- add database connection pool config
- implement sqlx repositories
- add integration tests against local database or Docker compose
- persist AgentRun and event records durably

Initial implementation can keep Learning OS read models fixture-backed while making AgentRun and
AgentRunEvent durable first. This keeps the first database step focused on replayable runtime state,
which is the highest-leverage persistence boundary for later State, Tool Manager, Evaluation, and
observability work.

Exit criteria:

- migration creates core Phase 2 tables
- database URL config can be loaded and redacted for logs
- Postgres repository can run migrations
- Postgres repository can create/read AgentRun records
- Postgres repository can append/replay AgentRunEvent records in sequence order
- local checks do not require PostgreSQL unless `MY_SIFU_DATABASE_URL` is explicitly set

## Phase 2.5: Local Runtime With Docker

Goal: make local infrastructure reproducible before Memory, RAG, and real model calls depend on
external services.

This phase is about running local dependencies, not deploying the product. The Python API, existing
Rust reference API, Next.js frontend, and Python workers can still run from the host during this
phase.

Recommended local runtime shape:

```text
Host
  ├─ Next.js frontend
  ├─ Python FastAPI API / BFF
  ├─ Python workspaces
  └─ Rust API / BFF reference, optional during the transition

Docker Compose
  ├─ PostgreSQL
  ├─ New API
  ├─ Redis
  └─ MinIO
```

### Phase 2.5a: PostgreSQL Compose Runtime

Goal: make Phase 2b PostgreSQL persistence runnable with one local command.

Deliverables:

- `docker-compose.yml`
- `.env.docker.example`
- `docker/postgres/` directory if initialization scripts are needed
- `just docker-up`
- `just docker-down`
- `just docker-logs`
- `just postgres-check-docker`

PostgreSQL requirements:

- service name: `postgres`
- exposed local port: `5432`
- database: `my_sifu`
- user: `my_sifu`
- password: development-only placeholder
- data volume: named Docker volume, not a repository directory
- healthcheck: `pg_isready`

Environment contract:

```text
MY_SIFU_DATABASE_URL=postgres://my_sifu:my_sifu@127.0.0.1:5432/my_sifu
```

Validation target:

```text
just docker-up
just postgres-check-docker
```

Exit criteria:

- PostgreSQL starts through Docker Compose
- healthcheck becomes healthy
- Python PostgreSQL repository migrations succeed
- AgentRun and AgentRunEvent integration test writes to the Docker database
- `just docker-down` stops services without deleting named volumes by default

### Phase 2.5b: New API Compose Runtime

Goal: run the New API gateway locally so Python can later send OpenAI-compatible requests through a
single gateway.

Deliverables:

- New API service added to `docker-compose.yml`
- New API environment block documented in `.env.docker.example`
- persistent New API data volume
- healthcheck or documented readiness check
- `just new-api-status` or documented browser/admin URL check

New API requirements:

- service name: `new-api`
- exposed local port: `3000`
- backend gateway URL:

```text
MY_SIFU_LLM_GATEWAY_PROVIDER=new-api
MY_SIFU_LLM_GATEWAY_BASE_URL=http://127.0.0.1:3000
MY_SIFU_LLM_GATEWAY_API_KEY=
MY_SIFU_DEFAULT_MODEL=gpt-4o-mini
```

Security rules:

- do not commit real upstream model keys
- `.env.docker.example` may contain placeholders only
- frontend must not call New API directly
- the backend remains the control plane for future model calls

Validation target:

```text
just docker-up
just dev-api
GET /api/model-gateway/status
```

Exit criteria:

- New API container starts
- model gateway status points to `http://127.0.0.1:3000`
- no real model key is committed
- docs explain where to configure upstream providers manually

### Phase 2.5c: Redis Runtime Placeholder

Goal: reserve the local runtime dependency for future queues, cache, rate limiting, and job lifecycle
coordination.

Deliverables:

- Redis service added to `docker-compose.yml`
- Redis URL added to `.env.docker.example`
- `MY_SIFU_REDIS_URL=redis://127.0.0.1:6379/0`
- healthcheck using `redis-cli ping`

Exit criteria:

- Redis starts through Docker Compose
- healthcheck becomes healthy
- no production behavior depends on Redis yet

### Phase 2.5d: MinIO Runtime Placeholder

Goal: reserve object storage for future uploaded documents, generated exports, and evaluation
artifacts.

Deliverables:

- MinIO service added to `docker-compose.yml`
- MinIO console exposed locally
- development access key and secret in `.env.docker.example`
- object-store endpoint added:

```text
MY_SIFU_OBJECT_STORE_ENDPOINT=http://127.0.0.1:9000
```

Exit criteria:

- MinIO starts through Docker Compose
- console is reachable locally
- docs explain that buckets and artifact write paths are implemented later

### Phase 2.5e: Developer Ergonomics And Verification

Goal: make the local runtime easy to operate without remembering raw Docker commands.

Recommended `just` commands:

```text
just docker-up
just docker-down
just docker-logs
just docker-ps
just docker-clean
just postgres-check-docker
```

`docker-clean` behavior:

- must be documented as destructive
- should require explicit command invocation
- should remove named volumes only when intentionally requested

Verification checklist:

- `docker compose config` succeeds
- `just docker-up` starts all services
- PostgreSQL healthcheck passes
- New API service is reachable
- Redis healthcheck passes
- MinIO console is reachable
- `just postgres-check-docker` passes
- `just docker-down` stops services
- `just check` still works without Docker

Out of scope:

- production deployment
- Kubernetes
- cloud secrets management
- real upstream model keys
- real RAG ingestion
- real Redis job queue
- real MinIO artifact writes
- containerizing the Python API, Rust reference API, worker services, or Next.js frontend

## Phase 3: Memory Service

Goal: implement long-term and task-relevant memory as a separate module.

Memory types:

- conversation summary
- user profile
- preference
- domain memory
- task history
- feedback memory

Memory write rules:

- store only useful long-term information
- distinguish explicit user facts from system inference
- record source and confidence
- support inspect/update/delete later
- do not mix textbook knowledge into user memory

Python ownership:

- memory API
- memory persistence
- access rules
- audit events
- read/write contracts

LLM-assisted memory responsibilities:

- summarization
- extraction candidates
- confidence scoring support

Suggested flow:

```text
AgentRun completed
  -> Python proposes memory candidates
  -> Python validates and stores approved memory items through explicit policy gates
  -> future runs request relevant memory by task context
```

Exit criteria:

- memory can be written, read, updated, and deleted
- memory records contain source, confidence, timestamps, and scope
- tests prove Memory is separate from RAG and State

## Phase 4: RAG / Knowledge Retrieval

Goal: add retrievable curriculum, textbook, question, pedagogy, rubric, and institution knowledge.

Knowledge layers:

- Curriculum KB
- Textbook KB
- Question KB
- Pedagogy KB
- Rubric KB
- Institution KB

Python ownership:

- document ingestion
- chunking
- embedding
- indexing
- retrieval
- reranking
- source attribution
- trust scoring

Python backend ownership:

- retrieval request contract
- source access control
- retrieval result persistence
- integration with AgentRun

Suggested Python service endpoints:

```text
POST /rag/ingest
POST /rag/search
POST /rag/rerank
GET  /rag/sources/{source_id}
```

Exit criteria:

- can ingest a sample textbook chapter
- can retrieve knowledge for "一次函数"
- retrieval results include source ids and trust scores
- generation phase can consume retrieval results without direct DB coupling

## Phase 5: Planning Module

Goal: decide how the Agent decomposes a user task into steps.

Planning responsibilities:

- interpret user goal
- select required knowledge sources
- decide whether to generate, edit, practice, review, or export
- choose skills from the preset skill catalog
- translate selected skills into allowed tool calls
- produce a step plan
- expose plan to frontend progress UI

Python ownership:

- plan state machine
- valid transitions
- plan persistence
- deterministic orchestration

LLM-assisted planning responsibilities:

- LLM planning prompts
- plan proposal generation
- plan critique or repair

Suggested flow:

```text
User Request
  -> Context Builder
  -> Memory Read
  -> RAG Search
  -> Python proposes plan
  -> Python validates allowed transitions/tools
  -> Python stores plan in AgentRun
```

Exit criteria:

- plan can be generated for a question-generation task
- plan references skill ids from the skill catalog rather than free-form tool names
- invalid plan steps are rejected
- frontend can show plan progress from persisted state

## Phase 5.5: Skill Catalog Seed

Goal: define the first preset Agent skills before implementing the full Tool Manager.

The current frontend desktop entries are UI shortcuts, not Agent skills. This phase defines the backend-facing skill catalog that Planning and Tool Manager will use later.

Skill design rules:

- Every skill has a stable `skill_id`.
- Every skill has typed input and output schemas.
- Every skill declares required context: memory, RAG results, question set, answer attempt, or report data.
- Every skill declares whether it may call LLMs, retrieval, external tools, or export jobs.
- Every skill declares guardrail requirements.
- Every skill emits structured events for AgentRun replay.
- Every skill is callable through the backend Tool Manager, even if parts of the implementation later move to Rust.

Seed skill catalog:

### `generate_question_set`

Purpose: generate a question set or paper from a learning goal.

Inputs:

- learning goal
- subject
- grade or learning stage
- textbook / source scope
- knowledge points
- difficulty target
- question count
- question type distribution
- relevant memory
- retrieval results

Outputs:

- question set id
- generated questions
- answer key
- explanations
- source references
- generation rationale

Implementation owner:

- Python backend: job lifecycle, input validation, persistence, event stream
- Python AI module: LLM prompt, RAG-grounded generation, structured output parsing

Required guardrails:

- curriculum alignment
- source grounding
- answer correctness
- age-appropriate content

### `edit_question`

Purpose: revise, replace, simplify, deepen, or re-balance an existing question.

Inputs:

- question id
- edit intent
- original question
- target difficulty
- target knowledge point
- quality issues

Outputs:

- edited question
- edit summary
- changed fields
- quality checks

Implementation owner:

- Python backend: versioning and audit trail
- Python AI module: rewrite and critique

Required guardrails:

- preserve answer correctness
- preserve source alignment
- prevent unexplained difficulty drift

### `explain_question`

Purpose: produce or improve a step-by-step explanation.

Inputs:

- question
- answer
- student answer if available
- explanation style preference
- relevant knowledge snippets

Outputs:

- explanation
- key steps
- common mistakes
- related knowledge points

Implementation owner:

- Python backend: request contract and persistence
- Python AI module: explanation generation

Required guardrails:

- mathematical correctness
- source consistency
- age-appropriate explanation style

### `grade_answer`

Purpose: judge a submitted answer and optionally partial reasoning.

Inputs:

- question
- correct answer
- user answer
- user reasoning steps
- scoring rubric

Outputs:

- correctness
- score
- feedback
- detected misconception
- evidence for decision

Implementation owner:

- Python backend: answer attempt lifecycle
- Python AI module: grading and rubric scoring

Required guardrails:

- deterministic checks before LLM judgment when possible
- rubric consistency
- explainable grading result

### `analyze_mistake`

Purpose: convert a wrong answer into structured mistake memory and weak-point data.

Inputs:

- question
- user answer
- correct answer
- explanation
- knowledge points
- prior mistakes

Outputs:

- mistake category
- likely cause
- weak knowledge points
- remediation suggestion
- memory candidate

Implementation owner:

- Python backend: mistake persistence and memory write approval boundary
- Python AI module: misconception classification

Required guardrails:

- do not store sensitive or unnecessary personal data
- distinguish observed facts from inferred causes

### `recommend_next_practice`

Purpose: recommend the next generation or practice settings from current performance.

Inputs:

- recent attempts
- mistake groups
- mastery metrics
- memory preferences
- available knowledge scope

Outputs:

- next task recommendation
- question count
- difficulty
- knowledge point focus
- rationale

Implementation owner:

- Python backend: recommendation contract and task creation
- Python AI module: recommendation reasoning

Required guardrails:

- avoid overfitting to one attempt
- keep recommendations explainable

### `search_knowledge`

Purpose: retrieve relevant textbook, curriculum, question, pedagogy, rubric, or institution knowledge.

Inputs:

- query
- source filters
- user/task context
- desired result count

Outputs:

- retrieval results
- source ids
- relevance scores
- trust scores
- snippets

Implementation owner:

- Python backend: request authorization, source access, persistence
- Python RAG module: embedding search, reranking, source scoring

Required guardrails:

- source access control
- trust threshold
- source attribution

### `check_curriculum_alignment`

Purpose: verify whether a question set matches the intended curriculum, textbook, and knowledge points.

Inputs:

- question set
- target curriculum scope
- retrieval/source references

Outputs:

- alignment score
- missing coverage
- off-scope items
- recommended corrections

Implementation owner:

- Python backend: threshold enforcement and result storage
- Python AI module: alignment scoring

Required guardrails:

- block or flag off-scope generated content
- preserve source references

### `evaluate_question_quality`

Purpose: evaluate generated questions before they are shown or exported.

Inputs:

- question set
- intended difficulty
- intended question type distribution
- source references
- rubric

Outputs:

- quality score
- correctness score
- difficulty score
- diversity score
- explanation quality score
- recommended regeneration actions

Implementation owner:

- Python backend: required quality gate
- Python eval module: rubric evaluation and batch scoring

Required guardrails:

- low-quality outputs cannot silently proceed
- score rationale must be stored

### `export_paper`

Purpose: produce an exportable paper, answer sheet, explanation document, or practice report.

Inputs:

- question set id
- export format
- include answers
- include explanations
- layout options

Outputs:

- export job id
- artifact metadata
- preview data
- download link when available

Implementation owner:

- Python backend: export job lifecycle, artifact storage, permissions
- Python or document renderer: document rendering if needed

Required guardrails:

- only export persisted, quality-checked question sets
- record generated artifact source

Skill catalog deliverables:

- `contracts/skills/skill-catalog.schema.json`
- `contracts/skills/generate_question_set.schema.json`
- `contracts/skills/edit_question.schema.json`
- `contracts/skills/explain_question.schema.json`
- `contracts/skills/grade_answer.schema.json`
- `contracts/skills/analyze_mistake.schema.json`
- `contracts/skills/recommend_next_practice.schema.json`
- `contracts/skills/search_knowledge.schema.json`
- `contracts/skills/check_curriculum_alignment.schema.json`
- `contracts/skills/evaluate_question_quality.schema.json`
- `contracts/skills/export_paper.schema.json`

Exit criteria:

- each seed skill has a stable id, input schema, output schema, owner, and guardrail list
- Planning can reference skills by id
- Tool Manager can register skill-backed tools later without renaming contracts
- frontend can display skill progress using stable names and event labels

## Phase 6: Tool Manager

Goal: safely expose tools to the Agent.

Initial tools should be derived from the Phase 5.5 skill catalog. A skill is the user-visible capability; a tool is the executable backend operation. Some skills may map to one tool, while others may orchestrate multiple tools.

Initial skill-backed tools:

- `generate_question_set`
- `edit_question`
- `explain_question`
- `grade_answer`
- `analyze_mistake`
- `recommend_next_practice`
- `search_knowledge`
- `check_curriculum_alignment`
- `evaluate_question_quality`
- `export_paper`

Python backend ownership:

- tool registry
- tool permissions
- tool call lifecycle
- timeouts and retries
- structured tool logs
- sandbox boundary for unsafe tools

Python AI module ownership:

- AI-heavy tool implementations
- scoring and generation internals

Tool call event shape should include:

```text
tool_call_id
agent_run_id
tool_name
input
output
status
started_at
finished_at
error
```

Exit criteria:

- tools are registered through a typed interface
- every registered tool maps to a skill catalog entry or a documented internal-only tool
- tool calls are auditable
- failed tools do not corrupt AgentRun state
- frontend can show tool progress events

## Phase 7: State Management

Goal: make every Agent run resumable, inspectable, and recoverable.

State should track:

- current phase
- active plan step
- generated artifacts
- tool calls
- user confirmations
- retry count
- final response status

Python ownership:

- state machine
- event sourcing or append-only transitions
- recovery logic
- idempotency

Worker design requirements:

- stateless workers where possible
- deterministic outputs from explicit inputs

Exit criteria:

- an interrupted generation job can resume
- repeated client requests do not duplicate work
- frontend can poll or stream current state

## Phase 8: Guardrails

Goal: enforce safety, privacy, quality, and domain constraints.

Guardrail categories:

- user data privacy
- age-appropriate content
- curriculum alignment
- hallucinated source prevention
- answer correctness checks
- toxic or irrelevant content filters
- tool permission checks

Python backend ownership:

- mandatory enforcement gates
- policy configuration
- request blocking
- audit logs

Python AI module ownership:

- content classification
- educational quality checks
- answer verification helpers

Exit criteria:

- generation cannot bypass required guardrail checks
- blocked outputs include reason codes
- guardrail outcomes are stored in AgentRun events

## Phase 9: Evaluation Module

Goal: measure whether generated questions and explanations are good enough.

Evaluation dimensions:

- correctness
- difficulty alignment
- knowledge point coverage
- source grounding
- explanation quality
- diversity
- student-practice usefulness
- mistake remediation value

Python ownership:

- evaluation prompts
- rubric scoring
- batch eval datasets
- regression eval scripts

Python backend ownership:

- store evaluation results
- enforce required quality thresholds
- expose evaluation summaries to frontend

Exit criteria:

- generated question sets receive structured scores
- low-quality outputs can trigger regeneration
- evaluation history is available for reports

## Phase 10: Harness And Observability

Goal: make Agent behavior testable, replayable, and debuggable.

Harness responsibilities:

- scenario runner
- golden test cases
- replay from AgentRun events
- load testing
- regression testing
- trace viewer
- prompt/version tracking

Python backend ownership:

- run replay
- event stream
- service metrics
- structured logs

Python eval module ownership:

- eval datasets
- offline scoring
- experiment reports

Exit criteria:

- one command runs regression scenarios
- a failed Agent run can be replayed from stored events
- prompt/version metadata is attached to each run

## Phase 11: Frontend API Integration

Goal: connect the existing Learning OS UI to real backend data incrementally.

Recommended order:

1. replace current task mock data with `GET /api/tasks/current`
2. replace window mock data with read-only API responses
3. add generation job creation
4. add event streaming for progress
5. add practice answer submission
6. add mistake book persistence
7. add report data from evaluation results

Frontend should keep:

- Learning OS desktop shell
- floating windows
- PC-first layout
- route-based default windows

Frontend should avoid:

- duplicating Agent state machine
- storing source of truth in React state
- making direct calls to Python AI modules or model gateway services

Exit criteria:

- frontend works against the backend BFF through OpenAPI contracts
- loading, empty, error, and success states exist
- e2e tests cover the main loop

## Phase 12: Export And Document Generation

Goal: turn generated content into usable materials.

Export targets:

- paper
- answer sheet
- explanation document
- practice report

Recommended ownership:

- Python coordinates export jobs and stores artifacts
- Python can render educational content templates if needed
- a dedicated document renderer can produce PDF/Docx later

Exit criteria:

- export preview is generated from stored QuestionSet
- exported artifacts are linked to AgentRun
- frontend can show export status and download links

## Phase 13: Deployment And Operations

Goal: make the system deployable without changing architecture.

Initial deployment shape:

- Next.js web app
- Python FastAPI API service
- Python worker or AI service
- PostgreSQL
- vector index
- object storage
- background worker
- optional Rust service only if a later performance or sandboxing phase requires it

Operational needs:

- environment config
- secrets management
- migrations
- health checks
- structured logs
- metrics
- backup and restore

Exit criteria:

- local docker compose or equivalent exists
- staging deploy is reproducible
- health checks cover web, Python API, Python worker or AI service, database, and vector store

## Recommended Phase Order

Use this order unless a product demo requires otherwise:

```text
0. Repo foundation
1. API contract and Python BFF skeleton
1.5. Model Gateway Foundation
2. Domain model and persistence
2.5. Local Runtime With Docker
3. Memory
4. RAG / Knowledge Retrieval
5. Planning
5.5. Skill Catalog Seed
6. Tool Manager
7. State Management
8. Guardrails
9. Evaluation
10. Harness and Observability
11. Frontend API integration
12. Export generation
13. Deployment and operations
```

Memory, RAG, State, and Tool Manager should not be merged into one generic "Agent service". Keeping them separate will make testing, replay, auditing, and future debugging much easier.

## Additional Recommendations

1. Start with Python FastAPI BFF before Python intelligence.
   The frontend needs stable contracts and job lifecycle semantics before real AI logic, and FastAPI keeps the first backend loop in the same language family as the Agent code.

2. Use Python behind TypeScript, not beside the frontend.
   Next.js should talk to the backend BFF. The backend should call New API, RAG, Memory, and tools. This keeps auth, state, tool permissions, and audit in one backend control plane.

3. Treat every Agent run as an event stream.
   This is the backbone for progress UI, debugging, replay, evaluation, and audit.

4. Do not put Memory, RAG, and State in the same table or abstraction.
   Memory is user/task context. RAG is external knowledge. State is current run progress.

5. Define contracts before prompts.
   Prompt outputs should satisfy typed schemas. If schemas are weak, debugging LLM behavior becomes expensive.

6. Add evaluation earlier than feels necessary.
   For an education Agent, correctness and source grounding are product requirements, not polish.

7. Keep the first real backend loop narrow.
   A good first backend milestone is: one static current task, one generation job, one fixture-backed question set, one event stream, one stored AgentRun.

8. Prefer PostgreSQL first.
   Add specialized stores only when the retrieval/evaluation workload proves the need.

9. Make source attribution non-optional.
   Every generated question should be able to point back to knowledge sources or clearly mark itself as template-derived.

10. Keep local development one-command.
   Python, frontend, database, model gateway, and worker startup should eventually be scriptable from a root task runner. Rust checks remain useful while the existing reference code stays in the repo.
