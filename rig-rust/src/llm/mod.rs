use anyhow::{anyhow, Result};
use async_trait::async_trait;
use serde::{Deserialize, Serialize};
use std::env;

/// LLM 메시지
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub role: String,
    pub content: String,
}

/// LLM 생성 응답
#[derive(Debug, Clone)]
pub struct GenerationResponse {
    pub content: String,
    pub finished: bool,
}

/// LLM 클라이언트 트레이트
#[async_trait]
pub trait LLMClient: Send + Sync {
    async fn generate(&self, messages: Vec<Message>) -> Result<String>;
    async fn generate_stream(&self, messages: Vec<Message>) -> Result<Vec<String>>;
}

/// OpenAI API 요청 구조체
#[derive(Debug, Serialize)]
struct OpenAIRequest {
    model: String,
    messages: Vec<Message>,
    temperature: f32,
    max_tokens: Option<u32>,
    stream: bool,
}

/// OpenAI API 응답 구조체
#[derive(Debug, Deserialize)]
struct OpenAIResponse {
    choices: Vec<Choice>,
}

#[derive(Debug, Deserialize)]
struct Choice {
    message: Message,
}

/// OpenAI 클라이언트 구현
pub struct OpenAIClient {
    api_key: String,
    model: String,
    client: reqwest::Client,
}

impl OpenAIClient {
    pub fn new(model: Option<String>) -> Result<Self> {
        let api_key = env::var("OPENAI_API_KEY")
            .map_err(|_| anyhow!("OPENAI_API_KEY environment variable not set"))?;

        Ok(Self {
            api_key,
            model: model.unwrap_or_else(|| "gpt-4".to_string()),
            client: reqwest::Client::new(),
        })
    }

    pub fn with_api_key(api_key: String, model: Option<String>) -> Self {
        Self {
            api_key,
            model: model.unwrap_or_else(|| "gpt-4".to_string()),
            client: reqwest::Client::new(),
        }
    }
}

#[async_trait]
impl LLMClient for OpenAIClient {
    async fn generate(&self, messages: Vec<Message>) -> Result<String> {
        let request_body = OpenAIRequest {
            model: self.model.clone(),
            messages,
            temperature: 0.7,
            max_tokens: Some(2000),
            stream: false,
        };

        let response = self
            .client
            .post("https://api.openai.com/v1/chat/completions")
            .header("Authorization", format!("Bearer {}", self.api_key))
            .header("Content-Type", "application/json")
            .json(&request_body)
            .send()
            .await?;

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await?;
            return Err(anyhow!("OpenAI API error {}: {}", status, error_text));
        }

        let openai_response: OpenAIResponse = response.json().await?;

        openai_response
            .choices
            .first()
            .map(|choice| choice.message.content.clone())
            .ok_or_else(|| anyhow!("No response from OpenAI"))
    }

    async fn generate_stream(&self, messages: Vec<Message>) -> Result<Vec<String>> {
        // 간단한 청킹 시뮬레이션 (실제 스트리밍은 더 복잡)
        let full_response = self.generate(messages).await?;

        // 응답을 단어 단위로 분할하여 스트리밍 시뮬레이션
        let chunks: Vec<String> = full_response
            .split_whitespace()
            .map(|s| s.to_string())
            .collect();

        Ok(chunks)
    }
}

/// 목(Mock) LLM 클라이언트 (테스트용)
pub struct MockLLMClient {
    response: String,
}

impl MockLLMClient {
    pub fn new(response: String) -> Self {
        Self { response }
    }
}

#[async_trait]
impl LLMClient for MockLLMClient {
    async fn generate(&self, _messages: Vec<Message>) -> Result<String> {
        Ok(self.response.clone())
    }

    async fn generate_stream(&self, _messages: Vec<Message>) -> Result<Vec<String>> {
        Ok(self.response.split_whitespace().map(|s| s.to_string()).collect())
    }
}
