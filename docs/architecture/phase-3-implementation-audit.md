# Phase 3 Implementation Audit

Date: 2026-05-28

This audit maps the Phase 3 implementation back to
`docs/architecture/phase-3-memory-and-personal-knowledge-base.md`.

Phase 3 remains a first-version contract and in-memory implementation. It does not seed curated
public knowledge content, run real RAG, call embedding providers, or perform real LLM generation.

## Current Commits

- `767bb6d` Add phase 3 memory contracts
- `30b92ba` Add phase 3 memory workspace
- `f11fdfd` Add phase 3 memory API contract
- `7bdd885` Add phase 3 user knowledge metadata
- `a03f3e3` Add phase 3 daily practice mastery updates
- `043921c` Tighten phase 3 generated question lifecycle
- `94f572e` Add phase 3 daily practice generation plan
- `9a77aa9` Expose phase 3 hybrid retrieval plan
- `efb6bf6` Add phase 3 public knowledge placeholder
- `ae17361` Guard phase 3 generated practice memory writes
- `1f3d203` Keep phase 3 public knowledge seed empty

## First-Version Scope Evidence

| Requirement | Status | Evidence |
| --- | --- | --- |
| Public knowledge point and tag contracts, with empty seed data | Implemented | `PublicKnowledgePoint`, `PublicTag`, `PublicKnowledgeSeedData`, `InMemoryPublicKnowledgeRepository`; `PublicKnowledgeSeedData.empty()`; non-empty seed rejection in `import_seed()` |
| Wrong-question fact store contracts | Implemented | `WrongQuestion`, `WrongQuestionKnowledgeLink`, `TagLink`, `InMemoryWrongQuestionRepository`, `Phase3MemoryApi.record_wrong_question()` |
| Personal knowledge node, edge, evidence, and build contracts | Implemented | `PersonalKnowledgeBuild`, `PersonalKnowledgeNode`, `PersonalKnowledgeEdge`, `PersonalKnowledgeEvidence`, `InMemoryPersonalKnowledgeRepository`, `activate_personal_knowledge_build()` |
| Daily practice schedule contracts | Implemented | `ReviewScheduleItem`, `ReviewScheduleStatus`, `InMemoryReviewScheduleRepository`, `DailyPracticeService.select_due_targets()` |
| Practice attempt and analysis contracts | Implemented | `PracticeAttempt`, `PracticeAttemptAnalysis`, `AttemptErrorLink`, `InMemoryPracticeRepository`, `record_practice_attempt_analysis()` |
| Generated question and verification report contracts | Implemented | `GeneratedQuestion`, `GeneratedQuestionKnowledgeLink`, `QuestionVerificationReport`, `QuestionGenerationService`, generated-question lifecycle methods |
| Hybrid retrieval design contracts for future Phase 4 RAG | Implemented as design-only | `HybridRetrievalRequest`, `Phase3MemoryApi.plan_hybrid_retrieval()`, OpenAPI `/api/memory/hybrid-retrieval/plan`; response sets `executesRetrieval: false` |

## Explicit Non-Goals Checked

| Non-goal | Current guard |
| --- | --- |
| Curated public knowledge content | Production path imports only `PublicKnowledgeSeedData.empty()`; non-empty seed raises `ValueError`; frontend `publicKnowledgeStatus` is zero-count and schema-only |
| Teacher, student, class, school, or multi-tenant memory | OpenAPI test rejects `teacher`, `student`, `classroom`, `school`, and `tenant`; implementation uses single `user_id` without role split |
| Tag-to-node promotion | Tags are `PublicTag`, `TagLink`, and custom note tags only; no tag-to-personal-node promotion service exists |
| Fully automated cross-chapter free-form generation without verification | Generated questions require verifier approval before practice, and failed verification regenerates once then goes to human review |
| Direct user editing of calculated mastery state | User note and feedback APIs are separate from calculated personal knowledge nodes; only `mark_mastered` can confirm pending mastery |
| Unverified generated questions entering daily practice | `approve_for_practice()` requires `verification_passed`; `mark_used_in_daily_practice()` requires `approved_for_practice` |
| Unverified generated questions updating personal knowledge | `record_practice_attempt_analysis()` rejects generated questions unless their status is `used_in_daily_practice` |
| Unbounded personal memory accumulation without review scheduling | Daily practice schedule and mastery pending confirmation are part of the workspace; mastered state requires user confirmation |

## Exit Criteria Evidence

| Exit criterion | Evidence |
| --- | --- |
| Public knowledge base and personal knowledge base are separate in schema and service boundaries | Separate repositories: `InMemoryPublicKnowledgeRepository` and `InMemoryPersonalKnowledgeRepository`; separate OpenAPI paths for public status/import and personal build activation |
| Wrong questions are stored as raw evidence, not personal knowledge nodes | `test_workspace_keeps_public_kb_empty_and_wrong_questions_out_of_personal_kb`; wrong-question repository is separate from personal knowledge repository |
| Personal knowledge can be rebuilt with build versions | `build_version` and build statuses; activating a later build supersedes the previous active build |
| Personal knowledge nodes and edges can cite evidence | `PersonalKnowledgeEvidence`; workspace rejects activation when evidence-counted targets lack citations |
| Multi-knowledge questions support `content_weight` | `WrongQuestionKnowledgeLink.content_weight` and `GeneratedQuestionKnowledgeLink.content_weight` |
| Wrong attempts support `error_weight` | `AttemptErrorLink.error_weight` and `PracticeAttemptAnalysisRequest.errorLinks` |
| Daily practice can select targets from personal knowledge state | `DailyPracticeService.select_due_targets()` selects due personal nodes sorted by weakness |
| LLM-generated questions require verifier approval before use | verifier lifecycle tests cover failed, passed, approved, used, and blocked paths |
| Tests prove Memory, RAG, wrong questions, and State remain separate concepts | Phase 3 tests cover memory snapshot, wrong-question evidence, hybrid retrieval plan-only behavior, and generated-question lifecycle state |

## Frontend Phase 3 Placeholder

The PC web Learning OS knowledge window now reserves a public knowledge entry point without seeding
content:

- visible label: `公共知识库`
- empty state: `内容暂为空`
- action placeholder: `录入公共知识库`
- static status: knowledge points `0`, tags `0`, edges `0`, import mode `schema-only`

The same window labels the existing mock knowledge cards as `个人知识库派生层` so the static personal
learning profile is not mistaken for curated public knowledge content.

## Verification Commands

Run after the final Phase 3 audit changes:

```powershell
just python-check
cd frontend; npm run test
cd frontend; npm run lint
cd frontend; npm run build
git diff --check
```

Expected boundaries:

- no production public knowledge seed beyond `PublicKnowledgeSeedData.empty()`
- no real embedding provider call
- no real vector search or RAG execution
- no teacher/student/class/school/multi-tenant split
