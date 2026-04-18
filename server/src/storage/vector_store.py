"""
ChromaDB vector store wrapper using LangChain's Chroma integration
and Azure OpenAI embeddings (via EPAM DIAL proxy).

Metadata serialization note:
  ChromaDB only accepts scalar metadata values (str, int, float, bool).
  List fields (countries_mentioned, metrics_mentioned) are serialized to
  JSON strings on write and deserialized back to lists on read.
"""
from __future__ import annotations

import asyncio
import copy
import json
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings

from ..config import settings

_COLLECTION_NAME = "hfi_chunks"

# Metadata fields that contain lists and must be serialized for ChromaDB
_LIST_FIELDS = ("countries_mentioned", "metrics_mentioned")


def _serialize_metadata(meta: dict) -> dict:
    """Convert list fields to JSON strings for ChromaDB storage."""
    out = dict(meta)
    for field in _LIST_FIELDS:
        if field in out:
            out[field] = json.dumps(out[field])
        # Replace None with empty string — ChromaDB rejects None values
        if out.get(field) is None:
            out[field] = ""
    # ChromaDB also rejects None for any field
    return {k: ("" if v is None else v) for k, v in out.items()}


def _deserialize_metadata(meta: dict) -> dict:
    """Convert JSON-string list fields back to Python lists."""
    out = dict(meta)
    for field in _LIST_FIELDS:
        raw = out.get(field, "[]")
        if isinstance(raw, str):
            try:
                out[field] = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                out[field] = []
    return out


def _serialize_chunks(chunks: list[Document]) -> list[Document]:
    """Return copies of chunks with serialized metadata (non-destructive)."""
    result = []
    for chunk in chunks:
        c = copy.copy(chunk)
        c.metadata = _serialize_metadata(chunk.metadata)
        result.append(c)
    return result


def _deserialize_results(
    results: list[tuple[Document, float]],
) -> list[tuple[Document, float]]:
    out = []
    for doc, score in results:
        d = copy.copy(doc)
        d.metadata = _deserialize_metadata(doc.metadata)
        out.append((d, score))
    return out


def _make_embeddings() -> AzureOpenAIEmbeddings:
    # Do NOT pass `dimensions` — EPAM DIAL proxy rejects it with 403.
    # EPAM DIAL requires raw text input, not pre-tokenized integers.
    return AzureOpenAIEmbeddings(
        azure_endpoint=settings.epam_dial_base_url,
        api_key=settings.epam_dial_api_key,
        azure_deployment=settings.embeddings_deployment,
        api_version=settings.api_version,
        check_embedding_ctx_length=False,
    )


class VectorStoreClient:
    def __init__(self) -> None:
        persist_dir = str(settings.chroma_db_dir)
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self._embeddings = _make_embeddings()
        self._store = Chroma(
            collection_name=_COLLECTION_NAME,
            embedding_function=self._embeddings,
            persist_directory=persist_dir,
        )

    # ── Write ─────────────────────────────────────────────────────────────────

    async def add_documents(self, chunks: list[Document]) -> None:
        """Embed and store *chunks*. Serializes list metadata for ChromaDB."""
        if not chunks:
            return
        serialized = _serialize_chunks(chunks)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._store.add_documents, serialized)

    # ── Read ──────────────────────────────────────────────────────────────────

    async def search(
        self,
        query: str,
        top_k: int = 5,
        document_id: str | None = None,
        chunk_type: str | None = None,
        country: str | None = None,
        countries_mentioned: str | None = None,
    ) -> list[tuple[Document, float]]:
        """
        Semantic search. Returns (Document, relevance_score) pairs.
        relevance_score is in [0, 1] — higher is more relevant.
        List metadata fields are deserialized back to Python lists.

        country:             restrict to chunks whose primary_country == country (exact scalar).
        countries_mentioned: restrict to chunks whose countries_mentioned JSON string contains
                             this country name (substring match — e.g. '"Austria"' in
                             '["Austria","Belgium"]').  Used as a softer fallback when
                             primary_country detection fails.
        """
        where: dict | None = None
        filters: list[dict] = []
        if document_id:
            filters.append({"document_id": {"$eq": document_id}})
        if chunk_type:
            filters.append({"chunk_type": {"$eq": chunk_type}})
        if country:
            filters.append({"primary_country": {"$eq": country}})
        if countries_mentioned:
            # countries_mentioned is stored as a JSON string e.g. '["Austria","Belgium"]'
            # Wrap in quotes so we match the exact name, not a substring of another name.
            filters.append({"countries_mentioned": {"$contains": f'"{countries_mentioned}"'}})
        if len(filters) == 1:
            where = filters[0]
        elif len(filters) > 1:
            where = {"$and": filters}

        loop = asyncio.get_event_loop()
        raw: list[tuple[Document, float]] = await loop.run_in_executor(
            None,
            lambda: self._store.similarity_search_with_relevance_scores(
                query, k=top_k, filter=where
            ),
        )
        return _deserialize_results(raw)

    # ── Delete ────────────────────────────────────────────────────────────────

    async def delete_document(self, document_id: str) -> int:
        """Delete all chunks belonging to *document_id*. Returns count deleted."""
        collection = self._store._collection
        results = collection.get(where={"document_id": {"$eq": document_id}})
        ids = results.get("ids", [])
        if ids:
            collection.delete(ids=ids)
        return len(ids)

    # ── Stats ─────────────────────────────────────────────────────────────────

    def stats(self) -> dict:
        collection = self._store._collection
        return {
            "collection": _COLLECTION_NAME,
            "total_chunks": collection.count(),
            "persist_directory": str(settings.chroma_db_dir),
        }
