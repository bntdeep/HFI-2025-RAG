"""
LangGraph agent graph — wires all nodes together and exposes the public API.

Graph topology:
  START → router ──[crud]──────────────────────────→ crud_handler → END
                ──[comparison|profile|trend|general]→ retriever → analyzer → formatter → END
"""
from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from .nodes.analyzer import analyzer_node
from .nodes.crud_handler import crud_handler_node
from .nodes.formatter import formatter_node
from .nodes.retriever import retriever_node
from .nodes.router import router_node
from .schemas import AgentState


# ── Conditional routing ───────────────────────────────────────────────────────

def _route_after_router(state: AgentState) -> str:
    return "crud_handler" if state["intent"] == "crud" else "retriever"


# ── Graph assembly ────────────────────────────────────────────────────────────

def _build_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("router", router_node)
    builder.add_node("retriever", retriever_node)
    builder.add_node("analyzer", analyzer_node)
    builder.add_node("crud_handler", crud_handler_node)
    builder.add_node("formatter", formatter_node)

    builder.set_entry_point("router")

    builder.add_conditional_edges(
        "router",
        _route_after_router,
        {
            "retriever": "retriever",
            "crud_handler": "crud_handler",
        },
    )

    builder.add_edge("retriever", "analyzer")
    builder.add_edge("analyzer", "formatter")
    builder.add_edge("formatter", END)
    builder.add_edge("crud_handler", END)

    return builder


# Compiled graph — stateless, safe to reuse across concurrent async requests
graph = _build_graph().compile()


# ── Public API ────────────────────────────────────────────────────────────────

async def run_query(
    query: str,
    mode: str = "chat",
    selected_countries: list[str] | None = None,
    selected_parameters: list[str] | None = None,
    history: list | None = None,
) -> AgentState:
    """
    Run the agent graph for a single query.

    Args:
        query:               The user's natural-language question.
        mode:                "chat" (default) or "structured" (UI-driven comparison).
        selected_countries:  Explicit country list; overrides LLM extraction.
        selected_parameters: Explicit parameter list; overrides LLM extraction.
        history:             Prior BaseMessage list for multi-turn context.

    Returns:
        Final AgentState dict with response_text, chart_config, sources, debug_events.
    """
    initial_state: AgentState = {
        "messages": history or [],
        "query": query,
        "mode": mode,
        "selected_countries": selected_countries,
        "selected_parameters": selected_parameters,
        # Fields populated by nodes — initialised to empty defaults
        "intent": "",
        "retrieved_chunks": [],
        "retrieval_scores": [],
        "extracted_data": None,
        "analysis_text": None,
        "chart_config": None,
        "response_text": "",
        "sources": [],
        "debug_events": [],
    }
    return await graph.ainvoke(initial_state)


def print_debug(result: AgentState) -> None:
    """Pretty-print the agent trace from a run_query() result."""
    SEP = "─" * 60
    print(f"\n{SEP}")
    print("  🤖 AGENT DEBUG TRACE")
    print(SEP)

    for event in result.get("debug_events", []):
        node = event.get("node", "?")

        if node == "router":
            intent = event.get("intent", "?")
            intent_emoji = {
                "comparison": "⚖️",
                "profile": "🪪",
                "trend": "📈",
                "general": "💬",
                "crud": "🗄️",
            }.get(intent, "❓")
            print(f"\n🔀 [router]")
            print(f"  {intent_emoji} intent     : {intent}")
            print(f"  🌍 countries  : {event.get('countries')}")
            print(f"  📊 parameters : {event.get('parameters')}")

        elif node == "retriever":
            strategy = event.get("strategy", "?")
            print(f"\n🔍 [retriever]")
            print(f"  📌 strategy   : {strategy}")
            for q in event.get("search_queries", []):
                print(f"  🔎 query      : {q!r}")
            print(f"  📦 chunks     : {event.get('chunks_retrieved')}  (after dedup)")
            print(f"  📉 top scores : {event.get('top_scores')}")

        elif node == "analyzer":
            structured = event.get("structured")
            mode = "✅ structured" if structured else "📝 free-form (fallback)"
            print(f"\n🧠 [analyzer]")
            print(f"  🎯 intent     : {event.get('intent')}")
            print(f"  ⚙️  mode       : {mode}")
            print(f"  📄 ctx chunks : {event.get('context_chunks')}")

        elif node == "crud_handler":
            print(f"\n🗄️  [crud_handler]")
            print("  ⚡ no LLM — direct DB/vector operation")

    chart = result.get("chart_config")
    chart_str = f"✅ {chart.get('chart_type', '?')} chart" if chart else "➖ none"
    print(f"\n🎨 [formatter]")
    print(f"  📊 chart      : {chart_str}")
    print(f"  🔗 sources    : {len(result.get('sources', []))}")
    print(SEP + "\n")


def configure_logging(level: int = logging.INFO) -> None:
    """Call once in test scripts or server startup to enable agent logs."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(name)s  %(message)s",
        datefmt="%H:%M:%S",
    )
