# LLM Apps, RAG, Vector DBs, Embeddings & Chunking — v3

> Comprehensive reference for building production LLM applications. Updated 2026.

---

## 1. LLM Application Architecture

### Prompt Engineering Fundamentals

**System Prompts** set behavior; **user prompts** carry task context. System prompt should be:
- Specific about role and output format
- Include hard constraints (never do X, always do Y)
- Include few-shot examples inline for edge cases

```
system: |
  You are a senior software architect. You respond ONLY in Markdown.
  Never suggest deprecated APIs. Prefer Rust or Go over C++ for new services.
  If you don't know, say "I don't know" — never hallucinate.
```

**Few-Shot Learning**: Provide 3-5 examples of input→output pairs. More examples ≠ better; diminishing returns past 5. Quality of examples matters more than quantity. For ambiguous tasks, include examples of "I don't know" responses.

**Chain-of-Thought (CoT)**: Prefix with "Let's think step by step" or "Think carefully before answering." Dramatically improves reasoning on math, logic, and multi-step tasks. For models < GPT-4 level, CoT is essential. For GPT-4o-class models, CoT helps for complex reasoning but simple questions may not benefit.

**Structured Output**: Use JSON mode (OpenAI `response_format={"type": "json_object"}`) or constrained decoding libraries (_outlines_, `guidance`, Instructor) for reliable structured extraction. Never rely on regex parsing of freeform LLM output for production.

### Tool Use & Function Calling

LLM tool use: the model decides WHEN and HOW to call tools, not you pre-deciding.

```
functions: [
  {
    "name": "search_docs",
    "description": "Search internal documentation for a query",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {"type": "string", "description": "Search query"}
      },
      "required": ["query"]
    }
  }
]
```

**LangChain**, **LlamaIndex**, and raw implementations vary in flexibility. Raw implementations give you more control; frameworks give you abstractions. For production: prefer raw or lightweight abstractions (Pydantic + httpx) over heavy frameworks that hide latency and failure modes.

**Parallel tool calls** (OpenAI `parallel_tool_calls=true`): useful when multiple independent searches needed. Feed all results back to model in one shot — don't do sequential single-tool calls.

---

## 2. RAG — Retrieval-Augmented Generation

### Full Pipeline Overview

```
Document → Ingestion → Chunking → Embedding → Vector DB → Retrieval → Rerank → Generate
```

### Ingestion

**Document processing pipeline:**
- PDFs: pdfminer, pymupdf (fitz), or LlamaParse for complex layouts
- Word/Docs: python-docx, Unstructured
- HTML: BeautifulSoup with heuristics for article extraction
- Images: OCR (pytesseract, EasyOCR) + layout detection (LayoutLM, Donut)
- Code: tree-sitter for AST-aware parsing, preserving function/class context

**Multi-modal docs**: Use document understanding models (GPT-4o with Vision, Gemini 1.5 Pro, Anthropic's PDF parsing) to extract text from images/tables before chunking. Tables require special handling — see chunking section.

### Chunking Strategies

**Fixed-size chunking** (most common, not always best):
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,  # 10% overlap for context continuity
    separators=["\n\n", "\n", ". ", " ", ""]
)
```

**Chunk size rules of thumb:**
- 256-512 tokens: high recall, lower precision (good for Q&A over many docs)
- 512-1024 tokens: balanced (most common production choice)
- 1024-2048 tokens: lower recall, higher precision, better for summaries
- Context window-aware: aim for chunks that fit within model context minus prompt overhead

**Semantic chunking** (more accurate, slower):
```python
# Cluster sentences by embedding similarity, break at topic boundaries
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
```

**Markdown/AST-aware chunking** — preserves structure:
```python
# Parse markdown headings as boundaries
# Use tree-sitter for code AST boundaries
# Preserve table structure as single chunks with metadata
```

**Table handling**:
- Tables as single chunks with caption
- Or serialize tables to markdown strings with row/col headers preserved
- For complex PDFs: extract tables with tablepyxl, pdfplumber

**Code chunking**: Use AST parsing (tree-sitter) to chunk at function/class level, preserving imports and docstrings within chunk. Pure text splitting destroys code semantics.

**Metadata enrichment** — critical for production RAG:
```python
chunks = []
for doc in documents:
    for chunk in chunker.split_text(doc.text):
        chunks.append({
            "text": chunk,
            "metadata": {
                "source": doc.source,
                "page": doc.page,
                "section_heading": doc.heading,
                "created_at": doc.created_at,
                "doc_type": doc.type,  # enables filtering
                "author": doc.author
            }
        })
