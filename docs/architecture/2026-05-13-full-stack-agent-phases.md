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

Use a Rust + Python backend split.

Rust should own stable runtime infrastructure:

- API gateway / BFF edge for frontend-facing contracts
- Agent runtime orchestration
- state machine and workflow execution
- tool execution boundary
- typed domain models
- persistence adapters
- audit logs and event records
- guardrail enforcement points
- high-concurrency streaming and job lifecycle

Python should own AI and knowledge workflows:

- LLM provider adapters
- prompt and response parsing
- RAG ingestion and retrieval pipelines
- embeddings and reranking
- question quality evaluation
- offline evaluation datasets
- data cleaning and document processing
- experimentation notebooks or scripts

Next.js should own product UI:

- PC web Learning OS interface
- static and interactive windows
- user workflows
- API calls to Rust BFF
- streaming UI for Agent progress

Avoid putting Agent decision logic in the frontend. Avoid making Python the core request router if the product needs strong state, concurrency, and long-running job control.

## Suggested Repository Shape

```text
apps/
  web/                         # Next.js 15 frontend
  api/                         # Rust HTTP API / BFF
crates/
  agent-core/                  # Runtime contracts, state machine, planning orchestration
  domain/                      # Shared Rust domain types
  tool-runtime/                # Tool registry and execution boundary
  persistence/                 # Database and event store adapters
python/
  ai-services/                 # FastAPI service for LLM/RAG/evaluation
  rag-pipeline/                # ingestion, chunking, embedding, indexing jobs
  evals/                       # datasets, rubrics, scoring scripts
contracts/
  openapi/                     # API schemas
  events/                      # event contracts
docs/
  architecture/
  superpowers/
```

This structure can be simplified at the start, but the ownership boundaries should stay clear.

## Phase 0: Repo And Engineering Foundation

Goal: make the repo ready for multi-language development.

Scope:

- choose package layout
- add Rust workspace
- add Python workspace
- move current Next prototype into `apps/web` or decide to keep `frontend/`
- add shared formatting, linting, testing commands
- define local environment conventions under `E:\DevData`
- add `.env.example`
- add CI-equivalent local scripts

Deliverables:

- `Cargo.toml` workspace
- Python project config, preferably `pyproject.toml`
- frontend package scripts
- root `justfile`, `makefile`, or task runner
- documented local dev commands

Recommended tools:

- Rust: `cargo`, `clippy`, `rustfmt`, `axum`, `tokio`, `serde`, `sqlx`
- Python: `uv`, `ruff`, `pytest`, `mypy` or `pyright`, `fastapi`
- Frontend: Next.js 15, TypeScript, Tailwind, Playwright

Exit criteria:

- one command runs backend checks
- one command runs Python checks
- one command runs frontend checks
- root docs explain how to start all services locally

## Phase 1: API Contract And BFF Skeleton

Goal: define how the frontend talks to the backend before implementing Agent intelligence.

Scope:

- design REST or RPC endpoints for Learning OS workflows
- create Rust BFF/API service
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

Rust ownership:

- request validation
- response contracts
- job ids
- frontend-facing errors
- typed DTOs

Python ownership:

- none yet, except optional fixture generation scripts

Exit criteria:

- frontend can replace mock data with API responses without changing UI structure
- OpenAPI contract exists
- API tests cover success and error responses

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

Rust ownership:

- migrations
- repository traits
- transaction boundaries
- typed persistence models
- event store

Python ownership:

- ingestion output data shapes
- embedding metadata schemas

Exit criteria:

- migrations can create a clean database
- core repositories have integration tests
- AgentRun and event records can be persisted and replayed

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

Rust ownership:

- memory API
- memory persistence
- access rules
- audit events
- read/write contracts

Python ownership:

- summarization
- extraction candidates
- confidence scoring support

Suggested flow:

```text
AgentRun completed
  -> Python proposes memory candidates
  -> Rust validates and stores approved memory items
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

Rust ownership:

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

Rust ownership:

- plan state machine
- valid transitions
- plan persistence
- deterministic orchestration

Python ownership:

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
  -> Rust validates allowed transitions/tools
  -> Rust stores plan in AgentRun
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
- Every skill is callable through Rust Tool Manager, even if the implementation lives in Python.

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

- Rust: job lifecycle, input validation, persistence, event stream
- Python: LLM prompt, RAG-grounded generation, structured output parsing

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

- Rust: versioning and audit trail
- Python: rewrite and critique

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

- Rust: request contract and persistence
- Python: explanation generation

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

- Rust: answer attempt lifecycle
- Python: grading and rubric scoring

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

- Rust: mistake persistence and memory write approval boundary
- Python: misconception classification

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

- Rust: recommendation contract and task creation
- Python: recommendation reasoning

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

- Rust: request authorization, source access, persistence
- Python: embedding search, reranking, source scoring

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

- Rust: threshold enforcement and result storage
- Python: alignment scoring

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

- Rust: required quality gate
- Python: rubric evaluation and batch scoring

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

- Rust: export job lifecycle, artifact storage, permissions
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

Rust ownership:

- tool registry
- tool permissions
- tool call lifecycle
- timeouts and retries
- structured tool logs
- sandbox boundary for unsafe tools

Python ownership:

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

Rust ownership:

- state machine
- event sourcing or append-only transitions
- recovery logic
- idempotency

Python ownership:

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

Rust ownership:

- mandatory enforcement gates
- policy configuration
- request blocking
- audit logs

Python ownership:

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

Rust ownership:

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

Rust ownership:

- run replay
- event stream
- service metrics
- structured logs

Python ownership:

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
- making direct calls to Python AI services

Exit criteria:

- frontend works against Rust BFF
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

- Rust coordinates export jobs and stores artifacts
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
- Rust API service
- Python AI service
- PostgreSQL
- vector index
- object storage
- background worker

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
- health checks cover web, Rust API, Python AI service, database, and vector store

## Recommended Phase Order

Use this order unless a product demo requires otherwise:

```text
0. Repo foundation
1. API contract and Rust BFF skeleton
2. Domain model and persistence
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

1. Start with Rust BFF before Python intelligence.
   The frontend needs stable contracts and job lifecycle semantics before real AI logic.

2. Use Python behind Rust, not beside the frontend.
   Next.js should talk to Rust. Rust should call Python AI services. This keeps auth, state, tool permissions, and audit in one backend control plane.

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
   Rust, Python, frontend, database, and worker startup should eventually be scriptable from a root task runner.
