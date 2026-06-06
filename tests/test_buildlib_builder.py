"""Unit tests for buildlib.builder module (build core logic)."""

from __future__ import annotations

import json
import threading

import pytest

from buildlib.builder import (
    _BuildCore,
    extract_log_path,
    parse_log_for_package_times,
)
from buildlib.config import ProjectConfig
from buildlib.runner import CommandRunner
from buildlib.ui import TerminalOutput


@pytest.fixture
def build_core(tmp_path):
    ui = TerminalOutput(use_color=False)
    runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
    config = ProjectConfig(build_dir=tmp_path / "build")
    return _BuildCore(config=config, runner=runner, ui=ui, jobs=1)


class TestParseLogForPackageTimes:
    """Test LaTeX log parsing for package timing data."""

    def test_parse_empty_log(self):
        result = parse_log_for_package_times("")
        assert result["packages"] == {}
        assert result["package_count"] == 0
        assert result["total_time_s"] is None

    def test_parse_package_lines(self):
        log = (
            "Package: fontspec 2024/01/01 v2.8a\n"
            "Package: hyperref 2024/02/15 v7.01\n"
            "Package: babel 2024/03/01 v3.95\n"
        )
        result = parse_log_for_package_times(log)
        assert result["package_count"] == 3
        assert "fontspec" in result["packages"]
        assert "hyperref" in result["packages"]
        assert result["packages"]["fontspec"]["date"] == "2024/01/01"

    def test_parse_total_time(self):
        log = "Output written on main.pdf (25 pages, 524288 bytes).\n42.5 seconds\n"
        result = parse_log_for_package_times(log)
        assert result["total_time_s"] == 42.5

    def test_parse_ignores_short_times(self):
        """Times under 0.5s should be ignored (likely not real build times)."""
        log = "0.1 seconds\n"
        result = parse_log_for_package_times(log)
        assert result["total_time_s"] is None

    def test_parse_luc_cache_lines(self):
        log = "(load luc: /path/to/font.luc)\n"
        result = parse_log_for_package_times(log)
        assert "font" in result["packages"]

    def test_parse_mixed_content(self):
        log = (
            "This is LuaTeX.\n"
            "Package: fontspec 2024/01/01 v2.8a\n"
            "(load luc: /fonts/mono.luc)\n"
            "No errors.\n"
            "25.3 seconds\n"
        )
        result = parse_log_for_package_times(log)
        assert result["package_count"] >= 2
        assert result["total_time_s"] == 25.3


class TestExtractLogPath:
    """Test log file discovery."""

    def test_log_exists(self, tmp_path):
        log = tmp_path / "main.log"
        log.write_text("test log content")
        result = extract_log_path(tmp_path)
        assert result == log

    def test_log_not_exists(self, tmp_path):
        result = extract_log_path(tmp_path)
        assert result is None


