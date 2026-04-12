## 6. Node.js BFF

6.1 REST API Endpoints

yaml


# Document Management
POST   /api/documents/upload     # Upload PDF → forward to MCP upload_document
GET    /api/documents            # List docs → forward to MCP list_documents  
DELETE /api/documents/:id        # Delete → forward to MCP delete_document

# Query / Chat
POST   /api/chat                 # Free-form chat query (streaming SSE response)
  body: { "message": "string", "conversation_id": "string" }
  response: SSE stream of tokens + final chart_config

POST   /api/compare              # Structured comparison
  body: { 
    "countries": ["Switzerland", "Japan"],
    "parameters": ["personal_freedom", "economic_freedom"]
  }
  response: SSE stream of tokens + final ComparisonResult

POST   /api/country/:name        # Country profile
  response: SSE stream + CountryProfile

# Metadata
GET    /api/countries            # Available countries with flags
GET    /api/parameters           # Available comparison parameters

# Health
GET    /api/health               # Health check (MCP connection status)
6.2 WebSocket (Debug Console)

yaml


# WS endpoint: ws://localhost:3001/ws/debug

# Server → Client events:
{
  "type": "mcp_call",
  "timestamp": "ISO",
  "tool": "search_documents",
  "params": { "query": "...", "top_k": 10 },
  "duration_ms": null  # null = started, number = completed
}

{
  "type": "llm_request",
  "timestamp": "ISO", 
  "model": "gpt-4.1-2025-04-14",
  "prompt_preview": "first 200 chars...",
  "token_count": 1847
}

{
  "type": "llm_response",
  "timestamp": "ISO",
  "model": "gpt-4.1-2025-04-14", 
  "response_preview": "first 200 chars...",
  "tokens_used": { "prompt": 1847, "completion": 423 },
  "duration_ms": 1200
}

{
  "type": "retrieval",
  "timestamp": "ISO",
  "query": "Switzerland freedom",
  "chunks_found": 5,
  "top_score": 0.89,
  "sections": ["Country Rankings", "Western Europe"]
}

{
  "type": "chart_ready",
  "timestamp": "ISO",
  "chart_type": "bar",
  "data_points": 10
}

{
  "type": "error",
  "timestamp": "ISO",
  "message": "string",
  "stack": "string | null"
}
