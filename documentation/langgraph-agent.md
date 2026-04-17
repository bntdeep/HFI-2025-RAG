# LangGraph Agent

Turns a user question into a structured answer by routing through specialized nodes.

## Flow

```
User query
   │
   ▼
1. Router          → classifies intent + extracts countries/parameters
   │
   ├─[crud]────────────────────────────────────┐
   │                                           ▼
   └─[comparison|profile|trend|general]   5. CRUD Handler → list / delete / upload guidance
        │
        ▼
2. Retriever       → fetches relevant chunks from ChromaDB
        │
        ▼
3. Analyzer        → extracts structured data or generates free-form text
        │
        ▼
4. Formatter       → assembles final response + chart config + sources
        │
        ▼
     Result
```

## Node Details

### 1. Router (`nodes/router.py`)
Makes a single LLM call to classify the query intent and extract entities.

**Intents:**

| Intent | When used | Example |
|--------|-----------|---------|
| `comparison` | 2+ countries being compared | "Compare Belarus and Austria on personal freedom" |
| `profile` | single country full profile | "Tell me about Norway's freedom scores" |
| `trend` | change over time | "How has press freedom changed in Russia?" |
| `general` | any other HFI question | "What is the global average HFI score?" |
| `crud` | document management | "List all indexed documents" |

Also extracts `countries` (normalized against 165 HFI jurisdictions) and `parameters` (HFI codes like `pf`, `ef_trade`). Caller-supplied values always override LLM extraction (used when the UI passes an explicit country selection).

### 2. Retriever (`nodes/retriever.py`)
Two strategies, chosen by intent:

- **Comparison** — searches per country in parallel using focused queries like `"Belarus pf freedom score rank"` (top_k=5 each), then deduplicates by `chunk_id`. Avoids embedding drift caused by including the full original query.
- **General** — single search with the original query (top_k=8). Used for profile, trend, and general intents.

Uses a module-level `VectorStoreClient` singleton to avoid reloading the ChromaDB HNSW index on every request.

### 3. Analyzer (`nodes/analyzer.py`)
Three paths, chosen by intent:

- **comparison** → asks LLM to return a `ComparisonResult` (scores matrix + chart config + insight)
- **profile** → asks LLM to return a `CountryProfile` (ranks, scores, strengths, weaknesses + radar chart)
- **trend / general** → free-form markdown answer

Structured paths fall back to free-form if the LLM returns malformed JSON. All LLM calls use `invoke_structured()` from `llm.py` — a proxy-compatible helper that embeds the Pydantic schema in the system prompt and parses the JSON response manually (EPAM DIAL blocks the OpenAI function-calling API).

### 4. Formatter (`nodes/formatter.py`)
No LLM calls. Assembles the final output:
- `response_text` — markdown string (comparison table, profile summary, or raw analysis)
- `chart_config` — dict extracted from `extracted_data["chart_config"]`, or `None`
- `sources` — list of `{chunk_id, page_number, section, relevance_score, chunk_type}` dicts

### 5. CRUD Handler (`nodes/crud_handler.py`)
No LLM calls. Keyword-dispatches on the query:
- `list / show` → `MetadataDB.list_documents()`
- `delete / remove` → `MetadataDB.delete_document()` + `VectorStoreClient.delete_document()`
- `upload / ingest` → returns guidance (actual upload goes through MCP/REST layer)

## Agent State

All nodes share a single `AgentState` TypedDict. Each node returns a **partial dict** (only updated keys) and LangGraph merges it into the full state automatically.

```
query               ──► router ──► intent, selected_countries, selected_parameters
                    ──► retriever ──► retrieved_chunks, retrieval_scores
                    ──► analyzer ──► extracted_data, analysis_text
                    ──► formatter ──► response_text, chart_config, sources
```

## LLM Compatibility Note

EPAM DIAL proxy blocks OpenAI function-calling (tools API). All structured LLM calls use the `invoke_structured(messages, ModelClass)` helper (`llm.py`) which:
1. Appends the Pydantic JSON schema to the system prompt
2. Calls `llm.ainvoke()` directly (plain completion)
3. Strips optional markdown code fences from the response
4. Parses with `json.loads()` + `model_class.model_validate()`

## Running the Agent

```bash
cd server

python3 - <<'EOF'
import asyncio
from src.rag import run_query, print_debug, configure_logging

configure_logging()

async def main():
    result = await run_query("Compare Belarus and Austria on personal freedom")
    print_debug(result)
    print(result["response_text"])

asyncio.run(main())
EOF
```

### Debug output

`configure_logging()` enables real-time logs during execution:
```
12:34:01  [router]    intent=comparison   countries=['Belarus', 'Austria']  params=['pf']
12:34:02  [retriever] strategy=comparison queries=['Belarus pf', 'Austria pf']  chunks=9
12:34:04  [analyzer]  intent=comparison   structured=True  context_chunks=9
```

`print_debug(result)` prints a post-run trace with emojis:
```
🔀 [router]   ⚖️ comparison  🌍 ['Belarus', 'Austria']
🔍 [retriever] 📌 comparison  📦 9 chunks  📉 top=[0.82, 0.80, ...]
🧠 [analyzer]  ✅ structured  📄 9 ctx chunks
🎨 [formatter] 📊 bar chart   🔗 9 sources
```
