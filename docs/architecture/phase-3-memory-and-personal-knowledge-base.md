# Phase 3 Memory And Personal Knowledge Base Design

Date: 2026-05-19

## Purpose

Phase 3 is no longer a generic "store useful memories" module. It is the foundation for a learning
memory system that combines:

- a public exam-oriented knowledge base defined by the product owner
- a wrong-question evidence store
- a rebuildable personal knowledge base for each user
- a deterministic daily practice scheduler
- LLM analysis and question generation behind explicit verification gates

The product target is a unified single-user learning workspace first. Do not introduce teacher,
student, class, school, or multi-tenant memory concepts in Phase 3.

## Core Decision

Use a two-layer knowledge design:

```text
Public Knowledge Base
  -> stable Chinese middle-school exam knowledge foundation
  -> product-owner-authored knowledge points, tags, prerequisites, templates, and exam patterns

Personal Knowledge Base
  -> user-specific derived layer
  -> long-term learning profile, behavior, preferences, weak points, mastery state, and linked evidence
```

The public knowledge base is the foundation. The personal knowledge base is the building constructed
on top of that foundation. Personal knowledge should reference public `knowledge_point_id` and
`tag_id` values rather than inventing disconnected labels.

## Public Knowledge Base

The public knowledge base is not user memory. It is the standard coordinate system for the product.
It should support Chinese middle-school exam preparation before any user has personal history.

Phase 3 should design the public knowledge base schema, contracts, import path, and references, but
it should not seed real middle-school knowledge data yet. Keep the public knowledge tables empty in
the first implementation. Fill them only after the full memory, wrong-question, daily-practice, and
verification design is implemented and stable enough to accept curated content.

Recommended entities:

```text
public_knowledge_points
- id
- subject
- grade_band
- exam_stage
- parent_id
- name
- aliases
- difficulty_band
- exam_frequency
- description

public_tags
- id
- tag_type
  - error_type
  - question_type
  - difficulty
  - behavior
  - exam_pattern
- name
- description

public_knowledge_point_tags
- knowledge_point_id
- tag_id

public_knowledge_point_edges
- source_knowledge_point_id
- target_knowledge_point_id
- relation_type
  - prerequisite
  - same_topic
  - often_combined
  - exam_pattern
- weight
- source
```

The public `knowledge_point_id` and `tag_id` values should become the primary join keys across
questions, wrong questions, personal knowledge, daily practice, reports, and RAG results.

## Wrong Question Store

Wrong questions are a fact store and evidence source. They are not the personal knowledge base.

Recommended entities:

```text
wrong_questions
- id
- user_id
- question_text
- correct_answer
- user_answer
- explanation
- source
- subject
- created_at

wrong_question_knowledge_links
- wrong_question_id
- knowledge_point_id
- role
  - primary
  - secondary
  - prerequisite
  - trap
- content_weight
- source
  - public_kb
  - llm
  - manual
- confidence

wrong_question_tags
- wrong_question_id
- tag_id
- source
- confidence
```

`content_weight` describes the knowledge composition of the question itself. It does not describe
the user's error responsibility.

## Personal Knowledge Base

The personal knowledge base is a rebuildable derived layer. It stores the system's current best
understanding of the user's learning state.

Recommended entities:

```text
personal_knowledge_builds
- id
- user_id
- build_version
- model
- prompt_version
- public_kb_version
- status
  - building
  - active
  - superseded
  - failed
- created_at

personal_knowledge_nodes
- id
- build_id
- user_id
- knowledge_point_id
- mastery_state
  - weak
  - learning
  - reviewing
  - mastered_pending_confirm
  - mastered
- mastery_score
- weakness_score
- confidence
- evidence_count
- summary
- summary_for_embedding
- created_at
- updated_at

personal_knowledge_edges
- id
- build_id
- user_id
- source_knowledge_point_id
- target_knowledge_point_id
- relation_type
  - co_failed
  - co_practiced
  - confused_with
  - prerequisite_gap
  - improves_with
- weight
- confidence
- evidence_count
- summary
- summary_for_embedding
- created_at
- updated_at

personal_knowledge_evidence
- id
- build_id
- user_id
- target_type
  - node
  - edge
- target_id
- evidence_type
  - wrong_question
  - practice_attempt
  - explicit_feedback
  - manual_confirmation
- evidence_id
- analysis_summary
- created_at
```

