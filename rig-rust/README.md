# 🧐 RIG (Retrieval Interleaved Generation) - Rust Implementation

Rust로 구현한 고성능 RIG (Retrieval Interleaved Generation) 시스템

## 📖 RIG란?

**RIG (Retrieval Interleaved Generation)**는 AI가 답변을 생성하는 도중에 필요한 정보를 실시간으로 검색(Retrieval)해서 끼워 넣는(Interleaved) 기법입니다.

### 🔄 기존 방식 (RAG) vs RIG

#### RAG (Retrieval Augmented Generation)
```
질문 입력 → 관련 문서 검색 → 그 문서를 바탕으로 답변 생성
```
👉 초반에 가져온 정보가 부족하면, 끝까지 잘못된 방향으로 갈 수 있음

#### ✨ RIG (Retrieval Interleaved Generation)
```
질문 입력 → 답변 조금 생성 → 검색 → 다시 생성 → 검색 → ... (반복)
```
👉 사람처럼 "쓰다가 → 찾아보고 → 다시 쓰는" 흐름

## 💙 RIG의 중요성

- ✓ **더 정확한 답변**: 생성 중 필요한 정보를 동적으로 검색
- ✓ **긴 추론·복잡한 질문에 강함**: 단계적으로 정보를 보강
- ✓ **최신 정보 반영에 유리**: 필요한 시점에 검색 수행
- ✓ **환각(Hallucination) 감소**: 사실 기반 정보 검색으로 검증

## 🏗️ 아키텍처

이 프로젝트는 다음 핵심 컴포넌트로 구성됩니다:

```
rig-rust/
├── src/
│   ├── retrieval/      # 문서 검색 시스템
│   │   └── mod.rs      # Vector Store, 코사인 유사도 검색
│   ├── llm/            # LLM 인터페이스
│   │   └── mod.rs      # OpenAI API 클라이언트
│   ├── engine/         # RIG 엔진
│   │   └── mod.rs      # 생성 중 검색 오케스트레이션
│   └── main.rs         # 데모 애플리케이션
├── Cargo.toml
└── README.md
```

### 핵심 모듈

#### 1. **Retrieval Module** (`src/retrieval/`)
- 벡터 스토어 구현 (InMemoryVectorStore)
- 코사인 유사도 기반 문서 검색
- 간단한 임베딩 생성기

```rust
pub trait VectorStore: Send + Sync {
    fn add_document(&mut self, doc: Document, embedding: Embedding);
    fn search(&self, query_embedding: Embedding, top_k: usize) -> Vec<RetrievalResult>;
}
```

#### 2. **LLM Module** (`src/llm/`)
- LLM 클라이언트 추상화
- OpenAI API 통합
- Mock 클라이언트 (테스트용)

```rust
#[async_trait]
pub trait LLMClient: Send + Sync {
    async fn generate(&self, messages: Vec<Message>) -> Result<String>;
    async fn generate_stream(&self, messages: Vec<Message>) -> Result<Vec<String>>;
}
```

#### 3. **Engine Module** (`src/engine/`)
- RIG 오케스트레이터
- 생성 중 검색 트리거 로직
- 단계별 생성 관리

```rust
pub struct RIGConfig {
    pub retrieval_trigger_tokens: usize,  // 검색 트리거 토큰 수
    pub max_retrievals: usize,            // 최대 검색 횟수
    pub top_k: usize,                     // 검색할 문서 개수
    pub max_steps: usize,                 // 최대 생성 단계
}
```

## 🚀 시작하기

### 필수 조건

- Rust 1.70 이상
- Cargo

### 설치 및 실행

1. 프로젝트 클론
```bash
cd rig-rust
```

2. 빌드
```bash
cargo build
```

3. 실행
```bash
cargo run
```

## 💻 사용 예제

### 기본 사용법

