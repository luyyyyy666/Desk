use domain::{AgentRunEvent, AgentRunEventKind, AgentRunStatus};
use persistence::{DatabaseConfig, PostgresLearningRepository};

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
