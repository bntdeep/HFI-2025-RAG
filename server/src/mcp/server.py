"""
MCP server — exposes the HFI RAG agent and storage layer as MCP tools/resources/prompts.

Tools (8):
  list_documents, upload_document, delete_document, search_documents  ← no LLM
  query, compare_countries, get_country_profile, extract_chart_data   ← LLM via run_query()

Resources (3):
  documents://list, countries://list, parameters://list

Prompts (3):
  analyze-country, compare-countries, extract-trends
"""
from __future__ import annotations

import json
import logging
from typing import Optional

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    from mcp.server.mcpserver import MCPServer as FastMCP  # type: ignore[no-redef]

from ..config import settings
from ..ingestion.pipeline import ingest_document
from ..rag import run_query
from ..storage.metadata_db import MetadataDB
from ..storage.vector_store import VectorStoreClient
from ..utils.countries import COUNTRIES
from ..utils.parameters import HFI_PARAMETERS

logger = logging.getLogger(__name__)

# ── App instance ──────────────────────────────────────────────────────────────

app = FastMCP("HFI RAG Server", port=settings.mcp_server_port)

# Module-level singletons — avoids re-initialising ChromaDB HNSW index on every call
_vs = VectorStoreClient()
_db = MetadataDB()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _agent_result(state: dict) -> dict:
    """Extract the three output fields that callers care about."""
    return {
        "response_text": state.get("response_text", ""),
        "chart_config": state.get("chart_config"),
        "sources": state.get("sources", []),
    }


# ════════════════════════════════════════════════════════════════════════════
# TOOLS
# ════════════════════════════════════════════════════════════════════════════

# ── Document management ───────────────────────────────────────────────────────

@app.tool()
async def list_documents() -> list[dict]:
    """List all indexed documents with metadata (id, name, pages, chunks, status)."""
    return await _db.list_documents()


@app.tool()
async def upload_document(
    file_path: str,
    document_name: Optional[str] = None,
) -> dict:
    """
    Upload and index a PDF document.

    Args:
        file_path:     Absolute path to the PDF file on the server filesystem.
        document_name: Optional display name; defaults to the filename.

    Returns:
        Summary dict with document_id, chunks_created, pages_processed, etc.
    """
    result = await ingest_document(file_path, document_name=document_name)
    return {
        "document_id": result.document_id,
        "document_name": result.document_name,
        "chunks_created": result.total_chunks,
        "pages_processed": result.total_pages,
        "tables_found": result.table_chunks,
        "images_found": result.image_chunks,
        "status": "indexed",
    }


@app.tool()
async def delete_document(document_id: str) -> dict:
    """
    Delete an indexed document and all its chunks from the vector store.

    Args:
        document_id: UUID of the document to delete.

    Returns:
        {deleted: bool, chunks_removed: int}
    """
    chunks_removed = await _vs.delete_document(document_id)
    deleted = await _db.delete_document(document_id)
    return {"deleted": deleted, "chunks_removed": chunks_removed}


@app.tool()
async def search_documents(
    query: str,
    top_k: int = 10,
    document_id: Optional[str] = None,
    chunk_type: Optional[str] = None,
) -> list[dict]:
    """
    Semantic search over indexed document chunks.

    Args:
        query:       Natural language search query.
        top_k:       Number of chunks to return (default 10).
        document_id: Filter results to a specific document UUID.
        chunk_type:  Filter by chunk type: "text", "table", or "image_description".

    Returns:
        List of {content, metadata, similarity_score} dicts ordered by relevance.
    """
    results = await _vs.search(
        query, top_k=top_k, document_id=document_id, chunk_type=chunk_type
    )
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata,
            "similarity_score": round(score, 4),
        }
        for doc, score in results
    ]


# ── Agent-powered queries ─────────────────────────────────────────────────────

@app.tool()
async def query(
    text: str,
    history: Optional[list] = None,
) -> dict:
    """
    General-purpose chat query over the Human Freedom Index.
    Routes through the LangGraph agent (intent detection → retrieval → analysis).

    Args:
        text:    The user's natural language question.
        history: Optional list of prior BaseMessage objects for multi-turn context.

    Returns:
        {response_text: str, chart_config: dict|None, sources: list}
    """
    state = await run_query(text, mode="chat", history=history)
    return _agent_result(state)


