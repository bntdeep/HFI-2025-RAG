# HFI RAG — 2025 Human Freedom Index

RAG application over the 2025 Human Freedom Index PDF.  
Query country freedom rankings, compare countries, and visualize results via an interactive UI.

## Architecture

```
React Frontend  :5173
    ↕
Node.js BFF     :3001
    ↕
Python Server   :8080  (FastAPI REST)
               :8003  (FastMCP — Claude Desktop / inspector)
```

---

## Quick Start

### 1. Environment

Copy `.env.example` to `server/.env` and fill in your EPAM DIAL credentials.

### 2. Install dependencies

```bash
cd server && pip install -e .
cd bff   && npm install
cd client && npm install
```

### 3. Ingest the PDF

```bash
python3 server/testing/ingest_document.py
```

### 4. Run all services (3 terminals)

```bash
# T1 — Python REST API
cd server && python3 -m src.main rest

# T2 — Node.js BFF
cd bff && npm run dev

# T3 — React client
cd client && npm run dev
```

Open **http://localhost:5173**

---

## MCP Server (Claude Desktop / Postman inspector)

```bash
cd server && python3 -m src.main streamable-http
# endpoint: http://localhost:8003/mcp
```

Kill the port if already in use:
```bash
lsof -ti :8003 | xargs kill -9
```

---

## Evaluation

```bash
cd server && python3 -m eval.precision_eval
```

---

## Database

**Clear and re-ingest from scratch:**
```bash
rm -rf server/chroma_db server/metadata.db
python3 server/testing/ingest_document.py
```

**Run ChromaDB standalone** (alternative to embedded mode):
```bash
chroma run --path server/chroma_db --port 8001
```
