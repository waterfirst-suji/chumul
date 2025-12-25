use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// 문서를 나타내는 구조체
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Document {
    pub id: String,
    pub content: String,
    pub metadata: HashMap<String, String>,
}

/// 간단한 임베딩 표현 (실제로는 더 정교한 벡터를 사용)
pub type Embedding = Vec<f32>;

/// 문서 검색 결과
#[derive(Debug, Clone)]
pub struct RetrievalResult {
    pub document: Document,
    pub score: f32,
}

/// 벡터 스토어 트레이트
pub trait VectorStore: Send + Sync {
    fn add_document(&mut self, doc: Document, embedding: Embedding);
    fn search(&self, query_embedding: Embedding, top_k: usize) -> Vec<RetrievalResult>;
}

/// 간단한 인메모리 벡터 스토어 구현
#[derive(Clone)]
pub struct InMemoryVectorStore {
    documents: Vec<Document>,
    embeddings: Vec<Embedding>,
}

impl InMemoryVectorStore {
    pub fn new() -> Self {
        Self {
            documents: Vec::new(),
            embeddings: Vec::new(),
        }
    }

    /// 코사인 유사도 계산
    fn cosine_similarity(a: &[f32], b: &[f32]) -> f32 {
        let dot_product: f32 = a.iter().zip(b.iter()).map(|(x, y)| x * y).sum();
        let norm_a: f32 = a.iter().map(|x| x * x).sum::<f32>().sqrt();
        let norm_b: f32 = b.iter().map(|x| x * x).sum::<f32>().sqrt();

        if norm_a == 0.0 || norm_b == 0.0 {
            0.0
        } else {
            dot_product / (norm_a * norm_b)
        }
    }
}

impl VectorStore for InMemoryVectorStore {
    fn add_document(&mut self, doc: Document, embedding: Embedding) {
        self.documents.push(doc);
        self.embeddings.push(embedding);
    }

    fn search(&self, query_embedding: Embedding, top_k: usize) -> Vec<RetrievalResult> {
        let mut results: Vec<(usize, f32)> = self
            .embeddings
            .iter()
            .enumerate()
            .map(|(idx, emb)| {
                let score = Self::cosine_similarity(&query_embedding, emb);
                (idx, score)
            })
            .collect();

        // 점수 순으로 정렬
        results.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());

        // 상위 k개 반환
        results
            .into_iter()
            .take(top_k)
            .map(|(idx, score)| RetrievalResult {
                document: self.documents[idx].clone(),
                score,
            })
            .collect()
    }
}

impl Default for InMemoryVectorStore {
    fn default() -> Self {
        Self::new()
    }
}

/// 간단한 임베딩 생성기 (실제로는 모델 사용)
pub fn simple_embedding(text: &str) -> Embedding {
    // 간단한 해시 기반 임베딩 (실제 구현에서는 BERT 등 사용)
    let mut embedding = vec![0.0; 384];
    for (i, c) in text.chars().enumerate() {
        let idx = (c as usize + i) % 384;
        embedding[idx] += 1.0;
    }

    // 정규화
    let norm: f32 = embedding.iter().map(|x| x * x).sum::<f32>().sqrt();
    if norm > 0.0 {
        embedding.iter_mut().for_each(|x| *x /= norm);
    }

    embedding
}
