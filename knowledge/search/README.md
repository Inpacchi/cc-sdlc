# Search Knowledge Store

Retrieval pipeline patterns, scoring mathematics, and evaluation frameworks for projects that build search, retrieval, or RAG (retrieval-augmented generation) systems. Applies to vector search, hybrid (lexical+vector) retrieval, and multi-strategy fusion pipelines.

**Use this store when:** the project uses vector similarity search (pgvector, FAISS, Qdrant, Weaviate, etc.), or builds query-time retrieval pipelines, or needs IR evaluation discipline (recall@k, nDCG, regression detection).

**Skip this store when:** the project's "search" is database `LIKE` queries or third-party search-as-a-service (Algolia, Elasticsearch with default config) — these patterns won't add value at that abstraction level.

## Knowledge Categories

| File | Domain | Primary Consumers |
|------|--------|-------------------|
| `retrieval-strategy-patterns.yaml` | Query-time RAG strategies (reranking, multi-query, self-reflective, agentic, hybrid fusion) | search-engineer, backend-developer, software-architect |
| `ingestion-pipeline-patterns.yaml` | Ingestion-time patterns (chunking, contextual enrichment, embedding model selection) | search-engineer, backend-developer, ml-engineer |
| `vector-index-tuning-patterns.yaml` | Index type selection, HNSW tuning, quantization, memory estimation | search-engineer, database-architect, performance-engineer |
| `retrieval-evaluation-patterns.yaml` | IR metrics, embedding comparison, RAG evaluation, regression detection | search-engineer, sdet, ml-engineer |
| `multi-strategy-retrieval-patterns.yaml` | Multi-strategy parallel retrieval (temporal, graph, RRF fusion, token-budget) | search-engineer, backend-developer, software-architect |
| `evidence-combination-frameworks.md` | Mathematical foundations for combining evidence into confidence scores | search-engineer |
| `score-transform-catalog.md` | Score normalization transforms (log-scale, sigmoid, etc.) | search-engineer |

## Agent Naming Note

Several entries reference roles like `search-engineer` and `db-engineer` that may not exist in every project. Substitute your project's equivalent — typically `backend-developer` or `data-architect` covers retrieval-pipeline work in projects without a dedicated search specialist. Use `/sdlc-create-agent` to scaffold a `search-engineer` agent if your project warrants one.

## Relationship to Other Knowledge Stores

- **`architecture/pipeline-design-patterns.yaml`** — General pipeline patterns. The ingestion pipeline patterns here are RAG-specific specializations.
- **`architecture/prompt-engineering-patterns.yaml`** — Prompt patterns including structured outputs, A/B testing, and versioning. Complements RAG evaluation patterns (LLM-as-judge uses prompt patterns).
- **`architecture/ml-system-design.yaml`** — ML production patterns including confidence gates, active learning, and shadow testing. Complements retrieval evaluation patterns.
