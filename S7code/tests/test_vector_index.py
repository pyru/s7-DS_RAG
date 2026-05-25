"""Tests for vector_index.py — the FAISS wrapper."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pytest

# Try to import faiss; skip tests if not installed
try:
    import faiss  # noqa: F401
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

pytestmark = pytest.mark.skipif(not FAISS_AVAILABLE, reason="faiss-cpu not installed")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_index(store_dir: Path):
    from vector_index import VectorIndex
    return VectorIndex(store_dir)


def _random_vec(dim: int = 16) -> list[float]:
    v = np.random.randn(dim).astype(np.float32)
    v /= np.linalg.norm(v)  # L2-normalize
    return v.tolist()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestVectorIndexBasics:
    def test_empty_index_size_is_zero(self, tmp_path):
        idx = _make_index(tmp_path)
        assert idx.size == 0

    def test_dim_is_none_before_first_add(self, tmp_path):
        idx = _make_index(tmp_path)
        assert idx.dim is None

    def test_add_sets_dim(self, tmp_path):
        idx = _make_index(tmp_path)
        idx.add("item1", _random_vec(16))
        assert idx.dim == 16

    def test_add_increases_size(self, tmp_path):
        idx = _make_index(tmp_path)
        idx.add("a", _random_vec(16))
        idx.add("b", _random_vec(16))
        assert idx.size == 2

    def test_search_returns_correct_count(self, tmp_path):
        idx = _make_index(tmp_path)
        for i in range(10):
            idx.add(f"item{i}", _random_vec(16))
        results = idx.search(_random_vec(16), k=5)
        assert len(results) <= 5

    def test_search_returns_tuples_with_id_and_score(self, tmp_path):
        idx = _make_index(tmp_path)
        idx.add("alpha", _random_vec(16))
        results = idx.search(_random_vec(16), k=1)
        assert len(results) == 1
        item_id, score = results[0]
        assert isinstance(item_id, str)
        assert isinstance(score, float)

    def test_search_empty_index_returns_empty(self, tmp_path):
        idx = _make_index(tmp_path)
        results = idx.search(_random_vec(16), k=5)
        assert results == []


class TestVectorIndexSemantic:
    def test_identical_vector_gets_highest_score(self, tmp_path):
        """The same vector should always be the nearest neighbor of itself."""
        idx = _make_index(tmp_path)
        v = _random_vec(64)
        idx.add("target", v)
        # Add noise vectors
        for i in range(20):
            idx.add(f"noise{i}", _random_vec(64))

        results = idx.search(v, k=5)
        top_id, top_score = results[0]
        assert top_id == "target"
        assert top_score > 0.99  # Cosine similarity ≈ 1.0 for same vector

    def test_semantically_close_vector_ranks_above_random(self, tmp_path):
        """A slightly perturbed copy of a vector should rank above unrelated vectors."""
        idx = _make_index(tmp_path)
        v = _random_vec(64)

        # Add unrelated vectors
        for i in range(50):
            idx.add(f"random{i}", _random_vec(64))

        # Add slightly perturbed version
        v_noise = (np.array(v) + np.random.randn(64) * 0.01).tolist()
        v_noise_norm = (np.array(v_noise) / np.linalg.norm(v_noise)).tolist()
        idx.add("close", v_noise_norm)

        results = idx.search(v, k=3)
        ids = [r[0] for r in results]
        assert "close" in ids


class TestVectorIndexPersistence:
    def test_persist_and_reload(self, tmp_path):
        from vector_index import VectorIndex

        # Build and persist index
        idx1 = VectorIndex(tmp_path)
        idx1.add("doc1", _random_vec(32))
        idx1.add("doc2", _random_vec(32))
        idx1.persist()

        # Reload in fresh object
        idx2 = VectorIndex(tmp_path)
        assert idx2.size == 2
        assert idx2.dim == 32

    def test_persisted_results_match_original(self, tmp_path):
        from vector_index import VectorIndex

        v = _random_vec(32)
        idx1 = VectorIndex(tmp_path)
        idx1.add("match_me", v)
        for i in range(5):
            idx1.add(f"other{i}", _random_vec(32))
        idx1.persist()

        idx2 = VectorIndex(tmp_path)
        results = idx2.search(v, k=1)
        assert results[0][0] == "match_me"

    def test_clear_removes_all_items(self, tmp_path):
        from vector_index import VectorIndex

        idx = VectorIndex(tmp_path)
        idx.add("a", _random_vec(16))
        idx.persist()
        idx.clear()

        idx2 = VectorIndex(tmp_path)
        assert idx2.size == 0
        assert not (tmp_path / "index.faiss").exists()


class TestVectorIndexEdgeCases:
    def test_dimension_mismatch_raises(self, tmp_path):
        idx = _make_index(tmp_path)
        idx.add("a", _random_vec(16))
        with pytest.raises(ValueError, match="dim"):
            idx.add("b", _random_vec(32))

    def test_search_k_larger_than_size(self, tmp_path):
        idx = _make_index(tmp_path)
        idx.add("only", _random_vec(16))
        results = idx.search(_random_vec(16), k=100)
        assert len(results) == 1  # Cannot return more than exist
