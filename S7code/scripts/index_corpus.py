#!/usr/bin/env python3
"""
index_corpus.py — Index all corpus documents into the FAISS memory store.

Supports plain text (.md .txt), PDF (.pdf), and Word (.docx) files.

Usage (from S7code/):
    uv run scripts/index_corpus.py                        # index sandbox/RAG/
    uv run scripts/index_corpus.py --corpus-dir sandbox/corpus
    uv run scripts/index_corpus.py --clear                # wipe state first

The script:
  1. Starts the LLM gateway (via gateway.ensure_gateway)
  2. Walks the corpus directory for .md / .txt / .pdf / .docx files
  3. Extracts plain text (PDF and DOCX parsed automatically)
  4. Chunks each file at 400 words / 80-word overlap (same as the MCP tool)
  5. Writes each chunk to Memory as an embedded `fact` record

After this script completes, the agent answers corpus questions directly
from the FAISS index without re-fetching any source file.
"""

from __future__ import annotations

import os
import sys
import time
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import httpx
import memory as _memory
from gateway import ensure_gateway

SUPPORTED_SUFFIXES = {".md", ".txt", ".pdf", ".docx"}
BATCH_SIZE = 100          # Gemini batchEmbedContents limit per API call
EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 768


def _batch_embed(texts: list[str], api_key: str) -> list[list[float] | None]:
    """Embed up to BATCH_SIZE texts in one Gemini batchEmbedContents call.

    Returns a list of float vectors (same length as `texts`).  Any failed
    slot is returned as None so the caller can fall back to gateway-per-item.
    """
    if not texts:
        return []
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{EMBED_MODEL}:batchEmbedContents?key={api_key}"
    )
    requests_payload = [
        {
            "model": f"models/{EMBED_MODEL}",
            "content": {"parts": [{"text": t}]},
            "taskType": "RETRIEVAL_DOCUMENT",
            "outputDimensionality": EMBED_DIM,
        }
        for t in texts
    ]
    try:
        resp = httpx.post(
            url,
            json={"requests": requests_payload},
            timeout=120,
        )
        resp.raise_for_status()
        embeddings = resp.json().get("embeddings", [])
        return [e.get("values") for e in embeddings]
    except Exception as exc:
        print(f"    [batch_embed] failed ({exc!r}); will fall back to gateway per-item")
        return [None] * len(texts)


def _decode_cid(text: str) -> str:
    """Decode /cXX decimal CID sequences that pypdf emits for non-standard fonts."""
    import re
    def _sub(m: "re.Match[str]") -> str:
        code = int(m.group(1))
        try:
            return bytes([code]).decode("windows-1252", errors="replace")
        except Exception:
            return chr(code)
    return re.sub(r"/c(\d+)", _sub, text)


