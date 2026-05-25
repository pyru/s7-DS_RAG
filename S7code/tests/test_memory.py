"""Tests for memory.py — typed memory service with vector + keyword retrieval."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dummy_embed(text: str, task_type: str = "retrieval_document") -> dict:
    """Deterministic 16-dim embedding keyed on text hash, for tests only."""
    h = abs(hash(text)) % 10000
    rng = np.random.RandomState(h)
    vec = rng.randn(16).astype(np.float32)
    vec /= np.linalg.norm(vec)
    return {"embedding": vec.tolist()}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _isolated_memory(tmp_path, monkeypatch):
    """Redirect memory persistence to a tmp dir and stub the gateway embed."""
    import memory as _mem
    monkeypatch.setattr(_mem, "STATE_PATH", tmp_path / "memory.json")
    with (
        patch("memory.ensure_gateway"),
        patch("memory._gateway_embed", side_effect=_dummy_embed),
    ):
        yield


# ---------------------------------------------------------------------------
# add_fact
# ---------------------------------------------------------------------------

class TestAddFact:
    def test_returns_fact_item(self):
        import memory as _mem
        item = _mem.add_fact(
            descriptor="The GIL serializes CPython threads",
            source="test",
            run_id="r1",
        )
        assert item.kind == "fact"
        assert item.source == "test"

    def test_item_has_embedding(self):
        import memory as _mem
        item = _mem.add_fact(descriptor="embedding should be set", source="test", run_id="r1")
        assert item.embedding is not None
        assert len(item.embedding) == 16

    def test_persists_to_json(self):
        import memory as _mem
        _mem.add_fact(descriptor="persisted item", source="test", run_id="r1")
        data = json.loads(_mem.STATE_PATH.read_text())
        assert len(data) == 1
        assert data[0]["descriptor"] == "persisted item"

    def test_custom_keywords_stored(self):
        import memory as _mem
        item = _mem.add_fact(
            descriptor="test item",
            keywords=["alpha", "beta"],
            source="test",
            run_id="r1",
        )
        assert "alpha" in item.keywords
        assert "beta" in item.keywords

    def test_multiple_facts_all_persisted(self):
        import memory as _mem
        for i in range(4):
            _mem.add_fact(descriptor=f"fact {i}", source="test", run_id="r1")
        data = json.loads(_mem.STATE_PATH.read_text())
        assert len(data) == 4

    def test_value_dict_stored(self):
        import memory as _mem
        item = _mem.add_fact(
            descriptor="temperature reading",
            value={"temperature": 42, "unit": "celsius"},
            source="test",
            run_id="r1",
        )
        assert item.value["temperature"] == 42

    def test_no_embedding_when_gateway_fails(self):
        import memory as _mem
        with patch("memory._gateway_embed", side_effect=Exception("gateway down")):
            item = _mem.add_fact(descriptor="no embed item", source="test", run_id="r1")
        assert item.embedding is None

    def test_item_still_persisted_without_embedding(self):
        import memory as _mem
        with patch("memory._gateway_embed", side_effect=Exception("gateway down")):
            _mem.add_fact(descriptor="bare item", source="test", run_id="r1")
        data = json.loads(_mem.STATE_PATH.read_text())
        assert len(data) == 1


# ---------------------------------------------------------------------------
# clear
# ---------------------------------------------------------------------------

class TestClear:
    def test_clear_removes_json_file(self):
        import memory as _mem
        _mem.add_fact(descriptor="to be cleared", source="test", run_id="r1")
        assert _mem.STATE_PATH.exists()
        _mem.clear()
        assert not _mem.STATE_PATH.exists()

    def test_clear_removes_faiss_files(self, tmp_path):
        import memory as _mem
        _mem.add_fact(descriptor="indexed item", source="test", run_id="r1")
        _mem.clear()
        assert not (tmp_path / "index.faiss").exists()
        assert not (tmp_path / "index_ids.json").exists()

    def test_read_after_clear_returns_empty(self):
        import memory as _mem
        _mem.add_fact(descriptor="keyword match item", source="test", run_id="r1")
        _mem.clear()
        with patch("memory._gateway_embed", side_effect=Exception("no embed")):
            results = _mem.read("keyword match item")
        assert results == []

    def test_clear_is_idempotent(self):
        import memory as _mem
        _mem.clear()  # nothing to clear — should not raise
        _mem.clear()


# ---------------------------------------------------------------------------
# record_outcome
# ---------------------------------------------------------------------------

class TestRecordOutcome:
    def _tool_call(self, name: str = "web_search", args: dict | None = None):
        from schemas import ToolCall
        return ToolCall(name=name, arguments=args or {"query": "test"})

    def test_kind_is_tool_outcome(self):
        import memory as _mem
        item = _mem.record_outcome(
            tool_call=self._tool_call(),
            result_text="results here",
            artifact_id=None,
            run_id="r1",
            goal_id=None,
        )
        assert item.kind == "tool_outcome"

    def test_tool_name_in_value(self):
        import memory as _mem
        item = _mem.record_outcome(
            tool_call=self._tool_call("fetch_url", {"url": "https://x.com"}),
            result_text="page text",
            artifact_id=None,
            run_id="r1",
            goal_id=None,
        )
        assert item.value["tool"] == "fetch_url"

    def test_artifact_id_stored_on_item(self):
        import memory as _mem
        item = _mem.record_outcome(
            tool_call=self._tool_call(),
            result_text="",
            artifact_id="art:abc123",
            run_id="r1",
            goal_id=None,
        )
        assert item.artifact_id == "art:abc123"

    def test_artifact_id_in_descriptor(self):
        import memory as _mem
        item = _mem.record_outcome(
            tool_call=self._tool_call(),
            result_text="",
            artifact_id="art:xyz",
            run_id="r1",
            goal_id=None,
        )
        assert "art:xyz" in item.descriptor

    def test_result_preview_truncated_at_400(self):
        import memory as _mem
        long_result = "x" * 1000
        item = _mem.record_outcome(
            tool_call=self._tool_call(),
            result_text=long_result,
            artifact_id=None,
            run_id="r1",
            goal_id=None,
        )
        assert len(item.value["result_preview"]) <= 400

    def test_outcome_persisted_to_json(self):
        import memory as _mem
        _mem.record_outcome(
            tool_call=self._tool_call(),
            result_text="results",
            artifact_id=None,
            run_id="r1",
            goal_id=None,
        )
        data = json.loads(_mem.STATE_PATH.read_text())
        assert len(data) == 1
        assert data[0]["kind"] == "tool_outcome"


# ---------------------------------------------------------------------------
# read — keyword fallback path
# ---------------------------------------------------------------------------

class TestReadKeywordFallback:
    """Force the vector path to fail so keyword fallback is exercised."""

    def test_returns_items_matching_by_keyword(self):
        import memory as _mem
        with patch("memory._gateway_embed", side_effect=Exception("no embed")):
            _mem.add_fact(
                descriptor="FAISS index cosine similarity search",
                keywords=["faiss", "cosine", "similarity"],
                source="test",
                run_id="r1",
            )
            results = _mem.read("FAISS cosine similarity")
        assert len(results) >= 1

    def test_kind_filter_excludes_wrong_kind(self):
        import memory as _mem
        with patch("memory._gateway_embed", side_effect=Exception("no embed")):
            _mem.add_fact(
                descriptor="fact about cats",
                keywords=["cats", "animals"],
                source="test",
                run_id="r1",
            )
            results = _mem.read("cats", kinds=["preference"])
        assert results == []

    def test_top_k_limits_results(self):
        import memory as _mem
        with patch("memory._gateway_embed", side_effect=Exception("no embed")):
            for i in range(10):
                _mem.add_fact(
                    descriptor=f"item {i} keyword test data",
                    keywords=["test"],
                    source="s",
                    run_id="r",
                )
            results = _mem.read("test keyword item data", top_k=3)
        assert len(results) <= 3

    def test_empty_store_returns_empty(self):
        import memory as _mem
        with patch("memory._gateway_embed", side_effect=Exception("no embed")):
            results = _mem.read("anything at all")
        assert results == []

    def test_no_overlap_returns_empty(self):
        import memory as _mem
        with patch("memory._gateway_embed", side_effect=Exception("no embed")):
            _mem.add_fact(
                descriptor="unrelated content about dragons",
                keywords=["dragons"],
                source="test",
                run_id="r1",
            )
            results = _mem.read("quantum computing physics")
        assert results == []


# ---------------------------------------------------------------------------
# read — vector path (with real embeddings via dummy)
# ---------------------------------------------------------------------------

class TestReadVectorPath:
    def test_vector_search_finds_embedded_item(self):
        import memory as _mem
        _mem.add_fact(descriptor="Python GIL global interpreter lock", source="test", run_id="r1")
        results = _mem.read("Python threading concurrency GIL", kinds=["fact"])
        assert len(results) >= 1

    def test_vector_fallback_to_keyword_when_embed_fails(self):
        """When vector query embedding fails, keyword fallback should fire."""
        import memory as _mem
        with patch("memory._gateway_embed", side_effect=Exception("no embed")):
            _mem.add_fact(
                descriptor="FAISS flat index cosine similarity",
                keywords=["faiss", "index", "cosine"],
                source="test",
                run_id="r1",
            )
        # Now query embed also fails → pure keyword path
        with patch("memory._gateway_embed", side_effect=Exception("no embed")):
            results = _mem.read("FAISS cosine index search")
        assert len(results) >= 1
