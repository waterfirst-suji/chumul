use crate::llm::{LLMClient, Message};
use crate::retrieval::{simple_embedding, RetrievalResult, VectorStore};
use anyhow::Result;
use std::sync::Arc;
use tokio::sync::RwLock;

/// RIG 생성 단계
#[derive(Debug, Clone)]
pub struct GenerationStep {
    pub step_number: usize,
    pub partial_response: String,
    pub retrieved_docs: Vec<RetrievalResult>,
    pub needs_retrieval: bool,
}

/// RIG 엔진 설정
#[derive(Debug, Clone)]
pub struct RIGConfig {
    /// 검색을 트리거하는 토큰 수
    pub retrieval_trigger_tokens: usize,
    /// 최대 검색 횟수
    pub max_retrievals: usize,
    /// 검색할 문서 개수
    pub top_k: usize,
    /// 최대 생성 단계
    pub max_steps: usize,
}

impl Default for RIGConfig {
    fn default() -> Self {
        Self {
            retrieval_trigger_tokens: 50,
            max_retrievals: 3,
            top_k: 3,
            max_steps: 10,
        }
    }
}

/// RIG 엔진
pub struct RIGEngine<V: VectorStore, L: LLMClient> {
    vector_store: Arc<RwLock<V>>,
    llm_client: Arc<L>,
    config: RIGConfig,
}

impl<V: VectorStore, L: LLMClient> RIGEngine<V, L> {
    pub fn new(vector_store: V, llm_client: L, config: RIGConfig) -> Self {
        Self {
            vector_store: Arc::new(RwLock::new(vector_store)),
            llm_client: Arc::new(llm_client),
            config,
        }
    }

    /// 검색이 필요한지 판단하는 휴리스틱
    fn should_retrieve(&self, current_response: &str, step: usize) -> bool {
        // 간단한 휴리스틱: 일정 토큰마다 검색
        let token_count = current_response.split_whitespace().count();
        token_count >= self.config.retrieval_trigger_tokens * (step + 1)
            && step < self.config.max_retrievals
    }

    /// 현재 응답에서 검색 쿼리 추출
    fn extract_query(&self, current_response: &str) -> String {
        // 간단한 휴리스틱: 마지막 문장을 쿼리로 사용
        current_response
            .split('.')
            .filter(|s| !s.trim().is_empty())
            .last()
            .unwrap_or(current_response)
            .trim()
            .to_string()
    }

    /// RIG 생성 실행
    pub async fn generate(&self, query: &str) -> Result<Vec<GenerationStep>> {
        let mut steps = Vec::new();
        let mut messages = vec![Message {
            role: "user".to_string(),
            content: query.to_string(),
        }];

        let mut retrieval_count = 0;
        let mut accumulated_response = String::new();

        for step in 0..self.config.max_steps {
            // LLM으로부터 응답 생성
            let response = self.llm_client.generate(messages.clone()).await?;
            accumulated_response.push_str(&response);
            accumulated_response.push(' ');

            // 검색이 필요한지 판단
            let needs_retrieval = self.should_retrieve(&accumulated_response, retrieval_count);

            let mut retrieved_docs = Vec::new();

            if needs_retrieval && retrieval_count < self.config.max_retrievals {
                // 검색 쿼리 추출
                let search_query = self.extract_query(&accumulated_response);

                // 검색 수행
                let query_embedding = simple_embedding(&search_query);
                let store = self.vector_store.read().await;
                retrieved_docs = store.search(query_embedding, self.config.top_k);
                drop(store);

                // 검색 결과를 메시지에 추가
                if !retrieved_docs.is_empty() {
                    let context = retrieved_docs
                        .iter()
                        .map(|r| format!("[관련 문서] {}", r.document.content))
                        .collect::<Vec<_>>()
                        .join("\n");

                    messages.push(Message {
                        role: "system".to_string(),
                        content: format!(
                            "다음 정보를 참고하여 답변을 계속하세요:\n{}",
                            context
                        ),
                    });

                    retrieval_count += 1;
                }
            }

            // 단계 기록
            steps.push(GenerationStep {
                step_number: step,
                partial_response: accumulated_response.clone(),
                retrieved_docs: retrieved_docs.clone(),
                needs_retrieval,
            });

            // 검색이 더 이상 필요 없으면 종료
            if !needs_retrieval || retrieval_count >= self.config.max_retrievals {
                break;
            }

            // 다음 단계를 위해 응답을 메시지에 추가
            messages.push(Message {
                role: "assistant".to_string(),
                content: response,
            });
        }

        Ok(steps)
    }

    /// 최종 응답 가져오기
    pub async fn generate_final(&self, query: &str) -> Result<String> {
        let steps = self.generate(query).await?;
        Ok(steps
            .last()
            .map(|s| s.partial_response.clone())
            .unwrap_or_default())
    }
}

/// RIG 엔진 빌더
pub struct RIGEngineBuilder<V: VectorStore, L: LLMClient> {
    vector_store: Option<V>,
    llm_client: Option<L>,
    config: RIGConfig,
}

impl<V: VectorStore, L: LLMClient> RIGEngineBuilder<V, L> {
    pub fn new() -> Self {
        Self {
            vector_store: None,
            llm_client: None,
            config: RIGConfig::default(),
        }
    }

    pub fn vector_store(mut self, store: V) -> Self {
        self.vector_store = Some(store);
        self
    }

    pub fn llm_client(mut self, client: L) -> Self {
        self.llm_client = Some(client);
        self
    }

    pub fn config(mut self, config: RIGConfig) -> Self {
        self.config = config;
        self
    }

    pub fn build(self) -> Result<RIGEngine<V, L>> {
        let vector_store = self
            .vector_store
            .ok_or_else(|| anyhow::anyhow!("Vector store not set"))?;
        let llm_client = self
            .llm_client
            .ok_or_else(|| anyhow::anyhow!("LLM client not set"))?;

        Ok(RIGEngine::new(vector_store, llm_client, self.config))
    }
}

impl<V: VectorStore, L: LLMClient> Default for RIGEngineBuilder<V, L> {
    fn default() -> Self {
        Self::new()
    }
}