```

### Embedding Models

| Model | Dim | Multilingual | MTEB Avg | Use Case |
|---|---|---|---|---|
| text-embedding-3-large (OpenAI) | 3072 | Yes | ~64.6 | Best quality, higher cost |
| text-embedding-3-small (OpenAI) | 1536 | Yes | ~62.3 | Good quality, lower cost |
| text-embedding-ada-002 (OpenAI) | 1536 | Yes | ~60.9 | Legacy, cheaper |
| Voyage Code 2 | 1536 | Code-only | — | Best for code search |
| voyage-law-2 | 1024 | Legal-domain | — | Legal docs, domain-specific |
| BGE-M3 (Beijing AI) | 1024 | 100+ lang | ~63.1 | Open-source multilingual |
| E5-Mistral-7b | 1024 | Multilingual | ~66.4 | Best open-source quality |
| Cohere embed-v3 | 1024 | Yes | ~64.1 | Good API, good reranking |

**Dimension reduction**: Use `PCA` or `SVD` (via `sentence-transformers`) to reduce dimensions (e.g., 3072→384) for cost savings in vector DB storage. Quality loss is typically <2% for 3-large→384 for semantic search tasks.

```python
from sklearn.decomposition import PCA
# After training PCA on your embeddings corpus
reducer = PCA(n_components=384)
reduced = reducer.fit_transform(embeddings)
```

### Vector Search & Re-ranking

**Hybrid search** — combine dense + sparse vectors:
```python
# Qdrant example: hybrid fusion (RRF - Reciprocal Rank Fusion)
client.search(
    collection_name="docs",
    query_filter=qdrant_filter,
    search_params=SearchParams(hibrid_hybrid_factor=0.7),
    vector_name="dense",
    with_vector=False
)
# OR sparse vectors from BM25 (splade, BM25SparseEncoded)
```

**Re-ranking** — critical for production quality:
1. Retrieve top-50 to top-100 candidates with vector search
2. Re-rank with cross-encoder (ColBERT-style or cross-encoder models)
3. Return top-10 to LLM

Re-rank models: `CrossEncoder` (sentence-transformers), Cohere Rerank, BGE-Reranker-large, Jina Reranker v2

```python
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("BAAI/bge-reranker-large")

pairs = [(query, chunk) for chunk in retrieved_chunks]
scores = reranker.predict(pairs)
ranked = sorted(zip(retrieved_chunks, scores), key=lambda x: x[1], reverse=True)
```

---

## 3. Vector Databases — Deep Comparison

### HNSW Index (Most Common)

Hierarchical Navigable Small World — layered graph. Higher `m` = better recall, higher latency/memory. Higher `ef_construction` = slower build, better quality.

```
ef_construction: 128–512 (higher = better recall, slower index build)
ef_search: 100–500 (higher = better recall, higher query latency)
m: 16–64 (connectivity per node)
```

For 1M vectors: construction takes 5-30 min, memory ~2-4GB at m=16.

### Qdrant

**Self-hosted or managed cloud.** Rust-based, strong performance.

```yaml
# qdrant collection config
vectors:
  size: 1536
  distance: Cosine
hnsw_config:
  m: 16
  ef_construct: 256
  full_scan_threshold: 10000  # below this, do brute force
