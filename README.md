# RAG Knowledge Assistant

A Python-based Retrieval-Augmented Generation (RAG) application built with Azure AI Search and Azure OpenAI. The project demonstrates how retrieval quality can be improved by addressing common RAG failure scenarios and evaluating the system before and after those improvements.

## 1. Project Overview

The system allows users to ask questions against an enterprise-style document collection and returns:

- A grounded answer
- Retrieved source documents
- Page/chunk metadata
- Conversation-aware answers for follow-up questions

The main goal of this project is not frontend complexity. It is to demonstrate **RAG design, debugging, evaluation, and improvement**.

## 2. Code Navigation

The main implementation areas are linked below for quick review.

| Area | Code |
|---|---|
| RAG pipeline | [`src/rag_knowledge_assistant/rag.py`](src/rag_knowledge_assistant/rag.py) |
| Document ingestion | [`src/rag_knowledge_assistant/ingestion.py`](src/rag_knowledge_assistant/ingestion.py) |
| Search index | [`src/rag_knowledge_assistant/search_index.py`](src/rag_knowledge_assistant/search_index.py) |
| Hybrid search | [`src/rag_knowledge_assistant/hybrid_search.py`](src/rag_knowledge_assistant/hybrid_search.py) |
| Hybrid store | [`src/rag_knowledge_assistant/hybrid_store.py`](src/rag_knowledge_assistant/hybrid_store.py) |
| Configuration | [`src/rag_knowledge_assistant/config.py`](src/rag_knowledge_assistant/config.py) |
| FastAPI | [`api/main.py`](api/main.py) |
| Frontend | [`frontend/`](frontend/) |
| Evaluation | [`evaluation/`](evaluation/) |

The main RAG implementation is [`rag.py`](src/rag_knowledge_assistant/rag.py). It contains the query rewriting, Azure AI Search retrieval, context construction, and grounded answer generation flow.

## 3. RAG Architecture

### Ingestion

```text
Documents
   ↓
Parsing
   ↓
Text Extraction
   ↓
Chunking
   ↓
Metadata Extraction
   ↓
Embeddings
   ↓
Azure AI Search
```

### Query

```text
User Question
     ↓
Conversation Context
     ↓
Query Rewriting
     ↓
Standalone Query
     ↓
Hybrid Search
 ┌───────────────┐
 │ Keyword Search│
 │ Vector Search │
 └───────┬───────┘
         ↓
   Search Results
         ↓
Semantic Ranking
         ↓
Metadata Filtering
         ↓
Context Construction
         ↓
Azure OpenAI
         ↓
Grounded Answer
         ↓
Sources / Citations
```

## 4. Azure Services

The implementation uses the following Azure components:

- **Azure AI Search** — document indexing, vector search, keyword search, hybrid retrieval, semantic ranking, and metadata filtering.
- **Azure OpenAI** — embeddings and answer generation.
- **Azure AI Foundry** — Azure AI development/deployment environment used by the project.
- **Python / FastAPI** — application and API layer.

The assignment also asks us to consider Azure Storage, authentication, secrets management, monitoring, scaling, security, data isolation, and cost for the production architecture. These are addressed as production design considerations; they are not all implemented in the demo.

## 5. Why Azure AI Search?

Azure AI Search was selected because it provides the retrieval capabilities required for this use case in one managed service:

- Keyword search
- Vector search
- Hybrid search
- Semantic ranking
- Metadata filtering

Hybrid search is used because enterprise questions can contain both exact terms and semantic concepts. Combining keyword and vector retrieval provides better coverage than relying on vector similarity alone.

## 6. RAG Failure Scenarios and Improvements

The project was developed by starting with a simpler RAG approach and then addressing failure cases from the assignment.

### Scenario 1 — Correct Document, Wrong Chunk

**Problem:** The correct document was retrieved, but the relevant information was not consistently returned in the top results.

**Investigation areas:**

- Chunk size
- Chunk overlap
- Embeddings
- Top-K
- Metadata
- Hybrid search
- Semantic ranking

**Improvement:**

- Improved chunking and metadata handling
- Added hybrid retrieval
- Added semantic ranking
- Increased retrieval coverage where required

### Scenario 2 — Information Across Multiple Sections

**Problem:** Some questions require information from multiple chunks or documents.

**Improvement:**

The retrieval pipeline retrieves multiple relevant chunks and constructs the context before generation instead of relying on a single retrieved chunk.

This allows questions requiring information from different sections or documents to be answered from combined evidence.

### Scenario 3 — Similar Documents / Conflicting Information

**Problem:** Multiple versions of a document can contain similar information. For example, a 2025 pricing document and a 2026 pricing document may both contain the same plan.