def extract_text(path: Path) -> str:
    """Return the plain-text content of a file regardless of format."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        pages = [_decode_cid(page.extract_text() or "") for page in reader.pages]
        return "\n\n".join(pages).strip()
    if suffix == ".docx":
        from docx import Document
        doc = Document(str(path))
        return "\n\n".join(para.text for para in doc.paragraphs if para.text.strip())
    return path.read_text(encoding="utf-8")


def chunk_text(text: str, size: int = 400, overlap: int = 80) -> list[str]:
    """Sliding-window word-count chunking (mirrors mcp_server._chunk_text)."""
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    stride = max(1, size - overlap)
    i = 0
    while i < len(words):
        chunks.append(" ".join(words[i:i + size]))
        if i + size >= len(words):
            break
        i += stride
    return chunks


def index_file(path: Path, run_id: str, gemini_key: str | None = None) -> int:
    """Extract, chunk, and index one file. Returns number of chunks written.

    When `gemini_key` is provided the descriptors are batch-embedded via the
    Gemini batchEmbedContents endpoint (100 texts per HTTP call) so the full
    corpus can be indexed in minutes rather than hours.
    """
    try:
        text = extract_text(path)
    except Exception as exc:
        print(f"    [SKIP] {path.name}: extraction failed — {exc}")
        return 0

    if not text.strip():
        print(f"    [SKIP] {path.name}: no text content")
        return 0

    chunks = chunk_text(text, size=400, overlap=80)
    source = f"corpus:{path.name}"
    descriptors = [
        f"[{source} chunk {i+1}/{len(chunks)}] {chunk[:120].replace(chr(10), ' ')}"
        for i, chunk in enumerate(chunks)
    ]

    # Batch-embed all descriptors in groups of BATCH_SIZE
    embeddings: list[list[float] | None] = []
    if gemini_key:
        for start in range(0, len(descriptors), BATCH_SIZE):
            batch = descriptors[start:start + BATCH_SIZE]
            vecs = _batch_embed(batch, gemini_key)
            embeddings.extend(vecs)
            print(f"        embedded batch {start//BATCH_SIZE + 1}/"
                  f"{(len(descriptors) - 1)//BATCH_SIZE + 1}", flush=True)
    else:
        embeddings = [None] * len(chunks)

    # Single bulk write — avoids reading memory.json once per chunk which
    # becomes unbearably slow once the store reaches hundreds of MB.
    items_data = [
        {
            "descriptor": descriptor,
            "value": {
                "chunk": chunk,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "source": source,
                "file": path.name,
            },
            "source": source,
            "run_id": run_id,
            "embedding": emb,
        }
        for i, (chunk, descriptor, emb) in enumerate(zip(chunks, descriptors, embeddings))
    ]
    print(f"        writing {len(items_data)} chunks to memory...", flush=True)
    _memory.add_facts_bulk(items_data)

    return len(chunks)


def collect_files(corpus_dir: Path) -> list[Path]:
    """Collect all supported files from the corpus directory (non-recursive)."""
    files = [
        p for p in sorted(corpus_dir.iterdir())
        if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    ]
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="Index corpus documents into FAISS memory")
    parser.add_argument(
        "--corpus-dir",
        default="sandbox/RAG",
        help="Directory to scan for .md/.txt/.pdf/.docx files (default: sandbox/RAG)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing memory before indexing (WARNING: deletes all prior state)",
    )
    args = parser.parse_args()

    corpus_dir = (ROOT / args.corpus_dir).resolve()
    if not corpus_dir.exists():
        print(f"[error] Corpus directory not found: {corpus_dir}")
        sys.exit(1)

    files = collect_files(corpus_dir)
    if not files:
        print(f"[error] No supported files (.md .txt .pdf .docx) in {corpus_dir}")
        sys.exit(1)

    # Read GEMINI_API_KEY from .env for batch embedding
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    gemini_key: str | None = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        print(f"[index_corpus] Batch embedding via Gemini ({EMBED_MODEL}, {BATCH_SIZE}/call)")
    else:
        print("[index_corpus] No GEMINI_API_KEY — will embed via gateway (slow)")

    print("[index_corpus] Starting gateway...")
    ensure_gateway()
    print("[index_corpus] Gateway up.")

    if args.clear:
        print("[index_corpus] Clearing existing memory...")
        _memory.clear()
        print("[index_corpus] Memory cleared.")

    run_id = f"index-corpus-{int(time.time())}"
    print(f"\n[index_corpus] Indexing {len(files)} file(s) from {corpus_dir}")
    print(f"[index_corpus] Run ID: {run_id}\n")

    total_chunks = 0
    start = time.time()

    for idx, f in enumerate(files, 1):
        size_mb = f.stat().st_size / 1_048_576
        print(f"  [{idx:2d}/{len(files)}] {f.name}  ({size_mb:.1f} MB)", flush=True)
        t0 = time.time()
        n = index_file(f, run_id, gemini_key=gemini_key)
        elapsed = time.time() - t0
        total_chunks += n
        print(f"          → {n} chunks  ({elapsed:.1f}s)", flush=True)

    elapsed_total = time.time() - start
    print(f"\n[index_corpus] Done.")
    print(f"  Files indexed : {len(files)}")
    print(f"  Total chunks  : {total_chunks}")
    print(f"  Total time    : {elapsed_total:.1f}s")
    print(f"  Memory path   : {ROOT / 'state' / 'memory.json'}")
    print(f"  FAISS index   : {ROOT / 'state' / 'index.faiss'}")
    print(f"\n  Agent can now answer corpus questions via search_knowledge.")


if __name__ == "__main__":
    main()