indexing_threshold: 0
```

**Key strengths:**
- Payload filtering (pre-filter and post-filter)
- Named vectors (multi-tenant, multi-vector per doc)
- Sparse+dense hybrid (full-text + vector in one DB)
- Snapshot-based backup
- 2025: Qdrant Cloud with autoscaling, EU data residency

**Cost model**: Free self-hosted; managed cloud from ~$25/mo for starter.

### Pinecone

**Managed serverless.** No index tuning — fully managed.

```python
index = pinecone.Index("production", dimension=1536, metric="cosine")
index.query(vector=query_vec, top_k=10, filter={"category": "docs"})
```

**Key strengths:**
- Serverless = no capacity planning
- Multi-tenancy via pod isolation
- Metadata filtering (server-side)
- gRPC for low latency

**Cost model**: Serverless pricing based on storage + read units. Pods: ~$70/mo per medium pod (1M vectors @ 1536d). Gets expensive at scale.

**Serverless gotcha**: Cold start latency, less predictable performance at high QPS.

### Weaviate

**Self-hosted or Weaviate Cloud.** Open-source (Apache 2.0).

```graphql
{
  Get {
    Document(
      nearVector: { vector: [0.1, ...], distanceType: cosine }
      where: { path: ["category"], operator: Equal, valueText: "docs" }
      limit: 10
    ) {
      content
      category
      _additional { distance }
    }
  }
}
```

**Key strengths:**
- GraphQL + REST + Python client
- Built-in BM25 (sparse vector) + vector hybrid
- Generative search (grouped by feature)
- Weaviate 1.24+: INVERTED INDEX as primary, HNSW for ANN fallback
- Schema validation
- Module system: transformer-based embedding modules (local)

**Cost model**: Free self-hosted; managed cloud ~$25/mo.

### Comparison Table

| Feature | Pinecone | Qdrant | Weaviate | Chroma (local) |
|---|---|---|---|---|
| License | Proprietary | Apache 2 | Apache 2 | Apache 2 |
| Managed cloud | Yes (serverless + pods) | Yes | Yes | No |
| Self-hosted | No | Yes | Yes | Yes |
| Hybrid search | Yes (sparse via BM25) | Yes (built-in) | Yes (built-in) | No |
| Metadata filtering | Yes | Yes | Yes | Limited |
| Multi-tenancy | Pod isolation | Namespaces + tenant isolation | Tenant classes | N/A |
| Open-source | No | Yes | Yes | Yes |
| Starter managed cost | ~$25/mo (serverless) | ~$25/mo | ~$25/mo | Free |
| Performance (1M, 1536d) | ~50ms p99 | ~20ms p99 | ~40ms p99 | ~30ms (local SSD) |
| Snapshot/backup | Yes | Yes | Yes | Export/import |

### Choosing a Vector DB

- **Pinecone**: If you want zero ops, have budget, and don't need fine-grained control
- **Qdrant**: If you want best-in-class performance + self-hosting flexibility; best for hybrid sparse+dense
- **Weaviate**: If you want built-in ML modules, graph API, or open-source with cloud option
- **Chroma**: Prototyping, <100K vectors, single-node, embedded apps
- **pgvector**: If you're on Postgres already, <1M vectors, want ACID + SQL joins (great for multi-tenant)

---

## 4. Advanced RAG Patterns

### Query Expansion
```python
# Multi-query expansion: generate sub-questions
expanded_queries = llm.generate([
    f"Generate 3 different phrasings of: {original_query}"
])
# Retrieve for each, dedupe, and combine context
```

### HyDE (Hypothetical Document Embeddings)
1. Ask LLM to write a hypothetical answer chunk
2. Embed that hypothetical chunk (not the query)
3. Retrieve docs similar to the hypothetical → often better recall

### CRAG (Corrective RAG)
```
Query → Retrieve → Classify relevance →
  GREEN (relevant): proceed to generate
  RED (irrelevant): fall back to web search or generic response
  YELLOW (partial): self-query for more specific info
```

### Self-Query Retrievers
Use LLM to extract metadata filters from natural language:
- "Find docs from last quarter about API changes" → filter by date range
- "Legal docs from 2024" → filter by doc_type + year

LangChain's SelfQueryRetriever wraps this pattern.

### Agentic RAG
Multi-hop reasoning: LLM plans which tools/queries to run, synthesizes across results.
```python
# OpenAI Assistants API + file_search tool
assistant = client.beta.assistants.create(
    instructions="Research agent for company analysis",
    tools=[{"type": "file_search"}, {"type": "code_interpreter"}],
    tool_resources={"file_search": {"vector_stores": [vs.id]}}
)
```

### GraphRAG / LightRAG

**GraphRAG** (Microsoft): Extract knowledge graph from documents → query graph + community summarization. Dramatically better for "global" questions ("What are the main themes?"). Requires entity extraction pipeline (LlamaIndex + OpenAI).

**LightRAG**: Simplified graph + vector hybrid. Easier to implement than full GraphRAG.

**memoRAG**: Uses LLM-generated memory to guide retrieval. Good for long conversations.

---

## 5. RAG Evaluation

### RAGAS (RAG Assessment Suite)

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)

result = evaluate(ds, metrics=[
    faithfulness,
    answer_relevancy, 
    context_precision,
    context_recall
])
```

