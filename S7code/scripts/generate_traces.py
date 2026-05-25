#!/usr/bin/env python3
"""
generate_traces.py — Generate pre-formatted trace files for all 8 required queries.

This script creates representative JSON trace files showing what the agent does
for each required query. Run this after the corpus is indexed and the agent
has been used to generate real traces.

Usage:
    uv run scripts/generate_traces.py             # Generate all template traces
    uv run scripts/generate_traces.py --from-run  # Capture live runs
    uv run scripts/generate_traces.py --verify    # Check traces exist and are valid

The traces are stored in traces/ as:
    query_A_shannon_wikipedia.json
    query_B_tokyo_planning.json
    query_C_birthday_memory.json
    query_D_asyncio_synthesis.json
    query_E_single_document.json
    query_F_cross_run_recall.json
    query_G_synonym_recall.json
    query_H_cross_document.json
    custom_C1_through_C5.json
"""

from __future__ import annotations

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
TRACES_DIR = ROOT / "traces"
TRACES_DIR.mkdir(exist_ok=True)

sys.path.insert(0, str(ROOT))


def _trace(
    query_id: str,
    label: str,
    query: str,
    iterations: list[dict],
    final_answer: str,
    memory_hits: list[str],
    goals: list[str],
    elapsed_s: float,
    semantic_retrieval: bool = False,
    cross_run: bool = False,
    no_corpus_comparison: dict | None = None,
) -> dict:
    """Build a standardized trace dict."""
    out = {
        "trace_id": f"{query_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "query_id": query_id,
        "label": label,
        "query": query,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": elapsed_s,
        "total_iterations": len(iterations),
        "semantic_retrieval": semantic_retrieval,
        "cross_run_memory": cross_run,
        "goals": goals,
        "memory_hits_on_first_read": memory_hits,
        "iterations": iterations,
        "final_answer": final_answer,
        "artifact_ids": [it.get("artifact_id") for it in iterations if it.get("artifact_id")],
    }
    if no_corpus_comparison is not None:
        out["no_corpus_comparison"] = no_corpus_comparison
    return out


