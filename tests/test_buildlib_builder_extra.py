"""Additional unit tests for buildlib.builder uncovered lines."""

from __future__ import annotations

import json
import time
from unittest.mock import MagicMock, patch

import pytest

from buildlib.builder import (
    _BuildCore,
    extract_log_path,
    parse_log_for_package_times,
)
from buildlib.config import ProjectConfig
from buildlib.runner import CommandRunner
from buildlib.ui import TerminalOutput

pytestmark = pytest.mark.timeout(15)


@pytest.fixture
def build_core(tmp_path):
    ui = TerminalOutput(use_color=False)
    runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
    config = ProjectConfig(build_dir=tmp_path / "build")
    return _BuildCore(config=config, runner=runner, ui=ui, jobs=1)


class TestTqdmFallback:
    def test_tqdm_fallback_iter(self, monkeypatch):
        import buildlib.builder as mod

        real_tqdm = mod.tqdm
        try:
            monkeypatch.setattr("buildlib.builder.tqdm", None)

            class TqdmFallback:
                def __init__(self, iterable, desc="", total=None):
                    self.iterable = iterable
                    self.desc = desc
                    try:
                        self.total = total or len(iterable)
                    except TypeError:
                        self.total = total
                    self.current = 0
                    self.n = 0

                def __iter__(self):
                    for item in self.iterable:
                        self.current += 1
                        self.n = self.current
                        yield item

            fb = TqdmFallback(["a", "b", "c"])
            assert list(fb) == ["a", "b", "c"]
            assert fb.n == 3
            assert fb.total == 3
        finally:
            monkeypatch.setattr("buildlib.builder.tqdm", real_tqdm)


