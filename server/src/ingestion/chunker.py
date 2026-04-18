"""
Steps 4 & 5: Header-based chunking + overflow splitting.

Strategy:
1. Replace tables with placeholders so MarkdownHeaderTextSplitter can't split them.
2. Split on H1/H2/H3 headers — each chunk inherits section path metadata.
3. For chunks > chunk_size tokens: apply RecursiveCharacterTextSplitter
   (using tiktoken cl100k_base encoder for accurate token counts).
4. Expand placeholders back into atomic table chunks.
5. Recover page numbers from the <!-- PAGE:N --> markers embedded by pdf_parser.
6. Drop any chunks below min_chunk_size tokens.

Returns a list of LangChain Document objects ready for metadata enrichment.
"""
from __future__ import annotations

import re
import uuid
from typing import Any

import tiktoken
from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from .table_extractor import replace_tables_with_placeholders
from ..utils.countries import COUNTRY_NAMES as _KNOWN_COUNTRIES

# Headers the splitter will use as boundaries
_HEADERS_TO_SPLIT_ON = [
    ("#",   "section_h1"),
    ("##",  "section_h2"),
    ("###", "section_h3"),
]

# Regex to detect and remove page-marker comments
_PAGE_MARKER_RE = re.compile(r"<!--\s*PAGE:(\d+)\s*-->")

# Regex to find table placeholders
_PLACEHOLDER_RE = re.compile(r"<<HFI_TABLE_\d+>>")

# Matches a line that is *only* **SOME TEXT** — used to detect in-section country markers
# e.g. "**AUSTRIA**" that the PDF uses instead of H3 headers
_BOLD_LINE_RE = re.compile(r"^\*\*([^\n*]+?)\*\*\s*$", re.MULTILINE)

# Fast lookup: uppercase country name → canonical name
_COUNTRY_UPPER: dict[str, str] = {n.upper(): n for n in _KNOWN_COUNTRIES}


def _detect_country_marker(text: str) -> str | None:
    """
    Return the canonical country name if *text* contains a line that is solely a bold
    country name (e.g. '**AUSTRIA**').  These appear in HFI PDFs as in-section dividers
    between country profiles when the PDF does not use H3 headers for countries.
    Returns the FIRST such match, or None.
    """
    for m in _BOLD_LINE_RE.finditer(text):
        candidate = m.group(1).strip().upper()
        canonical = _COUNTRY_UPPER.get(candidate)
        if canonical:
            return canonical
    return None

_ENCODER = tiktoken.get_encoding("cl100k_base")


def _count_tokens(text: str) -> int:
    return len(_ENCODER.encode(text))


def _extract_page_number(text: str) -> int | None:
    """Return the last PAGE marker found in *text* (1-based), or None."""
    matches = _PAGE_MARKER_RE.findall(text)
    return int(matches[-1]) if matches else None


def _strip_page_markers(text: str) -> str:
    return _PAGE_MARKER_RE.sub("", text).strip()


def _build_overflow_splitter(chunk_size: int, chunk_overlap: int) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )


