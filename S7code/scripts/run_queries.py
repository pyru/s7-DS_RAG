#!/usr/bin/env python3
"""
run_queries.py — Run all 8 required demonstration queries through agent7.

Usage (from S7code/):
    uv run scripts/run_queries.py               # Run all 8 queries
    uv run scripts/run_queries.py --query C     # Run only query C
    uv run scripts/run_queries.py --list        # Show query list
    uv run scripts/run_queries.py --save-traces # Save traces to traces/ directory

Prerequisite: Index the corpus first:
    uv run scripts/index_corpus.py

The 8 required queries:
    A. Shannon Wikipedia extraction
    B. Tokyo activity + weather planning
    C. Durable birthday memory (stores then recalls across runs)
    D. Asyncio research synthesis
    E. Single-document indexing (indexes and immediately queries)
    F. Cross-run document recall (verifies persisted memory without re-indexing)
    G. Synonym recall (semantic: "proximity search" → nearest_neighbor_search.md)
    H. Cross-document synthesis (combines info from multiple corpus files)
"""

from __future__ import annotations

import sys
import json
import time
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


QUERIES: dict[str, dict] = {
    "A": {
        "label": "Shannon Wikipedia extraction",
        "query": "Who was Claude Shannon? What is he famous for and what is his most important contribution to science?",
        "description": "Fetches Shannon's Wikipedia page, extracts key facts about information theory.",
    },
    "B": {
        "label": "Tokyo activity + weather planning",
        "query": "I'm planning a trip to Tokyo in April. What activities should I do and what should I expect for weather?",
        "description": "Synthesizes Tokyo weather (April = cherry blossom season) with top activities.",
    },
    "C": {
        "label": "Durable birthday memory",
        "query": "Please remember that my birthday is on 15 July. I want you to save this so it persists across runs.",
        "description": "Stores birthday fact in memory (persists as 'fact' kind in FAISS index).",
    },
    "C2": {
        "label": "Birthday recall (cross-run)",
        "query": "When is my birthday? You should have this stored in memory from a previous interaction.",
        "description": "Recalls birthday from persisted FAISS memory without re-stating it.",
    },
    "D": {
        "label": "Asyncio research synthesis",
        "query": "Explain Python asyncio: how does the event loop work, what is the difference between tasks and coroutines, and what are the best patterns for production use?",
        "description": "Synthesizes across asyncio_fundamentals.md and asyncio_advanced_patterns.md.",
    },
    "E": {
        "label": "Single-document indexing",
        "query": "Index the file corpus/faiss_vector_store.md and then tell me what index types FAISS supports and when to use each one.",
        "description": "Indexes one file and immediately queries the indexed content.",
    },
    "F": {
        "label": "Cross-run document recall",
        "query": "What are the key differences between BM25 and dense vector retrieval? What is RRF?",
        "description": "Uses pre-indexed corpus (run index_corpus.py first); proves cross-run persistence.",
    },
    "G": {
        "label": "Synonym recall (semantic retrieval)",
        "query": "Explain how proximity-based lookup works for finding similar items in large collections. What algorithms are used for approximate retrieval?",
        "description": "Semantically retrieves nearest_neighbor_search.md without matching 'vector similarity'.",
    },
    "H": {
        "label": "Cross-document synthesis",
        "query": "How do FAISS vector indices and sentence transformer embeddings work together in a RAG pipeline? What are the tradeoffs between different index types?",
        "description": "Synthesizes across faiss_vector_store.md, sentence_transformers_guide.md, retrieval_augmented_generation.md.",
    },
}

