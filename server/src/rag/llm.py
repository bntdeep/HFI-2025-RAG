"""
AzureChatOpenAI factory + structured-output helper for the LangGraph agent.

EPAM DIAL proxy blocks function-calling (tools API), so we cannot use
LangChain's with_structured_output() which relies on it.  Instead we:
  1. Embed the Pydantic JSON schema in the system prompt.
  2. Call the LLM normally (.ainvoke).
  3. Extract and parse the JSON from the response text.
  4. Validate with Pydantic.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Type, TypeVar

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel

from ..config import settings

M = TypeVar("M", bound=BaseModel)


@lru_cache(maxsize=1)
def get_llm() -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_endpoint=settings.epam_dial_base_url,
        api_key=settings.epam_dial_api_key,
        azure_deployment=settings.main_llm_deployment,
        api_version=settings.api_version,
        temperature=settings.main_llm_temperature,
        max_tokens=settings.main_llm_max_tokens,
    )


async def invoke_structured(
    messages: list[BaseMessage],
    model_class: Type[M],
) -> M:
    """
    Call the LLM and parse the response as a Pydantic model.

    Appends the JSON schema to the first SystemMessage so the model knows
    exactly what format to return.  Parses JSON from the response (handles
    optional markdown code-fence wrapping).

    Raises json.JSONDecodeError or pydantic.ValidationError on bad output.
    """
    schema_str = json.dumps(model_class.model_json_schema(), indent=2)
    json_instruction = (
        "\n\nRespond with ONLY a valid JSON object — no explanation, no markdown, "
        "no code fences — that matches this schema exactly:\n" + schema_str
    )

    # Inject instruction into the first SystemMessage (or prepend one)
    patched: list[BaseMessage] = []
    injected = False
    for msg in messages:
        if not injected and isinstance(msg, SystemMessage):
            patched.append(SystemMessage(content=msg.content + json_instruction))
            injected = True
        else:
            patched.append(msg)
    if not injected:
        patched = [SystemMessage(content=json_instruction)] + patched

    llm = get_llm()
    response = await llm.ainvoke(patched)
    content: str = response.content.strip()

    # Strip optional markdown code fence
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    json_str = fence_match.group(1) if fence_match else content

    # Grab the first {...} block if the model added extra text
    if not json_str.startswith("{"):
        brace_match = re.search(r"\{.*\}", json_str, re.DOTALL)
        if brace_match:
            json_str = brace_match.group(0)

    data = json.loads(json_str)
    return model_class.model_validate(data)
