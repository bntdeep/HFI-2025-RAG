"""
Formatter node — assembles the final response from analyzer outputs.

No LLM calls.  Builds:
  response_text  — markdown string ready for the frontend
  chart_config   — dict (from extracted_data["chart_config"]) or None
  sources        — list of source reference dicts
"""
from __future__ import annotations

from langchain_core.documents import Document

from ..schemas import AgentState


async def formatter_node(state: AgentState) -> dict:
    intent = state["intent"]
    extracted = state.get("extracted_data")
    analysis_text = state.get("analysis_text") or ""
    chunks = state["retrieved_chunks"]
    scores = state["retrieval_scores"]

    sources = _build_sources(chunks, scores)

    chart_config: dict | None = None
    if extracted and "chart_config" in extracted:
        chart_config = extracted["chart_config"]

    if intent == "comparison" and extracted:
        response_text = _format_comparison(extracted, analysis_text)
    elif intent == "profile" and extracted:
        response_text = _format_profile(extracted, analysis_text)
    else:
        response_text = analysis_text or "No answer available."

    return {
        "response_text": response_text,
        "chart_config": chart_config,
        "sources": sources,
    }


# ── Response formatters ───────────────────────────────────────────────────────

def _format_comparison(data: dict, insight: str) -> str:
    countries = [c["name"] for c in data.get("countries", [])]
    parameters = data.get("parameters", [])
    matrix = data.get("scores_matrix", {})

    if not countries or not matrix:
        return insight

    lines = [f"## Comparison: {' vs '.join(countries)}\n"]

    # Markdown table
    if parameters:
        header = "| Parameter | " + " | ".join(countries) + " |"
        sep = "|-----------|" + "|---------|" * len(countries)
        lines += [header, sep]
        for param in parameters:
            row = f"| {param} |"
            for country in countries:
                score = matrix.get(country, {}).get(param)
                row += f" {score:.2f} |" if score is not None else " — |"
            lines.append(row)
        lines.append("")

    if insight:
        lines.append(f"\n**Insight:** {insight}")

    return "\n".join(lines)


def _format_profile(data: dict, insight: str) -> str:
    name = data.get("name", "")
    flag = data.get("flag", "")
    overall_rank = data.get("overall_rank", "?")
    overall_score = data.get("overall_score", 0)
    pf = data.get("personal_freedom_score", 0)
    ef = data.get("economic_freedom_score", 0)
    strengths = data.get("strengths", [])
    weaknesses = data.get("weaknesses", [])

    lines = [
        f"## {flag} {name} — Freedom Profile\n",
        f"| Metric | Score |",
        f"|--------|-------|",
        f"| Overall rank | #{overall_rank} |",
        f"| Overall score | {overall_score:.2f} / 10 |",
        f"| Personal freedom | {pf:.2f} |",
        f"| Economic freedom | {ef:.2f} |",
        "",
    ]
    if strengths:
        lines.append("**Strengths:** " + ", ".join(strengths))
    if weaknesses:
        lines.append("**Areas of concern:** " + ", ".join(weaknesses))
    if insight:
        lines.append(f"\n**Insight:** {insight}")

    return "\n".join(lines)


# ── Source builder ────────────────────────────────────────────────────────────

def _build_sources(chunks: list[Document], scores: list[float]) -> list[dict]:
    sources = []
    for doc, score in zip(chunks, scores):
        m = doc.metadata
        sources.append({
            "chunk_id": m.get("chunk_id", ""),
            "page_number": m.get("page_number", 0),
            "section": m.get("section_h2") or m.get("section_h1") or "",
            "relevance_score": round(score, 4),
            "chunk_type": m.get("chunk_type", ""),
            "document_name": m.get("document_name", ""),
        })
    return sources
