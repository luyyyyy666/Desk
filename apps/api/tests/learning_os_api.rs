use axum::{
    body::{Body, to_bytes},
    http::{Request, StatusCode, header},
};
use serde_json::{Value, json};
use tower::ServiceExt;

async fn request_json(method: &str, uri: &str, body: Option<Value>) -> (StatusCode, Value) {
    let mut builder = Request::builder().method(method).uri(uri);
    if body.is_some() {
        builder = builder.header(header::CONTENT_TYPE, "application/json");
    }

    let request = builder
        .body(match body {
            Some(value) => Body::from(value.to_string()),
            None => Body::empty(),
        })
        .unwrap();

    let response = my_sifu_api::app().oneshot(request).await.unwrap();
    let status = response.status();
    let body = to_bytes(response.into_body(), usize::MAX).await.unwrap();

    (status, serde_json::from_slice(&body).unwrap())
}

#[tokio::test]
async fn current_task_matches_learning_os_fixture_contract() {
    let (status, body) = request_json("GET", "/api/tasks/current", None).await;

    assert_eq!(status, StatusCode::OK);
    assert_eq!(body["task"]["title"], "一次函数专项训练");
    assert_eq!(body["task"]["questionCount"], 12);
    assert_eq!(body["learningLoop"].as_array().unwrap().len(), 7);
    assert_eq!(body["desktopShortcuts"].as_array().unwrap().len(), 8);
}

#[tokio::test]
async fn generation_job_lifecycle_is_fixture_backed() {
    let (created_status, created_body) = request_json(
        "POST",
        "/api/generation-jobs",
        Some(json!({
            "learningGoal": "巩固一次函数图像、解析式与实际应用题",
            "subject": "八年级数学",
            "questionCount": 12
        })),
    )
    .await;

    assert_eq!(created_status, StatusCode::CREATED);
    assert_eq!(created_body["job"]["id"], "job_fixture_linear_function_001");
    assert_eq!(created_body["job"]["status"], "completed");

    let (read_status, read_body) = request_json(
        "GET",
        "/api/generation-jobs/job_fixture_linear_function_001",
        None,
    )
    .await;

    assert_eq!(read_status, StatusCode::OK);
    assert_eq!(
        read_body["job"]["questionSetId"],
        "qs_fixture_linear_function_001"
    );
}

#[tokio::test]
async fn reads_question_set_mistakes_knowledge_and_report() {
    let (question_status, question_body) =
        request_json("GET", "/api/questions/qs_fixture_linear_function_001", None).await;
    assert_eq!(question_status, StatusCode::OK);
    assert_eq!(question_body["questions"].as_array().unwrap().len(), 4);

    let (mistake_status, mistake_body) = request_json("GET", "/api/mistakes", None).await;
    assert_eq!(mistake_status, StatusCode::OK);
    assert_eq!(mistake_body["groups"].as_array().unwrap().len(), 2);

    let (knowledge_status, knowledge_body) =
        request_json("GET", "/api/knowledge/search?query=一次函数", None).await;
    assert_eq!(knowledge_status, StatusCode::OK);
    assert_eq!(knowledge_body["results"].as_array().unwrap().len(), 4);

    let (report_status, report_body) = request_json("GET", "/api/reports/current", None).await;
    assert_eq!(report_status, StatusCode::OK);
    assert_eq!(report_body["metrics"].as_array().unwrap().len(), 4);
}

#[tokio::test]
async fn generation_events_expose_future_stream_shape() {
    let request = Request::builder()
        .uri("/api/generation-jobs/job_fixture_linear_function_001/events")
        .body(Body::empty())
        .unwrap();

    let response = my_sifu_api::app().oneshot(request).await.unwrap();
    assert_eq!(response.status(), StatusCode::OK);
    assert_eq!(
        response.headers()[header::CONTENT_TYPE],
        "text/event-stream; charset=utf-8"
    );

    let body = to_bytes(response.into_body(), usize::MAX).await.unwrap();
    let text = String::from_utf8(body.to_vec()).unwrap();
    assert!(text.contains("event: job.completed"));
    assert!(text.contains("question_set_id"));
}

#[tokio::test]
async fn unknown_question_set_returns_frontend_facing_error() {
    let (status, body) = request_json("GET", "/api/questions/missing", None).await;

    assert_eq!(status, StatusCode::NOT_FOUND);
    assert_eq!(body["error"]["code"], "not_found");
    assert_eq!(body["error"]["message"], "question set not found");
}

#[tokio::test]
async fn model_gateway_status_exposes_only_non_sensitive_config() {
    let (status, body) = request_json("GET", "/api/model-gateway/status", None).await;

    assert_eq!(status, StatusCode::OK);
    assert_eq!(body["provider"], "new-api");
    assert_eq!(body["baseUrl"], "http://127.0.0.1:3000");
    assert_eq!(body["defaultModel"], "gpt-4o-mini");
    assert_eq!(body["apiKeyConfigured"], false);
    assert_eq!(body["apiKeyHint"], "missing");
}
