use domain::{AgentRunEvent, AgentRunEventKind, AgentRunStatus};
use persistence::{
    DatabaseConfig, PostgresEmbeddingVectorRecord, PostgresLearningRepository, RagSearchFilters,
};

#[test]
fn database_config_reads_url_and_masks_password() {
    let config = DatabaseConfig::from_env_with(|key| match key {
        "MY_SIFU_DATABASE_URL" => {
            Some("postgres://my_sifu:secret@127.0.0.1:5432/my_sifu".to_string())
        }
        _ => None,
    })
    .unwrap();

    assert_eq!(
        config.database_url,
        "postgres://my_sifu:secret@127.0.0.1:5432/my_sifu"
    );
    assert_eq!(
        config.redacted_database_url(),
        "postgres://my_sifu:***@127.0.0.1:5432/my_sifu"
    );
}

#[test]
fn migration_declares_core_phase2b_tables() {
    let migration = include_str!("../migrations/0001_phase2_core.sql");

    for table in [
        "CREATE TABLE IF NOT EXISTS users",
        "CREATE TABLE IF NOT EXISTS learning_profiles",
        "CREATE TABLE IF NOT EXISTS tasks",
        "CREATE TABLE IF NOT EXISTS question_sets",
        "CREATE TABLE IF NOT EXISTS questions",
        "CREATE TABLE IF NOT EXISTS agent_runs",
        "CREATE TABLE IF NOT EXISTS agent_run_events",
    ] {
        assert!(
            migration.contains(table),
            "missing migration table: {table}"
        );
    }

    assert!(migration.contains("UNIQUE (agent_run_id, sequence)"));
}

#[tokio::test]
async fn postgres_repository_persists_agent_run_events_when_database_is_configured() {
    let Some(config) = DatabaseConfig::from_env_with(|key| std::env::var(key).ok()) else {
        return;
    };

    let repository = PostgresLearningRepository::connect(&config).await.unwrap();
    repository.run_migrations().await.unwrap();

    let run = repository
        .create_agent_run("task_fixture_linear_function_001")
        .await
        .unwrap();
    repository
        .append_agent_run_event(AgentRunEvent::new(
            run.id.clone(),
            1,
            AgentRunEventKind::GenerationJobCreated,
            serde_json::json!({ "job_id": "job_fixture_linear_function_001" }),
        ))
        .await
        .unwrap();
    repository
        .update_agent_run_status(&run.id, AgentRunStatus::Completed)
        .await
        .unwrap();

    let stored_run = repository.agent_run(&run.id).await.unwrap().unwrap();
    let events = repository.agent_run_events(&run.id).await.unwrap();

    assert_eq!(stored_run.status, AgentRunStatus::Completed);
    assert_eq!(events.len(), 1);
    assert_eq!(events[0].kind, AgentRunEventKind::GenerationJobCreated);
}

#[tokio::test]
async fn postgres_repository_persists_and_searches_phase4_embedding_vectors() {
    let Some(config) = DatabaseConfig::from_env_with(|key| std::env::var(key).ok()) else {
        return;
    };

    let repository = PostgresLearningRepository::connect(&config).await.unwrap();
    repository.run_migrations().await.unwrap();

    repository
        .upsert_embedding_vector(PostgresEmbeddingVectorRecord {
            id: "vec_phase4_linear".to_string(),
            source_type: "public_knowledge_chunk".to_string(),
            source_id: "source_curriculum_001:chunk_0".to_string(),
            chunk_id: "source_curriculum_001:chunk_0".to_string(),
            embedding_model: "text-embedding-v1".to_string(),
            content_hash: "sha256:linear".to_string(),
            embedding: test_embedding(1.0),
            metadata: serde_json::json!({
                "subject": "math",
                "knowledgeLayer": "curriculum",
                "text": "一次函数的图像是一条直线。"
            }),
        })
        .await
        .unwrap();

    repository
        .upsert_embedding_vector(PostgresEmbeddingVectorRecord {
            id: "vec_phase4_english".to_string(),
            source_type: "public_knowledge_chunk".to_string(),
            source_id: "source_english_001:chunk_0".to_string(),
            chunk_id: "source_english_001:chunk_0".to_string(),
            embedding_model: "text-embedding-v1".to_string(),
            content_hash: "sha256:english".to_string(),
            embedding: test_embedding(1.0),
            metadata: serde_json::json!({
                "subject": "english",
                "knowledgeLayer": "curriculum"
            }),
        })
        .await
        .unwrap();

    let results = repository
        .search_embedding_vectors(
            &test_embedding(1.0),
            RagSearchFilters {
                subject: Some("math".to_string()),
                knowledge_layer: Some("curriculum".to_string()),
            },
            5,
        )
        .await
        .unwrap();

    assert_eq!(results.len(), 1);
    assert_eq!(results[0].source_id, "source_curriculum_001:chunk_0");
    assert_eq!(results[0].trust_score, 0.9);
    assert_eq!(results[0].metadata["subject"], "math");

    repository
        .persist_retrieval_results("一次函数", &results)
        .await
        .unwrap();

    let persisted = repository
        .retrieval_results_for_query("一次函数")
        .await
        .unwrap();
    assert_eq!(persisted.len(), 1);
    assert_eq!(persisted[0].source_id, "source_curriculum_001:chunk_0");
    assert_eq!(persisted[0].final_score, results[0].final_score);
}

fn test_embedding(first_value: f32) -> Vec<f32> {
    let mut values = vec![0.0; 1536];
    values[0] = first_value;
    values
}
