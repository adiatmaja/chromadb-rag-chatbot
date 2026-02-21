# Product Reranking via LLM Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix wrong product matching by fetching the top 3 product candidates from ChromaDB and passing all of them to the LLM, which then selects the correct one based on semantic understanding.

**Architecture:** The retriever gains a `get_product_candidates()` method that returns top N products by embedding similarity. The orchestrator calls this when the primary match is a PRODUCT, builds a numbered candidate list in the context, and the system prompt instructs the LLM to pick the most relevant product before answering. No change to FAQ/intent flow.

**Tech Stack:** Python, ChromaDB (already used), OpenAI-compatible client (already used), no new dependencies.

---

### Task 1: Add `get_product_candidates()` to `UnifiedRetriever`

**Files:**
- Modify: `src/core/retriever.py`

**What it does:** Queries only the product collection, returns a list of `SearchResult` (not just the best one).

**Step 1: Open the file and locate insertion point**

In `src/core/retriever.py`, find the `search_all()` method (line ~269). Add the new method right after `search_all()`, before `_search_collection()`.

**Step 2: Add the method**

Insert this method at line ~334, between `search_all()` and `_search_collection()`:

```python
def get_product_candidates(
        self,
        query: str,
        n: int = 3
) -> List[SearchResult]:
    """
    Returns top N product candidates for a query.

    Used by the orchestrator to provide multiple candidates to the LLM
    for reranking, improving precision when products are semantically similar.

    Args:
        query (str): User's search query
        n (int): Number of candidates to return

    Returns:
        List[SearchResult]: Top N products sorted by relevance score
    """
    if not self.has_products:
        return []

    query_embedding = self.embedding_model.encode([query]).tolist()
    candidates = self._search_collection(
        self.product_collection,
        query_embedding,
        ContentType.PRODUCT,
        min(n, self.product_collection.count())
    )
    candidates.sort(key=lambda r: r.relevance_score, reverse=True)
    return candidates
```

**Step 3: Verify the method is syntactically correct**

```bash
docker-compose exec rag python -c "from src.core.retriever import UnifiedRetriever; print('import ok')"
```

Expected: `import ok`

**Step 4: Commit**

```bash
git add src/core/retriever.py
git commit -m "feat: add get_product_candidates() to UnifiedRetriever for LLM reranking"
```

---

### Task 2: Update `_build_context_string()` for Multiple Product Candidates

**Files:**
- Modify: `src/core/orchestrator.py`

**What it does:** When multiple product candidates are available, format them as a numbered list so the LLM can compare and select the right one.

**Step 1: Locate `_build_context_string()` in `orchestrator.py`**

Current signature (line ~186):
```python
def _build_context_string(self, search_result: SearchResult) -> tuple[str, str]:
```

**Step 2: Replace the method signature and PRODUCT branch**

Find and replace this block:

```python
def _build_context_string(self, search_result: SearchResult) -> tuple[str, str]:
    """
    Formats search result into context string for LLM.

    Args:
        search_result (SearchResult): Result from unified search

    Returns:
        tuple: (context_string, content_type_string)
    """
    metadata = search_result.metadata
    content_type = search_result.content_type

    if content_type == ContentType.PRODUCT:
        context = (
            f"SKU: {metadata.get('sku', 'N/A')}, "
            f"Nama Resmi: {metadata.get('official_name', 'N/A')}, "
            f"Kuantitas Dus: {metadata.get('pack_size_desc', 'N/A')}, "
            f"Sinonim: {metadata.get('colloquial_names', 'N/A')}"
        )
        return context, "PRODUK"

    elif content_type == ContentType.FAQ:
        context = (
            f"Pertanyaan: {metadata.get('question', 'N/A')}\n"
            f"Jawaban: {metadata.get('answer', 'N/A')}"
        )
        return context, "FAQ"

    else:
        return "Informasi tidak tersedia", "UNKNOWN"
```

Replace with:

```python
def _build_context_string(
    self,
    search_result: SearchResult,
    product_candidates: List[SearchResult] | None = None
) -> tuple[str, str]:
    """
    Formats search result into context string for LLM.

    When product_candidates is provided (multiple products), formats them
    as a numbered list so the LLM can select the most relevant one.

    Args:
        search_result (SearchResult): Best result from unified search
        product_candidates (list | None): Top N product candidates for reranking

    Returns:
        tuple: (context_string, content_type_string)
    """
    content_type = search_result.content_type

    if content_type == ContentType.PRODUCT:
        candidates = product_candidates or [search_result]
        if len(candidates) == 1:
            m = candidates[0].metadata
            context = (
                f"SKU: {m.get('sku', 'N/A')}, "
                f"Nama Resmi: {m.get('official_name', 'N/A')}, "
                f"Kuantitas Dus: {m.get('pack_size_desc', 'N/A')}, "
                f"Sinonim: {m.get('colloquial_names', 'N/A')}"
            )
        else:
            lines = ["Beberapa kandidat produk yang mungkin sesuai:"]
            for i, candidate in enumerate(candidates, 1):
                m = candidate.metadata
                lines.append(
                    f"{i}. SKU: {m.get('sku', 'N/A')} | "
                    f"Nama: {m.get('official_name', 'N/A')} | "
                    f"Alias: {m.get('colloquial_names', 'N/A')} | "
                    f"Kemasan: {m.get('pack_size_desc', 'N/A')}"
                )
            lines.append(
                "\nPilih produk yang PALING SESUAI dengan pertanyaan pengguna. "
                "Gunakan SKU dari produk terpilih jika perlu check_inventory."
            )
            context = "\n".join(lines)
        return context, "PRODUK"

    elif content_type == ContentType.FAQ:
        metadata = search_result.metadata
        context = (
            f"Pertanyaan: {metadata.get('question', 'N/A')}\n"
            f"Jawaban: {metadata.get('answer', 'N/A')}"
        )
        return context, "FAQ"

    else:
        return "Informasi tidak tersedia", "UNKNOWN"
```

