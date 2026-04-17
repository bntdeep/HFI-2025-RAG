"""
Step 6: Enrich each chunk with countries_mentioned and metrics_mentioned.

Uses word-boundary regex matching (no external NLP dependencies needed).
"""
from __future__ import annotations

import re
from langchain_core.documents import Document

from ..utils.countries import COUNTRY_NAMES, ALIASES as COUNTRY_ALIASES
from ..utils.parameters import HFI_PARAMETERS, _ALIAS_MAP as PARAM_ALIAS_MAP


# ── Pre-compile country patterns ──────────────────────────────────────────────

def _word_pattern(text: str) -> re.Pattern:
    return re.compile(r"\b" + re.escape(text) + r"\b", re.IGNORECASE)


# Map of canonical_name_lower → compiled pattern
_COUNTRY_PATTERNS: dict[str, tuple[str, re.Pattern]] = {
    name.lower(): (name, _word_pattern(name))
    for name in COUNTRY_NAMES
}

# Alias patterns: alias_lower → (canonical_name, pattern)
_ALIAS_PATTERNS: dict[str, tuple[str, re.Pattern]] = {
    alias.lower(): (canonical, _word_pattern(alias))
    for alias, canonical in COUNTRY_ALIASES.items()
}

# ── Pre-compile parameter patterns ───────────────────────────────────────────

# code → compiled pattern (match exact code like "pf_rol")
_PARAM_CODE_PATTERNS: list[tuple[str, re.Pattern]] = [
    (p.code, re.compile(r"\b" + re.escape(p.code) + r"\b", re.IGNORECASE))
    for p in HFI_PARAMETERS
]

# name/alias → canonical code pattern
_PARAM_NAME_PATTERNS: list[tuple[str, re.Pattern]] = [
    (p.code, _word_pattern(p.name))
    for p in HFI_PARAMETERS
] + [
    (code, _word_pattern(alias))
    for alias, code in PARAM_ALIAS_MAP.items()
    if len(alias) > 4  # skip very short aliases to reduce false positives
]


def detect_countries(text: str) -> list[str]:
    """Return sorted list of canonical country names mentioned in *text*."""
    found: set[str] = set()

    for name_lower, (canonical, pattern) in _COUNTRY_PATTERNS.items():
        if pattern.search(text):
            found.add(canonical)

    for alias_lower, (canonical, pattern) in _ALIAS_PATTERNS.items():
        if pattern.search(text):
            found.add(canonical)

    return sorted(found)


def detect_parameters(text: str) -> list[str]:
    """Return sorted list of canonical parameter codes mentioned in *text*."""
    found: set[str] = set()

    for code, pattern in _PARAM_CODE_PATTERNS:
        if pattern.search(text):
            found.add(code)

    for code, pattern in _PARAM_NAME_PATTERNS:
        if pattern.search(text):
            found.add(code)

    return sorted(found)


def enrich_chunks(chunks: list[Document]) -> list[Document]:
    """
    Mutate each chunk in-place adding:
      - countries_mentioned: list[str]
      - metrics_mentioned:   list[str]
    Returns the same list (for chaining).
    """
    for chunk in chunks:
        chunk.metadata["countries_mentioned"] = detect_countries(chunk.page_content)
        chunk.metadata["metrics_mentioned"] = detect_parameters(chunk.page_content)
    return chunks