Personal knowledge can be rebuilt as models, prompts, public knowledge, or analysis rules improve.
Keep build versions so the system can compare, roll back, or explain changes.

## Obsidian-Like Experience

The user-facing personal knowledge base should feel like an Obsidian-style graph and note system,
but the source of truth must remain structured data.

The frontend can show:

- a note-like page for each personal knowledge node
- backlinks and related knowledge nodes
- related wrong questions and practice attempts
- why the system thinks this point is weak
- user notes and manual confirmations

Separate editable user notes from calculated state:

```text
user_knowledge_notes
- id
- user_id
- knowledge_point_id
- note
- custom_tags
- created_at
- updated_at

user_knowledge_feedback
- id
- user_id
- knowledge_point_id
- feedback_type
  - confirm_weakness
  - deny_weakness
  - pause_practice
  - resume_practice
  - mark_mastered
- comment
- created_at
```

Users can edit notes, confirm or deny system judgments, pause or resume practice, and add custom
tags. Users should not directly edit raw wrong-question facts, mastery calculation logs, evidence
links, or scheduler history.

## Node And Tag Granularity

Personal knowledge nodes should only represent concepts that are:

- independently reviewable
- independently practiceable
- measurable for mastery
- useful for question generation

Tags should represent:

- error type
- question type
- difficulty
- behavior pattern
- fine-grained phenomenon
- exam pattern

For Phase 3, tags do not become personal knowledge nodes. Avoid graph explosion in the first version.

## Multi-Knowledge Questions

Middle-school exam questions often combine multiple knowledge points. The system must support
multi-knowledge questions with weights.

Separate question composition from user error responsibility:

```text
question_knowledge_links
- question_id
- knowledge_point_id
- role
  - primary
  - secondary
  - prerequisite
  - trap
- content_weight
- source
- confidence

attempt_error_links
- attempt_id
- knowledge_point_id
- error_weight
- tag_id
- evidence_summary
- confidence
```

Use `content_weight` for question analysis, generation, and mastery increases after correct answers.
Use `error_weight` for wrong-answer analysis and mastery decreases.

## Embedding And Vector Search

Embedding should be used, but it is not itself the vector database. Start with PostgreSQL plus
`pgvector` unless retrieval scale proves that a separate vector database is needed.

First embedding targets:

- public knowledge base chunks
- public question templates and public questions
- wrong questions and their analysis summaries

Later embedding targets:

- personal knowledge node summaries
- personal knowledge edge summaries

Recommended entity:

```text
knowledge_embeddings
- id
- source_type
  - public_kb
  - public_question
  - public_template
  - wrong_question
  - personal_node
  - personal_edge
- source_id
- user_id nullable
- knowledge_point_ids
- embedding_model
- embedding_vector
- content_hash
- created_at
```

Retrieval should be hybrid:

```text
1. structured filter by subject, grade, exam stage, knowledge points, difficulty, and question type
2. graph expansion through public and personal knowledge edges
3. vector retrieval for similar questions, explanations, mistakes, and templates
4. rerank before passing context to the LLM
```

## Daily Practice

Daily practice prevents personal knowledge from becoming a stale pile of old conclusions. It should
continuously recalibrate mastery state.

Use a deterministic scheduler for timing and thresholds. Use LLMs for semantic analysis and update
recommendations.

Recommended entities:

```text
review_schedule_items
- id
- user_id
- knowledge_point_id
- next_review_at
- interval_days
- ease_factor
- consecutive_successes
- status
  - active
  - paused
  - mastered_pending_confirm
  - mastered
- created_at
- updated_at

practice_attempts
- id
- user_id
- question_id
- user_answer
- is_correct
- difficulty
- time_spent_seconds nullable
- hint_used boolean
- reviewed_explanation boolean
- created_at

practice_attempt_analysis
- id
- attempt_id
- model
- prompt_version
- analysis_summary
- mastery_delta
- weakness_delta
- confidence
- created_at
```

First version mastery update inputs:

- correct or incorrect
- `content_weight` or `error_weight`
- difficulty factor

Record but do not strongly depend on these fields in the first version:

- time spent
- hint used
- explanation reviewed
- review interval

When mastery reaches the configured threshold, set:

