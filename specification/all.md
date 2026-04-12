SPECIFICATION (Part 1/3)

markdown


# Human Freedom Index RAG Application
## Technical Specification v1.0

---

## 1. Project Overview

### 1.1 Purpose
A RAG-based application that analyzes the "2025 Human Freedom Index"
PDF document, extracts structured data through natural language queries,
and visualizes results with interactive charts.

### 1.2 Core Features
- PDF document ingestion with intelligent chunking (by headers)
- Table and image/chart extraction from PDF
- Semantic search over document content (RAG)
- Natural language Q&A with structured JSON output
- Interactive data visualization (bar, pie, line, radar charts)
- Structured comparison UI (country selector + parameter picker)
- Free-form chat interface
- Real-time debug console showing full request traceability
- Document CRUD (upload, list, delete indexed documents)

### 1.3 Document
- **Name**: 2025 Human Freedom Index
- **Source**: Cato Institute / Fraser Institute
- **Content**: 160+ country rankings across personal and economic
  freedom dimensions
- **Format**: PDF (~100 pages)

---

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


3. PDF Processing Pipeline

3.1 Ingestion Flow



Upload PDF
    │
    ▼
[Step 1] pymupdf4llm: PDF → Markdown
    │   - Preserves headers (# ## ###)
    │   - Preserves tables (| col | col |)
    │   - Extracts page numbers
    │
    ▼
[Step 2] Detect content types per page
    │   - Text sections → keep as markdown
    │   - Tables → extract separately, tag as "table"
    │   - Images/Charts → extract as PNG
    │
    ▼
[Step 3] Process images (if any)
    │   - Send PNG to gpt-4o vision
    │   - Get text description of chart/graph
    │   - Tag as "image_description"
    │
    ▼
[Step 4] Header-based chunking
    │   - MarkdownHeaderTextSplitter on H1/H2/H3
    │   - Each chunk inherits section path metadata
    │   - Tables stay as whole chunks (never split mid-table)
    │
    ▼
[Step 5] Overflow splitting
    │   - If chunk > 1000 tokens → RecursiveCharacterTextSplitter
    │   - chunk_size=1000, overlap=200
    │   - Preserve metadata from parent chunk
    │
    ▼
[Step 6] Enrich metadata
    │   - Detect mentioned countries via NER or regex
    │   - Detect mentioned metrics/categories
    │   - Add page numbers, section hierarchy
    │
    ▼
[Step 7] Embed & store
    │   - text-embedding-3-large → 3072d vector
    │   - Store in ChromaDB collection
    │   - Store document metadata in SQLite
    │
    ▼
[Done] Document indexed, available for RAG
3.2 Chunk Metadata Schema

json


{
  "chunk_id": "uuid-v4",
  "document_id": "uuid-v4",
  "document_name": "2025-human-freedom-index.pdf",
  "page_number": 42,
  "section_h1": "CHAPTER 3: COUNTRY RANKINGS",
  "section_h2": "Eastern Europe",
  "section_h3": null,
  "chunk_type": "text | table | image_description",
  "countries_mentioned": ["Estonia", "Latvia", "Lithuania"],
  "metrics_mentioned": ["personal_freedom", "rule_of_law"],
  "token_count": 487,
  "chunk_index": 12
}
3.3 Chunking Rules

Headers define chunk boundaries (H1 > H2 > H3)
Tables are NEVER split — each table = one chunk, regardless of size
Max chunk size: 1000 tokens (text), unlimited (tables)
Overlap: 200 tokens for text chunks split by overflow
Image descriptions: one chunk per image/chart
Minimum chunk size: 50 tokens (skip smaller fragments)
Metadata inheritance: child chunks inherit parent section headers
4. MCP Server

4.1 Tools

search_documents
json


{
  "name": "search_documents",
  "description": "Semantic search over indexed documents. Returns relevant chunks with metadata.",
  "parameters": {
    "query": { "type": "string", "description": "Natural language search query" },
    "top_k": { "type": "integer", "default": 10, "description": "Number of chunks to return" },
    "document_id": { "type": "string", "optional": true, "description": "Filter by specific document" },
    "chunk_type": { "type": "string", "optional": true, "enum": ["text", "table", "image_description"] }
  },
  "returns": {
    "chunks": [
      {
        "content": "string",
        "metadata": "ChunkMetadata",
        "similarity_score": "float"
      }
    ]
  }
}
compare_countries
json


{
  "name": "compare_countries",
  "description": "Compare multiple countries across specified freedom parameters. Uses RAG to find relevant data, then LLM to extract and structure comparison.",
  "parameters": {
    "countries": { "type": "array", "items": "string", "minItems": 2, "maxItems": 6 },
    "parameters": { "type": "array", "items": "string", "description": "Freedom parameters to compare" },
    "include_chart": { "type": "boolean", "default": true }
  },
  "returns": {
    "comparison": {
      "countries": [
        {
          "name": "string",
          "flag": "string (emoji)",
          "scores": { "param_name": "float" }
        }
      ]
    },
    "chart_data": "ChartConfig | null",
    "analysis": "string",
    "sources": ["ChunkReference"]
  }
}
get_country_profile
json


{
  "name": "get_country_profile",
  "description": "Get comprehensive freedom profile for a single country.",
  "parameters": {
    "country": { "type": "string" }
  },
  "returns": {
    "country": "string",
    "flag": "string",
    "overall_rank": "integer",
    "overall_score": "float",
    "personal_freedom": { "score": "float", "subcategories": {} },
    "economic_freedom": { "score": "float", "subcategories": {} },
    "chart_data": "ChartConfig",
    "analysis": "string",
    "sources": ["ChunkReference"]
  }
}
extract_chart_data
json


{
  "name": "extract_chart_data",
  "description": "Extract data from document suitable for visualization. LLM analyzes retrieved chunks and returns chart-ready JSON.",
  "parameters": {
    "query": { "type": "string", "description": "What to visualize" },
    "chart_type": { "type": "string", "enum": ["bar", "pie", "line", "radar", "scatter"], "optional": true }
  },
  "returns": {
    "chart_config": {
      "type": "string (chart type)",
      "title": "string",
      "data": "array",
      "xKey": "string",
      "yKeys": ["string"],
      "colors": ["string"]
    },
    "insight": "string",
    "sources": ["ChunkReference"]
  }
}
upload_document
json


{
  "name": "upload_document",
  "description": "Upload and index a new PDF document.",
  "parameters": {
    "file_path": { "type": "string", "description": "Path to uploaded PDF" },
    "document_name": { "type": "string", "optional": true }
  },
  "returns": {
    "document_id": "string",
    "document_name": "string",
    "chunks_created": "integer",
    "pages_processed": "integer",
    "tables_found": "integer",
    "images_found": "integer",
    "status": "string"
  }
}
delete_document
json


{
  "name": "delete_document",
  "description": "Delete an indexed document and all its chunks from vector store.",
  "parameters": {
    "document_id": { "type": "string" }
  },
  "returns": {
    "deleted": "boolean",
    "chunks_removed": "integer"
  }
}
list_documents
json


{
  "name": "list_documents",
  "description": "List all indexed documents with metadata.",
  "parameters": {},
  "returns": {
    "documents": [
      {
        "document_id": "string",
        "document_name": "string",
        "uploaded_at": "ISO datetime",
        "pages": "integer",
        "chunks": "integer",
        "file_size_bytes": "integer"
      }
    ]
  }
}
4.2 Resources

yaml


resources:
  - uri: "documents://list"
    name: "Indexed Documents"
    description: "List of all currently indexed documents"
    
  - uri: "countries://list"  
    name: "Available Countries"
    description: "All countries found in indexed documents with flags"
    # Populated during ingestion by scanning chunk metadata
    
  - uri: "parameters://list"
    name: "Freedom Parameters"  
    description: "All comparison parameters/categories available"
    # Static list based on HFI structure:
    # personal_freedom, economic_freedom, rule_of_law,
    # security_safety, movement, religion, expression,
    # relationships, size_of_government, legal_system,
    # sound_money, freedom_to_trade, regulation
4.3 Prompts

yaml


prompts:
  - name: "analyze-country"
    description: "Analyze a single country's freedom profile"
    arguments:
      - name: "country"
        required: true
    template: |
      Analyze {country}'s freedom profile from the Human Freedom Index.
      Include overall ranking, key strengths and weaknesses across 
      personal and economic freedom categories.
      Return structured JSON with scores and analysis.

  - name: "compare-countries"  
    description: "Compare countries across parameters"
    arguments:
      - name: "countries"
        required: true
      - name: "parameters"
        required: true
    template: |
      Compare {countries} across these parameters: {parameters}.
      Extract exact scores from the document.
      Return structured comparison JSON with chart data.

  - name: "extract-trends"
    description: "Extract trends and patterns from the index"
    arguments:
      - name: "topic"
        required: true
    template: |
      Analyze trends related to {topic} in the Human Freedom Index.
      Identify patterns, top/bottom performers, regional differences.
      Return data suitable for visualization.
5. LangGraph Agent

5.1 Graph Structure



                    ┌──────────┐
                    │  START    │
                    └────┬─────┘
                         ▼
                  ┌──────────────┐
                  │   Router     │  Classify intent:
                  │   Node       │  comparison | profile | 
                  └──┬───┬───┬──┘  trend | general | crud
                     │   │   │
          ┌──────────┘   │   └──────────┐
          ▼              ▼              ▼
   ┌────────────┐ ┌────────────┐ ┌────────────┐
   │ Retriever  │ │ Retriever  │ │  CRUD      │
   │ (comparison│ │ (general)  │ │  Handler   │
   │  focused)  │ │            │ │            │
   └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
         ▼              ▼              ▼
   ┌────────────┐ ┌────────────┐       │
   │ Analyzer   │ │ Analyzer   │       │
   │ (structured│ │ (free-form)│       │
   │  extract)  │ │            │       │
   └─────┬──────┘ └─────┬──────┘       │
         ▼              ▼              │
   ┌────────────┐ ┌────────────┐       │
   │ Formatter  │ │ Formatter  │       │
   │ (chart     │ │ (text +    │       │
   │  config)   │ │  optional  │       │
   │            │ │  chart)    │       │
   └─────┬──────┘ └─────┬──────┘       │
         └───────┬───────┘──────────────┘
                 ▼
          ┌──────────┐
          │   END    │
          └──────────┘
5.2 Agent State Schema

python


class AgentState(TypedDict):
    # Input
    messages: list[BaseMessage]
    query: str
    mode: str  # "chat" | "structured"
    
    # Structured mode inputs (optional)
    selected_countries: list[str] | None
    selected_parameters: list[str] | None
    
    # Router output
    intent: str  # "comparison" | "profile" | "trend" | "general" | "crud"
    
    # Retriever output  
    retrieved_chunks: list[Document]
    retrieval_scores: list[float]
    
    # Analyzer output
    extracted_data: dict | None
    analysis_text: str | None
    
    # Formatter output
    chart_config: dict | None
    response_text: str
    sources: list[dict]
    
    # Debug / tracing
    debug_events: list[dict]
5.3 Structured Output Schemas (Pydantic)

python


class CountryScore(BaseModel):
    name: str
    flag: str  # emoji
    score: float
    rank: int | None = None

class ChartConfig(BaseModel):
    chart_type: Literal["bar", "pie", "line", "radar", "scatter"]
    title: str
    data: list[dict]
    x_key: str
    y_keys: list[str]
    colors: list[str] | None = None

class ComparisonResult(BaseModel):
    countries: list[CountryScore]
    parameters: list[str]
    scores_matrix: dict[str, dict[str, float]]  
    # {"Switzerland": {"personal_freedom": 9.23, ...}}
    chart_config: ChartConfig
    insight: str

class CountryProfile(BaseModel):
    name: str
    flag: str
    overall_rank: int
    overall_score: float
    personal_freedom_score: float
    economic_freedom_score: float
    subcategories: dict[str, float]
    strengths: list[str]
    weaknesses: list[str]
    chart_config: ChartConfig
    insight: str

class ChartExtractionResult(BaseModel):
    chart_config: ChartConfig
    insight: str
    data_completeness: float  # 0-1, how much data was found

class SourceReference(BaseModel):
    chunk_id: str
    page_number: int
    section: str
    relevance_score: float
6. Node.js BFF

6.1 REST API Endpoints

yaml


# Document Management
POST   /api/documents/upload     # Upload PDF → forward to MCP upload_document
GET    /api/documents            # List docs → forward to MCP list_documents  
DELETE /api/documents/:id        # Delete → forward to MCP delete_document

# Query / Chat
POST   /api/chat                 # Free-form chat query (streaming SSE response)
  body: { "message": "string", "conversation_id": "string" }
  response: SSE stream of tokens + final chart_config

POST   /api/compare              # Structured comparison
  body: { 
    "countries": ["Switzerland", "Japan"],
    "parameters": ["personal_freedom", "economic_freedom"]
  }
  response: SSE stream of tokens + final ComparisonResult

POST   /api/country/:name        # Country profile
  response: SSE stream + CountryProfile

# Metadata
GET    /api/countries            # Available countries with flags
GET    /api/parameters           # Available comparison parameters

# Health
GET    /api/health               # Health check (MCP connection status)
6.2 WebSocket (Debug Console)

yaml


# WS endpoint: ws://localhost:3001/ws/debug

# Server → Client events:
{
  "type": "mcp_call",
  "timestamp": "ISO",
  "tool": "search_documents",
  "params": { "query": "...", "top_k": 10 },
  "duration_ms": null  # null = started, number = completed
}

{
  "type": "llm_request",
  "timestamp": "ISO", 
  "model": "gpt-4.1-2025-04-14",
  "prompt_preview": "first 200 chars...",
  "token_count": 1847
}

{
  "type": "llm_response",
  "timestamp": "ISO",
  "model": "gpt-4.1-2025-04-14", 
  "response_preview": "first 200 chars...",
  "tokens_used": { "prompt": 1847, "completion": 423 },
  "duration_ms": 1200
}

{
  "type": "retrieval",
  "timestamp": "ISO",
  "query": "Switzerland freedom",
  "chunks_found": 5,
  "top_score": 0.89,
  "sections": ["Country Rankings", "Western Europe"]
}

{
  "type": "chart_ready",
  "timestamp": "ISO",
  "chart_type": "bar",
  "data_points": 10
}

{
  "type": "error",
  "timestamp": "ISO",
  "message": "string",
  "stack": "string | null"
}
7. React Frontend

7.1 Layout



┌─────────────────────────────────────────────────────────────────┐
│  Header: "Human Freedom Index Analyzer"    [📄 Documents]       │
├────────────────────────────────┬────────────────────────────────┤
│          MAIN PANEL (60%)      │      DEBUG CONSOLE (40%)       │
│                                │                                │
│  ┌──────────────────────────┐  │  ┌──────────────────────────┐ │
│  │  Mode Toggle:            │  │  │  [Clear] [Pause] [Auto]  │ │
│  │  [💬 Chat] [📊 Compare]  │  │  │                          │ │
│  └──────────────────────────┘  │  │  12:03:01 [MCP] call     │ │
│                                │  │    tool: search_documents │ │
│  === IF COMPARE MODE ===       │  │    query: "Switzerland"   │ │
│  ┌──────────────────────────┐  │  │                          │ │
│  │ Countries:               │  │  │  12:03:01 [Retriever]    │ │
│  │ [🇨🇭 Switzerland ▼]      │  │  │    chunks: 5             │ │
│  │ [🇯🇵 Japan        ▼]      │  │  │    top_score: 0.89      │ │
│  │ [+ Add country]          │  │  │                          │ │
│  │                          │  │  │  12:03:02 [LLM] request  │ │
│  │ Parameters:              │  │  │    model: gpt-4.1        │ │
│  │ ☑ Personal Freedom       │  │  │    tokens: 1847          │ │
│  │ ☑ Economic Freedom       │  │  │                          │ │
│  │ ☐ Rule of Law            │  │  │  12:03:03 [LLM] response │ │
│  │ ☐ Security & Safety      │  │  │    tokens: 423           │ │
│  │ ...                      │  │  │    duration: 1.2s        │ │
│  │                          │  │  │                          │ │
│  │ [🔍 Compare]             │  │  │  12:03:03 [Chart] ready  │ │
│  └──────────────────────────┘  │  │    type: bar             │ │
│                                │  │    points: 2             │ │
│  === CHART AREA ===            │  │                          │ │
│  ┌──────────────────────────┐  │  │                          │ │
│  │                          │  │  │                          │ │
│  │   [Recharts Bar/Pie/etc] │  │  │                          │ │
│  │                          │  │  │                          │ │
│  └──────────────────────────┘  │  │                          │ │
│                                │  │                          │ │
│  === ANALYSIS TEXT ===         │  │                          │ │
│  ┌──────────────────────────┐  │  │                          │ │
│  │ Switzerland scores higher│  │  │                          │ │
│  │ in personal freedom by...│  │  │                          │ │
│  │ Sources: p.42, p.67      │  │  │                          │ │
│  └──────────────────────────┘  │  │                          │ │
│                                │  │                          │ │
│  === IF CHAT MODE ===          │  └──────────────────────────┘ │
│  ┌──────────────────────────┐  │                                │
│  │ Chat messages...          │  │                                │
│  │ [Type message...] [Send] │  │                                │
│  └──────────────────────────┘  │                                │
├────────────────────────────────┴────────────────────────────────┤
│  Footer: Connected ● | Docs: 1 | Chunks: 347                   │
└─────────────────────────────────────────────────────────────────┘
7.2 Documents Modal



┌─────────────────────────────────────────────┐
│  📄 Indexed Documents                  [✕]  │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ 📕 2025-human-freedom-index.pdf     │    │
│  │    Pages: 98 | Chunks: 347          │    │
│  │    Uploaded: 2025-01-15 14:30       │    │
│  │    Size: 4.2 MB                     │    │
│  │                          [🗑 Delete] │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┐    │
│  │   Drag & drop PDF here              │    │
│  │   or [Browse Files]                 │    │
│  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘    │
│                                             │
│  ⏳ Processing: analyzing tables... (43%)   │
│                                             │
└─────────────────────────────────────────────┘
7.3 Theme (Grayscale Minimalist)

javascript


// MUI theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#ffffff' },
    secondary: { main: '#9e9e9e' },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#e0e0e0',
      secondary: '#9e9e9e',
    },
  },
  typography: {
    fontFamily: '"JetBrains Mono", "Fira Code", monospace',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 2,
          textTransform: 'none',
        },
      },
    },
  },
});

