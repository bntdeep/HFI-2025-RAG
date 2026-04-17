"""
Pydantic v2 request/response models for the FastAPI REST layer.

These are separate from schemas.py (which serves the LangGraph agent) so that
the REST API contract can evolve independently.
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel


# ── Source reference ──────────────────────────────────────────────────────────

class SourceRef(BaseModel):
    page_number: int = 0
    section: str = ""
    relevance_score: float = 0.0
    document_name: str = ""


# ── Compare ───────────────────────────────────────────────────────────────────

class CompareRequest(BaseModel):
    countries: list[str]                    # exactly 2 country names
    params: list[str] = []                  # display-name params; defaults to BUTTERFLY_PARAMS
    history: list[dict[str, str]] = []      # [{role, content}, ...] — system prompt injected by BFF


class ButterflyRow(BaseModel):
    param: str
    country_a: float    # 0–10 (ranking normalized)
    country_b: float    # 0–10


class CompareResponse(BaseModel):
    countries: list[str]
    params: list[str]
    butterfly_data: list[ButterflyRow]
    scores_matrix: dict[str, dict[str, Any]]
    response_text: str
    sources: list[SourceRef] = []


# ── Country profile ───────────────────────────────────────────────────────────

class CountryProfileResponse(BaseModel):
    name: str
    flag: str = ""
    overall_rank: int = 0
    overall_score: float = 0.0
    personal_freedom_score: float = 0.0
    economic_freedom_score: float = 0.0
    # Explicitly surfaced subcategories for UI display
    rule_of_law: float | None = None
    security: float | None = None
    movement: float | None = None
    religion: float | None = None
    expression: float | None = None
    association: float | None = None
    # Full subcategory map for radar chart
    subcategories: dict[str, float] = {}
    strengths: list[str] = []
    weaknesses: list[str] = []
    response_text: str = ""
    sources: list[SourceRef] = []


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    history: list[dict[str, str]] = []     # [{role, content}, ...] — includes system prompt


class ChatResponse(BaseModel):
    response_text: str
    chart_config: dict | None = None
    sources: list[SourceRef] = []


# ── Documents ─────────────────────────────────────────────────────────────────

class DocumentRecord(BaseModel):
    id: str
    name: str
    path: str = ""
    total_chunks: int = 0
    status: str = "ready"
    created_at: str = ""
    updated_at: str = ""


class UploadResponse(BaseModel):
    document_id: str
    document_name: str
    chunks_created: int
    pages_processed: int
    tables_found: int
    images_found: int
    status: str = "indexed"


class DeleteResponse(BaseModel):
    deleted: bool
    chunks_removed: int