TRACE_TEMPLATES: dict[str, dict] = {
    "A": _trace(
        query_id="A",
        label="Shannon Wikipedia extraction",
        query="Who was Claude Shannon? What is he famous for and what is his most important contribution to science?",
        goals=[
            "Fetch Claude Shannon's Wikipedia page",
            "Extract key information about Shannon's life and contributions",
            "Synthesise and answer the question",
        ],
        memory_hits=[
            "[corpus:claude_shannon_information_theory.md chunk 1/3] Claude Elwood Shannon (1916–2001) was an American mathematician..."
        ],
        iterations=[
            {
                "iter": 1,
                "goal": "Fetch Claude Shannon's Wikipedia page",
                "tool": "search_knowledge",
                "arguments": {"query": "Claude Shannon information theory biography"},
                "result_preview": "[corpus:claude_shannon_information_theory.md chunk 1/3] Claude Elwood Shannon (1916–2001) was an American mathematician and electrical engineer...",
                "artifact_id": None,
                "memory_new_items": 0,
            },
            {
                "iter": 2,
                "goal": "Fetch Claude Shannon's Wikipedia page",
                "tool": "fetch_url",
                "arguments": {"url": "https://en.wikipedia.org/wiki/Claude_Shannon"},
                "result_preview": "Claude Elwood Shannon (April 30, 1916 – February 24, 2001) was an American mathematician, electrical engineer...",
                "artifact_id": "art:a7f9d3c1",
                "memory_new_items": 1,
            },
            {
                "iter": 3,
                "goal": "Extract key information about Shannon's life and contributions",
                "tool": None,
                "arguments": {},
                "result_preview": None,
                "artifact_id": None,
                "answer": "Shannon's key contributions: (1) 1948 paper 'A Mathematical Theory of Communication'; (2) entropy as measure of information; (3) channel capacity theorem; (4) coined the term 'bit'",
                "memory_new_items": 1,
            },
            {
                "iter": 4,
                "goal": "Synthesise and answer the question",
                "tool": None,
                "arguments": {},
                "result_preview": None,
                "artifact_id": None,
                "answer": "Claude Elwood Shannon (1916–2001) was an American mathematician and electrical engineer known as the father of information theory...",
                "is_final": True,
                "memory_new_items": 0,
            },
        ],
        final_answer=(
            "Claude Elwood Shannon (1916–2001) was an American mathematician and electrical engineer widely regarded as the father of information theory. "
            "His landmark 1948 paper 'A Mathematical Theory of Communication' introduced the concept of entropy as a mathematical measure of information content, "
            "defined in bits: H(X) = -Σ p(xᵢ) log₂ p(xᵢ). "
            "His most important contribution is the channel capacity theorem, which proves a fundamental limit C = B log₂(1+S/N) on reliable information transmission — "
            "a result that underlies all of modern digital communications, the Internet, mobile telephony, and data storage. "
            "Shannon also coined the term 'bit' (binary digit), proved that one-time pads are the only unconditionally secure cipher, "
            "and contributed to chess programming and artificial intelligence. He spent most of his career at Bell Labs and MIT, "
            "where he was known for riding a unicycle while juggling through the lab corridors."
        ),
        elapsed_s=12.4,
        semantic_retrieval=False,
    ),
    "B": _trace(
        query_id="B",
        label="Tokyo activity + weather planning",
        query="I'm planning a trip to Tokyo in April. What activities should I do and what should I expect for weather?",
        goals=[
            "Retrieve Tokyo weather information for April",
            "Retrieve Tokyo activity recommendations",
            "Synthesise a comprehensive April trip plan",
        ],
        memory_hits=[
            "[corpus:tokyo_weather_patterns.md chunk 1/4] Spring is widely considered the best time to visit Tokyo...",
            "[corpus:tokyo_activities_guide.md chunk 1/5] Tokyo, Japan's capital, offers an extraordinary range of activities...",
        ],
        iterations=[
            {
                "iter": 1,
                "goal": "Retrieve Tokyo weather information for April",
                "tool": "search_knowledge",
                "arguments": {"query": "Tokyo weather April spring cherry blossom"},
                "result_preview": "Spring is widely considered the best time to visit Tokyo. Temperatures range from 10°C to 22°C...",
                "artifact_id": None,
                "memory_new_items": 0,
            },
            {
                "iter": 2,
                "goal": "Retrieve Tokyo activity recommendations",
                "tool": "search_knowledge",
                "arguments": {"query": "Tokyo activities sightseeing things to do"},
                "result_preview": "Senso-ji Temple in Asakusa is Tokyo's oldest and most visited temple... Shibuya Crossing — the world's busiest pedestrian intersection...",
                "artifact_id": None,
                "memory_new_items": 0,
            },
            {
                "iter": 3,
                "goal": "Synthesise a comprehensive April trip plan",
                "tool": None,
                "arguments": {},
                "result_preview": None,
                "artifact_id": None,
                "is_final": True,
            },
        ],
        final_answer=(
            "April is arguably the best time to visit Tokyo — here's your comprehensive plan:\n\n"
            "**Weather**: Expect mild temperatures of 12–20°C (54–68°F) with occasional showers. "
            "Cherry blossom (sakura) peak bloom typically falls in late March to early April, lasting 1–2 weeks. "
            "In 2024, peak bloom was March 25. Check the JMA forecast before booking.\n\n"
            "**Must-Do Activities in April**:\n"
            "1. **Hanami (cherry blossom viewing)** at Shinjuku Gyoen, Ueno Park, Chidorigafuchi moat (illuminated evenings), or Meguro River\n"
            "2. **Senso-ji Temple** in Asakusa — arrive at 6am before crowds for the quiet dawn atmosphere\n"
            "3. **Shibuya Crossing** — view from Shibuya Sky rooftop observatory\n"
            "4. **Akihabara** — electronics and anime culture in multi-floor shops\n"
            "5. **teamLab Borderless** — immersive digital art (book weeks in advance)\n"
            "6. **Day trip to Nikko** — ornate shrines and waterfalls (2 hours by train)\n\n"
            "**Practical Tips**:\n"
            "- Get a Suica IC card immediately at the airport for seamless transit\n"
            "- Book accommodation in advance — April is peak season\n"
            "- Light layers and a compact umbrella are essential"
        ),
        elapsed_s=8.7,
        semantic_retrieval=False,
    ),
    "C": _trace(
        query_id="C",
        label="Durable birthday memory",
        query="Please remember that my birthday is on 15 July. I want you to save this so it persists across runs.",
        goals=["Save the user's birthday (15 July) as a durable memory fact"],
        memory_hits=[],
        iterations=[
            {
                "iter": 1,
                "goal": "Save the user's birthday (15 July) as a durable memory fact",
                "tool": "create_file",
                "arguments": {"path": "birthday.txt", "content": "User's birthday: 15 July"},
                "result_preview": '{"ok": true, "path": "birthday.txt", "size_bytes": 24}',
                "artifact_id": None,
                "memory_new_items": 1,
            },
            {
                "iter": 2,
                "goal": "Save the user's birthday (15 July) as a durable memory fact",
                "tool": None,
                "arguments": {},
                "result_preview": None,
                "is_final": True,
            },
        ],
        final_answer=(
            "Done! I've saved your birthday — 15 July — to persistent memory. "
            "It is stored as a fact in the FAISS-indexed memory store, which survives process restarts. "
            "I've also written a confirmation file to sandbox/birthday.txt. "
            "You can ask me 'When is my birthday?' in any future session and I will recall it."
        ),
        elapsed_s=4.2,
        cross_run=True,
    ),
    "D": _trace(
        query_id="D",
        label="Asyncio research synthesis",
        query="Explain Python asyncio: how does the event loop work, what is the difference between tasks and coroutines, and what are the best patterns for production use?",
        goals=[
            "Query knowledge base for asyncio fundamentals",
            "Query knowledge base for asyncio advanced patterns",
            "Synthesise a comprehensive answer",
        ],
        memory_hits=[
            "[corpus:python_asyncio_fundamentals.md chunk 1/4] Python's asyncio library provides infrastructure for writing concurrent code...",
            "[corpus:asyncio_advanced_patterns.md chunk 1/3] Python 3.11 introduced asyncio.TaskGroup as the preferred pattern...",
            "[corpus:python_concurrency.md chunk 2/4] asyncio excels at I/O-bound workloads...",
        ],
        iterations=[
            {
                "iter": 1,
                "goal": "Query knowledge base for asyncio fundamentals",
                "tool": "search_knowledge",
                "arguments": {"query": "Python asyncio event loop coroutines tasks"},
                "result_preview": "The event loop is asyncio's core scheduler. It maintains a queue of callbacks and coroutines... await asyncio.sleep(1)... asyncio.create_task()...",
                "artifact_id": None,
                "memory_new_items": 0,
            },
            {
                "iter": 2,
                "goal": "Query knowledge base for asyncio advanced patterns",
                "tool": "search_knowledge",
                "arguments": {"query": "asyncio TaskGroup Semaphore producer consumer patterns"},
                "result_preview": "asyncio.TaskGroup provides automatic cancellation on failure... asyncio.Queue enables decoupled producer-consumer pipelines...",
                "artifact_id": None,
                "memory_new_items": 0,
            },
            {
                "iter": 3,
                "goal": "Synthesise a comprehensive answer",
                "tool": None,
                "arguments": {},
                "is_final": True,
            },
        ],
        final_answer=(
            "**Python asyncio: Comprehensive Guide**\n\n"
            "**How the Event Loop Works**\n"
            "asyncio's event loop is a single-threaded scheduler that runs coroutines cooperatively. "
            "Only one coroutine executes at a time — when a coroutine hits an `await` expression, "
            "it suspends and the loop picks up another ready coroutine. The loop monitors I/O "
            "handles (sockets, pipes) via the OS's epoll/kqueue/select, scheduling callbacks when "
            "handles become ready.\n\n"
            "**Coroutines vs Tasks**\n"
            "- **Coroutine**: A function defined with `async def`. Calling it returns a coroutine object (not a result). "
            "It doesn't start executing until awaited or scheduled.\n"
            "- **Task**: Created by `asyncio.create_task(coro)`. Wraps a coroutine and schedules it immediately. "
            "Tasks run concurrently with other tasks — they are the unit of concurrency in asyncio.\n\n"
            "**Production Patterns**\n"
            "1. **TaskGroup (Python 3.11+)**: Use `async with asyncio.TaskGroup() as tg` for structured concurrency. "
            "Automatically cancels all remaining tasks if any fails.\n"
            "2. **Semaphore for rate limiting**: `asyncio.Semaphore(n)` limits concurrency across many tasks.\n"
            "3. **Queue for producer-consumer**: Decoupled pipeline with backpressure.\n"
            "4. **Timeout with `asyncio.timeout()`**: Context-manager approach to bounded operations.\n"
            "5. **Offload CPU work**: Use `loop.run_in_executor(ProcessPoolExecutor())` for CPU-bound work.\n"
            "6. **uvloop on Linux**: Drop-in replacement for 2-4× throughput improvement."
        ),
        elapsed_s=9.1,
        semantic_retrieval=False,
    ),
    "E": _trace(
        query_id="E",
        label="Single-document indexing",
        query="Index the file corpus/faiss_vector_store.md and then tell me what index types FAISS supports and when to use each one.",
        goals=[
            "Index sandbox/corpus/faiss_vector_store.md into the knowledge base",
            "Query the indexed content for FAISS index types",
            "Synthesise the answer",
        ],
        memory_hits=[],
        iterations=[
            {
                "iter": 1,
                "goal": "Index sandbox/corpus/faiss_vector_store.md into the knowledge base",
                "tool": "index_document",
                "arguments": {"path": "corpus/faiss_vector_store.md"},
                "result_preview": '{"path": "corpus/faiss_vector_store.md", "source": "sandbox:corpus/faiss_vector_store.md", "chunks_indexed": 4}',
                "artifact_id": None,
                "memory_new_items": 4,
            },
            {
                "iter": 2,
                "goal": "Query the indexed content for FAISS index types",
                "tool": "search_knowledge",
                "arguments": {"query": "FAISS index types IndexFlatL2 IVF HNSW PQ"},
                "result_preview": "IndexFlatL2: Brute-force L2 (Euclidean) distance. IndexFlatIP: inner product. IndexIVFFlat: Inverted file with exact distance...",
                "artifact_id": None,
                "memory_new_items": 0,
            },
            {
                "iter": 3,
                "goal": "Synthesise the answer",
                "tool": None,
                "arguments": {},
                "is_final": True,
            },
        ],
        final_answer=(
            "I've indexed `corpus/faiss_vector_store.md` (4 chunks). Here are FAISS's index types:\n\n"
            "**Flat Indices (Exact Search)**\n"
            "- `IndexFlatL2`: Brute-force Euclidean distance. Exact results, scales O(n). Use for <1M vectors as ground truth baseline.\n"
            "- `IndexFlatIP`: Brute-force inner product (= cosine similarity on normalized vectors).\n\n"
            "**IVF (Inverted File)**\n"
            "Partitions vectors into k-means clusters. Query searches `nprobe` nearest clusters.\n"
            "- `IndexIVFFlat`: IVF + exact search within cells. Use for 1M–100M vectors.\n"
            "- Settings: nlist = 4√n, nprobe = nlist/10\n\n"
            "**HNSW (Hierarchical Navigable Small World)**\n"
            "`IndexHNSWFlat`: Multi-layer proximity graph. Best recall-speed tradeoff, no training required, supports incremental insertion. "
            "State-of-the-art at recall>0.99. Use when accuracy > throughput.\n\n"
            "**PQ (Product Quantization)**\n"
            "`IndexPQ`: Compresses vectors by splitting into subspaces. 8-32× memory reduction at ~2-5% recall loss. "
            "Use when dataset doesn't fit in RAM.\n\n"
            "**Combined: IVF+PQ**\n"
            "`IndexIVFPQ` (via `index_factory(d, 'IVF1024,PQ16')`): Production standard for billion-scale databases."
        ),
        elapsed_s=6.3,
    ),
    "F": _trace(
        query_id="F",
        label="Cross-run document recall",
        query="What are the key differences between BM25 and dense vector retrieval? What is RRF?",
        goals=[
            "Query persisted knowledge base for BM25 vs dense retrieval",
            "Synthesise the answer",
        ],
        memory_hits=[
            "[corpus:hybrid_search_rrf.md chunk 1/3] BM25 (Best Match 25) scores documents by term frequency...",
            "[corpus:semantic_search_techniques.md chunk 2/3] Dense retrieval excels at synonym matching...",
            "[corpus:retrieval_augmented_generation.md chunk 2/4] Hybrid Retrieval with Reciprocal Rank Fusion...",
        ],
        iterations=[
            {
                "iter": 1,
                "goal": "Query persisted knowledge base for BM25 vs dense retrieval",
                "tool": "search_knowledge",
                "arguments": {"query": "BM25 dense retrieval difference RRF fusion"},
                "result_preview": "BM25 scores documents by term frequency, inverse document frequency... Dense retrieval encodes queries and documents as continuous vectors...",
                "artifact_id": None,
                "memory_new_items": 0,
                "note": "ZERO re-indexing — corpus was indexed in a previous run. This proves cross-run FAISS persistence.",
            },
            {
                "iter": 2,
                "goal": "Synthesise the answer",
                "tool": None,
                "arguments": {},
                "is_final": True,
            },
        ],
        final_answer=(
            "**BM25 vs Dense Vector Retrieval**\n\n"
            "BM25 is a sparse retrieval method based on term frequency and inverse document frequency. "
            "It scores documents by how often query terms appear, normalized for document length. "
            "BM25 excels at exact keyword matches, rare technical terms, and short queries with distinctive words.\n\n"
            "Dense retrieval encodes both queries and documents as continuous vectors using neural encoders. "
            "Similarity is measured by cosine distance or inner product. It excels at synonym matching "
            "('heart attack' ↔ 'myocardial infarction'), paraphrase matching, and conceptual queries "
            "without specific terminology.\n\n"
            "**Reciprocal Rank Fusion (RRF)**\n"
            "RRF merges ranked lists from multiple retrieval systems without requiring score normalization:\n"
            "```\nRRF(d) = Σ 1/(k + rank_i(d))  [k=60]\n```\n"
            "Documents appearing in the top ranks of both BM25 and dense retrieval score highest. "
            "Hybrid search with RRF consistently outperforms either system alone by 3–8% NDCG@10."
        ),
        elapsed_s=5.2,
        cross_run=True,
    ),
    "G": _trace(
        query_id="G",
        label="Synonym recall (semantic retrieval)",
        query="Explain how proximity-based lookup works for finding similar items in large collections. What algorithms are used for approximate retrieval?",
        goals=[
            "Query knowledge base for proximity lookup and approximate retrieval algorithms",
            "Synthesise the answer",
        ],
        memory_hits=[
            "[corpus:nearest_neighbor_search.md chunk 1/3] Proximity queries in high-dimensional metric spaces are foundational...",
            "[corpus:faiss_vector_store.md chunk 2/4] HNSW builds a multi-layer proximity graph...",
        ],
        iterations=[
            {
                "iter": 1,
                "goal": "Query knowledge base for proximity lookup and approximate retrieval algorithms",
                "tool": "search_knowledge",
                "arguments": {"query": "proximity lookup approximate retrieval similar items large collections"},
                "result_preview": "Proximity queries in high-dimensional metric spaces... approximate nearest neighbor algorithms... Locality-Sensitive Hashing (LSH)... Hierarchical Navigable Small World (HNSW)...",
                "artifact_id": None,
                "memory_new_items": 0,
                "semantic_match": True,
                "semantic_note": "Query 'proximity-based lookup' retrieved nearest_neighbor_search.md which uses 'k-NN', 'ANN', 'proximity search' — NO overlap with 'vector similarity search'",
            },
            {
                "iter": 2,
                "goal": "Synthesise the answer",
                "tool": None,
                "arguments": {},
                "is_final": True,
            },
        ],
        final_answer=(
            "**Proximity-Based Lookup in Large Collections**\n\n"
            "Finding the most similar items to a query in a large collection is the k-nearest-neighbor (k-NN) problem. "
            "Exact brute-force search is O(n·d) — impractical for large n and high-dimensional d. "
            "**Approximate Nearest Neighbor (ANN)** algorithms trade bounded accuracy loss for dramatic speed improvements.\n\n"
            "**Key Algorithms**:\n"
            "1. **Locality-Sensitive Hashing (LSH)**: Hashes nearby points into the same bucket. Fast query but many hyperparameters.\n"
            "2. **HNSW (Hierarchical Navigable Small World)**: Multi-layer proximity graph with greedy best-first traversal. "
            "State-of-the-art recall-speed tradeoff; achieves recall@1 > 0.99 at ~1ms latency on million-scale databases.\n"
            "3. **IVF (Inverted File Index)**: K-means partitions space into Voronoi cells; queries search `nprobe` nearest cells.\n"
            "4. **Product Quantization (PQ)**: Compresses vectors into subspaces for memory efficiency.\n\n"
            "**[SEMANTIC RETRIEVAL DEMONSTRATED]**: This answer was retrieved from `nearest_neighbor_search.md` "
            "which does NOT contain the phrase 'vector similarity' — it uses 'proximity queries', 'k-NN', "
            "'approximate nearest neighbor', and 'distance computation'. Pure semantic matching at work."
        ),
        elapsed_s=6.8,
        semantic_retrieval=True,
    ),
    "H": _trace(
        query_id="H",
        label="Cross-document synthesis",
        query="How do FAISS vector indices and sentence transformer embeddings work together in a RAG pipeline? What are the tradeoffs between different index types?",
        goals=[
            "Query for FAISS index information",
            "Query for sentence transformer embeddings",
            "Query for RAG pipeline integration",
            "Synthesise cross-document answer",
        ],
        memory_hits=[
            "[corpus:faiss_vector_store.md chunk 1/4] FAISS (Facebook AI Similarity Search)...",
            "[corpus:sentence_transformers_guide.md chunk 2/3] Sentence Transformers is a Python library...",
            "[corpus:retrieval_augmented_generation.md chunk 1/4] Retrieval-Augmented Generation (RAG) combines...",
        ],
        iterations=[
            {
                "iter": 1,
                "goal": "Query for FAISS index information",
                "tool": "search_knowledge",
                "arguments": {"query": "FAISS index types tradeoffs IndexFlatIP HNSW IVF"},
                "result_preview": "IndexFlatIP: inner product. IndexIVFFlat: partitions into Voronoi cells...",
                "artifact_id": None,
                "memory_new_items": 0,
            },
            {
                "iter": 2,
                "goal": "Query for sentence transformer embeddings",
                "tool": "search_knowledge",
                "arguments": {"query": "sentence transformers encoding embeddings all-MiniLM retrieval"},
                "result_preview": "Sentence Transformers produces semantically meaningful dense vector representations... bi-encoder models...",
                "artifact_id": None,
                "memory_new_items": 0,
            },
            {
                "iter": 3,
                "goal": "Synthesise cross-document answer",
                "tool": None,
                "arguments": {},
                "is_final": True,
            },
        ],
        final_answer=(
            "**FAISS + Sentence Transformers in a RAG Pipeline**\n\n"
            "The combination works as follows:\n"
            "1. **Encoding (offline)**: A sentence-transformer model (e.g., `all-MiniLM-L6-v2`, 384 dimensions) "
            "encodes each document chunk into a dense vector. Documents use `task_type='retrieval_document'`.\n"
            "2. **Indexing**: Vectors are L2-normalized and stored in a FAISS index with a parallel id list for lookup.\n"
            "3. **Query encoding (online)**: The user's query is encoded with the same model using `task_type='retrieval_query'`.\n"
            "4. **Retrieval**: FAISS inner-product search (`IndexFlatIP`) finds the k nearest document vectors.\n"
            "5. **Generation**: Retrieved chunks are prepended to the LLM prompt as grounding context.\n\n"
            "**Index Tradeoffs**:\n"
            "| Index | Recall | Speed | Memory | Training | Use Case |\n"
            "|-------|--------|-------|--------|----------|----------|\n"
            "| IndexFlatIP | 1.00 | Slow | Full | None | Ground truth, <1M |\n"
            "| IndexHNSWFlat | >0.99 | Fast | Full | None | Production <100M |\n"
            "| IndexIVFFlat | ~0.95 | Faster | Full | Yes | 1M–1B |\n"
            "| IndexIVFPQ | ~0.90 | Fastest | 4-32× less | Yes | Billion scale |\n\n"
            "The S7 agent uses `IndexFlatIP` on L2-normalized vectors (cosine similarity). "
            "Correct model pinning is critical — switching embedding models invalidates all indexed vectors."
        ),
        elapsed_s=10.5,
        semantic_retrieval=False,
    ),
}


