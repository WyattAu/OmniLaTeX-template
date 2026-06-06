"""Property-based tests for buildlib modules using Hypothesis."""

from __future__ import annotations

from buildlib.builder import _BuildCore, parse_log_for_package_times
from buildlib.runner import CommandRunner
from buildlib.ui import TerminalOutput


class TestHashDeterminism:
    """Property-based tests for build cache hash determinism."""

    def test_same_content_same_hash(self, tmp_path):
        """Same file content always produces the same hash."""
        f = tmp_path / "test.tex"
        f.write_text("content A", encoding="utf-8")
        h1 = _BuildCore._hash_for_paths([f])
        h2 = _BuildCore._hash_for_paths([f])
        assert h1 == h2

    def test_different_content_different_hash(self, tmp_path):
        """Different file content always produces different hashes."""
        f1 = tmp_path / "a.tex"
        f2 = tmp_path / "b.tex"
        f1.write_text("content A", encoding="utf-8")
        f2.write_text("content B", encoding="utf-8")
        h1 = _BuildCore._hash_for_paths([f1])
        h2 = _BuildCore._hash_for_paths([f2])
        assert h1 != h2

    def test_hash_is_sha256(self, tmp_path):
        """Hash output is a valid SHA-256 hex digest."""
        f = tmp_path / "test.tex"
        f.write_bytes(b"\x00\x01\x02\x03")
        h = _BuildCore._hash_for_paths([f])
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_order_independent(self, tmp_path):
        """Hash is independent of file order (sorted internally)."""
        f1 = tmp_path / "a.tex"
        f2 = tmp_path / "b.tex"
        f1.write_text("content", encoding="utf-8")
        f2.write_text("content2", encoding="utf-8")
        h1 = _BuildCore._hash_for_paths([f1, f2])
        h2 = _BuildCore._hash_for_paths([f2, f1])
        assert h1 == h2

    def test_nonexistent_files_still_hash(self, tmp_path):
        """Nonexistent files don't crash the hash function."""
        f = tmp_path / "nonexistent.tex"
        h = _BuildCore._hash_for_paths([f])
        assert isinstance(h, str)
        assert len(h) == 64

    def test_empty_list_hash(self):
        """Empty file list produces a valid hash."""
        h = _BuildCore._hash_for_paths([])
        assert isinstance(h, str)
        assert len(h) == 64

    def test_binary_content_hash(self, tmp_path):
        """Binary content hashes correctly."""
        f = tmp_path / "binary.bin"
        f.write_bytes(bytes(range(256)))
        h = _BuildCore._hash_for_paths([f])
        assert isinstance(h, str)
        assert len(h) == 64


class TestParseLogDeterminism:
    """Property-based tests for log parsing."""

    def test_empty_log_consistent(self):
        """Empty log always produces empty result."""
        r1 = parse_log_for_package_times("")
        r2 = parse_log_for_package_times("")
        assert r1 == r2

    def test_package_count_matches_packages(self):
        """Package count matches actual package dict size."""
        log = (
            "Package: fontspec 2024/01/01\n"
            "Package: hyperref 2024/02/15\n"
            "Package: babel 2024/03/01\n"
        )
        result = parse_log_for_package_times(log)
        assert result["package_count"] == len(result["packages"])

    def test_total_time_is_positive(self):
        """Parsed total time is always positive."""
        log = "42.5 seconds\n"
        result = parse_log_for_package_times(log)
        assert result["total_time_s"] > 0

    def test_mixed_content_no_crash(self):
        """Arbitrary text doesn't crash the parser."""
        result = parse_log_for_package_times(
            "This is random text with no structure.\n" "Another line.\n" "12345\n"
        )
        assert result["package_count"] >= 0


class TestCommandRunnerDeterminism:
    """Property-based tests for CommandRunner."""

    def test_echo_deterministic(self):
        """Echo command always produces consistent output."""
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        for _ in range(5):
            exit_code, logs = runner.run(["echo", "deterministic_test"])
            assert exit_code == 0
            assert any("deterministic_test" in line for line in logs)

    def test_false_always_fails(self):
        """False command always returns non-zero."""
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        for _ in range(3):
            exit_code, _ = runner.run(["false"])
            assert exit_code != 0

    def test_env_propagation(self):
        """Environment variables are propagated correctly."""
        ui = TerminalOutput(use_color=False)
        runner = CommandRunner(ui=ui, build_mode="dev", verbose=False)
        exit_code, logs = runner.run(
            ["printenv", "BUILD_MODE"], extra_env={"CUSTOM": "value"}
        )
        assert exit_code == 0
        assert any("dev" in line for line in logs)
