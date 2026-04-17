# PDF Ingestion Pipeline

Converts a PDF file into searchable chunks stored in ChromaDB and SQLite.

## Flow

```
PDF file
   │
   ▼
1. PDF Parser          → full markdown text + page markers
   │
   ▼
2. Table Extractor     → replaces GFM tables with <<HFI_TABLE_N>> placeholders
   │
   ▼
3. Header Chunker      → splits on H1/H2/H3 headers
   │
   ▼
4. Page Recovery       → each chunk gets its source page number
   │
   ▼
5. Table Expansion     → placeholders replaced back with original table text
   │
   ▼
6. Overflow Splitter   → chunks >1000 tokens split further (200-token overlap)
   │
   ▼
7. Metadata Enricher   → adds countries_mentioned, metrics_mentioned per chunk
   │
   ▼
8. Storage             → vectors → ChromaDB, document record → SQLite
```

## Step Details

### 1. PDF Parser (`pdf_parser.py`)
Uses `pymupdf4llm` to convert each PDF page to markdown. Pages are joined with `<!-- PAGE:N -->` markers so we can recover page numbers later.

### 2. Table Extractor (`table_extractor.py`)
GFM tables (markdown `|---|` format) are found and replaced with tokens like `<<HFI_TABLE_0>>`. This prevents tables from being cut in half during splitting.

### 3–4. Header Chunker + Page Recovery (`chunker.py`)
`MarkdownHeaderTextSplitter` splits the markdown on `#`, `##`, `###`. After splitting, each chunk scans its content for a `<!-- PAGE:N -->` marker. If none found, it inherits the last seen page number (carry-forward).

### 5. Table Expansion
Table placeholders are swapped back with the original table content. Each table becomes its own atomic chunk regardless of token count.

### 6. Overflow Splitter
Text chunks exceeding 1000 tokens are split again using `RecursiveCharacterTextSplitter.from_tiktoken_encoder` with 200-token overlap. Table chunks are never split.

### 7. Metadata Enricher (`metadata_enricher.py`)
Scans each chunk's text for:
- **`countries_mentioned`** — matches against 165 HFI jurisdictions (+ aliases like USA → United States)
- **`metrics_mentioned`** — matches against HFI parameter codes (`hf`, `pf`, `ef`, `hf_rank`, etc.)

All matches use word-boundary regex to avoid false positives.

### 8. Storage
- **ChromaDB** — chunk text is embedded via `text-embedding-3-large-1` (EPAM DIAL proxy) and stored with metadata
- **SQLite** — document record (id, name, path, chunk count, status) persisted via `aiosqlite`

## Chunk Metadata Schema

| Field | Type | Example |
|-------|------|---------|
| `document_id` | str | `"a1b2c3..."` |
| `document_name` | str | `"hfi-belgium.pdf"` |
| `chunk_type` | str | `"text"` / `"table"` |
| `page_number` | int | `42` |
| `section` | str | `"Personal Freedom"` |
| `countries_mentioned` | list[str] | `["Belgium", "France"]` |
| `metrics_mentioned` | list[str] | `["pf", "pf_rank"]` |

> **Note:** ChromaDB only accepts scalar metadata values. Lists are serialized to JSON strings on write and deserialized back on read transparently by `VectorStoreClient`.

## Running the Pipeline

```bash
cd server

# Dry run (no storage, no image API calls)
python3 -m src.ingestion.pipeline --pdf ../documents/hfi-belgium.pdf --no-images --no-store

# Full ingest (stores to ChromaDB + SQLite)
python3 -m src.ingestion.pipeline --pdf ../documents/hfi-belgium.pdf --no-images
```
