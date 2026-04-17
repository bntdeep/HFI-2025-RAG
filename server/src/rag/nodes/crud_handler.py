"""
CRUD handler node — manages documents without LLM involvement.

Dispatches based on keywords in the query:
  list    → MetadataDB.list_documents()
  delete  → MetadataDB.delete_document() + VectorStoreClient.delete_document()
  upload  → returns guidance (actual upload requires a file path via MCP/REST layer)
"""
from __future__ import annotations

import re

from ...storage.metadata_db import MetadataDB
from ...storage.vector_store import VectorStoreClient
from ..schemas import AgentState

_db = MetadataDB()
_vs = VectorStoreClient()


async def crud_handler_node(state: AgentState) -> dict:
    query_lower = state["query"].lower()

    if any(kw in query_lower for kw in ("delete", "remove")):
        response, data = await _handle_delete(state["query"])
    elif any(kw in query_lower for kw in ("upload", "ingest", "add document", "index")):
        response, data = _handle_upload_guidance()
    else:
        # default: list
        response, data = await _handle_list()

    return {
        "response_text": response,
        "extracted_data": data,
        "chart_config": None,
        "sources": [],
        "debug_events": state.get("debug_events", []) + [{"node": "crud_handler"}],
    }


async def _handle_list() -> tuple[str, dict]:
    docs = await _db.list_documents()
    if not docs:
        return "No documents indexed yet.", {"documents": []}

    lines = ["**Indexed documents:**\n"]
    for d in docs:
        status_badge = f"`{d['status']}`"
        lines.append(
            f"- **{d['name']}** — {d['total_chunks']} chunks — {status_badge} — id: `{d['id']}`"
        )
    return "\n".join(lines), {"documents": docs}


async def _handle_delete(query: str) -> tuple[str, dict]:
    # Try to extract a UUID from the query
    match = re.search(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        query,
        re.IGNORECASE,
    )
    if not match:
        return (
            "Please provide the document ID (UUID) to delete. "
            "Use 'list documents' to see all document IDs.",
            {},
        )

    doc_id = match.group(0)
    deleted_meta = await _db.delete_document(doc_id)
    if not deleted_meta:
        return f"Document `{doc_id}` not found.", {}

    deleted_chunks = await _vs.delete_document(doc_id)
    return (
        f"Deleted document `{doc_id}` ({deleted_chunks} chunks removed from the vector store).",
        {"deleted_id": doc_id, "deleted_chunks": deleted_chunks},
    )


def _handle_upload_guidance() -> tuple[str, dict]:
    return (
        "To upload a new document, use the `upload_document` MCP tool "
        "or the `/api/documents` REST endpoint with the file path.",
        {},
    )