Requires LLM-as-judge. Can use local models ( Ollama) for cost savings.

### Trulens

```python
from trulens import Feedback
from trulens.providers.litellm import LiteLLM

feedbacks = [
    Feedback(LiteLLM().context_relevance)
        .on_input()
        .on_context(),
    Feedback(LiteLLM().answer_relevance)
        .on_input()
        .on_output(),
]
```

### Key Metrics

| Metric | What it measures | Good threshold |
|---|---|---|
| Context Precision | % of relevant context in top results | >0.7 |
| Context Recall | % of ground truth context retrieved | >0.8 |
| Faithfulness | LLM answer grounded in context | >0.8 |
| Answer Relevancy | Answer addresses the question | >0.8 |
| Hallucination Rate | Unsupported claims in answer | <0.2 |

### Ground Truth Generation
Generating GT for evaluation: use LLM to generate (query, context, answer) triplets from your documents. Label manually for a subset to calibrate.

---

## 6. Production Considerations

### Latency Budget

| Component | Typical P50 | Typical P99 |
|---|---|---|
| Embedding (API call) | 100-300ms | 500-1000ms |
| Vector DB query | 10-50ms | 50-200ms |
| Re-ranking | 50-200ms | 200-500ms |
| LLM generation (streaming) | 500ms TTFT | 1500ms TTFT |
| **Total RAG E2E** | **1-3s** | **3-8s** |

### Token Budget & Cost

| Model | Input cost/1M tokens | Output cost/1M tokens |
|---|---|---|
| GPT-4o | $2.50 | $10 |
| GPT-4o-mini | $0.15 | $0.60 |
| Claude 3.5 Sonnet | $3 | $15 |
| Claude 3 Haiku | $0.25 | $1.25 |
| DeepSeek V3 | $0.27 | $1.10 |
| Gemini 1.5 Flash | $0.075 | $0.30 |

**Optimization tactics:**
- Smaller embedding model for high-volume retrieval (ada-002 or bge-m3)
- Context compression before generation (LLMlingua, RECOMP)
- Aggressive top-k reduction: retrieve 50, rerank, return 5-8 chunks
- Cache repeated queries with semantic equivalence (embed query, check cache)

### Semantic Caching (Redis)

```python
import redis, hashlib

cache = redis.Redis()
query_hash = hashlib.sha256(normalized_query.encode()).hexdigest()
cached = cache.get(query_hash)
if cached:
    return json.loads(cached)
# ... retrieve and generate ...
cache.setex(query_hash, ttl=3600, value=json.dumps(response))
```

### Streaming

```python
from openai import OpenAI
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    stream=True
)
for chunk in stream:
    yield chunk.choices[0].delta.content
```

Stream LLM output to client for perceived latency reduction. Embedding + retrieval should be done before starting stream.

### Hallucination Guardrails

1. **Force citation**: Ask LLM to cite sources with [DOC_ID] markers
2. **NLI-based checking**: Use NLI model to verify answer entailed by context
3. **Self-consistency sampling**: Generate answer 3x, check consistency
4. **Guardrail frameworks**: NeMo Guardrails (NVIDIA), LlamaGuard (Meta), Azure AI Content Safety

---

## 7. Emerging Patterns (2025-2026)

### CRAG (Corrective RAG)
Pipeline that scores retrieval relevance and routes to web search or generic fallback when local retrieval is poor.

### 2-Hop RAG / Iterative RAG
Model iteratively queries, refines, and re-retrieves. Good for complex multi-step questions.

### ColBERT / Late Interaction
Multi-vector per token retrieval. ColBERT v2 achieves BM25-level precision with neural ranking. Faster than cross-encoder reranking.

### Long Context Models Reducing Need for Chunks
Gemini 1.5 Pro (1M token context) and Claude 3 (200K tokens) reduce (but don't eliminate) the need for sophisticated chunking. Full-doc search still underperforms selective retrieval for targeted Q&A.

### Mixture of Retrievers
Ensemble: BM25 + dense + sparse → fusion (RRF or COIL) → rerank. Different retrievers catch different query types.

### Structured Data in RAG
LlamaIndex + DocArray for structured data tables. SQL database + semantic search hybrid is increasingly common.

---

*Generated 2026-04-22 — Requires web search for latest benchmark numbers*
