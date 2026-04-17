# HFI RAG Server — Testing Guide

## Prerequisites

- Python 3.11+
- EPAM DIAL API key

---

## 1. Install dependencies

```bash
cd server
pip3 install -e ".[dev]"
```

---

## 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set your key:

```
EPAM_DIAL_API_KEY=your_key_here
```

---

## 3. Test chunking only (no API calls, no storage)

Parses the PDF and chunks it locally — no network required.

```bash
cd server
python3 -m src.ingestion.pipeline \
  --pdf ../documents/2025-human-freedom-index.pdf \
  --no-images \
  --no-store
```

Expected output:
```
[pipeline] Parsing PDF: 2025-human-freedom-index.pdf
[pipeline] Parsed 438 pages
[pipeline] Chunking text...
[pipeline] Created 932 text/table chunks
[pipeline] Enriching metadata (countries, parameters)...
[pipeline] Done.
Document : 2025-human-freedom-index.pdf
Pages    : 438
Chunks   : 932 total  (467 text | 465 table | 0 image)
Tokens   : 555,211
```

---

## 4. Test chunking + embedding + storage (requires DIAL key)

Embeds all chunks via `text-embedding-3-large-1` and stores them in ChromaDB + SQLite.
**This will make ~932 embedding API calls.**

```bash
cd server
python3 -m src.ingestion.pipeline \
  --pdf ../documents/2025-human-freedom-index.pdf \
  --no-images
```

After completion, verify storage:

```bash
python3 - <<'EOF'
import asyncio
from src.storage.vector_store import VectorStoreClient
from src.storage.metadata_db import MetadataDB

async def main():
    vs = VectorStoreClient()
    db = MetadataDB()
    print("ChromaDB stats:", vs.stats())
    print("Documents in SQLite:", await db.list_documents())

asyncio.run(main())
EOF
```

---

## 5. Test full pipeline including image descriptions (requires DIAL key)

Sends each chart/figure to `gpt-4o` vision model for description.

```bash
cd server
python3 -m src.ingestion.pipeline \
  --pdf ../documents/2025-human-freedom-index.pdf
```

---

## 6. Test a semantic search query (requires storage from step 4)

```bash
python3 - <<'EOF'
import asyncio
from src.storage.vector_store import VectorStoreClient

async def main():
    vs = VectorStoreClient()

    queries = [
        "Switzerland freedom ranking",
        "personal freedom score Estonia Latvia Lithuania",
        "countries with declining freedom 2023",
    ]
    for q in queries:
        print(f"\n--- Query: {q!r}")
        results = await vs.search(q, top_k=3)
        for doc, score in results:
            m = doc.metadata
            print(f"  [{score:.3f}] page={m.get('page_number')} type={m['chunk_type']}")
            print(f"           countries={m['countries_mentioned'][:4]}")
            print(f"           {doc.page_content[:120].strip()!r}")

asyncio.run(main())
EOF
```

---

## 7. Inspect a specific chunk interactively

```bash
python3 - <<'EOF'
import asyncio
from src.ingestion.pipeline import ingest_document

async def main():
    result = await ingest_document(
        "../documents/2025-human-freedom-index.pdf",
        extract_images=False,
        store=False,
    )
    chunks = result.chunks

    # Filter to chunks mentioning a specific country
    country = "Switzerland"
    matches = [c for c in chunks if country in c.metadata["countries_mentioned"]]
    print(f"Chunks mentioning {country}: {len(matches)}")
    for c in matches[:3]:
        m = c.metadata
        print(f"\n  type={m['chunk_type']} page={m['page_number']} tokens={m['token_count']}")
        print(f"  {c.page_content[:200].strip()!r}")

asyncio.run(main())
EOF
```

---

## Chunk metadata schema reference

Each chunk has this metadata after ingestion:

| Field | Type | Example |
|-------|------|---------|
| `chunk_id` | str (UUID) | `"a3f2..."` |
| `document_id` | str (UUID) | `"f821..."` |
| `document_name` | str | `"2025-human-freedom-index.pdf"` |
| `chunk_type` | str | `"text"` / `"table"` / `"image_description"` |
| `chunk_index` | int | `42` |
| `page_number` | int | `87` |
| `section_h1` | str \| None | `"# Country Profiles"` |
| `section_h2` | str \| None | `"## Switzerland"` |
| `section_h3` | str \| None | `None` |
| `countries_mentioned` | list[str] | `["Switzerland", "Norway"]` |
| `metrics_mentioned` | list[str] | `["hf", "pf", "ef_legal"]` |
| `token_count` | int | `487` |