**Improvement:**

Document metadata is retained and used during retrieval. Version/effective-date information is also incorporated into the retrieval and generation strategy so that newer information is preferred when the question is time-sensitive.

Example:

```text
Pricing2025.pdf
Pricing2026.pdf
       ↓
Metadata + Retrieval
       ↓
Prefer applicable/current version
```

### Scenario 4 — Hallucination / Missing Information

**Problem:** An LLM can generate a plausible answer even when the knowledge base does not contain the requested information.

**Improvement:**

Generation is explicitly grounded in retrieved context. The model is instructed not to invent information that is not supported by the retrieved evidence.

This is demonstrated using questions whose answers are outside the knowledge base.

### Scenario 5 — Ambiguous Query

**Problem:**

A query such as:

> "What is the limit?"

may refer to multiple different limits.

**Approach:**

The system retrieves using the available context and metadata. Fully automatic ambiguity detection/clarification is considered a production enhancement and is not claimed as fully implemented.

### Scenario 6 — Conversational Context

**Problem:**

A follow-up such as:

```text
User: What is the Enterprise price?
Assistant: ...
User: What about the Starter tier?
```

is incomplete when treated as an independent search query.

**Improvement:**

Conversation history is passed to the backend and used to rewrite the follow-up question into a standalone search query before retrieval.

For example:

```text
"What about the Starter tier?"
             ↓
"What is the Starter tier price?"
             ↓
Retrieval
```

The frontend keeps the current conversation state and sends it with the request. Persistent server-side chat storage is intentionally not used for this demo.

## 7. Grounding and Source Traceability
**Implementation:** [`src/rag_knowledge_assistant/rag.py`](src/rag_knowledge_assistant/rag.py)


The response contains the generated answer together with source metadata from retrieved chunks.

Example:

```text
Answer
  ↓
Pricing2026.pdf
  Page: 1
  Chunk: 1
```

The source metadata allows the retrieved evidence to be traced back to the original document.

The frontend intentionally displays a compact source count rather than exposing raw retrieval metadata as part of the answer.

## 8. Metadata Filtering

The search index contains structured metadata such as document and department information.

The frontend currently demonstrates metadata filtering using hardcoded values.

These filters demonstrate the retrieval capability only. They are **not an authentication or authorization boundary**.

Production access control should enforce user permissions server-side before retrieval.

## 9. Evaluation
**Implementation:** [`evaluation/`](evaluation/)


A small evaluation dataset was created containing different question types, including:

- Straightforward questions
- Follow-up questions
- Multi-document questions
- Version-sensitive questions
- No-answer questions
- Difficult retrieval cases

The evaluation compares the baseline and improved RAG implementations using the same document/chunk corpus.

The recorded comparison used **46 chunks**.

### Recorded Retrieval Results

| Metric | Result |
|---|---:|
| Hit@1 | 87.5% |
| Hit@3 | 87.5% |
| Hit@5 | 87.5% |

The important finding is that retrieval hit rate alone does not capture the full quality of a RAG system.

Improvements were also made in:

- Ranking
- Context construction
- Query rewriting
- Version handling
- Grounded generation
- Conversation handling
- Source traceability

Additional evaluation such as citation correctness, hallucination rate, latency, and token/cost measurement remains an area for further improvement.

## 10. Architecture and Production Considerations

The current project is a working RAG demonstration rather than a complete production deployment.

For production, the architecture should additionally include:

- Microsoft Entra ID authentication
- Server-side authorization
- Document-level access control
- Azure Key Vault for secrets
- Application Insights / Log Analytics
- Monitoring and alerting
- Scaling strategy for large document collections
- Cost monitoring
- Data isolation

These should be presented as **production architecture decisions**, not as features already implemented in the demo.

For example, when scaling from thousands to millions of documents, the system would require careful index design, partitioning/replicas, ingestion orchestration, metadata strategy, and capacity planning.

## 11. Key Problem-Solving Questions

### Retrieval Quality

If five chunks are retrieved but only one is relevant:

1. Inspect the retrieved chunks.
2. Check chunk boundaries and overlap.
3. Check embedding quality.
4. Compare keyword, vector, and hybrid retrieval.
5. Tune Top-K.
6. Check metadata filters.
7. Evaluate semantic ranking/reranking.
8. Re-run the evaluation set.

The important debugging approach is to determine whether the failure occurred during:

```text
Query
 ↓
Retrieval
 ↓
Ranking
 ↓
Context construction
 ↓
Generation
```

### Latency

If response time increases from 3 seconds to 12 seconds, measure each stage independently:

```text
Query processing
     ↓
Embedding
     ↓
Search
     ↓
Ranking
     ↓
LLM generation
```

Then identify whether the increase is caused by retrieval, network latency, model generation, excessive context, or another application bottleneck.

### Scale

For a growth from 10,000 documents to millions of documents, consider:

- Azure AI Search capacity
- Index design
- Partitioning and replicas
- Ingestion throughput
- Metadata strategy
- Incremental ingestion
- Query performance
- Cost

### Security

For department-level isolation, filtering should not depend on values supplied directly by the client.

Production flow:

```text
Authenticated User
       ↓
Identity / Claims
       ↓
Server-side Authorization
       ↓
Allowed Metadata Filters
       ↓
Azure AI Search
       ↓
Retrieved Documents
```

This prevents users from simply changing a frontend filter to access another department's documents.

### Cost

If Azure OpenAI costs increase, investigate:

- Input token growth
- Output token growth
- Number of retrieved chunks
- Repeated queries
- Model selection
- Embedding volume
- Unnecessary context
- Caching opportunities

### Wrong Answer With a Valid Citation

Debug the complete chain:

```text
User Query
   ↓
Query Rewriting
   ↓
Retrieval
   ↓
Ranking
   ↓
Context
   ↓
Prompt
   ↓
LLM
   ↓
Citation
```

A valid-looking citation does not automatically mean the answer is correct. The cited chunk must actually support the generated claim.

## 12. Project Structure

```text
rag-knowledge-assistant/
│
├── api/
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── evaluation/
│   ├── questions.json
│   ├── evaluate.py
│   ├── compare_results.py
│   ├── baseline_results.json
│   └── improved_results.json
│
├── scripts/
│   ├── ingestion/
│   ├── setup/
│   └── testing/
│
├── src/
│   └── rag_knowledge_assistant/
│       ├── config.py
│       ├── ingestion.py
│       ├── search_index.py
│       ├── hybrid_search.py
│       ├── hybrid_store.py
│       └── rag.py
│
├── .env
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## 13. Setup

### Prerequisites

- Python 3.14+
- `uv`
- Azure OpenAI resource
- Azure AI Search resource
- Required Azure OpenAI deployments
- Configured Azure AI Search index

### Install

```powershell
uv sync
```

### Environment Variables

Create a `.env` file containing the Azure configuration required by the application.

```env
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_API_VERSION=...
AZURE_OPENAI_CHAT_DEPLOYMENT=...
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=...

AZURE_SEARCH_ENDPOINT=...
AZURE_SEARCH_ADMIN_KEY=...
AZURE_SEARCH_INDEX_NAME=...
AZURE_SEARCH_HYBRID_INDEX_NAME=...
```

Never commit `.env` or API keys.

## 14. Running the Application

### Start the API

```powershell
uv run uvicorn api.main:app --reload
```

The API runs on:

```text
http://127.0.0.1:8000
```

### Start the Frontend

From the project root:

```powershell
python -m http.server 5500 -d frontend
```

Open:

```text
http://127.0.0.1:5500
```

The frontend is intentionally simple because the assignment focuses on the RAG implementation rather than UI design.

## 15. Final Engineering Summary

The project evolved from a basic vector-based RAG approach into a more robust retrieval pipeline.

The main improvements are:

- Hybrid search
- Semantic ranking
- Metadata filtering
- Query rewriting for follow-up questions
- Version-aware retrieval/generation
- Grounded generation
- Source traceability
- Evaluation against a controlled dataset

The key engineering lesson is that RAG quality can fail at multiple layers. Improving the system therefore requires looking beyond embeddings and vector similarity and debugging the complete pipeline from **query → retrieval → ranking → context → generation → citation**.

<!-- ## 16. Implementation Status

### Implemented

- Python RAG application
- Azure AI Search integration
- Azure OpenAI integration
- Document ingestion
- Chunking and metadata
- Hybrid retrieval
- Semantic ranking
- Metadata filtering
- Query rewriting
- Conversation-aware retrieval
- Grounded generation
- Source traceability
- Evaluation dataset
- Baseline vs improved comparison
- Simple demonstration frontend

### Production Design / Not Fully Implemented

- Microsoft Entra ID authentication
- Server-side authorization
- Production document-level ACL enforcement
- Azure Key Vault integration
- Application Insights / Log Analytics
- Automatic ambiguity scoring and clarification
- Complete citation-correctness metrics
- Complete hallucination-rate metrics
- Million-document load testing
- Production-scale capacity testing
- Production token-cost dashboards

These limitations are intentionally documented so that the demo does not claim production capabilities that have not been implemented or measured. -->
