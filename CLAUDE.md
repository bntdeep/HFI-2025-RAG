# HFI RAG — Claude Code Project Context

## Project
RAG application over the **2025 Human Freedom Index** PDF.
Users can query country freedom rankings, compare countries, and visualize results via an interactive UI.

Source document: `documents/2025-human-freedom-index.pdf`

## Architecture (3-tier)

```
React Frontend (client/)
    ↕  REST + WebSocket
Node.js BFF — Express (bff/)
    ↕  MCP Protocol (SSE)
Python MCP Server (server/)
    ├── LangGraph Agent
    ├── PDF Ingestion Pipeline
    └── Storage: ChromaDB + SQLite
```

## Repo Structure (planned)

```
hfi_rag/
├── CLAUDE.md
├── documents/                  # Source PDFs
├── specification/              # Specs + task tracker
│   ├── TASKS.md                ← development progress
│   └── 01–10_*.md              ← spec sections
├── server/                     # Python MCP Server + RAG
│   └── src/
│       ├── mcp/                # tools, resources, prompts
│       ├── rag/                # LangGraph agent, retriever, schemas
│       ├── ingestion/          # PDF pipeline, chunker, extractors
│       └── storage/            # ChromaDB, SQLite wrappers
├── bff/                        # Node.js Express BFF (TypeScript)
│   └── src/
│       ├── routes/             # /api/chat, /api/compare, /api/documents
│       └── websocket/          # debug event streaming
└── client/                     # React + Vite + MUI
    └── src/
        ├── components/
        ├── hooks/
        └── store/              # Zustand
```

## Tech Stack

| Layer | Tech | Version |
|-------|------|---------|
| Python server | Python | 3.11+ |
| MCP framework | mcp python sdk | latest |
| LLM orchestration | LangGraph | 0.2+ |
| LLM framework | LangChain | 0.3+ |
| PDF parsing | pymupdf4llm | latest |
| Vector DB | ChromaDB | 0.5+ |
| Node BFF | Express.js | 4+ |
| MCP client | @modelcontextprotocol/sdk | latest |
| Frontend | React + Vite | 18+ |
| UI | MUI (Material UI) | 5+ |
| Charts | Recharts | 2+ |
| State | Zustand | 4+ |

## Models (EPAM DIAL proxy)

| Role | Model | Notes |
|------|-------|-------|
| Main LLM | `gpt-4.1-2025-04-14` | structured output, tool calls, streaming |
| Vision | `gpt-4o-2024-11-20` | PDF image/chart description during ingestion |
| Embeddings | `text-embedding-3-large-1` | 3072 dimensions |

- **Base URL**: `https://ai-proxy.lab.epam.com`
- **Auth header**: `Api-Key`
- **API version**: `2024-12-01-preview`
- Credentials come from `.env` — never hardcode keys

## Key Design Decisions

- **PDF chunking**: header-based (`MarkdownHeaderTextSplitter` on H1/H2/H3); tables are never split
- **Chunk size**: 1000 tokens max for text, unlimited for tables; 200-token overlap
- **Metadata per chunk**: `countries_mentioned`, `metrics_mentioned`, `chunk_type` (text/table/image_description)
- **Agent intents**: `comparison | profile | trend | general | crud`
- **Streaming**: all query responses are SSE streams; debug events go over WebSocket

## MCP Tools (Python server exposes)

- `search_documents(query, top_k, document_id?, chunk_type?)`
- `compare_countries(countries[], parameters[], include_chart)`
- `get_country_profile(country)`
- `extract_chart_data(query, chart_type?)`
- `upload_document(file_path, document_name?)`
- `delete_document(document_id)`
- `list_documents()`

## Development Order

See `specification/TASKS.md` for current progress.

1. **Phase 0** — Reference specs (01, 02)
2. **Phase 1** — RAG core: project scaffold → PDF pipeline → LangGraph agent → MCP server
3. **Phase 2** — RAG validation: evaluation script + Postman collection
4. **Phase 3** — Frontend: Node.js BFF → React client

Do not start Phase 3 until Phase 2 evaluation passes (≥80% answer accuracy, ≥85% retrieval hit rate).

## Commands

```bash
# Python server
cd server && pip install -e .
python -m src.main          # start MCP server (port 8000)
python eval/run_evaluation.py

# Node BFF
cd bff && npm install
npm run dev                 # port 3001

# React client
cd client && npm install
npm run dev                 # port 5173
```