CUSTOM_QUERIES: dict[str, dict] = {
    "C1": {
        "label": "Custom: Shannon entropy definition",
        "query": "What is Shannon entropy and how is it calculated? Give an example calculation.",
        "description": "Semantic: 'information content' → claude_shannon_information_theory.md + information_theory_basics.md",
    },
    "C2_custom": {
        "label": "Custom: Tokyo food recommendations",
        "query": "What are the best food experiences in Tokyo? I'm especially interested in affordable local options.",
        "description": "Retrieves from tokyo_activities_guide.md (food section) + japan_culture_etiquette.md",
    },
    "C3": {
        "label": "Custom: Semantic — non-blocking execution",
        "query": "How do programs handle many tasks simultaneously without blocking? What programming patterns enable waiting for multiple operations without freezing the program?",
        "description": "Semantic: retrieves event_driven_architecture.md + python_asyncio_fundamentals.md without 'asyncio' keyword",
    },
    "C4": {
        "label": "Custom: LoRA fine-tuning vs full fine-tuning",
        "query": "When should I use parameter-efficient fine-tuning versus full fine-tuning? What are the memory requirements?",
        "description": "Retrieves fine_tuning_llms.md, knowledge_distillation.md",
    },
    "C5": {
        "label": "Custom: Semantic — similarity computation algorithms",
        "query": "What algorithms efficiently find the most similar items to a query in a large collection of high-dimensional data points?",
        "description": "Semantic: retrieves nearest_neighbor_search.md, faiss_vector_store.md without matching exact query words",
    },
}


async def run_single_query(query_text: str, label: str) -> dict:
    """Run a single query through agent7 and return result."""
    from agent7 import run as agent_run

    print(f"\n{'═' * 70}")
    print(f"QUERY: {label}")
    print(f"{'─' * 70}")
    print(f"TEXT: {query_text}")
    print(f"{'═' * 70}")

    start = time.time()
    try:
        answer = await agent_run(query_text)
        elapsed = time.time() - start
        return {
            "label": label,
            "query": query_text,
            "answer": answer,
            "elapsed_s": round(elapsed, 2),
            "status": "ok",
        }
    except Exception as e:
        elapsed = time.time() - start
        print(f"[run_queries] ERROR: {e}")
        return {
            "label": label,
            "query": query_text,
            "answer": f"ERROR: {e}",
            "elapsed_s": round(elapsed, 2),
            "status": "error",
        }


async def run_queries(
    query_ids: list[str],
    save_traces: bool = False,
    include_custom: bool = False,
) -> list[dict]:
    """Run selected queries and optionally save results."""
    results = []
    all_queries = {**QUERIES}
    if include_custom:
        all_queries.update(CUSTOM_QUERIES)

    for qid in query_ids:
        if qid not in all_queries:
            print(f"[warning] Unknown query ID: {qid}")
            continue
        q = all_queries[qid]
        result = await run_single_query(q["query"], q["label"])
        result["query_id"] = qid
        result["description"] = q.get("description", "")
        results.append(result)

        if save_traces:
            save_trace(result)

    return results


def save_trace(result: dict) -> None:
    """Save a query result as a JSON trace file."""
    trace_dir = ROOT / "traces"
    trace_dir.mkdir(exist_ok=True)

    qid = result.get("query_id", "unknown")
    filename = f"query_{qid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path = trace_dir / filename

    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[trace] Saved: {path}")


def list_queries() -> None:
    """Print available query list."""
    print("\nRequired Queries (A–H):")
    for qid, q in QUERIES.items():
        print(f"  {qid}: {q['label']}")
        print(f"      {q['description']}")
    print("\nCustom Queries (C1–C5):")
    for qid, q in CUSTOM_QUERIES.items():
        print(f"  {qid}: {q['label']}")
        print(f"      {q['description']}")


async def main_async(args) -> None:
    if args.list:
        list_queries()
        return

    if args.query:
        query_ids = [q.strip().upper() for q in args.query.split(",")]
    else:
        query_ids = list(QUERIES.keys())
        if args.custom:
            query_ids += list(CUSTOM_QUERIES.keys())

    results = await run_queries(
        query_ids=query_ids,
        save_traces=args.save_traces,
        include_custom=args.custom,
    )

    print(f"\n{'═' * 70}")
    print("SUMMARY")
    print(f"{'─' * 70}")
    for r in results:
        status = "✓" if r["status"] == "ok" else "✗"
        print(f"  {status} [{r['query_id']}] {r['label']}: {r['elapsed_s']}s")
    print(f"{'═' * 70}")

    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Agent7 demonstration queries")
    parser.add_argument(
        "--query",
        help="Comma-separated query IDs (e.g., A,B,G). Default: all required queries.",
    )
    parser.add_argument("--list", action="store_true", help="List available queries and exit")
    parser.add_argument("--save-traces", action="store_true", help="Save results to traces/ directory")
    parser.add_argument("--custom", action="store_true", help="Also run custom queries (C1-C5)")
    parser.add_argument("--output", help="Save all results to a JSON file")
    args = parser.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