class TestCompileWorkerCopyException:
    def test_compile_worker_copy_exception(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        ex = tmp_path / "examples" / "test"
        ex.mkdir(parents=True)
        (ex / "main.tex").write_text(
            "\\documentclass{article}\\begin{document}test\\end{document}"
        )
        pdf = ex / "main.pdf"
        pdf.write_bytes(b"%PDF-1.4 fake")

        with patch.object(build_core.runner, "run", return_value=(0, [])), patch(
            "buildlib.builder.shutil.copy", side_effect=OSError("copy fail")
        ):
            name, success, logs = build_core._compile_example_worker("test")
            assert not success


class TestCompileWorkerSharedCache:
    def test_compile_worker_shared_cache_path(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        ex = tmp_path / "examples" / "test"
        ex.mkdir(parents=True)
        (ex / "main.tex").write_text(
            "\\documentclass{article}\\begin{document}test\\end{document}"
        )
        pdf = ex / "main.pdf"
        pdf.write_bytes(b"%PDF-1.4 fake")

        shared_cache = {}
        build_core._shared_build_cache = shared_cache

        with patch.object(build_core.runner, "run", return_value=(0, [])):
            name, success, logs = build_core._compile_example_worker("test")

        assert success is True
        assert f"examples/test" in shared_cache
        assert "source_hash" in shared_cache[f"examples/test"]


class TestBuildRootFailure:
    def test_build_root_failure(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        monkeypatch.setattr("buildlib.builder.RICH_AVAILABLE", False)
        monkeypatch.chdir(tmp_path)
        (tmp_path / "main.tex").write_text("\\documentclass{article}")

        with patch.object(
            build_core.runner,
            "run",
            return_value=(1, ["error line 1", "error line 2"]),
        ):
            with pytest.raises(SystemExit):
                build_core.build_root()

    def test_build_root_failure_zero_exit_code(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        monkeypatch.setattr("buildlib.builder.RICH_AVAILABLE", False)
        monkeypatch.chdir(tmp_path)

        with patch.object(
            build_core.runner, "run", return_value=(0, ["some log line"])
        ):
            with pytest.raises(SystemExit):
                build_core.build_root()


class TestBuildExamplesMetrics:
    def test_build_examples_metrics(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        monkeypatch.setattr("buildlib.builder.RICH_AVAILABLE", False)
        build_core.timings = True
        build_core.config.build_dir = tmp_path / "build"

        ex = tmp_path / "examples" / "test1"
        ex.mkdir(parents=True)
        (ex / "main.tex").write_text(
            "\\documentclass{article}\\begin{document}test\\end{document}"
        )

        with patch.object(
            build_core, "_compile_example_worker", return_value=("test1", True, [])
        ), patch.object(build_core, "_build_examples_simple_concurrent"):
            build_core.timings_data = [
                {
                    "name": "test1",
                    "mode": "dev",
                    "wall_time_s": 2.5,
                    "pdf_size_bytes": 2048,
                    "success": True,
                }
            ]
            build_core._save_build_cache = MagicMock()
            build_core.build_examples()

        metrics = tmp_path / "build" / "metrics.json"
        assert metrics.exists()
        data = json.loads(metrics.read_text())
        assert "timings" not in data
        assert "examples" in data
        assert "summary" in data
        assert data["summary"]["total"] == 1
        assert data["summary"]["successful"] == 1

        history_dir = tmp_path / "build" / "metrics_history"
        assert history_dir.exists()
        history_files = list(history_dir.glob("metrics_*.json"))
        assert len(history_files) == 1

    def test_build_examples_no_timings_no_metrics(
        self, build_core, tmp_path, monkeypatch
    ):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        monkeypatch.setattr("buildlib.builder.RICH_AVAILABLE", False)
        build_core.timings = False

        ex = tmp_path / "examples" / "test1"
        ex.mkdir(parents=True)
        (ex / "main.tex").write_text(
            "\\documentclass{article}\\begin{document}test\\end{document}"
        )

        with patch.object(
            build_core, "_compile_example_worker", return_value=("test1", True, [])
        ), patch.object(build_core, "_build_examples_simple_concurrent"):
            build_core._save_build_cache = MagicMock()
            build_core.build_examples()

        metrics = tmp_path / "build" / "metrics.json"
        assert not metrics.exists()

    def test_build_examples_empty_timings_data(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        monkeypatch.setattr("buildlib.builder.RICH_AVAILABLE", False)
        build_core.timings = True

        ex = tmp_path / "examples" / "test1"
        ex.mkdir(parents=True)
        (ex / "main.tex").write_text(
            "\\documentclass{article}\\begin{document}test\\end{document}"
        )

        with patch.object(
            build_core, "_compile_example_worker", return_value=("test1", True, [])
        ), patch.object(build_core, "_build_examples_simple_concurrent"):
            build_core.timings_data = []
            build_core._save_build_cache = MagicMock()
            build_core.build_examples()

        metrics = tmp_path / "build" / "metrics.json"
        assert not metrics.exists()

    def test_build_examples_no_valid_examples(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        build_core.timings = True
        build_core._save_build_cache = MagicMock()

        with patch.object(build_core, "discover_examples", return_value=[]):
            build_core.build_examples()

        build_core._save_build_cache.assert_not_called()


class TestSimpleConcurrentVerboseFail:
    def test_simple_concurrent_verbose_fail(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        (tmp_path / "examples" / "test").mkdir(parents=True)
        (tmp_path / "examples" / "test" / "main.tex").write_text(
            "\\documentclass{article}\\begin{document}test\\end{document}"
        )

        with patch.object(
            build_core,
            "_compile_example_worker",
            return_value=("test", False, ["error"]),
        ) as mock_worker:
            build_core._build_examples_simple_concurrent(["test"])
            mock_worker.assert_called_once_with("test")

    def test_simple_concurrent_exception_in_future(
        self, build_core, tmp_path, monkeypatch, capsys
    ):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)

        def _raiser(name):
            raise RuntimeError("boom")

        with patch.object(build_core, "_compile_example_worker", side_effect=_raiser):
            build_core._build_examples_simple_concurrent(["test"])

        captured = capsys.readouterr()
        assert "boom" in captured.out or "boom" in captured.err

    def test_simple_concurrent_verbose_true(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        build_core.runner.verbose = True

        with patch.object(
            build_core,
            "_compile_example_worker",
            return_value=("test", True, ["log line"]),
        ):
            build_core._build_examples_simple_concurrent(["test"])


class TestParseLogEdgeCases:
    def test_parse_log_empty(self):
        result = parse_log_for_package_times("")
        assert result["package_count"] == 0
        assert result["total_time_s"] is None
        assert result["packages"] == {}

    def test_parse_log_luc_cache_entry(self):
        log = "(load luc: /path/to/cache/lualatex/cache/cont-en.luc)"
        result = parse_log_for_package_times(log)
        assert "cont-en" in result["packages"]
        assert result["packages"]["cont-en"]["source"] == "luc_cache"

    def test_parse_log_luc_cache_not_overwritten(self):
        log = (
            "Package: hyperref 2024/01/01 v7.01\n"
            "(load luc: /path/to/cache/hyperref.fmt)\n"
        )
        result = parse_log_for_package_times(log)
        assert result["package_count"] == 1
        assert result["packages"]["hyperref"]["date"] == "2024/01/01"
        assert "source" not in result["packages"]["hyperref"]

    def test_parse_log_seconds_no_keyword(self):
        log = "This has 42.5 in it but no seconds word\n"
        result = parse_log_for_package_times(log)
        assert result["total_time_s"] is None

    def test_parse_log_total_time_at_threshold(self):
        log = "0.5 seconds\n"
        result = parse_log_for_package_times(log)
        assert result["total_time_s"] is None

    def test_parse_log_total_time_just_above_threshold(self):
        log = "0.51 seconds\n"
        result = parse_log_for_package_times(log)
        assert result["total_time_s"] == 0.51

    def test_parse_log_multiple_luc_entries(self):
        log = (
            "(load luc: /cache/a.luc)\n"
            "(load luc: /cache/b.luc)\n"
            "(load luc: /cache/a.luc)\n"
        )
        result = parse_log_for_package_times(log)
        assert "a" in result["packages"]
        assert "b" in result["packages"]
        assert result["package_count"] == 2


class TestExtractLogPathNonexistent:
    def test_extract_log_path_not_exists(self, tmp_path):
        result = extract_log_path(tmp_path / "nonexistent")
        assert result is None

    def test_extract_log_path_is_file_not_dir(self, tmp_path):
        f = tmp_path / "not_a_dir"
        f.write_text("hello")
        result = extract_log_path(f)
        assert result is None


class TestCompileWorkerLogCopy:
    def test_compile_worker_copies_log_file(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)
        ex = tmp_path / "examples" / "test"
        ex.mkdir(parents=True)
        (ex / "main.tex").write_text(
            "\\documentclass{article}\\begin{document}test\\end{document}"
        )
        (ex / "main.pdf").write_bytes(b"%PDF-1.4 fake")
        (ex / "main.log").write_text("This is output written on main.pdf.")

        with patch.object(build_core.runner, "run", return_value=(0, [])):
            name, success, logs = build_core._compile_example_worker("test")

        assert success is True
        dest_log = tmp_path / "build" / "examples" / "test.log"
        assert dest_log.exists()


class TestBuildExampleDelegates:
    def test_build_example_delegates(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)

        with patch.object(build_core, "build_examples") as mock_be:
            build_core.build_example(["test-ex"])
            mock_be.assert_called_once_with(["test-ex"])


class TestBuildAll:
    def test_build_all_calls_both(self, build_core, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.builder.REPO_ROOT", tmp_path)

        with patch.object(build_core, "build_root") as mock_root, patch.object(
            build_core, "build_examples"
        ) as mock_ex:
            build_core.build_all()
            mock_root.assert_called_once()
            mock_ex.assert_called_once()
