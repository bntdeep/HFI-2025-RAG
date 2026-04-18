## 7. Evaluation — Retrieval Precision@K

### 7.1 Scope

Phase 2 evaluation focuses on **retrieval precision only** — does the vector store surface
the right chunks when a country is queried?  No LLM calls are made during evaluation.

Answer accuracy and chart correctness are deferred until retrieval quality meets targets.

### 7.2 Test Dataset

3 countries from `documents/Albania-Burundi.pdf`, 3 queries each = **9 queries total**.

**Ground truth (2023 values, verified from PDF):**

| Country | Rank | HF Score | PF Score | EF Score | Rule of Law | Security | Movement | Religion |
|---------|------|----------|----------|----------|-------------|----------|----------|---------|
| Austria | 22   | 8.54     | 9.24     | 7.57     | 7.7         | 9.6      | 9.8      | 9.1     |
| Belarus | 140  | 5.20     | 4.69     | 5.92     | 3.7         | 7.6      | 5.2      | 3.6     |
| Belgium | 23   | 8.53     | 9.21     | 7.58     | 7.6         | 9.8      | 9.8      | 9.0     |

**Test queries:**

| # | Country | Query |
|---|---------|-------|
| 1 | Austria | "What is Austria's Human Freedom ranking and score?" |
| 2 | Austria | "Austria personal freedom economic freedom scores breakdown" |
| 3 | Austria | "Austria Rule of Law Movement Religion subcategory scores" |
| 4 | Belarus | "What is Belarus's Human Freedom ranking and score?" |
| 5 | Belarus | "Belarus personal freedom economic freedom scores breakdown" |
| 6 | Belarus | "Belarus Rule of Law Association Expression subcategory scores" |
| 7 | Belgium | "What is Belgium's Human Freedom ranking and score?" |
| 8 | Belgium | "Belgium personal freedom economic freedom scores breakdown" |
| 9 | Belgium | "Belgium Rule of Law Security Movement subcategory scores" |

### 7.3 Precision@K Definition

**K = 5** (matches the comparison retriever `top_k=5`).

A retrieved chunk is **relevant** if either condition holds:
1. `chunk.metadata["countries_mentioned"]` list contains the target country name, OR
2. The country name appears (case-insensitive) in `chunk.page_content`

```
Precision@5 = (number of relevant chunks in top 5) / 5
```

### 7.4 Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Precision@5 per query | relevant / 5 | ≥ 0.60 |
| Per-country avg Precision@5 | mean across country's 3 queries | ≥ 0.70 |
| MAP (Mean Average Precision) | mean across all 9 queries | ≥ 0.75 |

### 7.5 Evaluation Script

**Location:** `server/eval/precision_eval.py`

**Run:**
```bash
cd server
python -m eval.precision_eval
```

**Key design:**
- Uses `src.storage.vector_store.VectorStoreClient` directly — no LangGraph, no LLM
- Runs `asyncio.run(main())`
- Ground truth hardcoded in script (verified from PDF, not used for retrieval — only printed for reference)

### 7.6 Expected Console Output

```
=== RAG RETRIEVAL PRECISION EVALUATION ===
Countries: Austria, Belarus, Belgium  |  K=5  |  9 queries

  #  Country  Query (short)                      Relevant  Prec@5
  -  -------  ---------------------------------  --------  ------
  1  Austria  ranking and score                     ?/5      ?.??
  2  Austria  pf/ef breakdown                       ?/5      ?.??
  3  Austria  subcategory scores                    ?/5      ?.??
  4  Belarus  ranking and score                     ?/5      ?.??
  5  Belarus  pf/ef breakdown                       ?/5      ?.??
  6  Belarus  subcategory scores                    ?/5      ?.??
  7  Belgium  ranking and score                     ?/5      ?.??
  8  Belgium  pf/ef breakdown                       ?/5      ?.??
  9  Belgium  subcategory scores                    ?/5      ?.??

Per-Country Avg Precision@5:
  Austria : ?.?? [✓/✗]   Belarus : ?.?? [✓/✗]   Belgium : ?.?? [✓/✗]

MAP: ?.??  [target >= 0.75]

Low-precision queries (Prec@5 < 0.60):
  Q?  <Country> "<query>" — top chunk countries: [<country list>]
      Chunk 1: score=?.??? | country=<name> | section=<...> | type=<text/table>
      ...

Ground Truth Reference:
  Austria : rank=22   hf=8.54  pf=9.24  ef=7.57  rol=7.7  sec=9.6  mov=9.8  rel=9.1
  Belarus : rank=140  hf=5.20  pf=4.69  ef=5.92  rol=3.7  sec=7.6  mov=5.2  rel=3.6
  Belgium : rank=23   hf=8.53  pf=9.21  ef=7.58  rol=7.6  sec=9.8  mov=9.8  rel=9.0
```

Low-precision rows are printed with per-chunk details to help diagnose retrieval failures
(e.g. Belgium chunks being crowded out by Austria/Belarus due to embedding similarity).
