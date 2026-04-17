"""
Router node — classifies user intent and extracts entities (countries, parameters).

Uses a single LLM call with structured output (RouterOutput) so both tasks
happen in one round-trip.  Caller-supplied selected_countries / selected_parameters
always override LLM extraction (structured UI mode).
"""
from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from ...utils.countries import COUNTRY_NAMES, get_country
from ...utils.parameters import PARAMETER_CODES
from ..llm import invoke_structured
from ..schemas import AgentState, RouterOutput

logger = logging.getLogger(__name__)

_SYSTEM_TEMPLATE = """\
You are a query classifier for the Human Freedom Index (HFI) RAG application.

Classify the user query into exactly one intent:
- "comparison"  : comparing 2+ countries on any HFI metric
                  (e.g. "compare Switzerland and Germany on personal freedom")
- "profile"     : requesting a single country's full HFI profile
                  (e.g. "tell me about Norway's freedom scores")
- "trend"       : asking about change over time or trends
                  (e.g. "how has press freedom changed over the last 3 years")
- "general"     : any other HFI-related factual question
- "crud"        : document management (list documents, upload, delete)

Also extract:
- countries   : list of country names mentioned — use the canonical HFI registry names
- parameters  : list of HFI parameter codes mentioned (e.g. "pf_expression", "ef_trade")

Sample canonical country names (165 total):
{country_sample}

Available HFI parameter codes:
{parameter_codes}

If no countries or parameters are mentioned return empty lists.
"""

_HUMAN_TEMPLATE = "Query: {query}"


async def router_node(state: AgentState) -> dict:
    country_sample = ", ".join(COUNTRY_NAMES[:40]) + " … (165 total)"
    param_codes = ", ".join(PARAMETER_CODES)

    messages = [
        SystemMessage(content=_SYSTEM_TEMPLATE.format(
            country_sample=country_sample,
            parameter_codes=param_codes,
        )),
        HumanMessage(content=_HUMAN_TEMPLATE.format(query=state["query"])),
    ]

    result: RouterOutput = await invoke_structured(messages, RouterOutput)

    # Normalize country names through the registry; keep unknown names as-is
    def _normalize(names: list[str]) -> list[str]:
        out = []
        for n in names:
            country = get_country(n)
            out.append(country["name"] if country else n)
        return out

    # Caller-provided values take precedence over LLM extraction
    countries = state.get("selected_countries") or _normalize(result.countries)
    parameters = state.get("selected_parameters") or result.parameters

    logger.info(
        "[router] intent=%-12s countries=%s  params=%s",
        result.intent, countries, parameters,
    )

    debug_event = {
        "node": "router",
        "intent": result.intent,
        "countries": countries,
        "parameters": parameters,
    }

    return {
        "intent": result.intent,
        "selected_countries": countries,
        "selected_parameters": parameters,
        "debug_events": state.get("debug_events", []) + [debug_event],
    }
