"""Concurrency and thread safety tests for buildlib.builder."""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

import pytest

from buildlib.builder import _BuildCore
from buildlib.config import ProjectConfig
from buildlib.runner import CommandRunner
from buildlib.ui import TerminalOutput


@pytest.fixture
def build_core(tmp_path):
    ui = TerminalOutput(use_color=False)
    runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
    config = ProjectConfig(build_dir=tmp_path / "build")
    return _BuildCore(config=config, runner=runner, ui=ui, jobs=2)


class TestCacheThreadSafety:
    """Test that build cache operations are thread-safe."""

    def test_concurrent_cache_reads(self, build_core, tmp_path):
        """Multiple threads reading cache simultaneously should not crash."""
        build_core.config.build_dir = tmp_path / "build"
        build_core.config.build_dir.mkdir(parents=True)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        cache = {
            "examples/a": {"source_hash": "abc", "build_time": now},
            "examples/b": {"source_hash": "def", "build_time": now},
        }
        build_core._save_build_cache(cache)

        errors = []

        def read_cache():
            try:
                for _ in range(10):
                    loaded = build_core._load_build_cache()
                    assert "examples/a" in loaded
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=read_cache) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []

    def test_concurrent_cache_writes(self, build_core, tmp_path):
        """Multiple threads writing different cache keys should not corrupt."""
        build_core.config.build_dir = tmp_path / "build"
        build_core.config.build_dir.mkdir(parents=True)
        build_core._shared_build_cache = {}

        errors = []

        def write_cache(key):
            try:
                for i in range(5):
                    with build_core._cache_lock:
                        build_core._shared_build_cache[f"examples/{key}"] = {
                            "source_hash": f"hash_{key}_{i}",
                            "build_time": time.strftime(
                                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                            ),
                        }
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=write_cache, args=(f"ex{i}",)) for i in range(10)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []
        assert len(build_core._shared_build_cache) == 10

    def test_timings_data_thread_safety(self, build_core):
        """Multiple threads appending to timings_data should not lose data."""
        build_core.timings = True
        errors = []

        def append_timing(idx):
            try:
                for i in range(10):
                    with build_core._timings_lock:
                        build_core.timings_data.append(
                            {
                                "name": f"ex_{idx}_{i}",
                                "wall_time_s": 1.0,
                                "success": True,
                            }
                        )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=append_timing, args=(i,)) for i in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []
        assert len(build_core.timings_data) == 50


class TestConcurrentWorkerExecution:
    """Test _compile_example_worker under concurrent execution."""

    def test_workers_do_not_interfere(self, build_core, tmp_path, monkeypatch):
        """Multiple workers for different examples should not interfere."""
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        (tmp_path / "examples").mkdir()
        build_core._shared_build_cache = {}

        results = []
        errors = []

        def run_worker(name):
            try:
                with patch.object(build_core.runner, "run", return_value=(1, ["fail"])):
                    result = build_core._compile_example_worker(name)
                    results.append(result)
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(run_worker, f"ex{i}") for i in range(5)]
            for f in as_completed(futures):
                f.result()

        assert errors == []
        assert len(results) == 5
        names = {r[0] for r in results}
        assert names == {f"ex{i}" for i in range(5)}

    def test_cache_hit_during_concurrent_builds(
        self, build_core, tmp_path, monkeypatch
    ):
        """Cache hits should work correctly during concurrent builds."""
        monkeypatch.setattr("buildlib.config.REPO_ROOT", tmp_path)
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        examples_dir = tmp_path / "examples"
        examples_dir.mkdir()

        # Create a real example that will cache-hit
        ex_dir = examples_dir / "cached-ex"
        ex_dir.mkdir()
        (ex_dir / "main.tex").write_text(
            "\\documentclass{article}\\begin{document}hi\\end{document}"
        )

        build_core._shared_build_cache = {}
        build_core.config.build_dir = tmp_path / "build"
        build_examples_dir = tmp_path / "build" / "examples"
        build_examples_dir.mkdir(parents=True)
        (build_examples_dir / "cached-ex.pdf").write_bytes(b"%PDF-fake")

        # Pre-populate cache with correct hash
        source_files = build_core._collect_source_files("cached-ex")
        source_hash = _BuildCore._hash_for_paths(source_files)
        mtimes = _BuildCore._get_mtimes(source_files)
        build_core._shared_build_cache["examples/cached-ex"] = {
            "source_hash": source_hash,
            "mtimes": mtimes,
            "build_time": "2026-01-01T00:00:00Z",
        }

        # Run worker - should hit cache
        name, success, logs = build_core._compile_example_worker("cached-ex")
        assert success is True
        assert any("Cache hit" in line for line in logs)


class TestSourceFilesCaching:
    """Test that _get_source_files caching is thread-safe."""

    def test_concurrent_source_file_access(self, build_core):
        """Multiple threads accessing source_files should get same result."""
        results = []
        errors = []

        def get_files():
            try:
                files = build_core.source_files
                results.append(len(files))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=get_files) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert errors == []
        # All threads should get the same count
        assert len(set(results)) == 1
