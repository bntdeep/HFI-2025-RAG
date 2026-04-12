## 5. LangGraph Agent

5.1 Graph Structure



                    ┌──────────┐
                    │  START    │
                    └────┬─────┘
                         ▼
                  ┌──────────────┐
                  │   Router     │  Classify intent:
                  │   Node       │  comparison | profile | 
                  └──┬───┬───┬──┘  trend | general | crud
                     │   │   │
          ┌──────────┘   │   └──────────┐
          ▼              ▼              ▼
   ┌────────────┐ ┌────────────┐ ┌────────────┐
   │ Retriever  │ │ Retriever  │ │  CRUD      │
   │ (comparison│ │ (general)  │ │  Handler   │
   │  focused)  │ │            │ │            │
   └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
         ▼              ▼              ▼
   ┌────────────┐ ┌────────────┐       │
   │ Analyzer   │ │ Analyzer   │       │
   │ (structured│ │ (free-form)│       │
   │  extract)  │ │            │       │
   └─────┬──────┘ └─────┬──────┘       │
         ▼              ▼              │
   ┌────────────┐ ┌────────────┐       │
   │ Formatter  │ │ Formatter  │       │
   │ (chart     │ │ (text +    │       │
   │  config)   │ │  optional  │       │
   │            │ │  chart)    │       │
   └─────┬──────┘ └─────┬──────┘       │
         └───────┬───────┘──────────────┘
                 ▼
          ┌──────────┐
          │   END    │
          └──────────┘
5.2 Agent State Schema

python


class AgentState(TypedDict):
    # Input
    messages: list[BaseMessage]
    query: str
    mode: str  # "chat" | "structured"
    
    # Structured mode inputs (optional)
    selected_countries: list[str] | None
    selected_parameters: list[str] | None
    
    # Router output
    intent: str  # "comparison" | "profile" | "trend" | "general" | "crud"
    
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
5.3 Structured Output Schemas (Pydantic)

python


class CountryScore(BaseModel):
    name: str
    flag: str  # emoji
    score: float
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
    scores_matrix: dict[str, dict[str, float]]  
    # {"Switzerland": {"personal_freedom": 9.23, ...}}
    chart_config: ChartConfig
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
    data_completeness: float  # 0-1, how much data was found

class SourceReference(BaseModel):
    chunk_id: str
    page_number: int
    section: str
    relevance_score: float