```text
mastery_state = mastered_pending_confirm
review_status = paused_pending_user_confirmation
```

Only move to `mastered` after user confirmation.

## Question Generation Modes

Daily practice has two generation modes. In both modes, the personal knowledge base decides what to
practice.

### Mode A: Stable Bank / Similarity-Driven Practice

Use the personal knowledge target to retrieve public questions, public templates, and wrong-question
variants.

Retrieval inputs:

- weak knowledge point ids
- related personal edges
- public prerequisite and often-combined edges
- difficulty target
- question type target
- embedding similarity

This mode can use structural variation, but Phase 3 should not depend on advanced free-form
knowledge decomposition for this mode.

### Mode B: LLM Tool Generated Practice

Use the personal knowledge base and public knowledge base as context. Let the LLM call a question
generation skill or tool to produce a new question, answer, explanation, and structured metadata.

Required output:

```text
generated_question
- stem
- answer
- explanation
- knowledge_point_links
  - knowledge_point_id
  - content_weight
  - role
- difficulty
- question_type
- expected_error_traps
- grading_rubric
```

First version defaults:

- daily practice default count: 3 questions
- default mode allows at most 1 LLM-generated question
- enhanced mode allows 1 to 3 LLM-generated questions

## Generator And Verifier Agents

LLM-generated questions must pass a separate verification gate before practice.

```text
Generator Agent
  -> creates the question, answer, explanation, knowledge weights, difficulty, and rubric

Verifier Agent
  -> independently solves or checks the generated item
  -> verifies the answer and explanation
  -> checks whether the question is valid and not ambiguous
  -> checks whether knowledge point links are plausible
```

Question lifecycle:

```text
draft_generated
  -> verification_running
  -> verification_passed
  -> approved_for_practice
  -> used_in_daily_practice
```

Failure lifecycle:

```text
draft_generated
  -> verification_failed
  -> regenerated_once
  -> verification_failed
  -> needs_human_review
```

Recommended entities:

```text
generated_questions
- id
- user_id
- generation_request_id
- generation_attempt
- mode
  - stable_bank
  - llm_tool_generated
- status
  - draft_generated
  - verification_running
  - verification_passed
  - approved_for_practice
  - verification_failed
  - needs_human_review
- stem
- answer
- explanation
- difficulty
- question_type
- model
- prompt_version
- public_kb_version
- personal_knowledge_build_id
- created_at

question_verification_reports
- id
- question_id
- verifier_agent_id
- verdict
  - passed
  - failed
  - needs_review
- verifier_answer
- issue_summary
- failed_reason_type
  - no_valid_answer
  - answer_mismatch
  - ambiguous_condition
  - explanation_error
  - knowledge_tag_mismatch
  - difficulty_mismatch
- confidence
- created_at
```

Verifier Agent has veto power. A question that does not pass verification must not enter daily
practice and must not update the personal knowledge base.

First version failure handling:

- first verification failure: record the reason and regenerate once
- second verification failure: move to `needs_human_review`
- no infinite regeneration loops

## Phase 3 First-Version Scope

Implement these first:

1. public knowledge point and tag contracts, with empty seed data
2. wrong-question fact store contracts
3. personal knowledge node, edge, evidence, and build contracts
4. daily practice schedule contracts
5. practice attempt and analysis contracts
6. generated question and verification report contracts
7. hybrid retrieval design contracts for future Phase 4 RAG

Do not implement these in Phase 3 first version:

- curated public knowledge content
- teacher, student, class, school, or multi-tenant memory
- tag-to-node promotion
- fully automated cross-chapter free-form question generation without verification
- direct user editing of calculated mastery state
- unverified generated questions entering daily practice
- unbounded personal memory accumulation without review scheduling

## Exit Criteria

Phase 3 is ready to implement when:

- public knowledge base and personal knowledge base are separate in schema and service boundaries
- wrong questions are stored as raw evidence, not as personal knowledge nodes
- personal knowledge can be rebuilt with build versions
- personal knowledge nodes and edges can cite evidence
- multi-knowledge questions support `content_weight`
- wrong attempts support `error_weight`
- daily practice can select targets from personal knowledge state
- LLM-generated questions require verifier approval before use
- tests prove Memory, RAG, wrong questions, and State remain separate concepts