// Chart colors (grayscale with one accent)
const CHART_COLORS = [
  '#e0e0e0', // white-ish
  '#9e9e9e', // medium gray  
  '#616161', // dark gray
  '#424242', // darker
  '#bdbdbd', // light gray
  '#757575', // mid
];
7.4 Component Tree



App
├── Header
│   ├── Logo + Title
│   ├── ConnectionStatus (● Connected)
│   └── DocumentsButton → DocumentsModal
├── MainLayout (split horizontal)
│   ├── MainPanel (left 60%)
│   │   ├── ModeToggle (Chat | Compare)
│   │   ├── ComparePanel (if compare mode)
│   │   │   ├── CountrySelector (multi-select dropdown with flags)
│   │   │   ├── ParameterPicker (checkboxes)
│   │   │   └── CompareButton
│   │   ├── ChatPanel (if chat mode)
│   │   │   ├── MessageList (streaming messages)
│   │   │   └── MessageInput
│   │   ├── ChartArea
│   │   │   └── DynamicChart (renders based on chart_config)
│   │   ├── AnalysisText (markdown rendered)
│   │   └── SourceReferences (collapsible)
│   └── DebugConsole (right 40%)
│       ├── ConsoleToolbar (Clear | Pause | AutoScroll)
│       └── EventList (virtualized scroll)
│           └── DebugEvent (color-coded by type)
├── DocumentsModal
│   ├── DocumentList
│   │   └── DocumentCard (name, stats, delete)
│   └── UploadArea (drag & drop + progress)
└── Footer
    └── Stats (docs count, chunks count, connection)
