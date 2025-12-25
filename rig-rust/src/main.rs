mod engine;
mod llm;
mod retrieval;

use engine::{RIGConfig, RIGEngineBuilder};
use llm::MockLLMClient;
use retrieval::{simple_embedding, Document, InMemoryVectorStore, VectorStore};
use std::collections::HashMap;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    println!("🧐 RIG (Retrieval Interleaved Generation) 데모\n");
    println!("{}", "=".repeat(60));

    // 1. 벡터 스토어 초기화 및 문서 추가
    let mut vector_store = InMemoryVectorStore::new();

    let documents = vec![
        Document {
            id: "doc1".to_string(),
            content: "Rust는 메모리 안전성을 보장하는 시스템 프로그래밍 언어입니다. 소유권(Ownership) 시스템을 통해 컴파일 타임에 메모리 안전성을 검증합니다.".to_string(),
            metadata: HashMap::new(),
        },
        Document {
            id: "doc2".to_string(),
            content: "RIG는 생성 중에 필요한 정보를 실시간으로 검색하는 기법입니다. RAG와 달리 초반에 모든 정보를 가져오지 않고, 필요할 때마다 검색합니다.".to_string(),
            metadata: HashMap::new(),
        },
        Document {
            id: "doc3".to_string(),
            content: "벡터 데이터베이스는 임베딩을 저장하고 유사도 검색을 수행합니다. 코사인 유사도나 유클리드 거리를 사용하여 가장 관련성 높은 문서를 찾습니다.".to_string(),
            metadata: HashMap::new(),
        },
        Document {
            id: "doc4".to_string(),
            content: "LLM(Large Language Model)은 대규모 텍스트 데이터로 학습된 언어 모델입니다. GPT, Claude, LLaMA 등이 대표적인 예시입니다.".to_string(),
            metadata: HashMap::new(),
        },
    ];

    println!("\n📚 문서 로딩 중...");
    for doc in documents {
        let embedding = simple_embedding(&doc.content);
        let preview: String = doc.content.chars().take(30).collect();
        let preview = if doc.content.chars().count() > 30 {
            format!("{}...", preview)
        } else {
            preview
        };
        println!("  ✓ {}: {}", doc.id, preview);
        vector_store.add_document(doc, embedding);
    }

    // 2. Mock LLM 클라이언트 생성 (실제로는 OpenAI API 사용)
    let mock_responses = vec![
        "RIG는 Retrieval Interleaved Generation의 약자로",
        "생성 과정 중에 정보를 검색하는 기법입니다. 이는 RAG보다 더 동적이며",
        "필요한 시점에 정확한 정보를 가져올 수 있습니다. Rust로 구현하면",
    ];

    println!("\n🤖 LLM 클라이언트 초기화...");

    // 3. RIG 엔진 설정
    let config = RIGConfig {
        retrieval_trigger_tokens: 10,
        max_retrievals: 3,
        top_k: 2,
        max_steps: 5,
    };

    println!("\n⚙️  RIG 엔진 설정:");
    println!("  • 검색 트리거 토큰: {} 토큰마다", config.retrieval_trigger_tokens);
    println!("  • 최대 검색 횟수: {}", config.max_retrievals);
    println!("  • 검색 문서 개수: Top-{}", config.top_k);
    println!("  • 최대 생성 단계: {}", config.max_steps);

    // 각 단계별 응답을 시뮬레이션
    for (i, response) in mock_responses.iter().enumerate() {
        println!("\n{}", "=".repeat(60));
        println!("🔄 단계 {} 시작\n", i + 1);

        let llm_client = MockLLMClient::new(response.to_string());

        let engine = RIGEngineBuilder::new()
            .vector_store(vector_store.clone())
            .llm_client(llm_client)
            .config(config.clone())
            .build()?;

        let query = "RIG에 대해 설명해주세요";
        println!("❓ 질문: {}\n", query);

        let steps = engine.generate(query).await?;

        for step in &steps {
            println!("📝 단계 {}: 부분 응답 생성", step.step_number);
            println!("   응답: {}", step.partial_response);

            if step.needs_retrieval && !step.retrieved_docs.is_empty() {
                println!("\n   🔍 검색 수행:");
                for (idx, result) in step.retrieved_docs.iter().enumerate() {
                    let preview: String = result.document.content.chars().take(40).collect();
                    let preview = if result.document.content.chars().count() > 40 {
                        format!("{}...", preview)
                    } else {
                        preview
                    };
                    println!(
                        "     {}. [점수: {:.2}] {}",
                        idx + 1,
                        result.score,
                        preview
                    );
                }
            }
            println!();
        }
    }

    println!("\n{}", "=".repeat(60));
    println!("\n✨ RIG 프로세스 완료!\n");
    println!("🎯 핵심 차이점:");
    println!("  RAG: 질문 → 검색 → 생성");
    println!("  RIG: 질문 → 생성 → 검색 → 생성 → 검색 → ... (반복)\n");

    println!("💡 RIG의 장점:");
    println!("  ✓ 더 정확한 답변");
    println!("  ✓ 동적 정보 검색");
    println!("  ✓ 환각(Hallucination) 감소");
    println!("  ✓ 복잡한 추론에 강함\n");

    Ok(())
}
