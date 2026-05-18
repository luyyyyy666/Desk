use serde::{Deserialize, Serialize};
use serde_json::{Value, json};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ModelGatewayConfig {
    pub provider: String,
    pub base_url: String,
    pub api_key: Option<String>,
    pub default_model: String,
}

impl ModelGatewayConfig {
    pub fn from_env() -> Self {
        Self::from_env_with(|key| std::env::var(key).ok())
    }

    pub fn from_env_with<F>(read_env: F) -> Self
    where
        F: Fn(&str) -> Option<String>,
    {
        let provider = read_env("MY_SIFU_LLM_GATEWAY_PROVIDER")
            .filter(|value| !value.trim().is_empty())
            .unwrap_or_else(|| "new-api".to_string());
        let base_url = read_env("MY_SIFU_LLM_GATEWAY_BASE_URL")
            .filter(|value| !value.trim().is_empty())
            .unwrap_or_else(|| "http://127.0.0.1:3000".to_string())
            .trim_end_matches('/')
            .to_string();
        let api_key =
            read_env("MY_SIFU_LLM_GATEWAY_API_KEY").filter(|value| !value.trim().is_empty());
        let default_model = read_env("MY_SIFU_DEFAULT_MODEL")
            .filter(|value| !value.trim().is_empty())
            .unwrap_or_else(|| "gpt-4o-mini".to_string());

        Self {
            provider,
            base_url,
            api_key,
            default_model,
        }
    }

    pub fn chat_completions_url(&self) -> String {
        format!("{}/v1/chat/completions", self.base_url)
    }

    pub fn public_status(&self) -> ModelGatewayPublicStatus {
        let api_key_configured = self.api_key.is_some();

        ModelGatewayPublicStatus {
            provider: self.provider.clone(),
            base_url: self.base_url.clone(),
            default_model: self.default_model.clone(),
            api_key_configured,
            api_key_hint: if api_key_configured {
                "configured".to_string()
            } else {
                "missing".to_string()
            },
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct ModelGatewayPublicStatus {
    pub provider: String,
    pub base_url: String,
    pub default_model: String,
    pub api_key_configured: bool,
    pub api_key_hint: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ChatCompletionRequest {
    pub messages: Vec<ChatCompletionMessage>,
    pub temperature: Option<f64>,
    pub stream: bool,
    pub model: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ChatCompletionMessage {
    pub role: String,
    pub content: String,
}

impl ChatCompletionMessage {
    pub fn system(content: impl Into<String>) -> Self {
        Self {
            role: "system".to_string(),
            content: content.into(),
        }
    }

    pub fn user(content: impl Into<String>) -> Self {
        Self {
            role: "user".to_string(),
            content: content.into(),
        }
    }

    pub fn assistant(content: impl Into<String>) -> Self {
        Self {
            role: "assistant".to_string(),
            content: content.into(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct NewApiChatRequestBuilder {
    config: ModelGatewayConfig,
}

impl NewApiChatRequestBuilder {
    pub fn new(config: ModelGatewayConfig) -> Self {
        Self { config }
    }

    pub fn build_json(&self, request: ChatCompletionRequest) -> Value {
        let model = request
            .model
            .unwrap_or_else(|| self.config.default_model.clone());

        json!({
            "model": model,
            "messages": request.messages,
            "temperature": request.temperature,
            "stream": request.stream
        })
    }
}