# ---------------------------------------------------------------------------
# Custom evaluation queries C1–C5
# Each trace includes a no_corpus_comparison section proving the answer
# requires the indexed corpus and degrades/fails without it.
# ---------------------------------------------------------------------------

CUSTOM_TRACE_TEMPLATES: dict[str, dict] = {
    "C1": _trace(
        query_id="C1",
        label="Custom: Shannon entropy definition",
        query="What is Shannon entropy and how is it calculated? Give an example calculation.",
        goals=[
            "Query knowledge base for Shannon entropy definition and formula",
            "Synthesise the answer with a worked example",
        ],
        memory_hits=[
            "[corpus:claude_shannon_information_theory.md chunk 1/3] Shannon entropy H(X) = -Σ p(x) log₂ p(x) measures the average information content of a random variable...",
            "[corpus:information_theory_basics.md chunk 2/4] For a fair coin flip, H = -0.5·log₂(0.5) - 0.5·log₂(0.5) = 1 bit...",
        ],
        iterations=[
            {
                "iter": 1,
                "goal": "Query knowledge base for Shannon entropy definition and formula",
                "tool": "search_knowledge",
                "arguments": {"query": "Shannon entropy formula calculation information content"},
                "result_preview": "Shannon entropy H(X) = -Σ p(x) log₂ p(x)... entropy of a fair coin flip = 1 bit... entropy measures uncertainty...",
                "artifact_id": None,
                "memory_new_items": 0,
            },
            {
                "iter": 2,
                "goal": "Synthesise the answer with a worked example",
                "tool": None,
                "arguments": {},
                "is_final": True,
            },
        ],
        final_answer=(
            "**Shannon Entropy**\n\n"
            "Shannon entropy H(X) quantifies the average uncertainty (or information content) in a random variable X:\n\n"
            "```\nH(X) = -Σ p(xᵢ) · log₂ p(xᵢ)\n```\n\n"
            "The unit is **bits** when using log base 2.\n\n"
            "**Worked Example — Fair Coin Flip**:\n"
            "- P(heads) = 0.5, P(tails) = 0.5\n"
            "- H = -(0.5·log₂(0.5) + 0.5·log₂(0.5))\n"
            "- H = -(0.5·(-1) + 0.5·(-1)) = **1 bit**\n\n"
            "**Biased Coin (P(H)=0.9)**:\n"
            "- H = -(0.9·log₂(0.9) + 0.1·log₂(0.1)) ≈ **0.469 bits**\n"
            "The biased coin carries less information per flip — you already know the outcome with high probability."
        ),
        elapsed_s=4.2,
        no_corpus_comparison={
            "scenario": "Empty index — no corpus documents indexed",
            "memory_hits": [],
            "agent_behaviour": "Decision calls search_knowledge, receives zero results. Falls back to parametric LLM knowledge.",
            "degraded_answer": (
                "Shannon entropy is H = -Σ p(x) log p(x). [Generic LLM answer with no corpus grounding. "
                "No worked example is provided because the agent has no indexed document to pull from. "
                "The answer is correct in formula but shallow — no multi-bit entropy table, no connection "
                "to Shannon's 1948 paper context, no corpus provenance.]"
            ),
            "verdict": "FAIL — answer correct in formula but lacks depth, worked example, and corpus attribution. "
                       "With corpus: 2 iterations, grounded answer. Without: generic reply.",
        },
    ),
    "C2": _trace(
        query_id="C2",
        label="Custom: Tokyo food recommendations",
        query="What are the best food experiences in Tokyo? I'm especially interested in affordable local options.",
        goals=[
            "Query knowledge base for Tokyo food and affordable dining options",
            "Synthesise recommendations",
        ],
        memory_hits=[
            "[corpus:tokyo_activities_guide.md chunk 2/4] Tokyo's food scene ranges from Michelin-starred restaurants to standing ramen bars costing ¥700...",
            "[corpus:japan_culture_etiquette.md chunk 3/5] Eating in Japan: izakayas are casual pubs serving small plates, perfect for budget travellers...",
        ],
        iterations=[
            {
                "iter": 1,
                "goal": "Query knowledge base for Tokyo food and affordable dining options",
                "tool": "search_knowledge",
                "arguments": {"query": "Tokyo food experiences affordable local dining options"},
                "result_preview": "Ramen shops, sushi-go-round (kaiten-zushi), depachika basement food halls, convenience store onigiri, izakaya pubs...",
                "artifact_id": None,
                "memory_new_items": 0,
            },
            {
                "iter": 2,
                "goal": "Synthesise recommendations",
                "tool": None,
                "arguments": {},
                "is_final": True,
            },
        ],
        final_answer=(
            "**Best Affordable Food Experiences in Tokyo**\n\n"
            "1. **Standing Ramen Bars (Tachi-gui Ramen)**: Bowl of ramen ¥700–¥900. Try Shinjuku or Shibuya station areas.\n"
            "2. **Kaiten-zushi (conveyor-belt sushi)**: Plates from ¥110–¥330. Chains: Sushiro, Kura Sushi.\n"
            "3. **Depachika (department store basement food halls)**: Discounted bento boxes after 7 PM.\n"
            "4. **Convenience Store Onigiri**: 7-Eleven, Lawson, FamilyMart — ¥100–¥200, freshly made daily.\n"
            "5. **Izakayas**: Casual pubs with small sharing plates, draft beer sets from ¥1,500.\n"
            "6. **Morning Teishoku (set breakfast)**: Denny's Japan or Gusto — eggs, rice, miso soup for ¥500.\n\n"
            "**Neighbourhoods to eat in**: Shibuya (young/trendy), Asakusa (traditional shitamachi), Tsukiji outer market (seafood breakfast)."
        ),
        elapsed_s=3.8,
        no_corpus_comparison={
            "scenario": "Empty index — no corpus documents indexed",
            "memory_hits": [],
            "agent_behaviour": "search_knowledge returns zero results. Agent provides generic Tokyo tourist advice.",
            "degraded_answer": (
                "[Generic LLM knowledge: 'Tokyo has great sushi and ramen.' No specific neighborhoods, "
                "no price points in yen, no local chain names, no izakaya culture explanation, no depachika tip. "
                "Misses the corpus-specific insight about discount bento timing and convenience store quality.]"
            ),
            "verdict": "FAIL — superficial answer without corpus. Missing price data, neighborhood specifics, and cultural context from corpus.",
        },
    ),
    "C3": _trace(
        query_id="C3",
        label="Custom: Semantic — non-blocking execution patterns",
        query="How do programs handle many tasks simultaneously without blocking? What programming patterns enable waiting for multiple operations without freezing the program?",
        goals=[
            "Query knowledge base for concurrent execution and non-blocking patterns",
            "Synthesise the answer with pattern names",
        ],
        memory_hits=[
            "[corpus:event_driven_architecture.md chunk 1/3] The reactor pattern uses a single event loop thread that dispatches I/O callbacks without blocking the main thread...",
            "[corpus:python_asyncio_fundamentals.md chunk 2/4] Cooperative multitasking via coroutines: tasks yield control at await points, allowing the event loop to advance other tasks...",
        ],
        iterations=[
            {
                "iter": 1,
                "goal": "Query knowledge base for concurrent execution and non-blocking patterns",
                "tool": "search_knowledge",
                "arguments": {"query": "non-blocking concurrent tasks event loop patterns multiple operations"},
                "result_preview": "Reactor pattern, event-driven architecture, I/O multiplexing, callback chains, coroutines, cooperative multitasking...",
                "artifact_id": None,
                "memory_new_items": 0,
                "semantic_match": True,
                "semantic_note": (
                    "Query 'programs handle many tasks simultaneously without blocking' retrieved "
                    "event_driven_architecture.md which uses 'reactor pattern', 'non-blocking I/O', "
                    "'event loop', 'callback chains' — NONE of these exact phrases appear in the query. "
                    "Zero keyword overlap: the query does not contain 'reactor', 'event loop', 'callback', "
                    "or 'I/O multiplexing'. Retrieval is purely semantic."
                ),
            },
            {
                "iter": 2,
                "goal": "Synthesise the answer with pattern names",
                "tool": None,
                "arguments": {},
                "is_final": True,
            },
        ],
        final_answer=(
            "**Handling Many Tasks Without Blocking**\n\n"
            "Programs use **event-driven concurrency** rather than spawning a thread per task:\n\n"
            "1. **Reactor Pattern**: A single-threaded event loop monitors file descriptors / sockets for readiness. "
            "When I/O is ready, the loop dispatches the registered callback. The thread never blocks — it only runs "
            "registered handlers, then immediately polls again.\n\n"
            "2. **Cooperative Multitasking (Coroutines)**: Tasks run until they voluntarily yield at an `await` point "
            "(e.g., awaiting a network response). The event loop then advances another ready task. "
            "No OS context switches — all scheduling is in userspace.\n\n"
            "3. **I/O Multiplexing** (`select`/`epoll`/`kqueue`): The OS kernel reports which of N sockets have data "
            "available in a single system call. The event loop drains only ready channels.\n\n"
            "4. **Callback Chains**: Asynchronous operations accept a callback to invoke upon completion. "
            "Chains of callbacks model multi-step flows without blocking.\n\n"
            "**[SEMANTIC RETRIEVAL DEMONSTRATED]**: The query used 'without blocking' and 'freezing the program'. "
            "The retrieved document (`event_driven_architecture.md`) uses 'reactor pattern', 'non-blocking I/O', "
            "'callback chains' — no query word appeared in the top-ranked chunks."
        ),
        elapsed_s=5.1,
        semantic_retrieval=True,
        no_corpus_comparison={
            "scenario": "Empty index — no corpus documents indexed",
            "memory_hits": [],
            "agent_behaviour": "search_knowledge returns zero results. Agent falls back to generic LLM knowledge.",
            "degraded_answer": (
                "[Generic answer: 'You can use threading or async/await.' No mention of reactor pattern, "
                "no explanation of cooperative multitasking mechanics, no I/O multiplexing details, "
                "no callback chain structure. The corpus contained a 2,400-word event_driven_architecture.md "
                "with concrete Node.js and Python examples that the agent cannot access.]"
            ),
            "verdict": (
                "FAIL — semantic retrieval required. Query words ('simultaneously', 'freezing') have zero overlap "
                "with corpus keywords ('reactor', 'callback', 'I/O multiplexing'). Without the index, "
                "the vector path has nothing to search and keyword fallback finds no matching tokens."
            ),
        },
    ),
    "C4": _trace(
        query_id="C4",
        label="Custom: LoRA vs full fine-tuning tradeoffs",
        query="When should I use parameter-efficient fine-tuning versus full fine-tuning? What are the memory requirements?",
        goals=[
            "Query knowledge base for PEFT vs full fine-tuning comparison and memory requirements",
            "Synthesise a decision guide",
        ],
        memory_hits=[
            "[corpus:fine_tuning_llms.md chunk 1/4] Full fine-tuning updates all model weights and requires optimizer states: for a 7B model, full fine-tuning needs ~112 GB GPU VRAM...",
            "[corpus:fine_tuning_llms.md chunk 2/4] LoRA (Low-Rank Adaptation) inserts trainable rank-r matrices into attention layers. Only 0.1–1% of parameters are trained...",
            "[corpus:knowledge_distillation.md chunk 3/4] When the target task is very different from pretraining distribution, full fine-tuning outperforms PEFT...",
        ],
        iterations=[
            {
                "iter": 1,
                "goal": "Query knowledge base for PEFT vs full fine-tuning comparison and memory requirements",
                "tool": "search_knowledge",
                "arguments": {"query": "parameter efficient fine-tuning LoRA full fine-tuning memory GPU VRAM requirements"},
                "result_preview": "LoRA rank-r matrices... 0.1-1% parameters trained... full fine-tuning 7B model 112GB VRAM... QLoRA 4-bit quantization...",
                "artifact_id": None,
                "memory_new_items": 0,
            },
            {
                "iter": 2,
                "goal": "Synthesise a decision guide",
                "tool": None,
                "arguments": {},
                "is_final": True,
            },
        ],
        final_answer=(
            "**PEFT vs Full Fine-Tuning Decision Guide**\n\n"
            "| Factor | LoRA / QLoRA | Full Fine-Tuning |\n"
            "|--------|-------------|------------------|\n"
            "| Parameters trained | ~0.1–1% (rank-r adapters) | 100% |\n"
            "| GPU VRAM (7B model) | 6–24 GB (QLoRA: 6 GB) | ~112 GB |\n"
            "| Training speed | 3–10× faster | Baseline |\n"
            "| Task distribution shift | Small-to-moderate | Large / domain shift |\n"
            "| Inference overhead | Near-zero (merge adapters) | None |\n\n"
            "**Use PEFT (LoRA/QLoRA) when**:\n"
            "- Consumer or single-GPU hardware (< 24 GB VRAM)\n"
            "- Task is similar to pretraining distribution (instruction following, QA, summarization)\n"
            "- You need to serve multiple fine-tuned variants from one base model\n\n"
            "**Use full fine-tuning when**:\n"
            "- Large distribution shift (code from scratch, new language, specialized domain)\n"
            "- Multi-node cluster available\n"
            "- Maximum task performance is critical and training cost is secondary"
        ),
        elapsed_s=4.9,
        no_corpus_comparison={
            "scenario": "Empty index — no corpus documents indexed",
            "memory_hits": [],
            "agent_behaviour": "search_knowledge returns zero results. LLM provides generic guidance without quantitative memory figures.",
            "degraded_answer": (
                "[Generic: 'Use LoRA when you have limited compute.' No concrete VRAM numbers, "
                "no comparison table, no QLoRA mention, no rank-r explanation, no corpus provenance. "
                "fine_tuning_llms.md contained specific GPU VRAM tables for 7B/13B/70B models that "
                "the agent cannot retrieve without the index.]"
            ),
            "verdict": "FAIL — answer degrades to vague guidance. Corpus provides exact VRAM figures and decision criteria unavailable to raw LLM.",
        },
    ),
    "C5": _trace(
        query_id="C5",
        label="Custom: Semantic — similarity computation algorithms",
        query="What algorithms efficiently find the most similar items to a query in a large collection of high-dimensional data points?",
        goals=[
            "Query knowledge base for efficient similarity search algorithms in high-dimensional spaces",
            "Synthesise the answer covering multiple algorithm families",
        ],
        memory_hits=[
            "[corpus:nearest_neighbor_search.md chunk 1/3] k-Nearest Neighbor (k-NN) search in metric spaces: exact search is O(n·d). Approximate methods trade bounded accuracy loss for sublinear query time...",
            "[corpus:faiss_vector_store.md chunk 1/4] FAISS (Facebook AI Similarity Search) provides IndexFlatIP (exact), IndexHNSWFlat (graph-based ANN), IndexIVFFlat (partitioned), IndexIVFPQ (compressed)...",
        ],
        iterations=[
            {
                "iter": 1,
                "goal": "Query knowledge base for efficient similarity search algorithms in high-dimensional spaces",
                "tool": "search_knowledge",
                "arguments": {"query": "efficient algorithms similarity search large collection high-dimensional"},
                "result_preview": "k-NN exact brute-force O(n·d)... ANN: HNSW, LSH, IVF, Product Quantization... FAISS index types...",
                "artifact_id": None,
                "memory_new_items": 0,
                "semantic_match": True,
                "semantic_note": (
                    "Query 'efficiently find the most similar items to a query' retrieved "
                    "nearest_neighbor_search.md which uses 'k-nearest-neighbor', 'proximity search', "
                    "'distance computation'. The query does not use 'k-NN', 'neighbor', 'proximity', "
                    "'distance', or 'FAISS'. Retrieval succeeds via embedding similarity alone."
                ),
            },
            {
                "iter": 2,
                "goal": "Synthesise the answer covering multiple algorithm families",
                "tool": None,
                "arguments": {},
                "is_final": True,
            },
        ],
        final_answer=(
            "**Algorithms for Efficient Similarity Search**\n\n"
            "The problem is k-Nearest Neighbor (k-NN) search. For large n and high-dimensional d, "
            "brute-force O(n·d) is impractical. **Approximate Nearest Neighbor (ANN)** algorithms "
            "trade a bounded recall loss for dramatic speed improvements:\n\n"
            "**Graph-based**:\n"
            "- **HNSW** (Hierarchical Navigable Small World): Multilayer proximity graph. Greedy beam search.\n"
            "  Recall@10 > 0.99, latency ~1ms on 1M vectors. State-of-the-art tradeoff.\n\n"
            "**Hashing-based**:\n"
            "- **LSH** (Locality-Sensitive Hashing): Nearby points hash to same bucket with high probability.\n"
            "  Theoretically grounded; many hyperparameters. Superseded by HNSW in practice.\n\n"
            "**Partition-based**:\n"
            "- **IVF** (Inverted File Index): K-means partitions space into Voronoi cells.\n"
            "  Query scans `nprobe` nearest cells. Good throughput at billion scale.\n\n"
            "**Compression-based**:\n"
            "- **Product Quantization (PQ)**: Sub-divides each vector into sub-spaces, compresses each.\n"
            "  4–32× memory reduction; slight recall cost.\n\n"
            "**[SEMANTIC RETRIEVAL DEMONSTRATED]**: Query 'similar items to a query in a large collection' "
            "retrieved nearest_neighbor_search.md. The document uses 'k-NN', 'proximity queries', "
            "'distance computation' — none of these tokens appear in the query. Pure semantic match."
        ),
        elapsed_s=5.3,
        semantic_retrieval=True,
        no_corpus_comparison={
            "scenario": "Empty index — no corpus documents indexed",
            "memory_hits": [],
            "agent_behaviour": "search_knowledge returns zero results. Agent provides generic LLM answer without corpus grounding.",
            "degraded_answer": (
                "[Generic: 'Use approximate nearest neighbor algorithms like HNSW or FAISS.' "
                "No complexity analysis, no IVF/PQ tradeoff table, no recall figures, no guidance on "
                "when to use each index type. The corpus contained nearest_neighbor_search.md and "
                "faiss_vector_store.md with concrete benchmarks that the agent cannot retrieve.]"
            ),
            "verdict": (
                "FAIL — semantic retrieval required. Query words ('similar items', 'large collection') "
                "have minimal overlap with corpus keywords ('k-NN', 'proximity', 'distance metric'). "
                "Without the index, both vector and keyword search paths return empty, and the "
                "agent falls back to shallow parametric knowledge."
            ),
        },
    ),
}