8. Evaluation

8.1 Evaluation Dataset

Create eval/eval_dataset.json with 25+ question-answer pairs manually verified against the PDF document:

json


{
  "eval_questions": [
    {
      "id": "eval_001",
      "question": "Which country ranks #1 in the 2025 Human Freedom Index?",
      "expected_answer": "Switzerland",
      "answer_type": "exact_match",
      "category": "factual"
    },
    {
      "id": "eval_002", 
      "question": "What is Japan's personal freedom score?",
      "expected_answer": "8.59",
      "answer_type": "numeric",
      "tolerance": 0.05,
      "category": "factual"
    },
    {
      "id": "eval_003",
      "question": "Compare the economic freedom of Estonia and Poland",
      "expected_data": {
        "Estonia": { "economic_freedom": 8.15 },
        "Poland": { "economic_freedom": 7.02 }
      },
      "answer_type": "comparison",
      "category": "extraction"
    },
    {
      "id": "eval_004",
      "question": "Which region has the lowest average personal freedom?",
      "expected_answer": "Middle East & North Africa",
      "answer_type": "exact_match",
      "category": "analytical"
    }
    // ... 21+ more questions
  ]
}
8.2 Metrics

Metric 1: Answer Accuracy (Primary)
python


# For exact_match questions:
accuracy = correct_answers / total_questions

