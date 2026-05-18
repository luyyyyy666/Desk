use domain::{
    AgentRun, AgentRunEvent, AgentRunEventKind, AgentRunStatus, CurrentTaskResponse,
    GenerationJobResponse, KnowledgeSearchResponse, MistakesResponse, QuestionSetResponse,
    ReportResponse, fixtures,
};
use sqlx::{PgPool, Row, postgres::PgPoolOptions};
use std::cell::RefCell;
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PersistenceInfo {
    pub database_backend: &'static str,
}

impl PersistenceInfo {
    pub fn phase0() -> Self {
        Self {
            database_backend: "not_configured_yet",
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DatabaseConfig {
    pub database_url: String,
}

impl DatabaseConfig {
    pub fn from_env() -> Option<Self> {
        Self::from_env_with(|key| std::env::var(key).ok())
    }

    pub fn from_env_with<F>(read_env: F) -> Option<Self>
    where
        F: Fn(&str) -> Option<String>,
    {
        read_env("MY_SIFU_DATABASE_URL")
            .filter(|value| !value.trim().is_empty())
            .map(|database_url| Self { database_url })
    }

    pub fn redacted_database_url(&self) -> String {
        let Some((scheme, rest)) = self.database_url.split_once("://") else {
            return "***".to_string();
        };
        let Some((credentials, host)) = rest.split_once('@') else {
            return self.database_url.clone();
        };
        let Some((user, _password)) = credentials.split_once(':') else {
            return self.database_url.clone();
        };

        format!("{scheme}://{user}:***@{host}")
    }
}

pub trait LearningRepository {
    fn current_task(&self) -> Option<CurrentTaskResponse>;
    fn generation_job(&self, job_id: &str) -> Option<GenerationJobResponse>;
    fn question_set(&self, question_set_id: &str) -> Option<QuestionSetResponse>;
    fn mistakes(&self) -> MistakesResponse;
    fn knowledge_search(&self, query: String) -> KnowledgeSearchResponse;
    fn current_report(&self) -> ReportResponse;
    fn create_agent_run(&self, task_id: &str) -> AgentRun;
    fn agent_run(&self, run_id: &str) -> Option<AgentRun>;
    fn update_agent_run_status(&self, run_id: &str, status: AgentRunStatus);
    fn append_agent_run_event(&self, event: AgentRunEvent);
    fn agent_run_events(&self, run_id: &str) -> Vec<AgentRunEvent>;
}

#[derive(Debug, Default)]
pub struct InMemoryLearningRepository {
    current_task: Option<CurrentTaskResponse>,
    generation_jobs: RefCell<HashMap<String, GenerationJobResponse>>,
    question_sets: RefCell<HashMap<String, QuestionSetResponse>>,
    agent_runs: RefCell<HashMap<String, AgentRun>>,
    agent_run_events: RefCell<HashMap<String, Vec<AgentRunEvent>>>,
}

impl InMemoryLearningRepository {
    pub fn empty() -> Self {
        Self::default()
    }

    pub fn with_fixture_data() -> Self {
        let repository = Self {
            current_task: Some(fixtures::current_task()),
            ..Self::default()
        };

        repository.generation_jobs.borrow_mut().insert(
            fixtures::FIXTURE_JOB_ID.to_string(),
            fixtures::generation_job(),
        );
        repository.question_sets.borrow_mut().insert(
            fixtures::FIXTURE_QUESTION_SET_ID.to_string(),
            fixtures::question_set(),
        );

        repository
    }
}

impl LearningRepository for InMemoryLearningRepository {
    fn current_task(&self) -> Option<CurrentTaskResponse> {
        self.current_task.clone()
    }

    fn generation_job(&self, job_id: &str) -> Option<GenerationJobResponse> {
        self.generation_jobs.borrow().get(job_id).cloned()
    }

    fn question_set(&self, question_set_id: &str) -> Option<QuestionSetResponse> {
        self.question_sets.borrow().get(question_set_id).cloned()
    }

    fn mistakes(&self) -> MistakesResponse {
        fixtures::mistakes()
    }

    fn knowledge_search(&self, query: String) -> KnowledgeSearchResponse {
        fixtures::knowledge_search(query)
    }

    fn current_report(&self) -> ReportResponse {
        fixtures::report()
    }

    fn create_agent_run(&self, task_id: &str) -> AgentRun {
        let sequence = self.agent_runs.borrow().len() + 1;
        let run = AgentRun::new_pending(format!("run_memory_{sequence:04}"), task_id.to_string());

        self.agent_runs
            .borrow_mut()
            .insert(run.id.clone(), run.clone());

        run
    }

    fn agent_run(&self, run_id: &str) -> Option<AgentRun> {
        self.agent_runs.borrow().get(run_id).cloned()
    }

    fn update_agent_run_status(&self, run_id: &str, status: AgentRunStatus) {
        if let Some(run) = self.agent_runs.borrow_mut().get_mut(run_id) {
            run.status = status;
            run.updated_at = "2026-05-14T16:00:08+08:00".to_string();
        }
    }

    fn append_agent_run_event(&self, event: AgentRunEvent) {
        self.agent_run_events
            .borrow_mut()
            .entry(event.agent_run_id.clone())
            .or_default()
            .push(event);
    }

    fn agent_run_events(&self, run_id: &str) -> Vec<AgentRunEvent> {
        let mut events = self
            .agent_run_events
            .borrow()
            .get(run_id)
            .cloned()
            .unwrap_or_default();

        events.sort_by_key(|event| event.sequence);
        events
    }
}

#[derive(Debug, Clone)]
pub struct PostgresLearningRepository {
    pool: PgPool,
}

impl PostgresLearningRepository {
    pub async fn connect(config: &DatabaseConfig) -> Result<Self, sqlx::Error> {
        let pool = PgPoolOptions::new()
            .max_connections(5)
            .connect(&config.database_url)
            .await?;

        Ok(Self { pool })
    }

    pub async fn run_migrations(&self) -> Result<(), sqlx::Error> {
        sqlx::migrate!("./migrations").run(&self.pool).await?;
        Ok(())
    }

    pub async fn create_agent_run(&self, task_id: &str) -> Result<AgentRun, sqlx::Error> {
        let run = AgentRun::new_pending(next_run_id(), task_id.to_string());

        sqlx::query(
            r#"
            INSERT INTO agent_runs (id, task_id, status, current_step, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            "#,
        )
        .bind(&run.id)
        .bind(&run.task_id)
        .bind(agent_run_status_to_db(&run.status))
        .bind(&run.current_step)
        .bind(&run.created_at)
        .bind(&run.updated_at)
        .execute(&self.pool)
        .await?;

        Ok(run)
    }

    pub async fn agent_run(&self, run_id: &str) -> Result<Option<AgentRun>, sqlx::Error> {
        let row = sqlx::query(
            r#"
            SELECT id, task_id, status, current_step, created_at, updated_at
            FROM agent_runs
            WHERE id = $1
            "#,
        )
        .bind(run_id)
        .fetch_optional(&self.pool)
        .await?;

        Ok(row.map(|row| AgentRun {
            id: row.get("id"),
            task_id: row.get("task_id"),
            status: agent_run_status_from_db(row.get::<String, _>("status").as_str()),
            current_step: row.get("current_step"),
            created_at: row.get("created_at"),
            updated_at: row.get("updated_at"),
        }))
    }

    pub async fn update_agent_run_status(
        &self,
        run_id: &str,
        status: AgentRunStatus,
    ) -> Result<(), sqlx::Error> {
        sqlx::query(
            r#"
            UPDATE agent_runs
            SET status = $2, updated_at = $3
            WHERE id = $1
            "#,
        )
        .bind(run_id)
        .bind(agent_run_status_to_db(&status))
        .bind("2026-05-14T16:00:08+08:00")
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    pub async fn append_agent_run_event(&self, event: AgentRunEvent) -> Result<(), sqlx::Error> {
        sqlx::query(
            r#"
            INSERT INTO agent_run_events (id, agent_run_id, sequence, kind, payload, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (agent_run_id, sequence) DO NOTHING
            "#,
        )
        .bind(&event.id)
        .bind(&event.agent_run_id)
        .bind(event.sequence as i64)
        .bind(agent_run_event_kind_to_db(&event.kind))
        .bind(event.payload)
        .bind(&event.created_at)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    pub async fn agent_run_events(&self, run_id: &str) -> Result<Vec<AgentRunEvent>, sqlx::Error> {
        let rows = sqlx::query(
            r#"
            SELECT id, agent_run_id, sequence, kind, payload, created_at
            FROM agent_run_events
            WHERE agent_run_id = $1
            ORDER BY sequence ASC
            "#,
        )
        .bind(run_id)
        .fetch_all(&self.pool)
        .await?;

        Ok(rows
            .into_iter()
            .map(|row| AgentRunEvent {
                id: row.get("id"),
                agent_run_id: row.get("agent_run_id"),
                sequence: row.get::<i64, _>("sequence") as u64,
                kind: agent_run_event_kind_from_db(row.get::<String, _>("kind").as_str()),
                payload: row.get("payload"),
                created_at: row.get("created_at"),
            })
            .collect())
    }
}

fn next_run_id() -> String {
    format!("run_postgres_{}", uuid::Uuid::now_v7())
}

fn agent_run_status_to_db(status: &AgentRunStatus) -> &'static str {
    match status {
        AgentRunStatus::Pending => "pending",
        AgentRunStatus::Running => "running",
        AgentRunStatus::WaitingUser => "waiting_user",
        AgentRunStatus::WaitingTool => "waiting_tool",
        AgentRunStatus::Retrying => "retrying",
        AgentRunStatus::Failed => "failed",
        AgentRunStatus::Completed => "completed",
        AgentRunStatus::Cancelled => "cancelled",
    }
}

fn agent_run_status_from_db(status: &str) -> AgentRunStatus {
    match status {
        "running" => AgentRunStatus::Running,
        "waiting_user" => AgentRunStatus::WaitingUser,
        "waiting_tool" => AgentRunStatus::WaitingTool,
        "retrying" => AgentRunStatus::Retrying,
        "failed" => AgentRunStatus::Failed,
        "completed" => AgentRunStatus::Completed,
        "cancelled" => AgentRunStatus::Cancelled,
        _ => AgentRunStatus::Pending,
    }
}

fn agent_run_event_kind_to_db(kind: &AgentRunEventKind) -> &'static str {
    match kind {
        AgentRunEventKind::GenerationJobCreated => "generation_job_created",
        AgentRunEventKind::QuestionSetReady => "question_set_ready",
        AgentRunEventKind::ToolCallStarted => "tool_call_started",
        AgentRunEventKind::ToolCallCompleted => "tool_call_completed",
        AgentRunEventKind::EvaluationCompleted => "evaluation_completed",
    }
}

fn agent_run_event_kind_from_db(kind: &str) -> AgentRunEventKind {
    match kind {
        "question_set_ready" => AgentRunEventKind::QuestionSetReady,
        "tool_call_started" => AgentRunEventKind::ToolCallStarted,
        "tool_call_completed" => AgentRunEventKind::ToolCallCompleted,
        "evaluation_completed" => AgentRunEventKind::EvaluationCompleted,
        _ => AgentRunEventKind::GenerationJobCreated,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn phase0_persistence_is_not_configured_yet() {
        let info = PersistenceInfo::phase0();

        assert_eq!(info.database_backend, "not_configured_yet");
    }
}
