"""
FastAPI REST layer — provides typed HTTP endpoints for the Node.js BFF.

Runs on port 8080 (configurable via REST_API_PORT in .env).
Start: python -m src.main rest

Endpoints:
  POST   /api/compare            — butterfly chart comparison
  GET    /api/profile/{country}  — country freedom profile
  POST   /api/chat               — multi-turn chat
  GET    /api/documents          — list indexed docs
  POST   /api/documents          — upload + index PDF
  DELETE /api/documents/{id}     — delete doc + chunks
  GET    /api/countries           — all 165 HFI jurisdictions
  GET    /api/parameters          — all HFI parameters
  GET    /api/health              — health check
"""
from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any

import aiofiles
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from ..config import settings
from ..ingestion.pipeline import ingest_document
from ..rag import run_query
from ..storage.metadata_db import MetadataDB
from ..storage.vector_store import VectorStoreClient
from ..utils.countries import COUNTRIES
from ..utils.parameters import HFI_PARAMETERS
from .models import (
    ButterflyRow,
    ChatRequest,
    ChatResponse,
    CompareRequest,
    CompareResponse,
    CountryProfileResponse,
    DeleteResponse,
    DocumentRecord,
    SourceRef,
    UploadResponse,
)

logger = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────────────────────

rest = FastAPI(title="HFI RAG REST API", version="1.0.0")
rest.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Module-level singletons — shared with the MCP server if both run in the same process
_vs = VectorStoreClient()
_db = MetadataDB()


# ── Butterfly chart config ────────────────────────────────────────────────────

_MAX_RANK = 165

# Ordered list of params shown in the butterfly chart (display names)
BUTTERFLY_PARAMS = [
    "Score",
    "Ranking",
    "Rule of Law",
    "Security & Safety",
    "Movement",
    "Religion",
]

# Possible keys the LLM may use for each display param in scores_matrix
_PARAM_KEYS: dict[str, list[str]] = {
    "Rule of Law": ["Rule of Law", "rule_of_law", "pf_rol", "rol", "RuleOfLaw"],
    "Security & Safety": ["Security & Safety", "Security", "security", "pf_ss", "ss", "security_and_safety", "Security and Safety"],
    "Movement": ["Movement", "movement", "pf_movement"],
    "Religion": ["Religion", "religion", "pf_religion"],
    "Association & Assembly": ["Association & Assembly", "Association", "association", "pf_association", "association_assembly_civil_society", "Association Assembly Civil Society"],
    "Expression & Information": [
        "Expression & Information", "Expression", "expression", "pf_expression",
        "expression_and_information", "Expression and Information",
    ],
    "Relationships": ["Relationships", "relationships", "pf_identity"],
}


def _normalize_rank(rank: int | None) -> float:
    """Convert rank (1=best, 165=worst) to 0–10 score."""
    if not rank:
        return 0.0
    return round(max(0.0, (_MAX_RANK - rank) / (_MAX_RANK - 1) * 10), 2)


def _lookup(matrix: dict[str, Any], *keys: str) -> float:
    """Try multiple key variants; return first match or 0.0."""
    for k in keys:
        v = matrix.get(k)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return 0.0


# ── Response builders ─────────────────────────────────────────────────────────

def _to_source_refs(sources: list[dict]) -> list[SourceRef]:
    result = []
    for s in sources:
        result.append(SourceRef(
            page_number=s.get("page_number", 0),
            section=s.get("section", ""),
            relevance_score=s.get("relevance_score", 0.0),
            document_name=s.get("document_name", ""),
        ))
    return result


def _build_compare_response(
    state: dict,
    countries: list[str],
    params: list[str],
) -> CompareResponse:
    extracted = state.get("extracted_data") or {}
    sources = state.get("sources", [])

    # Country-level data (score + rank)
    country_scores: dict[str, dict] = {}
    for c in extracted.get("countries", []):
        name = c.get("name", "")
        if name:
            country_scores[name] = c

    scores_matrix: dict[str, dict[str, Any]] = extracted.get("scores_matrix", {})

    # Build butterfly rows for the default params
    butterfly_data: list[ButterflyRow] = []
    a_name = countries[0] if len(countries) > 0 else ""
    b_name = countries[1] if len(countries) > 1 else ""

    for param in BUTTERFLY_PARAMS:
        if param == "Score":
            a_val = float(country_scores.get(a_name, {}).get("score", 0.0) or 0.0)
            b_val = float(country_scores.get(b_name, {}).get("score", 0.0) or 0.0)
        elif param == "Ranking":
            a_val = _normalize_rank(country_scores.get(a_name, {}).get("rank"))
            b_val = _normalize_rank(country_scores.get(b_name, {}).get("rank"))
        else:
            lookup_keys = _PARAM_KEYS.get(param, [param])
            a_val = _lookup(scores_matrix.get(a_name, {}), *lookup_keys)
            b_val = _lookup(scores_matrix.get(b_name, {}), *lookup_keys)

        butterfly_data.append(ButterflyRow(param=param, country_a=a_val, country_b=b_val))

    return CompareResponse(
        countries=countries,
        params=params or BUTTERFLY_PARAMS,
        butterfly_data=butterfly_data,
        scores_matrix=scores_matrix,
        response_text=state.get("response_text", ""),
        sources=_to_source_refs(sources),
    )


def _get_sub(subcategories: dict, *keys: str) -> float | None:
    for k in keys:
        v = subcategories.get(k)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return None