@app.tool()
async def compare_countries(
    countries: list[str],
    parameters: Optional[list[str]] = None,
    include_chart: bool = True,
) -> dict:
    """
    Compare 2–6 countries across specified HFI freedom parameters.

    Args:
        countries:    List of country names (2–6).
        parameters:   HFI parameter codes to compare (e.g. ["pf", "ef"]).
                      If omitted the agent selects relevant parameters.
        include_chart: Whether to request chart config in the response.

    Returns:
        {response_text: str, chart_config: dict|None, sources: list}
    """
    country_list = ", ".join(countries)
    param_list = ", ".join(parameters) if parameters else "all available"
    q = f"Compare {country_list} on {param_list}"
    state = await run_query(
        q,
        mode="structured",
        selected_countries=countries,
        selected_parameters=parameters or [],
    )
    result = _agent_result(state)
    if not include_chart:
        result["chart_config"] = None
    return result


@app.tool()
async def get_country_profile(country: str) -> dict:
    """
    Get a comprehensive freedom profile for a single country.

    Args:
        country: Country name (e.g. "Norway", "Belarus").

    Returns:
        {response_text: str, chart_config: dict|None, sources: list}
    """
    state = await run_query(
        f"Tell me about {country}'s freedom profile",
        mode="structured",
        selected_countries=[country],
    )
    return _agent_result(state)


@app.tool()
async def extract_chart_data(
    query: str,
    chart_type: Optional[str] = None,
) -> dict:
    """
    Extract data suitable for visualization from the HFI document.

    Args:
        query:      Description of what to visualize (e.g. "top 10 countries by personal freedom").
        chart_type: Hint for the chart type: "bar", "line", "radar", "pie", "scatter".
                    The agent may override this based on the data shape.

    Returns:
        {chart_config: dict|None, insight: str, sources: list}
    """
    full_query = f"{query} (chart_type: {chart_type})" if chart_type else query
    state = await run_query(full_query, mode="chat")
    return {
        "chart_config": state.get("chart_config"),
        "insight": state.get("analysis_text") or state.get("response_text", ""),
        "sources": state.get("sources", []),
    }


# ════════════════════════════════════════════════════════════════════════════
# RESOURCES
# ════════════════════════════════════════════════════════════════════════════

@app.resource("documents://list")
async def resource_list_documents() -> str:
    """List of all currently indexed documents."""
    docs = await _db.list_documents()
    return json.dumps(docs, default=str)


@app.resource("countries://list")
def resource_list_countries() -> str:
    """All 165 HFI jurisdictions with name, flag emoji, ISO2 code, and region."""
    return json.dumps(
        [{"name": c["name"], "flag": c["flag"], "iso2": c["iso2"], "region": c["region"]}
         for c in COUNTRIES]
    )


@app.resource("parameters://list")
def resource_list_parameters() -> str:
    """All HFI freedom parameters with code, display name, and parent category."""
    return json.dumps(
        [{"code": p.code, "name": p.name, "parent": p.parent}
         for p in HFI_PARAMETERS]
    )


# ════════════════════════════════════════════════════════════════════════════
# PROMPTS
# ════════════════════════════════════════════════════════════════════════════

@app.prompt()
def analyze_country(country: str) -> str:
    """
    Generate a prompt to analyze a single country's freedom profile.

    Args:
        country: Country name to analyze.
    """
    return (
        f"Analyze {country}'s freedom profile from the Human Freedom Index 2025. "
        f"Include overall ranking, key strengths and weaknesses across personal and "
        f"economic freedom categories. Return structured JSON with scores and analysis."
    )


@app.prompt()
def compare_countries_prompt(countries: str, parameters: str) -> str:
    """
    Generate a prompt to compare countries across HFI parameters.

    Args:
        countries:  Comma-separated country names.
        parameters: Comma-separated HFI parameter codes or names.
    """
    return (
        f"Compare {countries} across these parameters: {parameters}. "
        f"Extract exact scores from the document. "
        f"Return structured comparison JSON with chart data."
    )


@app.prompt()
def extract_trends(topic: str) -> str:
    """
    Generate a prompt for trend and pattern analysis.

    Args:
        topic: The trend topic to analyze (e.g. "press freedom in Eastern Europe").
    """
    return (
        f"Analyze trends related to {topic} in the Human Freedom Index 2025. "
        f"Identify patterns, top/bottom performers, and regional differences. "
        f"Return data suitable for visualization."
    )
