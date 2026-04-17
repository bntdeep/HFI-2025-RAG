"""
HFI RAG Server entry point.

Start with:
    cd server && python -m src.main [transport]

Transports:
    stdio            — MCP over stdin/stdout (default; used by `mcp dev`)
    streamable-http  — MCP over HTTP on MCP_SERVER_PORT (default: 8003)
    sse              — MCP over SSE
    rest             — FastAPI REST API on REST_API_PORT (default: 8080)
"""
from __future__ import annotations

import sys

from dotenv import load_dotenv

load_dotenv()  # must run before importing src modules that read settings

from src.rag import configure_logging  # noqa: E402

configure_logging()

if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"

    if transport == "rest":
        import uvicorn
        from src.api.app import rest
        from src.config import settings
        uvicorn.run(rest, host="0.0.0.0", port=settings.rest_api_port)
    else:
        from src.mcp.server import app  # noqa: E402
        app.run(transport=transport)