# For numeric questions:
numeric_accuracy = answers_within_tolerance / total_numeric_questions

# Target: >= 80%
Metric 2: Retrieval Relevance
python


# For each question, check if the retrieved chunks 
# contain the information needed to answer

retrieval_hit_rate = questions_with_relevant_chunks / total_questions

# A "hit" = at least one chunk in top_k contains the answer
# Target: >= 85%
Metric 3: Chart Data Correctness
python


# For comparison/extraction questions:
# Check if chart_data values match expected values

chart_accuracy = correct_data_points / total_data_points

# Target: >= 75%
8.3 Evaluation Script



python eval/run_evaluation.py

Output:
┌─────────────────────────────────────────────┐
│  EVALUATION RESULTS                         │
├─────────────────────────────────────────────┤
│  Questions evaluated: 25                    │
│                                             │
│  Answer Accuracy:     84% (21/25)           │
│  Retrieval Hit Rate:  88% (22/25)           │
│  Chart Data Accuracy: 78% (18/23)           │
│                                             │
│  By Category:                               │
│    Factual:    90% (9/10)                   │
│    Extraction: 80% (8/10)                   │
│    Analytical: 80% (4/5)                    │
│                                             │
│  Failed Questions:                          │
│    eval_007: Expected "Norway", got "Sweden" │
│    eval_015: Score off by 0.3               │
│    eval_019: Chart missing 2 countries       │
│    eval_022: Retriever missed relevant chunk │
└─────────────────────────────────────────────┘
9. Project Structure



