use model_gateway::{
    ChatCompletionMessage, ChatCompletionRequest, ModelGatewayConfig, NewApiChatRequestBuilder,
};

#[test]
fn new_api_config_defaults_to_local_gateway_without_exposing_secret() {
    let config = ModelGatewayConfig::from_env_with(|key| match key {
        "MY_SIFU_LLM_GATEWAY_API_KEY" => Some("secret-key".to_string()),
        _ => None,
    });

    assert_eq!(config.provider, "new-api");
    assert_eq!(config.base_url, "http://127.0.0.1:3000");
    assert_eq!(config.default_model, "gpt-4o-mini");
    assert_eq!(
        config.chat_completions_url(),
        "http://127.0.0.1:3000/v1/chat/completions"
    );
    assert!(config.public_status().api_key_configured);
    assert_eq!(config.public_status().api_key_hint, "configured");
}

#[test]
fn new_api_config_honors_environment_overrides() {
    let config = ModelGatewayConfig::from_env_with(|key| match key {
        "MY_SIFU_LLM_GATEWAY_PROVIDER" => Some("new-api".to_string()),
        "MY_SIFU_LLM_GATEWAY_BASE_URL" => Some("http://127.0.0.1:3002/custom/".to_string()),
        "MY_SIFU_LLM_GATEWAY_API_KEY" => Some("sk-test".to_string()),
        "MY_SIFU_DEFAULT_MODEL" => Some("deepseek-chat".to_string()),
        _ => None,
    });

    assert_eq!(config.base_url, "http://127.0.0.1:3002/custom");
    assert_eq!(
        config.chat_completions_url(),
        "http://127.0.0.1:3002/custom/v1/chat/completions"
    );
    assert_eq!(config.default_model, "deepseek-chat");
}

#[test]
fn chat_request_builder_emits_openai_compatible_json_for_new_api() {
    let config = ModelGatewayConfig::from_env_with(|key| match key {
        "MY_SIFU_DEFAULT_MODEL" => Some("qwen-plus".to_string()),
        _ => None,
    });
    let request = ChatCompletionRequest {
        messages: vec![
            ChatCompletionMessage::system("你是我的师傅教育 Agent。"),
            ChatCompletionMessage::user("生成 3 道一次函数基础题。"),
        ],
        temperature: Some(0.3),
        stream: true,
        model: None,
    };

    let value = NewApiChatRequestBuilder::new(config).build_json(request);

    assert_eq!(value["model"], "qwen-plus");
    assert_eq!(value["stream"], true);
    assert_eq!(value["temperature"], 0.3);
    assert_eq!(value["messages"][0]["role"], "system");
    assert_eq!(value["messages"][1]["content"], "生成 3 道一次函数基础题。");
}
