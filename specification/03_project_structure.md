## 9. Project Structure



human-freedom-index-rag/
├── README.md
├── docker-compose.yml (optional)
│
├── server/                          # Python MCP Server
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── .env.example
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                  # MCP Server entry point
│   │   ├── config.py                # Models, paths, settings
│   │   ├── mcp/
│   │   │   ├── __init__.py
│   │   │   ├── server.py            # MCP server setup
│   │   │   ├── tools.py             # Tool definitions
│   │   │   ├── resources.py         # Resource definitions
│   │   │   └── prompts.py           # Prompt templates
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py             # LangGraph agent
│   │   │   ├── retriever.py         # ChromaDB retriever
│   │   │   ├── chains.py            # LLM chains (analysis, extraction)
│   │   │   └── schemas.py           # Pydantic output schemas
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py          # Full ingestion pipeline
│   │   │   ├── pdf_parser.py        # pymupdf4llm wrapper
│   │   │   ├── chunker.py           # Header-based chunking
│   │   │   ├── table_extractor.py   # Table detection & extraction
│   │   │   ├── image_extractor.py   # Image extraction + vision
│   │   │   └── metadata_enricher.py # Country/metric detection
│   │   ├── storage/
│   │   │   ├── __init__.py
│   │   │   ├── vector_store.py      # ChromaDB wrapper
│   │   │   └── metadata_db.py       # SQLite document metadata
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── countries.py          # Country names + flag emojis
│   │       ├── parameters.py         # HFI parameter definitions
│   │       └── debug_logger.py       # Debug event emitter
│   ├── eval/
│   │   ├── eval_dataset.json         # 25+ Q&A pairs
│   │   ├── run_evaluation.py         # Evaluation script
│   │   └── results/                  # Evaluation output
│   ├── uploads/                      # Uploaded PDFs
│   ├── chroma_db/                    # ChromaDB persistent storage
│   └── metadata.db                   # SQLite
│
├── bff/                              # Node.js BFF
│   ├── package.json
│   ├── tsconfig.json
│   ├── .env.example
│   ├── src/
│   │   ├── index.ts                  # Express entry point
│   │   ├── config.ts                 # BFF configuration
│   │   ├── mcp/
│   │   │   ├── client.ts             # MCP client (SSE transport)
│   │   │   └── types.ts              # MCP response types
│   │   ├── routes/
│   │   │   ├── documents.ts          # /api/documents/*
│   │   │   ├── chat.ts               # /api/chat (SSE streaming)
│   │   │   ├── compare.ts            # /api/compare
│   │   │   ├── country.ts            # /api/country/:name
│   │   │   └── metadata.ts           # /api/countries, /api/parameters
│   │   ├── websocket/
│   │   │   └── debug.ts              # WebSocket debug streaming
│   │   └── middleware/
│   │       ├── error.ts
│   │       └── logging.ts
│   └── postman/
│       └── mcp-test-collection.json  # Postman collection
│
├── client/                           # React Frontend
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── theme.ts                  # MUI grayscale theme
│   │   ├── store/
│   │   │   ├── useAppStore.ts        # Zustand store
│   │   │   └── useDebugStore.ts      # Debug events store
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── MainLayout.tsx    # Split panel
│   │   │   │   └── Footer.tsx
│   │   │   ├── main/
│   │   │   │   ├── ModeToggle.tsx
│   │   │   │   ├── ComparePanel.tsx
│   │   │   │   ├── CountrySelector.tsx
│   │   │   │   ├── ParameterPicker.tsx
│   │   │   │   ├── ChatPanel.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   ├── ChartArea.tsx
│   │   │   │   ├── DynamicChart.tsx
│   │   │   │   ├── AnalysisText.tsx
│   │   │   │   └── SourceReferences.tsx
│   │   │   ├── debug/
│   │   │   │   ├── DebugConsole.tsx
│   │   │   │   ├── ConsoleToolbar.tsx
│   │   │   │   └── DebugEvent.tsx
│   │   │   └── documents/
│   │   │       ├── DocumentsModal.tsx
│   │   │       ├── DocumentCard.tsx
│   │   │       └── UploadArea.tsx
│   │   ├── hooks/
│   │   │   ├── useChat.ts
│   │   │   ├── useCompare.ts
│   │   │   ├── useDocuments.ts
│   │   │   ├── useDebugWebSocket.ts
│   │   │   └── useCountries.ts
│   │   ├── api/
│   │   │   └── client.ts             # Axios/fetch wrapper
│   │   └── types/
│   │       ├── chart.ts
│   │       ├── country.ts
│   │       └── debug.ts
│   └── public/
│       └── favicon.ico
│
└── docs/
    ├── SPECIFICATION.md              # This document
    ├── ARCHITECTURE.md
    └── EVALUATION.md
