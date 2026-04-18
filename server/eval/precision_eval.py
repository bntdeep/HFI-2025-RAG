"""
RAG Retrieval Precision Evaluation
===================================
Measures Precision@5 for Austria, Belarus, Belgium — 3 queries per country.

A chunk is "relevant" if:
  1. chunk.metadata["countries_mentioned"] contains the target country, OR
  2. The country name appears (case-insensitive) in chunk.page_content

No LLM calls. Pure vector store evaluation.

Run:
    cd server
    python -m eval.precision_eval
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Allow running from the server/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.storage.vector_store import VectorStoreClient

# ── Ground truth (verified from Albania-Burundi.pdf, 2023 values) ────────────

GROUND_TRUTH: dict[str, dict] = {
    "Austria": {
        "rank": 22,   "hf_score": 8.54, "pf_score": 9.24, "ef_score": 7.57,
        "rule_of_law": 7.7, "security": 9.6, "movement": 9.8, "religion": 9.1,
    },
    "Belarus": {
        "rank": 140,  "hf_score": 5.20, "pf_score": 4.69, "ef_score": 5.92,
        "rule_of_law": 3.7, "security": 7.6, "movement": 5.2, "religion": 3.6,
    },
    "Belgium": {
        "rank": 23,   "hf_score": 8.53, "pf_score": 9.21, "ef_score": 7.58,
        "rule_of_law": 7.6, "security": 9.8, "movement": 9.8, "religion": 9.0,
    },
}

# ── Test queries ──────────────────────────────────────────────────────────────

TEST_QUERIES: list[tuple[str, str]] = [
    ("Austria", "What is Austria's Human Freedom ranking and score?"),
    ("Austria", "Austria personal freedom economic freedom scores breakdown"),
    ("Austria", "Austria Rule of Law Movement Religion subcategory scores"),
    ("Belarus", "What is Belarus's Human Freedom ranking and score?"),
    ("Belarus", "Belarus personal freedom economic freedom scores breakdown"),
    ("Belarus", "Belarus Rule of Law Association Expression subcategory scores"),
    ("Belgium", "What is Belgium's Human Freedom ranking and score?"),
    ("Belgium", "Belgium personal freedom economic freedom scores breakdown"),
    ("Belgium", "Belgium Rule of Law Security Movement subcategory scores"),
]

TOP_K = 5
PRECISION_THRESHOLD = 0.60
COUNTRY_AVG_THRESHOLD = 0.70
MAP_THRESHOLD = 0.75

# ── Relevance check ───────────────────────────────────────────────────────────

def _is_relevant(chunk, country: str) -> bool:
    """True if chunk is relevant for the given country."""
    countries = chunk.metadata.get("countries_mentioned", [])
    if isinstance(countries, list) and country in countries:
        return True
    if isinstance(countries, str) and country in countries:
        return True
    return country.lower() in chunk.page_content.lower()


def _short_query(query: str, max_len: int = 35) -> str:
    words = query.split()
    # strip country name (first word usually)
    short = " ".join(words[1:]) if len(words) > 3 else query
    return (short[:max_len - 1] + "…") if len(short) > max_len else short

# ── Main evaluation ───────────────────────────────────────────────────────────

async def main() -> None:
    vs = VectorStoreClient()

    results: list[dict] = []

    for country, query in TEST_QUERIES:
        chunks_with_scores = await vs.search(query, top_k=TOP_K)
        chunks = [doc for doc, _ in chunks_with_scores]
        scores = [s for _, s in chunks_with_scores]

        relevant = [_is_relevant(c, country) for c in chunks]
        precision = sum(relevant) / TOP_K

        # Collect top-chunk country info for diagnostics
        chunk_info = []
        for doc, score in chunks_with_scores:
            countries = doc.metadata.get("countries_mentioned", [])
            if isinstance(countries, str):
                import json
                try:
                    countries = json.loads(countries)
                except Exception:
                    countries = [countries]
            section = (
                doc.metadata.get("section_h2")
                or doc.metadata.get("section_h1")
                or ""
            )
            chunk_info.append({
                "score": round(score, 3),
                "countries": countries[:3],  # top 3 for display
                "section": section[:40] if section else "—",
                "type": doc.metadata.get("chunk_type", "?"),
            })

        results.append({
            "country": country,
            "query": query,
            "relevant_count": sum(relevant),
            "precision": precision,
            "chunk_info": chunk_info,
        })

    # ── Print results table ───────────────────────────────────────────────────

    header = f"\n{'='*65}"
    print(header)
    print("  RAG RETRIEVAL PRECISION EVALUATION")
    print(f"  Countries: Austria, Belarus, Belgium  |  K={TOP_K}  |  {len(TEST_QUERIES)} queries")
    print('='*65)

    col = "  {:>2}  {:<8}  {:<37}  {:>8}  {:>6}"
    print(col.format("#", "Country", "Query", "Relevant", "Prec@5"))
    print("  " + "-"*61)

    country_precs: dict[str, list[float]] = {c: [] for c in GROUND_TRUTH}

    for i, r in enumerate(results, 1):
        flag = "✓" if r["precision"] >= PRECISION_THRESHOLD else "✗ LOW"
        rel_str = f"{r['relevant_count']}/{TOP_K}"
        short = _short_query(r["query"])
        print(col.format(i, r["country"], short, rel_str, f"{r['precision']:.2f} {flag}"))
        country_precs[r["country"]].append(r["precision"])

    # ── Per-country averages ──────────────────────────────────────────────────

    print()
    print("  Per-Country Avg Precision@5:")
    country_avgs: dict[str, float] = {}
    for country, precs in country_precs.items():
        avg = sum(precs) / len(precs)
        country_avgs[country] = avg
        flag = "✓" if avg >= COUNTRY_AVG_THRESHOLD else "✗ LOW"
        print(f"    {country:<8}: {avg:.2f}  {flag}")

    # ── MAP ───────────────────────────────────────────────────────────────────

    map_score = sum(r["precision"] for r in results) / len(results)
    map_flag = "✓" if map_score >= MAP_THRESHOLD else "✗ BELOW TARGET"
    print()
    print(f"  MAP: {map_score:.2f}  {map_flag}  (target >= {MAP_THRESHOLD})")

    # ── Low-precision details ─────────────────────────────────────────────────

    low = [r for r in results if r["precision"] < PRECISION_THRESHOLD]
    if low:
        print()
        print("  Low-precision queries (Prec@5 < 0.60):")
        for i, r in enumerate(results):
            if r["precision"] >= PRECISION_THRESHOLD:
                continue
            idx = results.index(r) + 1
            print(f"    Q{idx}  {r['country']}  \"{r['query'][:60]}\"")
            for j, ci in enumerate(r["chunk_info"], 1):
                countries_str = ", ".join(ci["countries"]) if ci["countries"] else "—"
                print(
                    f"      Chunk {j}: score={ci['score']:.3f}"
                    f" | countries=[{countries_str}]"
                    f" | type={ci['type']}"
                    f" | section={ci['section']!r}"
                )
    else:
        print()
        print("  All queries meet the precision threshold.")

    # ── Ground truth reference ────────────────────────────────────────────────

    print()
    print("  Ground Truth Reference (2023 values from PDF):")
    for country, gt in GROUND_TRUTH.items():
        print(
            f"    {country:<8}: rank={gt['rank']:<4} "
            f"hf={gt['hf_score']}  pf={gt['pf_score']}  ef={gt['ef_score']}"
            f"  rol={gt['rule_of_law']}  sec={gt['security']}"
            f"  mov={gt['movement']}  rel={gt['religion']}"
        )

    print(f"\n{'='*65}\n")

    # Exit with non-zero if targets not met
    if map_score < MAP_THRESHOLD:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
