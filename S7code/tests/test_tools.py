"""Tests for mcp_server.py — chunking, sandbox safety, and file tools."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    """Point mcp_server.SANDBOX at an isolated temp directory."""
    import mcp_server
    sb = tmp_path / "sandbox"
    sb.mkdir()
    monkeypatch.setattr(mcp_server, "SANDBOX", sb)
    return sb


# ---------------------------------------------------------------------------
# _chunk_text — pure sliding-window chunker
# ---------------------------------------------------------------------------

class TestChunkText:
    def _chunk(self, text: str, size: int = 400, overlap: int = 80) -> list[str]:
        from mcp_server import _chunk_text
        return _chunk_text(text, size=size, overlap=overlap)

    def test_empty_string_returns_empty(self):
        assert self._chunk("") == []

    def test_whitespace_only_returns_empty(self):
        assert self._chunk("   \n\t  ") == []

    def test_single_word_is_one_chunk(self):
        assert self._chunk("hello") == ["hello"]

    def test_short_text_fits_one_chunk(self):
        text = " ".join(f"w{i}" for i in range(10))
        assert len(self._chunk(text, size=400, overlap=80)) == 1

    def test_exact_size_boundary_is_one_chunk(self):
        text = " ".join(f"w{i}" for i in range(400))
        assert len(self._chunk(text, size=400, overlap=80)) == 1

    def test_one_word_over_limit_makes_two_chunks(self):
        text = " ".join(f"w{i}" for i in range(401))
        chunks = self._chunk(text, size=400, overlap=80)
        assert len(chunks) == 2

    def test_chunk_count_for_1000_words(self):
        # stride = 400-80 = 320; 1000 words → 3 chunks
        text = " ".join(f"w{i}" for i in range(1000))
        chunks = self._chunk(text, size=400, overlap=80)
        assert len(chunks) == 3

    def test_overlap_shared_words_between_consecutive_chunks(self):
        words = [f"tok{i}" for i in range(500)]
        text = " ".join(words)
        chunks = self._chunk(text, size=400, overlap=80)
        # stride=320; chunk1 covers words[0:400], chunk2 covers words[320:720]
        # words[320:400] appear in both
        c1_words = set(chunks[0].split())
        c2_first_stride = chunks[1].split()[:80]  # first 80 words of chunk2 are the overlap
        assert all(w in c1_words for w in c2_first_stride[:10])

    def test_each_chunk_word_count_at_most_size(self):
        text = " ".join(f"w{i}" for i in range(900))
        for chunk in self._chunk(text, size=400, overlap=80):
            assert len(chunk.split()) <= 400

    def test_custom_small_size_and_overlap(self):
        text = " ".join(f"x{i}" for i in range(20))
        chunks = self._chunk(text, size=5, overlap=2)
        # stride=3; 20 words → chunks start at 0,3,6,...,18 → 7 chunks
        assert len(chunks) >= 4

    def test_all_words_present_across_chunks(self):
        """No word should be silently dropped."""
        words = [f"unique_{i}" for i in range(500)]
        text = " ".join(words)
        chunks = self._chunk(text, size=400, overlap=80)
        combined = set()
        for c in chunks:
            combined.update(c.split())
        for w in words:
            assert w in combined


# ---------------------------------------------------------------------------
# Sandbox path safety
# ---------------------------------------------------------------------------

class TestSandboxSafety:
    def test_simple_filename_resolves_in_sandbox(self, sandbox):
        from mcp_server import _safe
        result = _safe("notes.txt")
        assert result == (sandbox / "notes.txt").resolve()

    def test_dot_slash_stays_in_sandbox(self, sandbox):
        from mcp_server import _safe
        result = _safe("./notes.txt")
        assert result == (sandbox / "notes.txt").resolve()

    def test_subdirectory_path_allowed(self, sandbox):
        from mcp_server import _safe
        (sandbox / "docs").mkdir()
        result = _safe("docs/readme.txt")
        assert result.parent == (sandbox / "docs").resolve()

    def test_parent_traversal_raises(self, sandbox):
        from mcp_server import _safe
        with pytest.raises(ValueError, match="escapes"):
            _safe("../outside.txt")

    def test_deep_traversal_raises(self, sandbox):
        from mcp_server import _safe
        with pytest.raises(ValueError, match="escapes"):
            _safe("a/b/../../../etc/passwd")

    def test_absolute_path_outside_sandbox_raises(self, sandbox):
        from mcp_server import _safe
        with pytest.raises(ValueError, match="escapes"):
            _safe("/etc/passwd")


# ---------------------------------------------------------------------------
# create_file
# ---------------------------------------------------------------------------

class TestCreateFile:
    def test_creates_file_with_content(self, sandbox):
        from mcp_server import create_file
        result = create_file("hello.txt", "world")
        assert (sandbox / "hello.txt").read_text(encoding="utf-8") == "world"
        assert result["ok"] is True

    def test_reports_correct_path(self, sandbox):
        from mcp_server import create_file
        result = create_file("doc.txt", "content")
        assert result["path"] == "doc.txt"

    def test_reports_size_bytes(self, sandbox):
        from mcp_server import create_file
        result = create_file("sized.txt", "abc")
        assert result["size_bytes"] == 3

    def test_raises_if_file_already_exists(self, sandbox):
        from mcp_server import create_file
        (sandbox / "existing.txt").write_text("old")
        with pytest.raises(ValueError, match="already exists"):
            create_file("existing.txt", "new content")

    def test_raises_if_parent_missing(self, sandbox):
        from mcp_server import create_file
        with pytest.raises(ValueError):
            create_file("no_dir/file.txt", "content")


# ---------------------------------------------------------------------------
# read_file
# ---------------------------------------------------------------------------

class TestReadFile:
    def test_reads_utf8_content(self, sandbox):
        from mcp_server import read_file
        (sandbox / "test.txt").write_text("hello world", encoding="utf-8")
        result = read_file("test.txt")
        assert result["content"] == "hello world"
        assert result["path"] == "test.txt"

    def test_reports_size_bytes(self, sandbox):
        from mcp_server import read_file
        (sandbox / "sized.txt").write_text("a" * 100, encoding="utf-8")
        result = read_file("sized.txt")
        assert result["size_bytes"] == 100

    def test_reports_encoding(self, sandbox):
        from mcp_server import read_file
        (sandbox / "enc.txt").write_text("x")
        assert read_file("enc.txt")["encoding"] == "utf-8"

    def test_raises_on_missing_file(self, sandbox):
        from mcp_server import read_file
        with pytest.raises(Exception):
            read_file("ghost.txt")


# ---------------------------------------------------------------------------
# update_file
# ---------------------------------------------------------------------------

class TestUpdateFile:
    def test_overwrites_content(self, sandbox):
        from mcp_server import update_file
        (sandbox / "doc.txt").write_text("original")
        update_file("doc.txt", "updated")
        assert (sandbox / "doc.txt").read_text() == "updated"

    def test_ok_flag_true(self, sandbox):
        from mcp_server import update_file
        (sandbox / "doc.txt").write_text("x")
        result = update_file("doc.txt", "y")
        assert result["ok"] is True

    def test_raises_if_not_exists(self, sandbox):
        from mcp_server import update_file
        with pytest.raises(ValueError, match="does not exist"):
            update_file("ghost.txt", "content")


# ---------------------------------------------------------------------------
# edit_file
# ---------------------------------------------------------------------------

class TestEditFile:
    def test_simple_replacement(self, sandbox):
        from mcp_server import edit_file
        (sandbox / "code.py").write_text("foo = 1")
        edit_file("code.py", "foo", "bar")
        assert (sandbox / "code.py").read_text() == "bar = 1"

    def test_returns_ok_and_replacement_count(self, sandbox):
        from mcp_server import edit_file
        (sandbox / "f.txt").write_text("aaa bbb aaa")
        result = edit_file("f.txt", "aaa", "xxx", replace_all=True)
        assert result["ok"] is True
        assert result["replacements"] == 2

    def test_replace_all_changes_all_occurrences(self, sandbox):
        from mcp_server import edit_file
        (sandbox / "f.txt").write_text("x = x + x")
        edit_file("f.txt", "x", "y", replace_all=True)
        assert (sandbox / "f.txt").read_text() == "y = y + y"

    def test_raises_if_token_not_found(self, sandbox):
        from mcp_server import edit_file
        (sandbox / "f.txt").write_text("alpha beta")
        with pytest.raises(ValueError, match="not found"):
            edit_file("f.txt", "gamma", "delta")

    def test_raises_on_ambiguous_without_replace_all(self, sandbox):
        from mcp_server import edit_file
        (sandbox / "f.txt").write_text("x x x")
        with pytest.raises(ValueError, match="replace_all"):
            edit_file("f.txt", "x", "y")

    def test_single_occurrence_without_flag_works(self, sandbox):
        from mcp_server import edit_file
        (sandbox / "f.txt").write_text("hello world")
        edit_file("f.txt", "hello", "hi")
        assert (sandbox / "f.txt").read_text() == "hi world"


# ---------------------------------------------------------------------------
# list_dir
# ---------------------------------------------------------------------------

class TestListDir:
    def test_lists_files_and_dirs(self, sandbox):
        from mcp_server import list_dir
        (sandbox / "file.txt").write_text("hi")
        (sandbox / "subdir").mkdir()
        result = list_dir(".")
        assert "file.txt" in result["names"]
        assert "subdir" in result["names"]

    def test_count_matches_actual(self, sandbox):
        from mcp_server import list_dir
        for i in range(3):
            (sandbox / f"f{i}.txt").write_text("x")
        result = list_dir(".")
        assert result["count"] == 3

    def test_entries_have_type_and_size(self, sandbox):
        from mcp_server import list_dir
        (sandbox / "a.txt").write_text("abc")
        (sandbox / "d").mkdir()
        result = list_dir(".")
        by_name = {e["name"]: e for e in result["entries"]}
        assert by_name["a.txt"]["type"] == "file"
        assert by_name["d"]["type"] == "dir"

    def test_empty_dir_returns_zero_count(self, sandbox):
        from mcp_server import list_dir
        result = list_dir(".")
        assert result["count"] == 0


# ---------------------------------------------------------------------------
# index_document
# ---------------------------------------------------------------------------

class TestIndexDocument:
    def test_indexes_file_returns_chunk_count(self, sandbox, monkeypatch):
        import mcp_server
        from mcp_server import index_document
        content = " ".join(f"word{i}" for i in range(100))
        (sandbox / "doc.md").write_text(content)
        mock_add = MagicMock()
        monkeypatch.setattr(mcp_server._memory, "add_fact", mock_add)
        result = index_document("doc.md", chunk_size=400, overlap=80)
        assert result["chunks_indexed"] == 1
        assert mock_add.call_count == 1

    def test_empty_file_returns_warning(self, sandbox, monkeypatch):
        import mcp_server
        from mcp_server import index_document
        (sandbox / "empty.md").write_text("")
        monkeypatch.setattr(mcp_server._memory, "add_fact", MagicMock())
        result = index_document("empty.md")
        assert result["chunks_indexed"] == 0
        assert "warning" in result

    def test_large_file_produces_multiple_chunks(self, sandbox, monkeypatch):
        import mcp_server
        from mcp_server import index_document
        content = " ".join(f"word{i}" for i in range(1000))
        (sandbox / "large.md").write_text(content)
        mock_add = MagicMock()
        monkeypatch.setattr(mcp_server._memory, "add_fact", mock_add)
        result = index_document("large.md", chunk_size=400, overlap=80)
        assert result["chunks_indexed"] == 3
        assert mock_add.call_count == 3

    def test_returns_source_and_path(self, sandbox, monkeypatch):
        import mcp_server
        from mcp_server import index_document
        (sandbox / "spec.md").write_text("content here to index")
        monkeypatch.setattr(mcp_server._memory, "add_fact", MagicMock())
        result = index_document("spec.md")
        assert result["path"] == "spec.md"
        assert "sandbox:spec.md" in result["source"]

    def test_chunk_descriptors_contain_source(self, sandbox, monkeypatch):
        import mcp_server
        from mcp_server import index_document
        (sandbox / "notes.md").write_text(" ".join(f"tok{i}" for i in range(50)))
        captured: list[dict] = []
        def fake_add_fact(descriptor, **kwargs):
            captured.append({"descriptor": descriptor})
        monkeypatch.setattr(mcp_server._memory, "add_fact", fake_add_fact)
        index_document("notes.md")
        assert any("sandbox:notes.md" in c["descriptor"] for c in captured)
