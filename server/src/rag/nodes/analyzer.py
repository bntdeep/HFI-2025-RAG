"""
Analyzer node — extracts structured data or generates free-form text.

  comparison  → ComparisonResult  (structured, with chart config)
  profile     → CountryProfile    (structured, with chart config)
  trend/general → plain text      (free-form markdown)

Falls back to free-form text if structured extraction fails (e.g. Pydantic
validation error from a malformed LLM response).
"""
from __future__ import annotations

import logging

from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import ValidationError

from ..llm import get_llm, invoke_structured
from ..schemas import AgentState, ComparisonResult, CountryProfile

logger = logging.getLogger(__name__)

# ── Prompt templates ──────────────────────────────────────────────────────────

_COMPARISON_SYSTEM = """\
You are an expert analyst for the Human Freedom Index (HFI) 2025 report.
Extract precise numerical data from the provided source excerpts.

Countries to compare: {countries}
Focus on parameters: {parameters}

Return a ComparisonResult with:
- scores_matrix: map each country to its parameter scores (use null if data missing)
- chart_config: bar chart comparing the countries on the main parameters
- insight: 2–3 sentence summary of the key findings

IMPORTANT: Do NOT invent scores not present in the sources — use null for missing values.
"""

_PROFILE_SYSTEM = """\
You are an expert analyst for the Human Freedom Index (HFI) 2025 report.
Extract a complete freedom profile for: {country}

Return a CountryProfile with:
- overall_rank and overall_score (scale 0–10)
- personal_freedom_score and economic_freedom_score
- subcategories: all available sub-scores as a dict (code → score)
- strengths: top 3 areas where this country scores well vs global average
- weaknesses: top 3 areas of concern
- chart_config: radar chart showing the main category scores
- insight: 2–3 sentence summary

If a value is absent from the sources, use 0.0 for scores and omit from subcategories.
"""

_GENERAL_SYSTEM = """\
You are an expert on the Human Freedom Index (HFI) 2025, published by the Cato Institute
and Fraser Institute.

Answer the user's question using ONLY the provided source excerpts.
Be specific; cite page numbers when relevant.
If the sources do not contain sufficient information, say so clearly.
Format your response in clear, readable markdown prose.
"""

# ── Context assembly ──────────────────────────────────────────────────────────

def _build_context(chunks: list[Document], scores: list[float]) -> str:
    parts = []
    for i, (doc, score) in enumerate(zip(chunks, scores)):
        m = doc.metadata
        section = m.get("section_h2") or m.get("section_h1") or ""
        header = (
            f"[Source {i + 1}] "
            f"page={m.get('page_number', '?')} "
            f"type={m.get('chunk_type', '?')} "
            f"section={section!r} "
            f"score={score:.3f}"
        )
        parts.append(f"{header}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


# ── Node ──────────────────────────────────────────────────────────────────────

async def analyzer_node(state: AgentState) -> dict:
    intent = state["intent"]
    chunks = state["retrieved_chunks"]
    scores = state["retrieval_scores"]
    query = state["query"]
    countries = state.get("selected_countries") or []
    parameters = state.get("selected_parameters") or []
    context = _build_context(chunks, scores)

    llm = get_llm()

    if intent == "comparison":
        extracted_data, analysis_text = await _structured_comparison(
            llm, context, query, countries, parameters
        )
    elif intent == "profile":
        country = countries[0] if countries else query
        extracted_data, analysis_text = await _structured_profile(
            llm, context, query, country
        )
    else:  # trend | general
        extracted_data = None
        analysis_text = await _freeform_analysis(llm, context, query)

    structured = extracted_data is not None
    logger.info(
        "[analyzer] intent=%-12s structured=%s  context_chunks=%d",
        intent, structured, len(chunks),
    )
    if not structured:
        logger.info("[analyzer] fell back to free-form (structured extraction failed or not applicable)")

    return {
        "extracted_data": extracted_data,
        "analysis_text": analysis_text,
        "debug_events": state.get("debug_events", []) + [{
            "node": "analyzer",
            "intent": intent,
            "structured": structured,
            "context_chunks": len(chunks),
        }],
    }


# ── Strategy helpers ──────────────────────────────────────────────────────────

async def _structured_comparison(
    llm,
    context: str,
    query: str,
    countries: list[str],
    parameters: list[str],
) -> tuple[dict | None, str]:
    messages = [
        SystemMessage(content=_COMPARISON_SYSTEM.format(
            countries=", ".join(countries) or "all mentioned",
            parameters=", ".join(parameters) or "all available",
        )),
        HumanMessage(content=f"Sources:\n{context}\n\nQuestion: {query}"),
    ]
    try:
        result: ComparisonResult = await invoke_structured(messages, ComparisonResult)
        return result.model_dump(), result.insight
    except Exception as exc:
        logger.warning("[analyzer] structured comparison failed (%s: %s), falling back to free-form", type(exc).__name__, exc)
        text = await _freeform_analysis(llm, context, query)
        return None, text


async def _structured_profile(
    llm,
    context: str,
    query: str,
    country: str,
) -> tuple[dict | None, str]:
    messages = [
        SystemMessage(content=_PROFILE_SYSTEM.format(country=country)),
        HumanMessage(content=f"Sources:\n{context}\n\nQuestion: {query}"),
    ]
    try:
        result: CountryProfile = await invoke_structured(messages, CountryProfile)
        return result.model_dump(), result.insight
    except Exception:
        text = await _freeform_analysis(llm, context, query)
        return None, text


async def _freeform_analysis(llm, context: str, query: str) -> str:
    messages = [
        SystemMessage(content=_GENERAL_SYSTEM),
        HumanMessage(content=f"Sources:\n{context}\n\nQuestion: {query}"),
    ]
    response = await llm.ainvoke(messages)
    return response.content