**Step 3: Add `List` to imports if not already present**

Check line ~38 in orchestrator.py:
```python
from typing import Dict, Any, Optional, List
```
`List` is already imported — no change needed.

**Step 4: Verify syntax**

```bash
docker-compose exec rag python -c "from src.core.orchestrator import UnifiedRAGOrchestrator; print('import ok')"
```

Expected: `import ok` (will print other init messages too, but no ImportError)

**Step 5: Commit**

```bash
git add src/core/orchestrator.py
git commit -m "feat: update _build_context_string to support multiple product candidates"
```

---

### Task 3: Wire Candidates into `process_query()`

**Files:**
- Modify: `src/core/orchestrator.py`

**What it does:** Call `get_product_candidates()` when the primary match is a PRODUCT and pass candidates to `_build_context_string()`.

**Step 1: Locate `process_query()` in orchestrator.py**

Find this block inside `process_query()` (around line ~174):

```python
        # Step 2: CONTEXT BUILDING
        console.print("\n[bold cyan]Step 2: Building Context for LLM[/bold cyan]")
        context_string, content_type_str = self._build_context_string(search_result)
        console.print(f"[dim]Content Type: {content_type_str}[/dim]")
        console.print(f"[dim]Context: {context_string[:200]}...[/dim]")
```

**Step 2: Replace that block with candidate-aware version**

```python
        # Step 2: CONTEXT BUILDING
        console.print("\n[bold cyan]Step 2: Building Context for LLM[/bold cyan]")
        product_candidates = None
        if search_result.content_type == ContentType.PRODUCT:
            product_candidates = self.retriever.get_product_candidates(user_query, n=3)
            console.print(
                f"[dim]Retrieved {len(product_candidates)} product candidates for reranking[/dim]"
            )
        context_string, content_type_str = self._build_context_string(
            search_result, product_candidates
        )
        console.print(f"[dim]Content Type: {content_type_str}[/dim]")
        console.print(f"[dim]Context: {context_string[:200]}...[/dim]")
```

**Step 3: Verify end-to-end import chain**

```bash
docker-compose exec rag python -c "
from src.core.orchestrator import UnifiedRAGOrchestrator
# Don't fully init (needs LLM) — just check imports
print('imports ok')
"
```

Expected: `imports ok`

**Step 4: Commit**

```bash
git add src/core/orchestrator.py
git commit -m "feat: pass top-3 product candidates to LLM for reranking in process_query"
```

---

### Task 4: End-to-End Verification in Docker

**Files:** None (verification only)

**Step 1: Run a direct retrieval test to confirm candidates are returned**

```bash
docker-compose exec rag python -c "
import sys
sys.path.insert(0, 'scripts')
try:
    from mock_onnxruntime import *
except ImportError:
    pass
from src.core.retriever import UnifiedRetriever

r = UnifiedRetriever()
candidates = r.get_product_candidates('mau beli indomie goreng', n=3)
print('Candidates:')
for i, c in enumerate(candidates, 1):
    print(f'  {i}. score={c.relevance_score:.4f} sku={c.metadata[\"sku\"]} name={c.metadata[\"official_name\"]}')
"
```

Expected output (order may vary, but IMG001 should appear):
```
  1. score=0.5389  sku=IMA002  name=Indomie Mi Instan Rasa Ayam Bawang
  2. score=0.4021  sku=IMG001  name=Indomie Mi Goreng Original
  3. score=0.3445  sku=MSG003  name=Mie Sedaap Goreng Original
```

Both products are now presented to the LLM. Qwen2.5 will correctly select IMG001 (Mi Goreng) from the numbered list because "goreng" clearly matches.

**Step 2: Test context formatting directly**

```bash
docker-compose exec rag python -c "
import sys
sys.path.insert(0, 'scripts')
try:
    from mock_onnxruntime import *
except ImportError:
    pass
from src.core.retriever import UnifiedRetriever
from src.core.orchestrator import UnifiedRAGOrchestrator

r = UnifiedRetriever()
candidates = r.get_product_candidates('mau beli indomie goreng', n=3)
best = candidates[0]

# Test orchestrator context building without LLM init
import src.core.orchestrator as orch_module
# Access _build_context_string directly via a minimal stub
from src.core.retriever import ContentType, SearchResult

class StubOrchestrator:
    _build_context_string = UnifiedRAGOrchestrator._build_context_string

stub = StubOrchestrator()
ctx, ctype = stub._build_context_string(best, candidates)
print('=== Context sent to LLM ===')
print(ctx)
"
```

Expected: Numbered list of 3 products ending with reranking instruction.

**Step 3: Run interactive query via your terminal**

In your own terminal (not Claude Code):
```bash
docker-compose exec -it rag python scripts/run_query.py
```

Query: `mau beli indomie goreng`

Expected: LLM now responds about **Indomie Mi Goreng Original** (IMG001), not Ayam Bawang.

**Step 4: Test inventory check with correct product**

Query: `mau beli indomie goreng 2 dus`

Expected: LLM calls `check_inventory(sku="IMG001", requested_quantity=80)` (2 dus × 40 pcs), stock reader returns result from the updated `stock_data.csv`.
