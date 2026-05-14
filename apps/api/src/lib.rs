use agent_core::RuntimeInfo;
use axum::{
    Json, Router,
    extract::{Path, Query},
    http::{StatusCode, header},
    response::{IntoResponse, Response},
    routing::{get, post},
};
use domain::{
    ApiErrorBody, ApiErrorEnvelope, CreateGenerationJobRequest, GenerationJobResponse,
    HealthResponse, KnowledgeSearchResponse, fixtures,
};
use serde::Deserialize;
use tool_runtime::ToolRegistryInfo;

pub fn app() -> Router {
    Router::new()
        .route("/health", get(health))
        .route("/api/tasks/current", get(current_task))
        .route("/api/generation-jobs", post(create_generation_job))
        .route("/api/generation-jobs/{job_id}", get(generation_job))
        .route(
            "/api/generation-jobs/{job_id}/events",
            get(generation_events),
        )
        .route("/api/questions/{question_set_id}", get(question_set))
        .route("/api/mistakes", get(mistakes))
        .route("/api/knowledge/search", get(search_knowledge))
        .route("/api/reports/current", get(current_report))
}

pub async fn health() -> Json<HealthResponse> {
    Json(HealthResponse {
        service: "my-sifu-api",
        status: "ok",
        runtime: RuntimeInfo::phase0().name,
        tool_registry: ToolRegistryInfo::phase0().status,
    })
}

async fn current_task() -> Json<domain::CurrentTaskResponse> {
    Json(fixtures::current_task())
}

async fn create_generation_job(
    Json(request): Json<CreateGenerationJobRequest>,
) -> Result<(StatusCode, Json<GenerationJobResponse>), ApiError> {
    if request.learning_goal.trim().is_empty()
        || request.subject.trim().is_empty()
        || request.question_count == 0
    {
        return Err(ApiError::bad_request("invalid generation job request"));
    }

    Ok((StatusCode::CREATED, Json(fixtures::generation_job())))
}

async fn generation_job(
    Path(job_id): Path<String>,
) -> Result<Json<GenerationJobResponse>, ApiError> {
    if job_id != fixtures::FIXTURE_JOB_ID {
        return Err(ApiError::not_found("generation job not found"));
    }

    Ok(Json(fixtures::generation_job()))
}

async fn generation_events(Path(job_id): Path<String>) -> Result<Response, ApiError> {
    if job_id != fixtures::FIXTURE_JOB_ID {
        return Err(ApiError::not_found("generation job not found"));
    }

    let event = serde_json::json!({
        "job_id": fixtures::FIXTURE_JOB_ID,
        "question_set_id": fixtures::FIXTURE_QUESTION_SET_ID,
        "status": "completed",
        "progress": 100
    });
    let body = format!("event: job.completed\ndata: {event}\n\n");

    Ok((
        StatusCode::OK,
        [(header::CONTENT_TYPE, "text/event-stream; charset=utf-8")],
        body,
    )
        .into_response())
}

async fn question_set(
    Path(question_set_id): Path<String>,
) -> Result<Json<domain::QuestionSetResponse>, ApiError> {
    if question_set_id != fixtures::FIXTURE_QUESTION_SET_ID {
        return Err(ApiError::not_found("question set not found"));
    }

    Ok(Json(fixtures::question_set()))
}

async fn mistakes() -> Json<domain::MistakesResponse> {
    Json(fixtures::mistakes())
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct KnowledgeSearchQuery {
    query: Option<String>,
}

async fn search_knowledge(
    Query(query): Query<KnowledgeSearchQuery>,
) -> Json<KnowledgeSearchResponse> {
    Json(fixtures::knowledge_search(
        query.query.unwrap_or_else(|| "一次函数".to_string()),
    ))
}

async fn current_report() -> Json<domain::ReportResponse> {
    Json(fixtures::report())
}

#[derive(Debug, Clone)]
struct ApiError {
    status: StatusCode,
    code: &'static str,
    message: &'static str,
}

impl ApiError {
    fn bad_request(message: &'static str) -> Self {
        Self {
            status: StatusCode::BAD_REQUEST,
            code: "bad_request",
            message,
        }
    }

    fn not_found(message: &'static str) -> Self {
        Self {
            status: StatusCode::NOT_FOUND,
            code: "not_found",
            message,
        }
    }
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let body = Json(ApiErrorEnvelope {
            error: ApiErrorBody {
                code: self.code,
                message: self.message,
            },
        });

        (self.status, body).into_response()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn health_returns_phase0_contract() {
        let Json(response) = health().await;

        assert_eq!(response.service, "my-sifu-api");
        assert_eq!(response.status, "ok");
        assert_eq!(response.runtime, "phase0-runtime-foundation");
        assert_eq!(response.tool_registry, "not_registered_yet");
    }

    #[tokio::test]
    async fn create_generation_job_rejects_empty_goal() {
        let request = CreateGenerationJobRequest {
            learning_goal: " ".to_string(),
            subject: "八年级数学".to_string(),
            question_count: 12,
        };

        let error = create_generation_job(Json(request)).await.unwrap_err();

        assert_eq!(error.status, StatusCode::BAD_REQUEST);
        assert_eq!(error.code, "bad_request");
    }
}
