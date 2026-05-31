# Phase 5 Planning Implementation Audit

Date: 2026-05-31

This audit maps the current Phase 5 and Phase 5.5 implementation back to
`docs/architecture/2026-05-13-full-stack-agent-phases.md`.

Phase 5 now has a deterministic Python planning contract for question-generation tasks, a seed
skill catalog with stable backend skill ids, JSON schema deliverables for the catalog and each seed
skill, OpenAPI contracts for plan generation and persisted plan reads, replayable `plan_created`
AgentRun event support, and a static PC frontend surface that shows persisted plan progress.

## Current Commits

- `a5105d0` Add phase 5 planning contracts
- `be18d5b` Expose phase 5 plan progress

## Implemented

| Requirement | Status | Evidence |
| --- | --- | --- |
| Plan can be generated for a question-generation task | Implemented | `Phase5PlanningApi.generate_plan()` accepts `taskType: question_generation`; `generate_question_generation_plan()` creates a ready plan |
| Plan references skill ids from the skill catalog rather than free-form tool names | Implemented | `_QUESTION_GENERATION_SKILL_ORDER` uses `search_knowledge`, `generate_question_set`, `check_curriculum_alignment`, and `evaluate_question_quality`; `validate_plan()` calls `SkillCatalog.require()` for every step |
| Invalid plan steps are rejected | Implemented | `validate_plan()` rejects unknown skills and non-matching step order; `test_planner_rejects_unknown_skill_id_and_invalid_step_order()` covers both cases |
| Plan persistence and readback | Implemented as in-memory backend contract | `InMemoryPlanRepository.save()` and `get()`; `Phase5PlanningApi.get_plan()` returns persisted plan state |
| AgentRun event emitted for planning | Implemented | `generate_plan()` returns an `agentRunEvent` with kind `plan_created`; Rust `AgentRunEventKind::PlanCreated` maps to/from DB value `plan_created` |
| Frontend can show plan progress from persisted state | Implemented as static PC UI | `persistedPlan` fixture in `frontend/lib/mock-data.ts`; Generator window renders plan id, current step, status, and skill ids |
| OpenAPI declares Phase 5 plan contracts | Implemented | `/api/plans/generate`, `/api/plans/{plan_id}`, `PlanGenerateRequest`, `PlanResponse`, `Plan`, `PlanStep`, and `AgentRunEvent` schemas |
| OpenAPI contract parses as YAML | Implemented as regression coverage | `frontend/tests/openapi-contract.test.ts` parses `contracts/openapi/learning-os.yaml` with `js-yaml` |

## Phase 5.5 Skill Catalog Seed

| Requirement | Status | Evidence |
| --- | --- | --- |
| Every seed skill has a stable id | Implemented | `SkillCatalog.seed()` defines ten skill ids matching `contracts/skills/*.schema.json` |
| Every seed skill has typed input and output schemas | Implemented in contract | `contracts/skills/skill-catalog.schema.json` plus one schema file per seed skill |
| Every seed skill declares required context | Implemented | `SkillDefinition.required_context`; generated `PlanStep.requiredContext`; `skill-catalog.schema.json` requires `requiredContext` for catalog entries |
| Every seed skill declares capabilities and guardrails | Implemented | `SkillDefinition.capabilities` and `guardrails`; `skill-catalog.schema.json` requires `capabilities` and `guardrails` for catalog entries |
| Stable event labels exist for replay and frontend progress | Implemented | `SkillDefinition.event_labels`; `AgentRunEventKind` supports `plan_created` and `retrieval_context_ready` |

## Not Complete Yet

| Requirement | Current state | Needed next |
| --- | --- | --- |
| LLM-assisted planning | Not implemented | Add plan proposal, critique, and repair only after prompt contracts and repair policy are specified |
| Real Tool Manager execution | Not implemented in Phase 5 | Phase 6 should register skill-backed tools without renaming the Phase 5.5 contracts |
| Durable database-backed plan repository | In-memory contract only | Add PostgreSQL persistence when AgentRun orchestration needs durable plan state beyond replayable events |
| Live frontend API integration | Static fixture UI only | Wire frontend to the BFF after backend endpoints are implemented behind OpenAPI-generated client types |

## Verification

Run after current Phase 5 changes:

```text
uv run pytest tests/test_phase3_openapi_contract.py python/my_sifu_agent/tests/test_phase5_planning_contracts.py
uv run ruff check python/my_sifu_agent/planning.py python/my_sifu_agent/tests/test_phase5_planning_contracts.py tests/test_phase3_openapi_contract.py
cargo test -p domain --test phase2_domain_models
cargo test -p persistence --test in_memory_learning_repository --test postgres_persistence_contract
cargo clippy -p domain -p persistence --all-targets -- -D warnings
cd frontend; npm run test
cd frontend; npm run lint
cd frontend; npm run build
git diff --check
```

Latest observed results for the code commits above:

- Python focused tests: `9 passed`
- Python lint: passed
- Frontend focused plan test: `7 passed`
- Frontend full tests: `13 passed`
- Frontend lint: passed
- Frontend build: passed
- Rust domain model contract: `6 passed`
- Rust persistence contracts: `2 passed` and `5 passed`
- Rust clippy: passed
- Docker compose config: passed; PostgreSQL image resolves to `pgvector/pgvector:pg17`
- OpenAPI YAML parse regression: passed
- `git diff --check`: passed, with CRLF conversion warnings only

## Boundary Checks

- The frontend still does not call model providers, embedding providers, or Python AI modules directly.
- Planning currently selects backend skill ids, not arbitrary tool names.
- Phase 5 does not implement real question generation; it prepares a validated plan for later execution.
- Phase 5.5 defines skill contracts, but does not replace Phase 6 Tool Manager registration.
- Public knowledge curated content remains empty.
