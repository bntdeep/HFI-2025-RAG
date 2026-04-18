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


async def _search_for_country(
    country: str,
    param_hint: str,
) -> list[tuple[Document, float]]:
    """
    Search for a single country's chunks with a three-tier fallback:

    1. primary_country filter (exact scalar match) — most precise; requires the PDF
       to give countries their own header level so enricher can detect the primary country.
    2. countries_mentioned filter ($contains on the stored JSON string) — works even when
       multiple countries share a section; still excludes chunks that don't mention the
       country at all.
    3. Fully unfiltered — last resort; may return regional-overview chunks.
    """
    # Tier 1: primary_country exact match
    results = await asyncio.gather(
        _vs.search(f"{country} {param_hint}", top_k=4, country=country),
        _vs.search(f"{country} Human Freedom Index score rank", top_k=3, country=country),
    )
    flat = [item for batch in results for item in batch]

    if not flat:
        # Tier 2: countries_mentioned contains this country (JSON substring match)
        logger.info("[retriever] primary_country=0 for %r — trying countries_mentioned filter", country)
        results = await asyncio.gather(
            _vs.search(f"{country} {param_hint}", top_k=4, countries_mentioned=country),
            _vs.search(f"{country} Human Freedom Index score rank", top_k=3, countries_mentioned=country),
        )
        flat = [item for batch in results for item in batch]

    if not flat:
        # Tier 3: fully unfiltered
        logger.info("[retriever] countries_mentioned=0 for %r — falling back to unfiltered", country)
        results = await asyncio.gather(
            _vs.search(f"{country} {param_hint}", top_k=4),
            _vs.search(f"{country} Human Freedom Index score rank", top_k=3),
        )
        flat = [item for batch in results for item in batch]

    return flat


async def _comparison_search(
    countries: list[str],
    parameters: list[str],
) -> list[tuple[Document, float]]:
    """
    Issue focused searches per country, filtered to chunks primarily about that country.
    Falls back to unfiltered search if primary_country metadata is absent/empty.
    """
    param_hint = " ".join(parameters) if parameters else "freedom score rank"
    nested = await asyncio.gather(*[
        _search_for_country(c, param_hint) for c in countries
    ])
    flat: list[tuple[Document, float]] = [item for batch in nested for item in batch]
    flat.sort(key=lambda x: x[1], reverse=True)
    return flat
