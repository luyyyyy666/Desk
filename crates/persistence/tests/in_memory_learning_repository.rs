use domain::{AgentRunEvent, AgentRunEventKind, AgentRunStatus, fixtures};
use persistence::{InMemoryLearningRepository, LearningRepository};

#[test]
fn repository_reads_fixture_backed_learning_os_data() {
    let repository = InMemoryLearningRepository::with_fixture_data();

    let current_task = repository.current_task().unwrap();
    let question_set = repository
        .question_set(fixtures::FIXTURE_QUESTION_SET_ID)
        .unwrap();
    let mistakes = repository.mistakes();
    let report = repository.current_report();

    assert_eq!(current_task.task.title, "一次函数专项训练");
    assert_eq!(question_set.questions.len(), 4);
    assert_eq!(mistakes.groups.len(), 2);
    assert_eq!(report.metrics.len(), 4);
}

#[test]
fn repository_persists_agent_run_and_replays_events_in_sequence_order() {
    let repository = InMemoryLearningRepository::empty();
    let run = repository.create_agent_run("task_fixture_linear_function_001");

    repository.append_agent_run_event(AgentRunEvent::new(
        run.id.clone(),
        2,
        AgentRunEventKind::QuestionSetReady,
        serde_json::json!({ "question_set_id": fixtures::FIXTURE_QUESTION_SET_ID }),
    ));
    repository.append_agent_run_event(AgentRunEvent::new(
        run.id.clone(),
        1,
        AgentRunEventKind::PlanCreated,
        serde_json::json!({
            "planId": "plan_run_memory_0001",
            "status": "ready",
            "skillIds": ["search_knowledge", "generate_question_set"]
        }),
    ));
    repository.append_agent_run_event(AgentRunEvent::new(
        run.id.clone(),
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
    ));
    repository.update_agent_run_status(&run.id, AgentRunStatus::Completed);

    let stored_run = repository.agent_run(&run.id).unwrap();
    let events = repository.agent_run_events(&run.id);

    assert_eq!(stored_run.status, AgentRunStatus::Completed);
    assert_eq!(events[0].sequence, 1);
    assert_eq!(events[0].kind, AgentRunEventKind::PlanCreated);
    assert_eq!(events[1].sequence, 2);
    assert_eq!(events[1].kind, AgentRunEventKind::QuestionSetReady);
    assert_eq!(events[2].kind, AgentRunEventKind::RetrievalContextReady);
    assert_eq!(events[2].payload["query"], "一次函数");
}
