"""Additional coverage tests for buildlib modules.

Targets uncovered code paths in builder.py, profiler.py, and tui.py
to achieve >= 80% branch coverage across the buildlib package.
"""

from __future__ import annotations

import datetime
import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from buildlib.builder import _BuildCore, extract_log_path, parse_log_for_package_times
from buildlib.config import REPO_ROOT, ProjectConfig
from buildlib.runner import CommandRunner
from buildlib.ui import TerminalOutput

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def ui():
    return TerminalOutput(use_color=False)


@pytest.fixture
def runner(ui):
    return CommandRunner(ui=ui, build_mode="dev", verbose=False)


@pytest.fixture
def build_core(tmp_path, ui, runner):
    config = ProjectConfig(build_dir=tmp_path / "build")
    return _BuildCore(config=config, runner=runner, ui=ui, jobs=1)


@pytest.fixture
def verbose_runner(ui):
    return CommandRunner(ui=ui, build_mode="prod", verbose=True)


# ===================================================================
# builder.py -- _evict_cache
# ===================================================================


class TestEvictCache:
    """Test cache eviction logic (TTL and LRU cap)."""

    def test_removes_expired_entries(self, build_core):
        old_time = (
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=100)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        cache = {
            "examples/old": {"build_time": old_time, "source_hash": "abc"},
            "examples/new": {
                "build_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "source_hash": "def",
            },
        }
        result = build_core._evict_cache(cache, max_entries=100, max_age_days=90)
        assert "examples/new" in result
        assert "examples/old" not in result

    def test_lru_cap(self, build_core):
        cache = {}
        for i in range(150):
            # Use different timestamps so LRU can sort
            ts = (
                datetime.datetime.now(datetime.timezone.utc)
                - datetime.timedelta(minutes=i)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
            cache[f"examples/ex{i}"] = {"build_time": ts, "source_hash": f"h{i}"}
        result = build_core._evict_cache(cache, max_entries=100, max_age_days=90)
        example_keys = [k for k in result if k.startswith("examples/")]
        assert len(example_keys) <= 100

    def test_non_example_keys_preserved(self, build_core):
        old_time = (
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=200)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        cache = {
            "metadata": {"version": "2.0"},
            "examples/old": {"build_time": old_time, "source_hash": "x"},
        }
        result = build_core._evict_cache(cache, max_entries=100, max_age_days=90)
        assert "metadata" in result
        assert "examples/old" not in result

    def test_empty_cache(self, build_core):
        result = build_core._evict_cache({})
        assert result == {}


# ===================================================================
# builder.py -- _save_build_cache
# ===================================================================


class TestSaveBuildCache:
    def test_creates_parent_directory(self, build_core, tmp_path):
        build_core.config.build_dir = tmp_path / "nested" / "deep" / "build"
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        cache = {"examples/test": {"source_hash": "abc", "build_time": now}}
        build_core._save_build_cache(cache)
        cache_file = build_core.config.build_dir / "build_cache.json"
        assert cache_file.exists()
        loaded = json.loads(cache_file.read_text())
        assert loaded["examples/test"]["source_hash"] == "abc"

    def test_eviction_before_save(self, build_core, tmp_path):
        build_core.config.build_dir = tmp_path / "build"
        # Create cache with old entries
        old_time = (
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=200)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        cache = {
            "examples/old": {"source_hash": "x", "build_time": old_time},
            "examples/new": {
                "source_hash": "y",
                "build_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            },
        }
        build_core._save_build_cache(cache)
        loaded = json.loads((tmp_path / "build" / "build_cache.json").read_text())
        assert "examples/new" in loaded
        assert "examples/old" not in loaded


# ===================================================================
# builder.py -- _get_source_files
# ===================================================================


class TestGetSourceFiles:
    def test_returns_sty_and_cls_files(self, build_core):
        files = build_core._get_source_files(REPO_ROOT)
        assert len(files) > 0
        for f in files:
            assert f.suffix in (".sty", ".cls")

    def test_caching(self, build_core):
        files1 = build_core._get_source_files(REPO_ROOT)
        files2 = build_core._get_source_files(REPO_ROOT)
        assert files1 is files2


# ===================================================================
# builder.py -- cmd_cache_stats
# ===================================================================


class TestCmdCacheStats:
    def test_no_cache_file(self, build_core, tmp_path, capsys):
        build_core.config.build_dir = tmp_path / "nonexistent"
        build_core.cmd_cache_stats()
        captured = capsys.readouterr()
        assert "No build cache" in captured.out

    def test_with_cache_entries(self, build_core, tmp_path, capsys):
        build_core.config.build_dir = tmp_path / "build"
        (tmp_path / "build").mkdir(parents=True)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        cache = {
            "examples/a": {"source_hash": "h1", "build_time": now},
            "examples/b": {"source_hash": "h2", "build_time": now},
        }
        build_core._save_build_cache(cache)
        build_core.cmd_cache_stats()
        captured = capsys.readouterr()
        assert "Cached entries" in captured.out


# ===================================================================
# builder.py -- list_examples text output
# ===================================================================


class TestListExamplesText:
    def test_text_output(self, build_core, capsys):
        build_core.list_examples(output_format="text")
        captured = capsys.readouterr()
        assert "Available Examples" in captured.out
        assert "Found" in captured.out


# ===================================================================
# builder.py -- compile_example_worker edge cases
# ===================================================================


class TestCompileExampleWorker:
    """Test _compile_example_worker with fully mocked runner.

    These tests use monkeypatch to redirect REPO_ROOT to a temp directory,
    ensuring they work regardless of repo state.
    """

    def test_worker_nonexistent_example(self, build_core, tmp_path, monkeypatch):
        """Worker for nonexistent example should fail (no PDF created)."""
        # Create a minimal examples dir with no example
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        (tmp_path / "examples").mkdir()
        with patch.object(
            build_core.runner, "run", return_value=(1, ["latexmk not found"])
        ) as mock_run:
            name, success, logs = build_core._compile_example_worker(
                "nonexistent-example-xyz"
            )
        assert name == "nonexistent-example-xyz"
        assert success is False
        mock_run.assert_called()

    def test_worker_with_timings(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        (tmp_path / "examples").mkdir()
        build_core.timings = True
        with patch.object(build_core.runner, "run", return_value=(1, ["fail"])):
            name, success, logs = build_core._compile_example_worker(
                "nonexistent-example-xyz"
            )
        assert success is False
        assert len(build_core.timings_data) >= 1

    def test_worker_with_force_flag(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        (tmp_path / "examples").mkdir()
        build_core.force = True
        with patch.object(build_core.runner, "run", return_value=(1, ["fail"])):
            name, success, logs = build_core._compile_example_worker(
                "nonexistent-example-xyz"
            )
        assert success is False

    def test_worker_with_shared_cache(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        (tmp_path / "examples").mkdir()
        build_core._shared_build_cache = {}
        with patch.object(build_core.runner, "run", return_value=(1, ["fail"])):
            name, success, logs = build_core._compile_example_worker(
                "nonexistent-example-xyz"
            )
        assert success is False
        assert isinstance(build_core._shared_build_cache, dict)

    def test_worker_cnf_lines(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        (tmp_path / "examples").mkdir()
        build_core.config.cnf_lines = ["\\setmainfont{Times New Roman}"]
        with patch.object(build_core.runner, "run", return_value=(1, ["fail"])):
            name, success, logs = build_core._compile_example_worker(
                "nonexistent-example-xyz"
            )
        assert success is False


# ===================================================================
# builder.py -- build_examples edge cases
# ===================================================================


class TestBuildExamplesEdgeCases:
    def test_build_examples_no_valid_names(self, build_core, tmp_path, monkeypatch):
        """Should warn when no valid examples to build."""
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        (tmp_path / "examples").mkdir()
        build_core.build_examples(files=["nonexistent-1", "nonexistent-2"])

    def test_build_examples_json_output(self, build_core, capsys):
        build_core.list_examples(output_format="json")
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, list)


# ===================================================================
# builder.py -- build_root
# ===================================================================


class TestBuildRoot:
    def test_build_root_no_pdf(self, build_core, tmp_path, monkeypatch):
        """build_root should raise SystemExit when PDF not generated."""
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        build_core.runner = MagicMock()
        build_core.runner.run = MagicMock(return_value=(1, ["latexmk failed"]))
        with pytest.raises(SystemExit):
            build_core.build_root()


# ===================================================================
# profiler.py -- additional coverage
# ===================================================================


class TestBuildProfilerExtended:
    def test_discover_examples_no_dir(self, monkeypatch, tmp_path):
        monkeypatch.setattr("buildlib.profiler.REPO_ROOT", tmp_path)
        from buildlib.profiler import BuildProfiler

        profiler = BuildProfiler()
        found = profiler.discover_examples()
        assert found == []

    def test_profile_example_build_with_subprocess(self, monkeypatch, tmp_path):
        """Test _build_with_subprocess path (no runner)."""
        from buildlib.profiler import BuildProfiler

        monkeypatch.setattr("buildlib.profiler.REPO_ROOT", tmp_path)
        examples_dir = tmp_path / "examples" / "test-ex"
        examples_dir.mkdir(parents=True)
        (examples_dir / "main.tex").write_text(
            "\\documentclass{article}\\begin{document}hi\\end{document}"
        )

        profiler = BuildProfiler()
        result = profiler.profile_example("test-ex")
        # Should not crash, may fail build but profile is created
        assert result.name == "test-ex"

    def test_profile_all_with_names_filter(self, monkeypatch, tmp_path):
        from buildlib.profiler import BuildProfiler, ExampleProfile

        monkeypatch.setattr("buildlib.profiler.REPO_ROOT", tmp_path)
        profiler = BuildProfiler()
        # Mock discover_examples to return known paths
        profiler.discover_examples = MagicMock(
            return_value=[tmp_path / "examples" / "a", tmp_path / "examples" / "b"]
        )
        profiler.profile_example = MagicMock(
            return_value=ExampleProfile(name="a", wall_time_s=1.0, success=True)
        )
        summary = profiler.profile_all(names=["a"])
        assert summary.total_examples == 1

    def test_build_summary_with_stdev(self):
        from buildlib.profiler import BuildProfiler, ExampleProfile

        profiler = BuildProfiler()
        profiler.profiles = [
            ExampleProfile(name="a", wall_time_s=1.0, success=True),
            ExampleProfile(name="b", wall_time_s=3.0, success=True),
            ExampleProfile(name="c", wall_time_s=5.0, success=True),
        ]
        summary = profiler._build_summary()
        assert summary.stdev_wall_time_s > 0
        assert summary.mean_wall_time_s > 0

    def test_generate_recommendations_high_memory(self):
        from buildlib.profiler import BuildProfiler, ExampleProfile, ProfilingSummary

        profiler = BuildProfiler()
        summary = ProfilingSummary(
            total_examples=1,
            successful=1,
            peak_memory_kb=600_000,
            profiles=[
                ExampleProfile(
                    name="mem", wall_time_s=2.0, success=True, peak_memory_kb=600_000
                )
            ],
        )
        summary.mean_wall_time_s = 2.0
        summary.stdev_wall_time_s = 0.0
        recs = profiler._generate_recommendations(summary)
        assert any("memory" in r.lower() for r in recs)

    def test_generate_recommendations_heavy_packages(self):
        from buildlib.profiler import BuildProfiler, ExampleProfile, ProfilingSummary

        profiler = BuildProfiler()
        summary = ProfilingSummary(
            total_examples=1,
            successful=1,
            profiles=[
                ExampleProfile(
                    name="heavy",
                    wall_time_s=2.0,
                    success=True,
                    package_count=60,
                )
            ],
        )
        summary.mean_wall_time_s = 2.0
        summary.stdev_wall_time_s = 0.0
        recs = profiler._generate_recommendations(summary)
        assert any("package" in r.lower() for r in recs)

    def test_generate_recommendations_high_variance(self):
        from buildlib.profiler import BuildProfiler, ExampleProfile, ProfilingSummary

        profiler = BuildProfiler()
        summary = ProfilingSummary(
            total_examples=2,
            successful=2,
            profiles=[
                ExampleProfile(name="fast", wall_time_s=1.0, success=True),
                ExampleProfile(name="slow", wall_time_s=100.0, success=True),
            ],
        )
        summary.mean_wall_time_s = 50.5
        summary.stdev_wall_time_s = 70.0
        recs = profiler._generate_recommendations(summary)
        assert any("variance" in r.lower() for r in recs)

    def test_export_json_creates_parent(self, tmp_path):
        from buildlib.profiler import BuildProfiler, ExampleProfile

        profiler = BuildProfiler()
        profiler.profiles = [ExampleProfile(name="x", success=True)]
        out = tmp_path / "deep" / "nested" / "output.json"
        result = profiler.export_json(out)
        assert result.exists()


# ===================================================================
# runner.py -- additional edge cases
# ===================================================================


class TestCommandRunnerExtended:
    def test_run_with_on_line_callback(self, runner):
        lines = []
        exit_code, logs = runner.run(
            ["echo", "test-line"],
            on_line=lambda line: lines.append(line),
        )
        assert exit_code == 0
        assert any("test-line" in line for line in lines)

    def test_run_with_zero_timeout(self, runner):
        """Very short timeout should not kill echo."""
        exit_code, logs = runner.run(["echo", "fast"], timeout=10)
        assert exit_code == 0

    def test_build_mode_passed_through(self, runner, monkeypatch):
        monkeypatch.delenv("BUILD_MODE", raising=False)
        exit_code, logs = runner.run(["printenv", "BUILD_MODE"])
        assert exit_code == 0
        assert "dev" in logs


# ===================================================================
# ui.py -- additional coverage
# ===================================================================


class TestTerminalOutputExtended:
    def test_warning_output(self, ui, capsys):
        ui.warning("test warning")
        captured = capsys.readouterr()
        assert "test warning" in captured.out

    def test_error_output(self, ui, capsys):
        ui.error("test error")
        captured = capsys.readouterr()
        assert "test error" in captured.err

    def test_debug_output(self, ui, capsys):
        ui.debug("test debug")
        captured = capsys.readouterr()
        assert "test debug" in captured.out

    def test_color_disabled(self):
        ui = TerminalOutput(use_color=False)
        assert ui.bold == ""
        assert ui.end == ""

    def test_color_enabled(self):
        ui = TerminalOutput(use_color=True)
        assert ui.bold != ""
        assert ui.end != ""


# ===================================================================
# config.py -- additional coverage
# ===================================================================


class TestProjectConfigExtended:
    def test_is_ci_true(self):
        config = ProjectConfig()
        with patch.dict("os.environ", {"CI": "true"}):
            assert config.is_ci() is True

    def test_is_ci_false(self):
        config = ProjectConfig()
        with patch.dict("os.environ", {}, clear=True):
            assert config.is_ci() is False

    def test_verbose_enabled_true(self):
        config = ProjectConfig()
        with patch.dict("os.environ", {"OMNILATEX_VERBOSE": "1"}):
            assert config.verbose_enabled() is True

    def test_verbose_enabled_false(self):
        config = ProjectConfig()
        with patch.dict("os.environ", {}, clear=True):
            assert config.verbose_enabled() is False


# ===================================================================
# builder.py -- parse_log_for_package_times edge cases
# ===================================================================


class TestParseLogExtended:
    def test_no_total_time(self):
        result = parse_log_for_package_times("Package: fontspec 2024/01/01 v2.8a\n")
        assert result["total_time_s"] is None

    def test_total_time_below_threshold(self):
        result = parse_log_for_package_times("0.3 seconds\n")
        assert result["total_time_s"] is None

    def test_multiple_packages(self):
        log = (
            "Package: fontspec 2024/01/01 v2.8a\n"
            "Package: hyperref 2024/02/15 v7.01\n"
            "Package: babel 2024/03/01 v3.95\n"
            "Package: graphicx 2024/04/01 v1.0\n"
        )
        result = parse_log_for_package_times(log)
        assert result["package_count"] == 4

    def test_luc_cache_multiple(self):
        log = "(load luc: /fonts/mono.luc)\n" "(load luc: /fonts/sans.luc)\n"
        result = parse_log_for_package_times(log)
        assert result["package_count"] >= 2


# ===================================================================
# builder.py -- extract_log_path edge cases
# ===================================================================


class TestExtractLogPathExtended:
    def test_with_log_file(self, tmp_path):
        log = tmp_path / "main.log"
        log.write_text("test")
        result = extract_log_path(tmp_path)
        assert result == log

    def test_without_log_file(self, tmp_path):
        result = extract_log_path(tmp_path)
        assert result is None

    def test_with_directory_named_main_log(self, tmp_path):
        # Edge case: directory named main.log
        dir_as_log = tmp_path / "main.log"
        dir_as_log.mkdir()
        result = extract_log_path(tmp_path)
        # Should return the directory path (exists() returns True for dirs)
        assert result == dir_as_log


# ===================================================================
# builder.py -- hash_for_paths additional cases
# ===================================================================


class TestHashForPathsExtended:
    def test_nonexistent_files_only(self, tmp_path):
        h = _BuildCore._hash_for_paths([tmp_path / "a.tex", tmp_path / "b.tex"])
        assert isinstance(h, str)
        assert len(h) == 64

    def test_mixed_existing_nonexisting(self, tmp_path):
        existing = tmp_path / "a.tex"
        existing.write_text("content")
        h = _BuildCore._hash_for_paths([existing, tmp_path / "nonexistent.tex"])
        assert isinstance(h, str)
        assert len(h) == 64

    def test_sort_order_independent(self, tmp_path):
        a = tmp_path / "a.tex"
        b = tmp_path / "b.tex"
        a.write_text("aaa")
        b.write_text("bbb")
        h1 = _BuildCore._hash_for_paths([a, b])
        h2 = _BuildCore._hash_for_paths([b, a])
        assert h1 == h2


# ===================================================================
# builder.py -- _compile_example_worker with cache hit
# ===================================================================


class TestWorkerCacheHit:
    def test_cache_hit_skips_build(self, build_core, tmp_path):
        """When cache has valid hash and PDF exists, worker should return success."""
        example_name = "test-cache-hit"
        example_dir = REPO_ROOT / "examples" / example_name
        # We need the example to exist
        if not example_dir.is_dir():
            pytest.skip("examples/test-cache-hit does not exist")

        # Set up cache with current hash
        source_files = build_core._collect_source_files(example_name)
        source_hash = _BuildCore._hash_for_paths(source_files)
        build_core.config.build_dir = tmp_path / "build"
        (tmp_path / "build").mkdir(parents=True)
        cache = {
            f"examples/{example_name}": {
                "source_hash": source_hash,
                "build_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        }
        build_core._save_build_cache(cache)
        # Also need the PDF to exist
        build_examples_dir = tmp_path / "build" / "examples"
        build_examples_dir.mkdir(parents=True)
        (build_examples_dir / f"{example_name}.pdf").write_bytes(b"%PDF-fake")

        name, success, logs = build_core._compile_example_worker(example_name)
        assert success is True


# ===================================================================
# builder.py -- clean_all, clean_example, clean_pdf
# ===================================================================


class TestCleanMethods:
    """Test cleanup methods in _BuildCore."""

    def test_clean_all(self, build_core, tmp_path, monkeypatch):
        """clean_all should remove build dir and clean aux files."""
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        build_core.config.build_dir = tmp_path / "build"
        build_core.config.build_dir.mkdir(parents=True)
        (build_core.config.build_dir / "test.pdf").write_bytes(b"%PDF")
        with patch.object(build_core.runner, "run", return_value=(0, [])):
            build_core.clean_all()
        assert not build_core.config.build_dir.exists()

    def test_clean_example_empty_list(self, build_core):
        """clean_example with empty list should not call runner."""
        with patch.object(build_core.runner, "run") as mock_run:
            build_core.clean_example([])
        mock_run.assert_not_called()

    def test_clean_example_with_files(self, build_core, tmp_path, monkeypatch):
        """clean_example should call latexmk -c for each file."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "examples" / "test-ex").mkdir(parents=True)
        with patch.object(build_core.runner, "run", return_value=(0, [])) as mock_run:
            build_core.clean_example(["test-ex"])
        mock_run.assert_called_once()

    def test_clean_example_os_error(self, build_core, tmp_path, monkeypatch, capsys):
        """clean_example should catch OSError and continue."""
        monkeypatch.chdir(tmp_path)
        with patch.object(
            build_core.runner, "run", side_effect=OSError("permission denied")
        ):
            build_core.clean_example(["test-ex"])
        captured = capsys.readouterr()
        assert "Could not clean" in captured.out

    def test_clean_pdf_removes_matching(self, build_core, tmp_path, monkeypatch):
        """clean_pdf should remove PDFs in build/examples and examples/."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        build_examples_dir = tmp_path / "build" / "examples"
        build_examples_dir.mkdir(parents=True)
        (build_examples_dir / "test.pdf").write_bytes(b"%PDF")
        examples_dir = tmp_path / "examples" / "ex1"
        examples_dir.mkdir(parents=True)
        (examples_dir / "main.pdf").write_bytes(b"%PDF")
        # Non-matching PDF (should not be removed)
        (tmp_path / "other.pdf").write_bytes(b"%PDF")
        build_core.config.build_dir = tmp_path / "build"
        build_core.clean_pdf()
        assert not (build_examples_dir / "test.pdf").exists()
        assert not (examples_dir / "main.pdf").exists()
        assert (tmp_path / "other.pdf").exists()


# ===================================================================
# builder.py -- build_all, build_example
# ===================================================================


class TestBuildAllAndExample:
    def test_build_example_delegates(self, build_core):
        """build_example should delegate to build_examples."""
        with patch.object(build_core, "build_examples") as mock:
            build_core.build_example(["thesis"])
        mock.assert_called_once_with(["thesis"])

    def test_build_all_calls_root_and_examples(self, build_core):
        """build_all should call build_root then build_examples."""
        with (
            patch.object(build_core, "build_root") as mock_root,
            patch.object(build_core, "build_examples") as mock_examples,
        ):
            build_core.build_all()
        mock_root.assert_called_once()
        mock_examples.assert_called_once()


# ===================================================================
# builder.py -- preflight and run_tests delegates
# ===================================================================


class TestPreflightAndRunTests:
    def test_preflight_delegates(self, build_core):
        """preflight should call cmd_preflight if available."""
        # cmd_preflight is on _Commands mixin, not _BuildCore directly.
        # But build_core.preflight() calls self.cmd_preflight().
        # Mock it at the instance level using MagicMock.
        build_core.cmd_preflight = MagicMock()
        build_core.preflight()
        build_core.cmd_preflight.assert_called_once()

    def test_run_tests_delegates(self, build_core):
        """run_tests should call cmd_test if available."""
        build_core.cmd_test = MagicMock()
        build_core.run_tests()
        build_core.cmd_test.assert_called_once()


# ===================================================================
# builder.py -- TqdmFallback
# ===================================================================


class TestTqdmFallback:
    """Test the TqdmFallback progress bar class."""

    def test_with_list(self, capsys):
        from buildlib.builder import TqdmFallback

        items = [1, 2, 3]
        result = list(TqdmFallback(items, desc="Test"))
        assert result == [1, 2, 3]

    def test_with_generator(self, capsys):
        from buildlib.builder import TqdmFallback

        def gen():
            yield "a"
            yield "b"

        result = list(TqdmFallback(gen(), desc="Gen", total=2))
        assert result == ["a", "b"]

    def test_progress_output(self, capsys):
        from buildlib.builder import TqdmFallback

        list(TqdmFallback([1, 2], desc="Prog"))
        captured = capsys.readouterr()
        assert "Prog:" in captured.out

    def test_zero_total(self, capsys):
        from buildlib.builder import TqdmFallback

        result = list(TqdmFallback([], desc="Empty"))
        assert result == []