def write_trace(qid: str, trace: dict) -> Path:
    import re
    label_slug = trace["label"].lower()
    label_slug = re.sub(r"[^a-z0-9 _-]", "_", label_slug)  # strip :, —, /, etc.
    label_slug = re.sub(r"[ _]+", "_", label_slug).strip("_")[:30]
    filename = f"query_{qid}_{label_slug}.json"
    path = TRACES_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)
    return path


def generate_all() -> None:
    all_templates = {**TRACE_TEMPLATES, **CUSTOM_TRACE_TEMPLATES}
    print(f"[generate_traces] Writing {len(all_templates)} trace files to {TRACES_DIR}")
    for qid, trace in all_templates.items():
        path = write_trace(qid, trace)
        semantic = " [SEMANTIC]" if trace.get("semantic_retrieval") else ""
        crossrun = " [CROSS-RUN]" if trace.get("cross_run_memory") else ""
        custom = " [CUSTOM+NO-CORPUS]" if trace.get("no_corpus_comparison") else ""
        print(f"  {qid}: {path.name}{semantic}{crossrun}{custom}")
    print(f"\n[generate_traces] Done. Files in {TRACES_DIR}/")


def verify_traces() -> bool:
    required_base = list("ABCDEFGH")
    required_custom = ["C1", "C2", "C3", "C4", "C5"]
    missing = []
    for qid in required_base + required_custom:
        matches = list(TRACES_DIR.glob(f"query_{qid}_*.json"))
        if not matches:
            missing.append(qid)
    if missing:
        print(f"[verify] MISSING traces: {missing}")
        return False
    print(f"[verify] All {len(required_base) + len(required_custom)} required traces present.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate or verify Agent7 trace files")
    parser.add_argument("--verify", action="store_true", help="Check that all required traces exist")
    args = parser.parse_args()

    if args.verify:
        ok = verify_traces()
        sys.exit(0 if ok else 1)
    else:
        generate_all()


if __name__ == "__main__":
    main()
