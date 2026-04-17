"""
Retriever node — fetches relevant chunks from ChromaDB.

Two strategies selected by intent already in state:
  comparison  — parallel per-country searches (top_k=3 each), deduped by chunk_id
  general     — single search (top_k=8); also used for profile and trend
"""
from __future__ import annotations

import asyncio
import logging

from langchain_core.documents import Document

from ...storage.vector_store import VectorStoreClient
from ..schemas import AgentState

logger = logging.getLogger(__name__)

# Module-level singleton avoids reloading the ChromaDB HNSW index per request
_vs = VectorStoreClient()


async def retriever_node(state: AgentState) -> dict:
    intent = state["intent"]
    query = state["query"]
    countries = state.get("selected_countries") or []
    parameters = state.get("selected_parameters") or []

    if intent == "comparison" and countries:
        param_hint = " ".join(parameters) if parameters else "freedom score rank"
        search_queries = [f"{c} {param_hint}" for c in countries]
        results = await _comparison_search(countries, parameters)
        strategy = "comparison"
    else:
        search_queries = [query]
        results = await _vs.search(query, top_k=8)
        strategy = "general"

    # Deduplicate by chunk_id, preserve relevance order
    seen: set[str] = set()
    unique: list[tuple[Document, float]] = []
    for doc, score in results:
        cid = doc.metadata.get("chunk_id", "")
        if cid not in seen:
            seen.add(cid)
            unique.append((doc, score))

    chunks = [doc for doc, _ in unique]
    scores = [score for _, score in unique]

    top_scores = [round(s, 3) for s in scores[:5]]
    logger.info(
        "[retriever] strategy=%-12s queries=%s  chunks=%d  top_scores=%s",
        strategy, search_queries, len(chunks), top_scores,
    )

    return {
        "retrieved_chunks": chunks,
        "retrieval_scores": scores,
        "debug_events": state.get("debug_events", []) + [{
            "node": "retriever",
            "strategy": strategy,
            "search_queries": search_queries,
            "chunks_retrieved": len(chunks),
            "top_scores": top_scores,
        }],
    }


async def _comparison_search(
    countries: list[str],
    parameters: list[str],
) -> list[tuple[Document, float]]:
    """
    Issue multiple focused searches per country concurrently.

    Two queries per country:
    1. "<country> <param_hint>" — finds sections mentioning both
    2. "<country> Human Freedom Index score rank" — catches the country's profile page

    Using short, country-specific queries avoids embedding drift toward other countries.
    """
    param_hint = " ".join(parameters) if parameters else "freedom score rank"
    tasks = []
    for country in countries:
        tasks.append(_vs.search(f"{country} {param_hint}", top_k=5))
        tasks.append(_vs.search(f"{country} Human Freedom Index score rank", top_k=5))
    nested = await asyncio.gather(*tasks)
    flat: list[tuple[Document, float]] = []
    for results in nested:
        flat.extend(results)
    flat.sort(key=lambda x: x[1], reverse=True)
    return flat
