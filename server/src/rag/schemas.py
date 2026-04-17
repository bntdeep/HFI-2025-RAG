"""
Shared type definitions for the LangGraph agent.

  AgentState    — the full state dict flowing through the graph
  RouterOutput  — structured LLM output for intent classification
  All Pydantic output schemas from spec 5.3
"""
from __future__ import annotations

from typing import Literal, TypedDict

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from pydantic import BaseModel


# ── Agent State ───────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    # Input
    messages: list[BaseMessage]
    query: str
    mode: str                           # "chat" | "structured"

    # Structured mode inputs (optional — override LLM extraction)
    selected_countries: list[str] | None
    selected_parameters: list[str] | None

    # Router output
    intent: str                         # "comparison"|"profile"|"trend"|"general"|"crud"

    # Retriever output
    retrieved_chunks: list[Document]
    retrieval_scores: list[float]

    # Analyzer output
    extracted_data: dict | None
    analysis_text: str | None

    # Formatter output
    chart_config: dict | None
    response_text: str
    sources: list[dict]

    # Debug / tracing
    debug_events: list[dict]


# ── Router structured output ──────────────────────────────────────────────────

class RouterOutput(BaseModel):
    intent: Literal["comparison", "profile", "trend", "general", "crud"]
    countries: list[str]        # canonical country names extracted from the query
    parameters: list[str]       # HFI parameter codes extracted from the query


# ── Output schemas (spec 5.3) ─────────────────────────────────────────────────

class CountryScore(BaseModel):
    name: str
    flag: str = ""              # emoji; may be empty if LLM can't determine it
    score: float | None = None  # null when data not found in sources
    rank: int | None = None


class ChartConfig(BaseModel):
    chart_type: Literal["bar", "pie", "line", "radar", "scatter"]
    title: str
    data: list[dict]
    x_key: str
    y_keys: list[str]
    colors: list[str] | None = None


class ComparisonResult(BaseModel):
    countries: list[CountryScore]
    parameters: list[str]
    scores_matrix: dict[str, dict[str, float | None]]
    # {"Switzerland": {"personal_freedom": 9.23, ...}}; None means data not found
    chart_config: ChartConfig | None = None  # optional — may be absent if data is sparse
    insight: str


class CountryProfile(BaseModel):
    name: str
    flag: str
    overall_rank: int
    overall_score: float
    personal_freedom_score: float
    economic_freedom_score: float
    subcategories: dict[str, float]
    strengths: list[str]
    weaknesses: list[str]
    chart_config: ChartConfig
    insight: str


class ChartExtractionResult(BaseModel):
    chart_config: ChartConfig
    insight: str
    data_completeness: float    # 0-1, how much data was found


class SourceReference(BaseModel):
    chunk_id: str
    page_number: int
    section: str
    relevance_score: float
