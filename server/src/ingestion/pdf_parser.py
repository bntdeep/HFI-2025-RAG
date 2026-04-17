"""
Step 1: Convert PDF to per-page markdown using pymupdf4llm.

Returns a ParsedDocument with:
  - full_markdown: entire document as one string (with <!-- PAGE:N --> markers)
  - pages: list of per-page info dicts (page_number, text, has_images, image_list)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf4llm
import fitz  # PyMuPDF — used for raw image extraction


@dataclass
class PageInfo:
    page_number: int      # 1-based
    text: str             # raw markdown for this page
    has_images: bool
    has_tables: bool      # heuristic: "|" present in text
    image_xrefs: list[int] = field(default_factory=list)  # fitz image xrefs


@dataclass
class ParsedDocument:
    # Full document markdown with embedded <!-- PAGE:N --> markers so that
    # chunk_markdown() can later recover which page each chunk starts on.
    full_markdown: str
    pages: list[PageInfo]
    total_pages: int

    @property
    def page_numbers_with_images(self) -> list[int]:
        return [p.page_number for p in self.pages if p.has_images]


def parse_pdf(pdf_path: str | Path) -> ParsedDocument:
    """
    Parse a PDF into per-page markdown + image metadata.

    Strategy:
    1. Use pymupdf4llm with page_chunks=True to get per-page text preserving
       headers and markdown tables.
    2. Insert <!-- PAGE:N --> markers between pages.
    3. Build full_markdown from the concatenation (for MarkdownHeaderTextSplitter).
    4. Record which pages have images (for the image_extractor step).
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # --- pymupdf4llm per-page extraction ---
    page_chunks: list[dict] = pymupdf4llm.to_markdown(
        str(pdf_path),
        page_chunks=True,
        show_progress=False,
    )

    # --- fitz pass to collect image xrefs per page ---
    doc = fitz.open(str(pdf_path))
    page_image_xrefs: dict[int, list[int]] = {}  # 0-based page index → xrefs
    for page_idx in range(len(doc)):
        xrefs = [img[0] for img in doc[page_idx].get_images(full=True)]
        page_image_xrefs[page_idx] = xrefs
    doc.close()

    pages: list[PageInfo] = []
    markdown_parts: list[str] = []

    for chunk in page_chunks:
        # pymupdf4llm metadata uses 0-based "page" key
        meta = chunk.get("metadata", {})
        page_idx = meta.get("page", 0)
        page_num = page_idx + 1
        text: str = chunk.get("text", "")

        xrefs = page_image_xrefs.get(page_idx, [])
        has_images = bool(xrefs)
        has_tables = bool(re.search(r"^\|.+\|", text, re.MULTILINE))

        pages.append(PageInfo(
            page_number=page_num,
            text=text,
            has_images=has_images,
            has_tables=has_tables,
            image_xrefs=xrefs,
        ))

        # Inject page marker then page content
        markdown_parts.append(f"\n\n<!-- PAGE:{page_num} -->\n\n{text}")

    full_markdown = "".join(markdown_parts)

    return ParsedDocument(
        full_markdown=full_markdown,
        pages=pages,
        total_pages=len(pages),
    )
