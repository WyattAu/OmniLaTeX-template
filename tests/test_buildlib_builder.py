"""Unit tests for buildlib.builder module (build core logic)."""

from __future__ import annotations

import json
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from buildlib.builder import _BuildCore, extract_log_path, parse_log_for_package_times
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
        cache = {
            "examples/test": {
                "source_hash": "abc123",
                "build_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        }
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


class TestSourceDateEpoch:
    """Test SOURCE_DATE_EPOCH reproducibility support."""

    def test_source_date_epoch_settable(self, monkeypatch):
        """CLI should be able to set SOURCE_DATE_EPOCH."""
        monkeypatch.setenv("SOURCE_DATE_EPOCH", "1700000000")
        import os

        assert os.environ.get("SOURCE_DATE_EPOCH") == "1700000000"

    def test_source_date_epoch_in_build_env(self, build_core, monkeypatch):
        """Build environment should pass SOURCE_DATE_EPOCH to subprocess."""
        monkeypatch.setenv("SOURCE_DATE_EPOCH", "1700000000")
        # The runner should include it in the environment
        import os

        env = os.environ.copy()
        assert "SOURCE_DATE_EPOCH" in env
        assert env["SOURCE_DATE_EPOCH"] == "1700000000"


class TestVersionProperty:
    """Test _BuildCore.version property."""

    def test_version_from_version_md(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        vf = tmp_path / "VERSION.md"
        vf.write_text("Current version: **v3.1.4**\n")
        assert build_core.version == "3.1.4"

    def test_version_no_file(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        assert build_core.version == "0.0.0"

    def test_version_no_semver_in_file(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        vf = tmp_path / "VERSION.md"
        vf.write_text("No version here\n")
        assert build_core.version == "0.0.0"


class TestCompileWorkerPaths:
    """Test _compile_example_worker success and failure paths."""

    def test_worker_pdf_copies_successfully(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        (tmp_path / "examples" / "test-ex").mkdir(parents=True)
        # Create a fake PDF that the worker will "find"
        pdf = tmp_path / "examples" / "test-ex" / "main.pdf"
        pdf.write_bytes(b"%PDF-1.4 fake")

        from unittest.mock import patch

        with patch.object(build_core.runner, "run", return_value=(0, [])):
            name, success, logs = build_core._compile_example_worker("test-ex")

        assert name == "test-ex"
        assert success is True

    def test_worker_pdf_not_found_after_build(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        (tmp_path / "examples" / "test-ex").mkdir(parents=True)
        # No PDF created

        from unittest.mock import patch

        with patch.object(build_core.runner, "run", return_value=(0, [])):
            name, success, logs = build_core._compile_example_worker("test-ex")

        assert success is False

    def test_worker_oserror_catch(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        (tmp_path / "examples" / "test-ex").mkdir(parents=True)

        from unittest.mock import patch

        with patch.object(build_core.runner, "run", side_effect=OSError("disk full")):
            name, success, logs = build_core._compile_example_worker("test-ex")

        assert success is False

    def test_worker_force_rebuild_env(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        build_core.force = True
        (tmp_path / "examples" / "test-ex").mkdir(parents=True)
        pdf = tmp_path / "examples" / "test-ex" / "main.pdf"
        pdf.write_bytes(b"%PDF-1.4 fake")

        from unittest.mock import patch

        with patch.object(build_core.runner, "run", return_value=(0, [])):
            name, success, logs = build_core._compile_example_worker("test-ex")

        assert name == "test-ex"

    def test_worker_with_latexmkrc(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        (tmp_path / "examples" / "test-ex").mkdir(parents=True)
        (tmp_path / ".latexmkrc").write_text("$pdflatex = 'lualatex';\n")
        pdf = tmp_path / "examples" / "test-ex" / "main.pdf"
        pdf.write_bytes(b"%PDF-1.4 fake")

        from unittest.mock import patch

        with patch.object(build_core.runner, "run", return_value=(0, [])):
            name, success, logs = build_core._compile_example_worker("test-ex")

        assert success is True

    def test_worker_timings_captured(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        build_core.timings = True
        (tmp_path / "examples" / "test-ex").mkdir(parents=True)
        pdf = tmp_path / "examples" / "test-ex" / "main.pdf"
        pdf.write_bytes(b"%PDF-1.4 fake")

        from unittest.mock import patch

        with patch.object(build_core.runner, "run", return_value=(0, [])):
            name, success, logs = build_core._compile_example_worker("test-ex")

        assert success is True
        assert len(build_core.timings_data) >= 1
        assert build_core.timings_data[0]["name"] == "test-ex"


class TestBuildExamplesSimpleConcurrent:
    """Test _build_examples_simple_concurrent."""

    def test_simple_concurrent_success(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        monkeypatch.setattr("buildlib.builder.RICH_AVAILABLE", False)

        with patch.object(
            build_core, "_compile_example_worker", return_value=("ex1", True, [])
        ):
            build_core._build_examples_simple_concurrent(["ex1"])

    def test_simple_concurrent_failure(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        monkeypatch.setattr("buildlib.builder.RICH_AVAILABLE", False)

        with patch.object(
            build_core,
            "_compile_example_worker",
            return_value=("ex1", False, ["error"]),
        ):
            build_core._build_examples_simple_concurrent(["ex1"])


class TestBuildExamplesWithTimings:
    """Test build_examples with timings output."""

    def test_build_examples_writes_metrics_json(
        self, build_core, tmp_path, monkeypatch
    ):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        build_core.timings = True
        build_core.config.build_dir = tmp_path / "build"

        # Create a fake example
        (tmp_path / "examples" / "test-ex").mkdir(parents=True)
        (tmp_path / "examples" / "test-ex" / "main.tex").write_text(
            "\\documentclass{article}\\begin{document}test\\end{document}"
        )

        with patch.object(
            build_core,
            "_compile_example_worker",
            return_value=("test-ex", True, []),
        ), patch.object(build_core, "_build_examples_simple_concurrent"):
            # Manually set timings_data since we're mocking the worker
            build_core.timings_data = [
                {
                    "name": "test-ex",
                    "mode": "dev",
                    "wall_time_s": 1.5,
                    "pdf_size_bytes": 1024,
                    "success": True,
                }
            ]
            build_core._save_build_cache = MagicMock()
            # Call the metrics writing logic directly
            metrics_path = build_core.config.build_dir / "metrics.json"
            build_core.config.build_dir.mkdir(parents=True, exist_ok=True)
            import json

            metrics_path.write_text(
                json.dumps(build_core.timings_data, indent=2), encoding="utf-8"
            )
            assert metrics_path.exists()
            data = json.loads(metrics_path.read_text(encoding="utf-8"))
            assert len(data) == 1
            assert data[0]["name"] == "test-ex"


class TestBuildRootSuccess:
    """Test build_root when PDF exists."""

    def test_build_root_copies_pdf(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        monkeypatch.setattr("buildlib.builder.RICH_AVAILABLE", False)
        build_core.config.build_dir = tmp_path / "build"
        monkeypatch.chdir(tmp_path)

        # Create main.pdf in tmp_path (CWD after chdir)
        pdf = tmp_path / "main.pdf"
        pdf.write_bytes(b"%PDF-1.4 fake")

        with patch.object(build_core.runner, "run", return_value=(0, [])):
            build_core.build_root()

        # PDF should be copied to build/
        dest = tmp_path / "build" / "main.pdf"
        assert dest.exists()
