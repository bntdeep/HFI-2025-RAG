## 10. Postman Collection Skeleton

json


{
  "info": {
    "name": "HFI RAG - MCP Server Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    { "key": "base_url", "value": "http://localhost:8000" }
  ],
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/health"
      }
    },
    {
      "name": "List Documents",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"list_documents\",\"arguments\":{}},\"id\":1}"
        }
      }
    },
    {
      "name": "Search Documents",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"search_documents\",\"arguments\":{\"query\":\"Switzerland freedom score\",\"top_k\":5}},\"id\":2}"
        }
      }
    },
    {
      "name": "Compare Countries",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"compare_countries\",\"arguments\":{\"countries\":[\"Switzerland\",\"Japan\"],\"parameters\":[\"personal_freedom\",\"economic_freedom\"],\"include_chart\":true}},\"id\":3}"
        }
      }
    },
    {
      "name": "Get Country Profile",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"get_country_profile\",\"arguments\":{\"country\":\"Switzerland\"}},\"id\":4}"
        }
      }
    },
    {
      "name": "Extract Chart Data",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"params\":{\"name\":\"extract_chart_data\",\"arguments\":{\"query\":\"Top 10 countries by overall freedom score\",\"chart_type\":\"bar\"}},\"id\":5}"
        }
      }
    },
    {
      "name": "List Resources - Countries",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"resources/read\",\"params\":{\"uri\":\"countries://list\"},\"id\":6}"
        }
      }
    },
    {
      "name": "List Resources - Parameters",
      "request": {
        "method": "POST",
        "url": "{{base_url}}/mcp",
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"method\":\"resources/read\",\"params\":{\"uri\":\"parameters://list\"},\"id\":7}"
        }
      }
    }
  ]
}