def chunk_document(
    full_markdown: str,
    document_id: str,
    document_name: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    min_chunk_size: int = 50,
) -> list[Document]:
    """
    Chunk *full_markdown* (output of pdf_parser.parse_pdf) into LangChain Documents.

    Each document's metadata contains:
      document_id, document_name, chunk_type, chunk_index,
      section_h1/h2/h3, page_number, token_count
      (chunk_id is assigned here as a stable UUID)
    """
    # ── Step 1: protect tables ────────────────────────────────────────────────
    processed_md, table_map = replace_tables_with_placeholders(full_markdown)

    # ── Step 2: header-based split ────────────────────────────────────────────
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=_HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )
    header_chunks: list[Document] = header_splitter.split_text(processed_md)

    overflow_splitter = _build_overflow_splitter(chunk_size, chunk_overlap)

    # ── Regex for stripping markdown bold from header text ────────────────────
    _bold_strip = re.compile(r'\*\*([^*]+)\*\*')

    final_chunks: list[Document] = []
    chunk_index = 0
    current_page: int | None = None  # carry-forward for chunks without a page marker

    # section_country persists ACROSS header boundaries.
    # The HFI PDF pattern is:  ## **ALBANIA**  (country H2, empty body)
    #                           ## EASTERN EUROPE  (region H2, holds Albania's data)
    # We must NOT reset on non-country headers so the country context flows through.
    section_country: str | None = None

    for hchunk in header_chunks:
        content: str = hchunk.page_content
        section_meta: dict[str, Any] = {
            k: v for k, v in hchunk.metadata.items()
            if k in ("section_h1", "section_h2", "section_h3")
        }

        # Update section_country when the section header itself names a country
        # (e.g. section_h2 = "**ALBANIA**").  Leave it unchanged for non-country
        # headers like "EASTERN EUROPE" so Albania's context propagates forward.
        for field in ("section_h3", "section_h2", "section_h1"):
            hdr = section_meta.get(field, "")
            if hdr:
                plain = _bold_strip.sub(r'\1', hdr).strip().upper()
                canonical = _COUNTRY_UPPER.get(plain)
                if canonical:
                    section_country = canonical
                    break

        # ── Step 5: recover page number ──────────────────────────────────────
        # If this chunk contains a page marker use it; otherwise fall back to
        # the last page we saw (handles page breaks that precede a new header).
        page_number = _extract_page_number(content)
        if page_number is not None:
            current_page = page_number
        else:
            page_number = current_page
        content_clean = _strip_page_markers(content)

        # ── Step 4: expand table placeholders ────────────────────────────────
        # Split on placeholders while keeping them in the parts list
        parts = _PLACEHOLDER_RE.split(content_clean)
        placeholders_found = _PLACEHOLDER_RE.findall(content_clean)

        # Interleave: parts[0], placeholder[0], parts[1], placeholder[1], ...
        interleaved: list[tuple[str, bool]] = []  # (text, is_table)
        for i, part in enumerate(parts):
            if part.strip():
                interleaved.append((part, False))
            if i < len(placeholders_found):
                ph = placeholders_found[i]
                if ph in table_map:
                    interleaved.append((table_map[ph], True))

        for segment_text, is_table in interleaved:
            segment_text = segment_text.strip()
            if not segment_text:
                continue

            # Secondary: also detect bold country markers in body text
            # (handles PDFs where **COUNTRY** appears inside a section rather
            # than as its own H2 header).
            if not is_table:
                detected = _detect_country_marker(segment_text)
                if detected is not None:
                    section_country = detected
                    if _count_tokens(segment_text) < min_chunk_size:
                        continue

            base_meta = {
                **section_meta,
                "document_id": document_id,
                "document_name": document_name,
                "page_number": page_number,
            }
            if section_country:
                base_meta["section_country"] = section_country

            if is_table:
                # Prepend country + section headers to the table so the embedding
                # captures the country name.  The section headers only contain the
                # region (e.g. "EASTERN EUROPE"), so we prepend the country name
                # explicitly when we have it so tables aren't anonymous.
                ctx_lines = []
                if section_country:
                    ctx_lines.append(f"## {section_country}")
                ctx_lines += [
                    f"{'#' * int(k[-1])} {v}"
                    for k, v in sorted(section_meta.items())
                    if v
                ]
                enriched_text = ("\n".join(ctx_lines) + "\n\n" + segment_text).strip() if ctx_lines else segment_text
                # Tables are never split
                token_count = _count_tokens(enriched_text)
                final_chunks.append(Document(
                    page_content=enriched_text,
                    metadata={
                        **base_meta,
                        "chunk_id": str(uuid.uuid4()),
                        "chunk_type": "table",
                        "token_count": token_count,
                        "chunk_index": chunk_index,
                    },
                ))
                chunk_index += 1
            else:
                # Text: check size and split if needed
                token_count = _count_tokens(segment_text)
                if token_count < min_chunk_size:
                    continue

                if token_count <= chunk_size:
                    sub_segments = [segment_text]
                else:
                    sub_segments = overflow_splitter.split_text(segment_text)

                for sub in sub_segments:
                    sub = sub.strip()
                    tc = _count_tokens(sub)
                    if tc < min_chunk_size:
                        continue
                    final_chunks.append(Document(
                        page_content=sub,
                        metadata={
                            **base_meta,
                            "chunk_id": str(uuid.uuid4()),
                            "chunk_type": "text",
                            "token_count": tc,
                            "chunk_index": chunk_index,
                        },
                    ))
                    chunk_index += 1

    return final_chunks
