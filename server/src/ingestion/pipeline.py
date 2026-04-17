"""
Full ingestion pipeline — Steps 1-7.

Usage (CLI):
    cd server
    python -m src.ingestion.pipeline --pdf ../documents/2025-human-freedom-index.pdf

Usage (API):
    from src.ingestion.pipeline import ingest_document
    result = await ingest_document(pdf_path, document_name="HFI 2025")
"""
from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from langchain_core.documents import Document

from ..config import settings
from .pdf_parser import parse_pdf
from .chunker import chunk_document
from .image_extractor import extract_image_chunks
from .metadata_enricher import enrich_chunks


@dataclass
class IngestionResult:
    document_id: str
    document_name: str
    pdf_path: str
    total_pages: int
    total_chunks: int
    text_chunks: int
    table_chunks: int
    image_chunks: int
    total_tokens: int
    chunks: list[Document] = field(default_factory=list, repr=False)

    def summary(self) -> str:
        lines = [
            f"Document : {self.document_name} ({self.document_id})",
            f"Pages    : {self.total_pages}",
            f"Chunks   : {self.total_chunks} total  "
            f"({self.text_chunks} text | {self.table_chunks} table | {self.image_chunks} image)",
            f"Tokens   : {self.total_tokens:,}",
        ]
        return "\n".join(lines)


async def ingest_document(
    pdf_path: str | Path,
    document_name: str | None = None,
    document_id: str | None = None,
    *,
    extract_images: bool = True,
    store: bool = True,
) -> IngestionResult:
    """
    Run the full ingestion pipeline for a PDF file.

    Args:
        pdf_path:       Path to the PDF.
        document_name:  Human-readable name (defaults to filename).
        document_id:    Stable UUID for this document (auto-generated if None).
        extract_images: Whether to call the vision LLM for image descriptions.
        store:          Whether to persist chunks to ChromaDB + SQLite.

    Returns:
        IngestionResult with all chunk metadata and a human-readable summary.
    """
    pdf_path = Path(pdf_path)
    document_id = document_id or str(uuid.uuid4())
    document_name = document_name or pdf_path.name

    print(f"[pipeline] Parsing PDF: {pdf_path.name}")

    # ── Step 1: PDF → markdown ────────────────────────────────────────────────
    parsed = parse_pdf(pdf_path)
    print(f"[pipeline] Parsed {parsed.total_pages} pages")

    # ── Steps 4-5: chunk text ─────────────────────────────────────────────────
    print("[pipeline] Chunking text...")
    text_and_table_chunks = chunk_document(
        full_markdown=parsed.full_markdown,
        document_id=document_id,
        document_name=document_name,
        chunk_size=settings.chunk_size_tokens,
        chunk_overlap=settings.chunk_overlap_tokens,
        min_chunk_size=settings.min_chunk_size_tokens,
    )
    print(f"[pipeline] Created {len(text_and_table_chunks)} text/table chunks")

    # ── Step 3: image descriptions ────────────────────────────────────────────
    image_chunks: list[Document] = []
    if extract_images and parsed.page_numbers_with_images:
        print(f"[pipeline] Describing images on {len(parsed.page_numbers_with_images)} pages...")
        image_chunks = await extract_image_chunks(
            pdf_path=pdf_path,
            pages=parsed.pages,
            document_id=document_id,
            document_name=document_name,
        )
        print(f"[pipeline] Created {len(image_chunks)} image chunks")

    # ── Step 6: enrich metadata ───────────────────────────────────────────────
    all_chunks = text_and_table_chunks + image_chunks
    print("[pipeline] Enriching metadata (countries, parameters)...")
    enrich_chunks(all_chunks)

    # ── Re-index chunk_index for image chunks ─────────────────────────────────
    # Text/table chunks already have sequential chunk_index; image chunks start after
    offset = len(text_and_table_chunks)
    for i, ch in enumerate(image_chunks):
        ch.metadata["chunk_index"] = offset + i

    # ── Step 7: store ─────────────────────────────────────────────────────────
    if store:
        await _store_chunks(all_chunks, document_id, document_name, pdf_path)

    # ── Build result ──────────────────────────────────────────────────────────
    text_n  = sum(1 for c in all_chunks if c.metadata.get("chunk_type") == "text")
    table_n = sum(1 for c in all_chunks if c.metadata.get("chunk_type") == "table")
    img_n   = sum(1 for c in all_chunks if c.metadata.get("chunk_type") == "image_description")
    total_tokens = sum(c.metadata.get("token_count", 0) for c in all_chunks)

    result = IngestionResult(
        document_id=document_id,
        document_name=document_name,
        pdf_path=str(pdf_path),
        total_pages=parsed.total_pages,
        total_chunks=len(all_chunks),
        text_chunks=text_n,
        table_chunks=table_n,
        image_chunks=img_n,
        total_tokens=total_tokens,
        chunks=all_chunks,
    )
    print(f"[pipeline] Done.\n{result.summary()}")
    return result


async def _store_chunks(
    chunks: list[Document],
    document_id: str,
    document_name: str,
    pdf_path: Path,
) -> None:
    """Persist chunks to ChromaDB and record document metadata in SQLite."""
    # Lazy import to avoid import errors when running without EPAM DIAL creds
    from ..storage.vector_store import VectorStoreClient
    from ..storage.metadata_db import MetadataDB

    vs = VectorStoreClient()
    db = MetadataDB()

    await db.add_document(
        document_id=document_id,
        document_name=document_name,
        pdf_path=str(pdf_path),
        total_chunks=len(chunks),
    )

    print(f"[pipeline] Embedding and storing {len(chunks)} chunks in ChromaDB...")
    await vs.add_documents(chunks)
    print("[pipeline] Storage complete.")


# ── CLI entry point ────────────────────────────────────────────────────────────

def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Ingest a PDF into the HFI RAG system")
    parser.add_argument("--pdf", required=True, help="Path to PDF file")
    parser.add_argument("--name", default=None, help="Document display name")
    parser.add_argument("--no-images", action="store_true", help="Skip image extraction")
    parser.add_argument("--no-store", action="store_true", help="Dry-run: skip ChromaDB/SQLite")
    args = parser.parse_args()

    result = asyncio.run(ingest_document(
        pdf_path=args.pdf,
        document_name=args.name,
        extract_images=not args.no_images,
        store=not args.no_store,
    ))
    print("\n" + result.summary())


if __name__ == "__main__":
    _cli()