human-freedom-index-rag/
├── README.md
├── docker-compose.yml (optional)
│
├── server/                          # Python MCP Server
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                  # MCP Server entry point
│   │   ├── config.py                # Models, paths, settings
│   │   ├── mcp/
│   │   │   ├── __init__.py
│   │   │   ├── server.py            # MCP server setup
│   │   │   ├── tools.py             # Tool definitions
│   │   │   ├── resources.py         # Resource definitions
│   │   │   └── prompts.py           # Prompt templates
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py             # LangGraph agent
│   │   │   ├── retriever.py         # ChromaDB retriever
│   │   │   ├── chains.py            # LLM chains (analysis, extraction)
│   │   │   └── schemas.py           # Pydantic output schemas
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py          # Full ingestion pipeline
│   │   │   ├── pdf_parser.py        # pymupdf4llm wrapper
│   │   │   ├── chunker.py           # Header-based chunking
│   │   │   ├── table_extractor.py   # Table detection & extraction
│   │   │   ├── image_extractor.py   # Image extraction + vision
│   │   │   └── metadata_enricher.py # Country/metric detection
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   ├── vector_store.py      # ChromaDB wrapper
│   │   │   └── metadata_db.py       # SQLite document metadata
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── countries.py          # Country names + flag emojis
│   │       ├── parameters.py         # HFI parameter definitions
│   │       └── debug_logger.py       # Debug event emitter
│   ├── eval/
│   │   ├── eval_dataset.json         # 25+ Q&A pairs
│   │   ├── run_evaluation.py         # Evaluation script
│   │   └── results/                  # Evaluation output
│   ├── uploads/                      # Uploaded PDFs
│   ├── chroma_db/                    # ChromaDB persistent storage
│   └── metadata.db                   # SQLite
│
├── bff/                              # Node.js BFF
│   ├── package.json
│   ├── tsconfig.json
│   ├── .env.example
│   ├── src/
│   │   ├── index.ts                  # Express entry point
│   │   ├── config.ts                 # BFF configuration
│   │   ├── mcp/
│   │   │   ├── client.ts             # MCP client (SSE transport)
│   │   │   └── types.ts              # MCP response types
│   │   ├── routes/
│   │   │   ├── documents.ts          # /api/documents/*
│   │   │   ├── chat.ts               # /api/chat (SSE streaming)
│   │   │   ├── compare.ts            # /api/compare
│   │   │   ├── country.ts            # /api/country/:name
│   │   │   └── metadata.ts           # /api/countries, /api/parameters
│   │   ├── websocket/
│   │   │   └── debug.ts              # WebSocket debug streaming
│   │   └── middleware/
│   │       ├── error.ts
│   │       └── logging.ts
│   └── postman/
│       └── mcp-test-collection.json  # Postman collection
│
├── client/                           # React Frontend
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── theme.ts                  # MUI grayscale theme
│   │   ├── store/
│   │   │   ├── useAppStore.ts        # Zustand store
│   │   │   └── useDebugStore.ts      # Debug events store
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── MainLayout.tsx    # Split panel
│   │   │   │   └── Footer.tsx
│   │   │   ├── main/
│   │   │   │   ├── ModeToggle.tsx
│   │   │   │   ├── ComparePanel.tsx
│   │   │   │   ├── CountrySelector.tsx
│   │   │   │   ├── ParameterPicker.tsx
│   │   │   │   ├── ChatPanel.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   ├── ChartArea.tsx
│   │   │   │   ├── DynamicChart.tsx
│   │   │   │   ├── AnalysisText.tsx
│   │   │   │   └── SourceReferences.tsx
│   │   │   ├── debug/
│   │   │   │   ├── DebugConsole.tsx
│   │   │   │   ├── ConsoleToolbar.tsx
│   │   │   │   └── DebugEvent.tsx
│   │   │   └── documents/
│   │   │       ├── DocumentsModal.tsx
│   │   │       ├── DocumentCard.tsx
│   │   │       └── UploadArea.tsx
│   │   ├── hooks/
│   │   │   ├── useChat.ts
│   │   │   ├── useCompare.ts
│   │   │   ├── useDocuments.ts
│   │   │   ├── useDebugWebSocket.ts
│   │   │   └── useCountries.ts
│   │   ├── api/
│   │   │   └── client.ts             # Axios/fetch wrapper
│   │   └── types/
│   │       ├── chart.ts
│   │       ├── country.ts
│   │       └── debug.ts
│   └── public/
│       └── favicon.ico
│
└── docs/
    ├── SPECIFICATION.md              # This document
    ├── ARCHITECTURE.md
    └── EVALUATION.md
