"""
Inspect chunk metadata for a PDF without storing to ChromaDB.
Run from server/:  python -m testing.inspect_chunk
"""
import asyncio
from dotenv import load_dotenv
load_dotenv()

from src.rag import configure_logging
from src.ingestion.pipeline import ingest_document

PDF_PATH = "/Users/Artsiom_Sushchenia/VSCodeProjects/hfi_rag/documents/Albania-Burundi.pdf"
COUNTRIES = ["Albania", "Austria", "Bolivia"]

async def main():
    result = await ingest_document(PDF_PATH, extract_images=False, store=False)
    chunks = result.chunks
    print(f"Total chunks: {len(chunks)}\n")

    for country in COUNTRIES:
        matches = [c for c in chunks if country in c.metadata.get("countries_mentioned", [])]
        primary = [c for c in matches if c.metadata.get("primary_country") == country]
        print(f"=== {country}: {len(matches)} chunks mentioned, {len(primary)} primary ===")
        for c in primary[:3]:
            m = c.metadata
            print(f"  type={m['chunk_type']}  section_h2={m.get('section_h2')!r}  section_country={m.get('section_country')!r}")
            print(f"  content[:100]: {c.page_content[:100].strip()!r}")
        print()

asyncio.run(main())