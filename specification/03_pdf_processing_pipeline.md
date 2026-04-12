## 3. PDF Processing Pipeline

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
