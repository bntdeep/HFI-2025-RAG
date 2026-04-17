# MCP Server

Thin protocol adapter that exposes the HFI RAG agent and storage layer as MCP tools, resources, and prompts over SSE.

## Architecture

```
MCP Client (Node.js BFF)
   │  MCP Protocol over SSE
   ▼
FastMCP Server  (src/mcp/server.py)
   │
   ├── Tools (8)
   │     ├── Document management  → MetadataDB + VectorStoreClient  (no LLM)
   │     └── Agent queries        → run_query() → LangGraph agent
   │
   ├── Resources (3)              → static/live JSON over URI
   │
   └── Prompts (3)                → pre-filled message templates
```

## Tools

### Document Management (no LLM)

| Tool | Parameters | Calls | Returns |
|------|-----------|-------|---------|
| `list_documents` | — | `MetadataDB.list_documents()` | `[{id, name, pages, chunks, status}]` |
| `upload_document` | `file_path`, `document_name?` | `ingest_document()` | `{document_id, chunks_created, pages_processed, ...}` |
| `delete_document` | `document_id` | `MetadataDB.delete_document()` + `VectorStoreClient.delete_document()` | `{deleted, chunks_removed}` |
| `search_documents` | `query`, `top_k=10`, `document_id?`, `chunk_type?` | `VectorStoreClient.search()` | `[{content, metadata, similarity_score}]` |

`search_documents` is a raw semantic search — no LLM, no analysis, just ranked chunks.

### Agent Queries (LLM via run_query)

| Tool | Parameters | Agent mode | Returns |
|------|-----------|------------|---------|
| `query` | `text`, `history?` | `mode="chat"` | `{response_text, chart_config, sources}` |
| `compare_countries` | `countries[]`, `parameters?`, `include_chart=True` | `mode="structured"`, explicit countries injected | `{response_text, chart_config, sources}` |
| `get_country_profile` | `country` | `mode="structured"`, explicit country injected | `{response_text, chart_config, sources}` |
| `extract_chart_data` | `query`, `chart_type?` | `mode="chat"` | `{chart_config, insight, sources}` |

`compare_countries` and `get_country_profile` pass `selected_countries` directly to `run_query`, bypassing the router's LLM extraction step.

## Resources

Resources are read-only and fetched by URI.

| URI | Content | Live? |
|-----|---------|-------|
| `documents://list` | All indexed documents (same as `list_documents` tool) | Yes — queries SQLite each time |
| `countries://list` | All 165 HFI jurisdictions: `{name, flag, iso2, region}` | No — static registry |
| `parameters://list` | All HFI freedom parameters: `{code, name, parent}` | No — static registry |

The `countries://list` and `parameters://list` resources are useful for clients to build filter dropdowns without making an LLM call.

## Prompts

Prompts return pre-filled user message strings that MCP clients can inject into the conversation.

| Prompt | Arguments | Use case |
|--------|-----------|---------|
| `analyze_country` | `country` | Single-country profile analysis |
| `compare_countries_prompt` | `countries`, `parameters` | Multi-country comparison |
| `extract_trends` | `topic` | Trend and pattern analysis |

## Server Startup

```bash
cd server && python -m src.main
```

`src/main.py` loads `.env`, configures logging, then starts the FastMCP SSE server:

```python
app.run(transport="sse", port=settings.mcp_server_port)  # default: 8000
```

The server listens at `http://localhost:8000/sse`.

## MCP Inspector (dev testing)

```bash
cd server && mcp dev src/main.py
```

Opens a browser-based inspector where you can invoke any tool interactively without a BFF.

## Response Shape (agent tools)

All agent-powered tools return the same three fields:

```json
{
  "response_text": "## Comparison: Belarus vs Austria\n...",
  "chart_config": {
    "chart_type": "bar",
    "title": "Personal Freedom: Belarus vs Austria",
    "data": [...],
    "xKey": "country",
    "yKeys": ["pf"],
    "colors": ["#4CAF50", "#2196F3"]
  },
  "sources": [
    {"chunk_id": "...", "page_number": 42, "section": "Personal Freedom", "relevance_score": 0.82}
  ]
}
```

`chart_config` is `null` for general/trend queries that don't produce structured data.
