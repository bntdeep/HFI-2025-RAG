import asyncio
from src.storage.vector_store import VectorStoreClient

async def main():
    vs = VectorStoreClient()

    queries = [
        "Belarus freedom ranking",
        "personal freedom score Argentina Armenia Belarus",
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