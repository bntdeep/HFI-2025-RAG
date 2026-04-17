"""
Step 3: Extract images from PDF pages and describe them using gpt-4o vision.

Only images larger than MIN_IMAGE_BYTES are sent to the vision API
(smaller ones are typically logos, icons, or decorative elements).
"""
from __future__ import annotations

import asyncio
import base64
import uuid
from pathlib import Path

import fitz  # PyMuPDF
from langchain_core.documents import Document
from openai import AsyncAzureOpenAI

from ..config import settings
from .pdf_parser import PageInfo

MIN_IMAGE_BYTES = 8_000   # skip tiny decorative images


def _make_vision_client() -> AsyncAzureOpenAI:
    return AsyncAzureOpenAI(
        api_key=settings.epam_dial_api_key,
        azure_endpoint=settings.epam_dial_base_url,
        api_version=settings.api_version,
        azure_deployment=settings.vision_llm_deployment,
    )


_VISION_PROMPT = (
    "This image is from the 2025 Human Freedom Index report published by "
    "the Cato Institute and Fraser Institute. "
    "Describe what this figure shows. Include: chart type (bar, line, scatter, etc.), "
    "any countries or regions mentioned, the specific freedom metrics displayed, "
    "key data points or trends visible, axis labels and units if present. "
    "Be concise but specific — your description will be indexed for semantic search."
)


async def _describe_image(
    client: AsyncAzureOpenAI,
    image_bytes: bytes,
    image_ext: str,
    page_number: int,
) -> str:
    b64 = base64.b64encode(image_bytes).decode()
    mime = f"image/{image_ext}"
    try:
        resp = await client.chat.completions.create(
            model=settings.vision_llm_deployment,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": _VISION_PROMPT},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                ],
            }],
            max_tokens=settings.vision_llm_max_tokens,
        )
        return resp.choices[0].message.content or ""
    except Exception as exc:
        return f"[Could not describe image on page {page_number}: {exc}]"


async def extract_image_chunks(
    pdf_path: str | Path,
    pages: list[PageInfo],
    document_id: str,
    document_name: str,
) -> list[Document]:
    """
    For every page that has images, extract each image (above MIN_IMAGE_BYTES),
    send it to the vision LLM, and return a list of Documents tagged as
    chunk_type='image_description'.
    """
    pages_with_images = [p for p in pages if p.has_images]
    if not pages_with_images:
        return []

    pdf_path = Path(pdf_path)
    doc = fitz.open(str(pdf_path))
    client = _make_vision_client()

    tasks: list[tuple[int, int, bytes, str]] = []  # (page_num, img_idx, bytes, ext)
    for page_info in pages_with_images:
        page = doc[page_info.page_number - 1]
        for img_idx, xref in enumerate(page_info.image_xrefs):
            try:
                base_img = doc.extract_image(xref)
            except Exception:
                continue
            img_bytes: bytes = base_img["image"]
            if len(img_bytes) < MIN_IMAGE_BYTES:
                continue
            tasks.append((page_info.page_number, img_idx, img_bytes, base_img["ext"]))

    doc.close()

    if not tasks:
        return []

    # Describe all images concurrently (respect rate limits with a semaphore)
    sem = asyncio.Semaphore(5)

    async def describe_with_sem(page_num: int, img_idx: int, img_bytes: bytes, ext: str) -> Document | None:
        async with sem:
            description = await _describe_image(client, img_bytes, ext, page_num)
        if not description.strip():
            return None
        return Document(
            page_content=description,
            metadata={
                "chunk_id": str(uuid.uuid4()),
                "document_id": document_id,
                "document_name": document_name,
                "page_number": page_num,
                "chunk_type": "image_description",
                "image_index": img_idx,
            },
        )

    results = await asyncio.gather(
        *[describe_with_sem(pn, ii, ib, ext) for pn, ii, ib, ext in tasks],
        return_exceptions=False,
    )
    return [r for r in results if r is not None]