def _build_profile_response(state: dict) -> CountryProfileResponse:
    extracted = state.get("extracted_data") or {}
    sources = state.get("sources", [])
    subcategories: dict[str, float] = {}
    for k, v in (extracted.get("subcategories") or {}).items():
        try:
            subcategories[k] = float(v)
        except (TypeError, ValueError):
            pass

    return CountryProfileResponse(
        name=extracted.get("name", ""),
        flag=extracted.get("flag", ""),
        overall_rank=int(extracted.get("overall_rank", 0) or 0),
        overall_score=float(extracted.get("overall_score", 0.0) or 0.0),
        personal_freedom_score=float(extracted.get("personal_freedom_score", 0.0) or 0.0),
        economic_freedom_score=float(extracted.get("economic_freedom_score", 0.0) or 0.0),
        rule_of_law=_get_sub(subcategories, *_PARAM_KEYS["Rule of Law"]),
        security=_get_sub(subcategories, *_PARAM_KEYS["Security & Safety"]),
        movement=_get_sub(subcategories, *_PARAM_KEYS["Movement"]),
        religion=_get_sub(subcategories, *_PARAM_KEYS["Religion"]),
        expression=_get_sub(subcategories, *_PARAM_KEYS["Expression & Information"]),
        association=_get_sub(subcategories, *_PARAM_KEYS["Association & Assembly"]),
        subcategories=subcategories,
        strengths=extracted.get("strengths", []),
        weaknesses=extracted.get("weaknesses", []),
        response_text=state.get("response_text", ""),
        sources=_to_source_refs(sources),
    )


# ── History conversion ────────────────────────────────────────────────────────

def _to_messages(history: list[dict[str, str]]) -> list[BaseMessage]:
    """Convert [{role, content}] dicts to LangChain BaseMessage objects."""
    result: list[BaseMessage] = []
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            result.append(SystemMessage(content=content))
        elif role == "assistant":
            result.append(AIMessage(content=content))
        else:
            result.append(HumanMessage(content=content))
    return result


# ════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════

@rest.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "hfi-rag-rest"}


# ── Compare ───────────────────────────────────────────────────────────────────

@rest.post("/api/compare", response_model=CompareResponse)
async def compare(body: CompareRequest) -> CompareResponse:
    """
    Compare 2 countries across HFI parameters.
    Returns butterfly_data ready for the diverging bar chart.
    """
    if len(body.countries) < 2:
        raise HTTPException(status_code=422, detail="At least 2 countries required")

    # Always request the 4 extractable params (Score and Ranking come from CountryScore)
    extractable_params = [p for p in BUTTERFLY_PARAMS if p not in ("Score", "Ranking")]

    state = await run_query(
        f"Compare {' and '.join(body.countries)} across: {', '.join(extractable_params)}",
        mode="structured",
        selected_countries=body.countries,
        selected_parameters=extractable_params,
        history=_to_messages(body.history),
    )
    return _build_compare_response(state, body.countries, body.params or BUTTERFLY_PARAMS)


# ── Country profile ───────────────────────────────────────────────────────────

@rest.get("/api/profile/{country}", response_model=CountryProfileResponse)
async def profile(country: str) -> CountryProfileResponse:
    """Get a detailed freedom profile for a single country."""
    state = await run_query(
        f"Provide a complete freedom profile for {country} including all subcategory scores, "
        f"rank, and strengths/weaknesses. Include Movement and Religion scores.",
        mode="structured",
        selected_countries=[country],
        history=[],
    )
    return _build_profile_response(state)


# ── Chat ──────────────────────────────────────────────────────────────────────

@rest.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    """Multi-turn chat over the HFI document."""
    state = await run_query(
        body.message,
        mode="chat",
        history=_to_messages(body.history),
    )
    return ChatResponse(
        response_text=state.get("response_text", ""),
        chart_config=state.get("chart_config"),
        sources=_to_source_refs(state.get("sources", [])),
    )


# ── Documents ─────────────────────────────────────────────────────────────────

@rest.get("/api/documents", response_model=list[DocumentRecord])
async def list_documents() -> list[DocumentRecord]:
    rows = await _db.list_documents()
    return [DocumentRecord(**r) for r in rows]


@rest.post("/api/documents", response_model=UploadResponse)
async def upload_document(file: UploadFile) -> UploadResponse:
    """Upload a PDF and index it into the vector store."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=422, detail="Only PDF files are supported")

    # Save to uploads directory
    uploads_dir = settings.uploads_dir
    uploads_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_{file.filename}"
    dest = uploads_dir / safe_name

    contents = await file.read()
    async with aiofiles.open(dest, "wb") as f:
        await f.write(contents)

    try:
        result = await ingest_document(str(dest), document_name=file.filename)
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc

    return UploadResponse(
        document_id=result.document_id,
        document_name=result.document_name,
        chunks_created=result.total_chunks,
        pages_processed=result.total_pages,
        tables_found=result.table_chunks,
        images_found=result.image_chunks,
        status="indexed",
    )


@rest.delete("/api/documents/{doc_id}", response_model=DeleteResponse)
async def delete_document(doc_id: str) -> DeleteResponse:
    chunks_removed = await _vs.delete_document(doc_id)
    deleted = await _db.delete_document(doc_id)
    return DeleteResponse(deleted=deleted, chunks_removed=chunks_removed)


# ── Metadata ──────────────────────────────────────────────────────────────────

@rest.get("/api/countries")
def countries_list() -> list[dict]:
    """All 165 HFI jurisdictions: {name, flag, iso2, region}."""
    return COUNTRIES


@rest.get("/api/parameters")
def parameters_list() -> list[dict]:
    """All HFI freedom parameters: {code, name, parent}."""
    return [
        {"code": p.code, "name": p.name, "parent": p.parent}
        for p in HFI_PARAMETERS
    ]
