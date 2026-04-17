import asyncio
from src.ingestion.pipeline import ingest_document

async def main():
    result = await ingest_document(
        "/Users/Artsiom_Sushchenia/Library/CloudStorage/OneDrive-EPAM/Learn/trainings/AI Architect/module 3. rag/hfi_rag/documents/hfi-belgium.pdf",
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