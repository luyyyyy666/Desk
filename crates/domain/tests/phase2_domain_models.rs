use domain::{
    AgentRun, AgentRunEvent, AgentRunEventKind, AgentRunStatus, KnowledgeSource, LearningProfile,
    LearningStage, MemoryItem, RetrievalResult, Task, TaskStatus, User,
};

#[test]
fn phase2_domain_models_serialize_with_stable_camel_case_fields() {
    let task = Task::new_fixture();
    let value = serde_json::to_value(task).unwrap();

    assert_eq!(value["id"], "task_fixture_linear_function_001");
    assert_eq!(
        value["learningGoal"],
        "巩固一次函数图像、解析式与实际应用题"
    );
    assert_eq!(value["status"], "active");
}

#[test]
fn agent_run_event_carries_replay_metadata() {
    let run = AgentRun::new_fixture();
    let event = AgentRunEvent::new(
        run.id.clone(),
        1,
        AgentRunEventKind::GenerationJobCreated,
        serde_json::json!({
            "job_id": "job_fixture_linear_function_001"
        }),
    );

    assert_eq!(run.status, AgentRunStatus::Completed);
    assert_eq!(event.sequence, 1);
    assert_eq!(event.kind, AgentRunEventKind::GenerationJobCreated);
    assert_eq!(event.payload["job_id"], "job_fixture_linear_function_001");
}

#[test]
fn agent_run_event_supports_retrieval_context_ready_for_phase4_rag_replay() {
    let event = AgentRunEvent::new(
        "run_fixture_linear_function_001".to_string(),
        3,
        AgentRunEventKind::RetrievalContextReady,
        serde_json::json!({
            "query": "一次函数",
            "sourceReferences": [
                {
                    "sourceId": "source_curriculum_001:chunk_0",
                    "chunkId": "source_curriculum_001:chunk_0",
                    "trustScore": 0.9,
                    "trustTier": "curated"
                }
            ],
            "directDatabaseAccess": false
        }),
    );
    let value = serde_json::to_value(&event).unwrap();

    assert_eq!(event.kind, AgentRunEventKind::RetrievalContextReady);
    assert_eq!(value["kind"], "retrieval_context_ready");
    assert_eq!(event.payload["query"], "一次函数");
}

#[test]
fn agent_run_event_supports_plan_created_for_phase5_replay() {
    let event = AgentRunEvent::new(
        "run_plan_001".to_string(),
        1,
        AgentRunEventKind::PlanCreated,
        serde_json::json!({
            "planId": "plan_run_plan_001",
            "status": "ready",
            "skillIds": [
                "search_knowledge",
                "generate_question_set",
                "check_curriculum_alignment",
                "evaluate_question_quality"
            ]
        }),
    );
    let value = serde_json::to_value(&event).unwrap();

    assert_eq!(event.kind, AgentRunEventKind::PlanCreated);
    assert_eq!(value["kind"], "plan_created");
    assert_eq!(event.payload["planId"], "plan_run_plan_001");
}

#[test]
fn phase2_supporting_entities_exist_for_future_memory_and_rag() {
    let user = User::fixture();
    let profile = LearningProfile::fixture_for_user(user.id.clone());
    let source = KnowledgeSource::fixture();
    let retrieval = RetrievalResult::fixture(source.id.clone());
    let memory = MemoryItem::fixture_for_user(user.id.clone());

    assert_eq!(profile.stage, LearningStage::Grade8);
    assert_eq!(source.source_type, "textbook");
    assert_eq!(retrieval.trust_score, 0.95);
    assert_eq!(memory.memory_type, "preference");
}

#[test]
fn task_status_serializes_as_lowercase_contract_value() {
    let value = serde_json::to_value(TaskStatus::Active).unwrap();

    assert_eq!(value, "active");
}
