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


def detect_primary_country(chunk: Document, countries_mentioned: list[str]) -> str:
    """
    Return the single country this chunk is primarily about, or '' if ambiguous.

    Priority:
    1. section_country set by the chunker — propagated from a bold country marker
       (e.g. **AUSTRIA**) that precedes this chunk inside a regional section.
       Most reliable for HFI PDFs where countries are bold text, not H3 headers.
    2. Most-specific section header (h3 → h2 → h1) naming exactly one country.
    3. Exactly one country mentioned anywhere in the chunk.
    """
    # Priority 1: country context injected by the chunker
    sc = chunk.metadata.get("section_country", "")
    if sc:
        return sc

    # Priority 2: section header uniquely identifies a country
    for field in ("section_h3", "section_h2", "section_h1"):
        header = chunk.metadata.get(field, "")
        if header:
            found = detect_countries(header)
            if len(found) == 1:
                return found[0]

    # Priority 3: only one country in the whole chunk
    if len(countries_mentioned) == 1:
        return countries_mentioned[0]

    return ""


def enrich_chunks(chunks: list[Document]) -> list[Document]:
    """
    Mutate each chunk in-place adding:
      - countries_mentioned: list[str]
      - metrics_mentioned:   list[str]
      - primary_country:     str  (scalar — the single country this chunk is about, or '')
    Returns the same list (for chaining).
    """
    for chunk in chunks:
        # Include section headers in country detection — table chunks have the country
        # name only in section_h2 (e.g. "**AUSTRIA**"), not in the numeric table body.
        text_to_scan = chunk.page_content
        for field in ("section_h1", "section_h2", "section_h3"):
            section = chunk.metadata.get(field, "")
            if section:
                text_to_scan += " " + section
        countries = detect_countries(text_to_scan)
        # If the chunker injected a section_country (from a bold country marker),
        # ensure it's in countries_mentioned even if the chunk body text doesn't
        # spell out the country name (e.g. a table of numbers under **AUSTRIA**).
        sc = chunk.metadata.get("section_country", "")
        if sc and sc not in countries:
            countries = sorted(set(countries) | {sc})
        chunk.metadata["countries_mentioned"] = countries
        chunk.metadata["metrics_mentioned"] = detect_parameters(chunk.page_content)
        chunk.metadata["primary_country"] = detect_primary_country(chunk, countries)
    return chunks