10. Postman Collection Skeleton

json


{
  "info": {
    "name": "HFI RAG - MCP Server Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    { "key": "base_url", "value": "http://localhost:8000" }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/health"
      }
    },
    {
      "name": "List Documents",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"list_documents\",\"arguments\":{}},\"id\":1}"
        }
      }
    },
    {
      "name": "Search Documents",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"search_documents\",\"arguments\":{\"query\":\"Switzerland freedom score\",\"top_k\":5}},\"id\":2}"
        }
      }
    },
    {
      "name": "Compare Countries",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"compare_countries\",\"arguments\":{\"countries\":[\"Switzerland\",\"Japan\"],\"parameters\":[\"personal_freedom\",\"economic_freedom\"],\"include_chart\":true}},\"id\":3}"
        }
      }
    },
    {
      "name": "Get Country Profile",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"get_country_profile\",\"arguments\":{\"country\":\"Switzerland\"}},\"id\":4}"
        }
      }
    },
    {
      "name": "Extract Chart Data",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"extract_chart_data\",\"arguments\":{\"query\":\"Top 10 countries by overall freedom score\",\"chart_type\":\"bar\"}},\"id\":5}"
        }
      }
    },
    {
      "name": "List Resources - Countries",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"resources/read\",\"params\":{\"uri\":\"countries://list\"},\"id\":6}"
        }
      }
    },
    {
      "name": "List Resources - Parameters",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"resources/read\",\"params\":{\"uri\":\"parameters://list\"},\"id\":7}"
        }
      }
    }
  ]
}