class TestBuildCore:
    """Test _BuildCore mixin class."""

    def test_version_property(self, build_core):
        version = build_core.version
        assert isinstance(version, str)
        # Should match semver pattern or fallback to 0.0.0
        parts = version.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_hash_for_paths(self, tmp_path):
        f1 = tmp_path / "a.tex"
        f1.write_text("content")
        f2 = tmp_path / "b.tex"
        f2.write_text("content")
        h1 = _BuildCore._hash_for_paths([f1, f2])
        assert isinstance(h1, str)
        assert len(h1) == 64  # SHA-256 hex digest

    def test_hash_for_paths_deterministic(self, tmp_path):
        f1 = tmp_path / "a.tex"
        f1.write_text("deterministic content")
        h1 = _BuildCore._hash_for_paths([f1])
        h2 = _BuildCore._hash_for_paths([f1])
        assert h1 == h2

    def test_hash_for_paths_different_content(self, tmp_path):
        f1 = tmp_path / "a.tex"
        f1.write_text("content A")
        f2 = tmp_path / "b.tex"
        f2.write_text("content B")
        h1 = _BuildCore._hash_for_paths([f1])
        h2 = _BuildCore._hash_for_paths([f2])
        assert h1 != h2

    def test_hash_for_paths_empty(self):
        h = _BuildCore._hash_for_paths([])
        assert isinstance(h, str)
        assert len(h) == 64

    def test_hash_for_paths_nonexistent(self, tmp_path):
        h = _BuildCore._hash_for_paths([tmp_path / "nonexistent.tex"])
        assert isinstance(h, str)

    def test_cache_load_save_cycle(self, build_core, tmp_path):
        build_core.config.build_dir = tmp_path / "build"
        (tmp_path / "build").mkdir(parents=True)
        cache = {"examples/test": {"source_hash": "abc123", "build_time": "2024-01-01"}}
        build_core._save_build_cache(cache)
        loaded = build_core._load_build_cache()
        assert loaded["examples/test"]["source_hash"] == "abc123"

    def test_cache_load_empty_when_no_file(self, build_core, tmp_path):
        build_core.config.build_dir = tmp_path / "nonexistent"
        loaded = build_core._load_build_cache()
        assert loaded == {}

    def test_cache_load_handles_corrupt_json(self, build_core, tmp_path):
        build_core.config.build_dir = tmp_path / "build"
        (tmp_path / "build").mkdir(parents=True)
        cache_file = tmp_path / "build" / "build_cache.json"
        cache_file.write_text("NOT VALID JSON{{{")
        loaded = build_core._load_build_cache()
        assert loaded == {}

    def test_discover_examples(self, build_core):
        """discover_examples() should find examples/ directories with main.tex."""
        examples = build_core.discover_examples()
        assert isinstance(examples, list)
        # The repo should have at least a few examples
        assert len(examples) > 0
        for ex in examples:
            assert (ex / "main.tex").exists()

    def test_discover_examples_returns_sorted(self, build_core):
        examples = build_core.discover_examples()
        names = [e.name for e in examples]
        assert names == sorted(names)

    def test_source_files_property(self, build_core):
        source_files = build_core.source_files
        assert isinstance(source_files, list)
        assert len(source_files) > 0
        # All files should be .sty or .cls
        for f in source_files:
            assert f.suffix in (".sty", ".cls")

    def test_source_files_caching(self, build_core):
        """Repeated access should use the cache."""
        files1 = build_core.source_files
        files2 = build_core.source_files
        assert files1 is files2

    def test_collect_source_files(self, build_core):
        """_collect_source_files should gather all relevant files for an example."""
        files = build_core._collect_source_files("minimal-starter")
        assert len(files) > 0
        # Should include main.tex
        tex_files = [f for f in files if f.name == "main.tex"]
        assert len(tex_files) == 1
        # Should include .sty files
        sty_files = [f for f in files if f.suffix == ".sty"]
        assert len(sty_files) > 0

    def test_thread_locks_initialized(self, build_core):
        assert isinstance(build_core._timings_lock, type(threading.Lock()))
        assert isinstance(build_core._cache_lock, type(threading.Lock()))

    def test_list_examples_json_output(self, build_core, capsys):
        build_core.list_examples(output_format="json")
        captured = capsys.readouterr()
        # Should be valid JSON
        data = json.loads(captured.out)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "name" in data[0]
        assert "path" in data[0]

    def test_list_examples_text_output(self, build_core, capsys):
        build_core.list_examples(output_format="text")
        captured = capsys.readouterr()
        assert "Available Examples" in captured.out

    def test_cmd_cache_clear(self, build_core, tmp_path):
        build_core.config.build_dir = tmp_path / "build"
        (tmp_path / "build").mkdir(parents=True)
        cache_file = tmp_path / "build" / "build_cache.json"
        cache_file.write_text("{}")
        build_core.cmd_cache_clear()
        assert not cache_file.exists()

    def test_cmd_cache_clear_no_file(self, build_core, tmp_path):
        build_core.config.build_dir = tmp_path / "nonexistent"
        # Should not raise
        build_core.cmd_cache_clear()
