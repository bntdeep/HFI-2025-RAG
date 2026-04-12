## 4. MCP Server

4.1 Tools

search_documents
json


{
  "name": "search_documents",
  "description": "Semantic search over indexed documents. Returns relevant chunks with metadata.",
  "parameters": {
    "query": { "type": "string", "description": "Natural language search query" },
    "top_k": { "type": "integer", "default": 10, "description": "Number of chunks to return" },
    "document_id": { "type": "string", "optional": true, "description": "Filter by specific document" },
    "chunk_type": { "type": "string", "optional": true, "enum": ["text", "table", "image_description"] }
  },
  "returns": {
    "chunks": [
      {
        "content": "string",
        "metadata": "ChunkMetadata",
        "similarity_score": "float"
      }
    ]
  }
}
compare_countries
json


{
  "name": "compare_countries",
  "description": "Compare multiple countries across specified freedom parameters. Uses RAG to find relevant data, then LLM to extract and structure comparison.",
  "parameters": {
    "countries": { "type": "array", "items": "string", "minItems": 2, "maxItems": 6 },
    "parameters": { "type": "array", "items": "string", "description": "Freedom parameters to compare" },
    "include_chart": { "type": "boolean", "default": true }
  },
  "returns": {
    "comparison": {
      "countries": [
        {
          "name": "string",
          "flag": "string (emoji)",
          "scores": { "param_name": "float" }
        }
      ]
    },
    "chart_data": "ChartConfig | null",
    "analysis": "string",
    "sources": ["ChunkReference"]
  }
}
get_country_profile
json


{
  "name": "get_country_profile",
  "description": "Get comprehensive freedom profile for a single country.",
  "parameters": {
    "country": { "type": "string" }
  },
  "returns": {
    "country": "string",
    "flag": "string",
    "overall_rank": "integer",
    "overall_score": "float",
    "personal_freedom": { "score": "float", "subcategories": {} },
    "economic_freedom": { "score": "float", "subcategories": {} },
    "chart_data": "ChartConfig",
    "analysis": "string",
    "sources": ["ChunkReference"]
  }
}
extract_chart_data
json


{
  "name": "extract_chart_data",
  "description": "Extract data from document suitable for visualization. LLM analyzes retrieved chunks and returns chart-ready JSON.",
  "parameters": {
    "query": { "type": "string", "description": "What to visualize" },
    "chart_type": { "type": "string", "enum": ["bar", "pie", "line", "radar", "scatter"], "optional": true }
  },
  "returns": {
    "chart_config": {
      "type": "string (chart type)",
      "title": "string",
      "data": "array",
      "xKey": "string",
      "yKeys": ["string"],
      "colors": ["string"]
    },
    "insight": "string",
    "sources": ["ChunkReference"]
  }
}
upload_document
json


{
  "name": "upload_document",
  "description": "Upload and index a new PDF document.",
  "parameters": {
    "file_path": { "type": "string", "description": "Path to uploaded PDF" },
    "document_name": { "type": "string", "optional": true }
  },
  "returns": {
    "document_id": "string",
    "document_name": "string",
    "chunks_created": "integer",
    "pages_processed": "integer",
    "tables_found": "integer",
    "images_found": "integer",
    "status": "string"
  }
}
delete_document
json


{
  "name": "delete_document",
  "description": "Delete an indexed document and all its chunks from vector store.",
  "parameters": {
    "document_id": { "type": "string" }
  },
  "returns": {
    "deleted": "boolean",
    "chunks_removed": "integer"
  }
}
list_documents
json


{
  "name": "list_documents",
  "description": "List all indexed documents with metadata.",
  "parameters": {},
  "returns": {
    "documents": [
      {
        "document_id": "string",
        "document_name": "string",
        "uploaded_at": "ISO datetime",
        "pages": "integer",
        "chunks": "integer",
        "file_size_bytes": "integer"
      }
    ]
  }
}
4.2 Resources

yaml


resources:
  - uri: "documents://list"
    name: "Indexed Documents"
    description: "List of all currently indexed documents"
    
  - uri: "countries://list"  
    name: "Available Countries"
    description: "All countries found in indexed documents with flags"
    # Populated during ingestion by scanning chunk metadata
    
  - uri: "parameters://list"
    name: "Freedom Parameters"  
    description: "All comparison parameters/categories available"
    # Static list based on HFI structure:
    # personal_freedom, economic_freedom, rule_of_law,
    # security_safety, movement, religion, expression,
    # relationships, size_of_government, legal_system,
    # sound_money, freedom_to_trade, regulation
4.3 Prompts

yaml


prompts:
  - name: "analyze-country"
    description: "Analyze a single country's freedom profile"
    arguments:
      - name: "country"
        required: true
    template: |
      Analyze {country}'s freedom profile from the Human Freedom Index.
      Include overall ranking, key strengths and weaknesses across 
      personal and economic freedom categories.
      Return structured JSON with scores and analysis.

  - name: "compare-countries"  
    description: "Compare countries across parameters"
    arguments:
      - name: "countries"
        required: true
      - name: "parameters"
        required: true
    template: |
      Compare {countries} across these parameters: {parameters}.
      Extract exact scores from the document.
      Return structured comparison JSON with chart data.

  - name: "extract-trends"
    description: "Extract trends and patterns from the index"
    arguments:
      - name: "topic"
        required: true
    template: |
      Analyze trends related to {topic} in the Human Freedom Index.
      Identify patterns, top/bottom performers, regional differences.
      Return data suitable for visualization.
