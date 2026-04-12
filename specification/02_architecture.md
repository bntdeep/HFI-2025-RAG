## 2. Architecture

### 2.1 High-Level Architecture
┌──────────────────────────────────────────────────────────────┐ │ React Frontend │ │ ┌──────────────────────────┬──────────────────────────────┐ │ │ │ Main Panel │ Debug Console │ │ │ │ ┌────────────────────┐ │ > [MCP] tool:search_docs │ │ │ │ │ Country Selector │ │ > [LLM] prompt: ... │ │ │ │ │ 🇨🇭 Switzerland │ │ > [LLM] tokens: 847 │ │ │ │ │ Parameter Picker │ │ > [Retriever] 5 chunks │ │ │ │ │ [Compare] Button │ │ > [MCP] tool:extract_data │ │ │ │ ├────────────────────┤ │ > [LLM] structured output │ │ │ │ │ Chat Interface │ │ > [Chart] bar_chart ready │ │ │ │ │ (streaming) │ │ │ │ │ │ ├────────────────────┤ │ │ │ │ │ │ Charts / Viz Area │ │ │ │ │ │ └────────────────────┘ │ │ │ │ └──────────────────────────┴──────────────────────────────┘ │ └──────────────────────┬───────────────────────────────────────┘ │ REST API + WebSocket ▼ ┌──────────────────────────────────────────────────────────────┐ │ Node.js BFF (Express) │ │ ├── REST endpoints (proxy to MCP tools) │ │ ├── WebSocket server (debug event streaming) │ │ ├── MCP Client (connects to Python MCP Server via SSE) │ │ ├── File upload handling (multer) │ │ └── Event aggregation & forwarding │ └──────────────────────┬───────────────────────────────────────┘ │ MCP Protocol (SSE/HTTP) ▼ ┌──────────────────────────────────────────────────────────────┐ │ Python MCP Server │ │ ┌────────────────────────────────────────────────────────┐ │ │ │ MCP Layer (mcp python sdk) │ │ │ │ ├── Tools │ │ │ │ │ ├── search_documents(query, top_k) │ │ │ │ │ ├── compare_countries(countries[], params[]) │ │ │ │ │ ├── get_country_profile(country) │ │ │ │ │ ├── extract_chart_data(query, chart_type) │ │ │ │ │ ├── upload_document(file) │ │ │ │ │ ├── delete_document(document_id) │ │ │ │ │ └── list_documents() │ │ │ │ ├── Resources │ │ │ │ │ ├── documents://list │ │ │ │ │ ├── countries://list │ │ │ │ │ └── parameters://list │ │ │ │ └── Prompts │ │ │ │ ├── analyze-country │ │ │ │ ├── compare-countries │ │ │ │ └── extract-trends │ │ │ ├────────────────────────────────────────────────────────┤ │ │ │ LangGraph Agent │ │ │ │ ├── Router Node (classify intent) │ │ │ │ ├── Retriever Node (ChromaDB vector search) │ │ │ │ ├── Analyzer Node (LLM structured extraction) │ │ │ │ └── Formatter Node (prepare chart-ready JSON) │ │ │ ├────────────────────────────────────────────────────────┤ │ │ │ PDF Processing Pipeline │ │ │ │ ├── pymupdf4llm (PDF → Markdown with headers) │ │ │ │ ├── unstructured (table extraction fallback) │ │ │ │ ├── gpt-4o vision (image/chart → text description) │ │ │ │ ├── MarkdownHeaderTextSplitter (header-based chunks) │ │ │ │ └── RecursiveCharacterTextSplitter (overflow chunks) │ │ │ ├────────────────────────────────────────────────────────┤ │ │ │ Storage │ │ │ │ ├── ChromaDB (vector store, persistent, ./chroma_db) │ │ │ │ ├── SQLite (document metadata, ./metadata.db) │ │ │ │ └── Filesystem (uploaded PDFs, ./uploads/) │ │ │ └────────────────────────────────────────────────────────┘ │ └──────────────────────────────────────────────────────────────┘




### 2.2 Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | React | 18+ |
| UI Library | MUI (Material UI) | 5+ |
| Charts | Recharts | 2+ |
| State Management | Zustand | 4+ |
| BFF | Express.js | 4+ |
| MCP Client (Node) | @modelcontextprotocol/sdk | latest |
| WebSocket | ws (Node) | 8+ |
| MCP Server | mcp python sdk | latest |
| LLM Orchestration | LangGraph | 0.2+ |
| LLM Framework | LangChain | 0.3+ |
| PDF Processing | pymupdf4llm | latest |
| Table Extraction | unstructured | latest |
| Vector DB | ChromaDB | 0.5+ |
| Embeddings | text-embedding-3-large (3072d) | - |
| Main LLM | gpt-4.1-2025-04-14 | - |
| Vision LLM | gpt-4o-2024-11-20 | - |
| Python | Python | 3.11+ |
| Node.js | Node.js | 20+ |

### 2.3 Models Configuration

```yaml
models:
  main_llm:
    provider: "epam-dial"
    base_url: "https://ai-proxy.lab.epam.com"
    deployment: "gpt-4.1-2025-04-14"
    api_version: "2024-12-01-preview"
    auth_header: "Api-Key"
    temperature: 0.1
    max_tokens: 4096
    context_window: 200000
    features:
      - structured_output
      - tool_calls
      - streaming

  vision:
    provider: "epam-dial"
    base_url: "https://ai-proxy.lab.epam.com"
    deployment: "gpt-4o-2024-11-20"
    api_version: "2024-12-01-preview"
    auth_header: "Api-Key"
    temperature: 0
    max_tokens: 1024
    purpose: "PDF image/chart description during ingestion"

  embeddings:
    provider: "epam-dial"
    base_url: "https://ai-proxy.lab.epam.com"
    deployment: "text-embedding-3-large-1"
    api_version: "2024-12-01-preview"
    auth_header: "Api-Key"
    dimensions: 3072