```rust
use rig_system::{
    engine::{RIGConfig, RIGEngineBuilder},
    llm::MockLLMClient,
    retrieval::{simple_embedding, Document, InMemoryVectorStore, VectorStore},
};

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // 1. 벡터 스토어 초기화
    let mut vector_store = InMemoryVectorStore::new();

    // 2. 문서 추가
    let doc = Document {
        id: "doc1".to_string(),
        content: "RIG는 생성 중에 검색하는 기법입니다.".to_string(),
        metadata: Default::default(),
    };
    let embedding = simple_embedding(&doc.content);
    vector_store.add_document(doc, embedding);

    // 3. LLM 클라이언트 생성
    let llm_client = MockLLMClient::new("테스트 응답".to_string());

    // 4. RIG 엔진 구성
    let config = RIGConfig {
        retrieval_trigger_tokens: 10,
        max_retrievals: 3,
        top_k: 2,
        max_steps: 5,
    };

    // 5. RIG 엔진 생성
    let engine = RIGEngineBuilder::new()
        .vector_store(vector_store)
        .llm_client(llm_client)
        .config(config)
        .build()?;

    // 6. 질문 생성
    let steps = engine.generate("RIG에 대해 설명해주세요").await?;

    // 7. 결과 출력
    for step in steps {
        println!("단계 {}: {}", step.step_number, step.partial_response);
        if !step.retrieved_docs.is_empty() {
            println!("검색된 문서: {} 개", step.retrieved_docs.len());
        }
    }

    Ok(())
}
```

### OpenAI API 사용

환경 변수 설정 후 OpenAI 클라이언트 사용:

```rust
use rig_system::llm::OpenAIClient;

// 환경 변수에서 API 키 로드
let llm_client = OpenAIClient::new(Some("gpt-4".to_string()))?;

// 또는 직접 API 키 제공
let llm_client = OpenAIClient::with_api_key(
    "your-api-key".to_string(),
    Some("gpt-4".to_string())
);
```

## 🔧 설정 옵션

### RIGConfig

| 필드 | 설명 | 기본값 |
|------|------|--------|
| `retrieval_trigger_tokens` | 검색을 트리거하는 토큰 수 | 50 |
| `max_retrievals` | 최대 검색 횟수 | 3 |
| `top_k` | 검색할 문서 개수 | 3 |
| `max_steps` | 최대 생성 단계 | 10 |

## 📊 성능

- **비동기 처리**: Tokio 기반 비동기 런타임
- **메모리 효율**: Rust의 소유권 시스템 활용
- **타입 안전성**: 컴파일 타임 검증
- **확장성**: 트레이트 기반 추상화

## 🛠️ 기술 스택

- **언어**: Rust 2021 Edition
- **비동기 런타임**: Tokio
- **HTTP 클라이언트**: Reqwest
- **직렬화**: Serde
- **수치 연산**: ndarray

## 📝 의존성

```toml
[dependencies]
tokio = { version = "1.35", features = ["full"] }
reqwest = { version = "0.11", features = ["json", "stream"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
anyhow = "1.0"
async-trait = "0.1"
futures = "0.3"
ndarray = "0.15"
rand = "0.8"
```

## 🧪 테스트

```bash
cargo test
```

## 📈 향후 계획

- [ ] 실제 임베딩 모델 통합 (BERT, Sentence-BERT)
- [ ] 영구 벡터 스토어 (Qdrant, Milvus, Weaviate)
- [ ] 스트리밍 응답 지원
- [ ] 더 정교한 검색 트리거 로직
- [ ] 멀티모달 지원
- [ ] 벤치마크 및 성능 최적화

## 🤝 기여

기여를 환영합니다! 이슈나 PR을 자유롭게 제출해주세요.

## 📄 라이선스

MIT License

## 🙏 참고 자료

- [RIG 논문](https://arxiv.org/abs/2401.13417) (가상 링크)
- [RAG 소개](https://arxiv.org/abs/2005.11401)
- [Rust 공식 문서](https://doc.rust-lang.org/)

---

**Made with 💙 in Rust**
