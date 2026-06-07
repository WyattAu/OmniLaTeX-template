"""Tests for buildlib/commands/preflight_test.py mixin.

The PreflightTestMixin is tested directly by constructing a minimal object.
"""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from buildlib.commands.preflight_test import PreflightTestMixin


class _Stub(PreflightTestMixin):
    """Minimal object inheriting PreflightTestMixin for testing."""

    def __init__(self):
        self.ui = MagicMock()
        self.runner = MagicMock()


@pytest.fixture
def stub():
    return _Stub()


class TestCheckTool:
    def test_tool_found(self, stub, monkeypatch):
        monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/" + name)
        name, ok, detail = stub._check_tool("lualatex", "LuaTeX engine")
        assert ok is True
        assert "Found at" in detail

    def test_tool_missing_required(self, stub, monkeypatch):
        monkeypatch.setattr("shutil.which", lambda name: None)
        name, ok, detail = stub._check_tool("lualatex", "LuaTeX engine", required=True)
        assert ok is False
        assert "NOT FOUND" in detail

    def test_tool_missing_optional(self, stub, monkeypatch):
        monkeypatch.setattr("shutil.which", lambda name: None)
        name, ok, detail = stub._check_tool("inkscape", "Inkscape", required=False)
        assert ok is True
        assert "optional" in detail


class TestGetTexliveVersion:
    def test_version_parsed(self, stub):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                stdout="LuaHBTeX 1.18.0 (TeX Live 2025)\n",
                returncode=0,
            )
            result = stub._get_texlive_version()
            assert result == 2025

    def test_no_version(self, stub):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="unknown", returncode=0)
            result = stub._get_texlive_version()
            assert result is None

    def test_subprocess_error(self, stub):
        with patch("subprocess.run", side_effect=subprocess.SubprocessError):
            result = stub._get_texlive_version()
            assert result is None

    def test_os_error(self, stub):
        with patch("subprocess.run", side_effect=OSError):
            result = stub._get_texlive_version()
            assert result is None


class TestCheckLatexPackage:
    def test_package_found(self, stub):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert stub._check_latex_package("fontspec") is True

    def test_package_not_found(self, stub):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            assert stub._check_latex_package("nonexistent") is False

    def test_subprocess_error(self, stub):
        with patch("subprocess.run", side_effect=subprocess.SubprocessError):
            assert stub._check_latex_package("fontspec") is False

    def test_os_error(self, stub):
        with patch("subprocess.run", side_effect=OSError):
            assert stub._check_latex_package("fontspec") is False


class TestCheckAllLatexPackages:
    def test_delegates_per_package(self, stub):
        with patch.object(stub, "_check_latex_package", return_value=True):
            result = stub._check_all_latex_packages(["fontspec", "biblatex"])
            assert result == {"fontspec": True, "biblatex": True}


class TestCmdPreflight:
    _REQUIRED_PACKAGES = [
        "fontspec",
        "unicode-math",
        "hyperref",
        "minted",
        "biblatex",
        "siunitx",
        "circuitikz",
        "forest",
    ]

    def test_all_pass(self, stub, monkeypatch):
        monkeypatch.setattr("shutil.which", lambda name: "/usr/bin/" + name)
        monkeypatch.setattr("sys.version_info", (3, 12, 0))
        with patch.object(
            stub, "_get_texlive_version", return_value=2025
        ), patch.object(
            stub,
            "_check_all_latex_packages",
            return_value={p: True for p in self._REQUIRED_PACKAGES},
        ):
            stub.cmd_preflight()
            stub.ui.success.assert_called()

    def test_some_fail(self, stub, monkeypatch):
        monkeypatch.setattr("shutil.which", lambda name: None)
        monkeypatch.setattr("sys.version_info", (3, 9, 0))
        with patch.object(
            stub, "_get_texlive_version", return_value=None
        ), patch.object(
            stub,
            "_check_all_latex_packages",
            return_value={p: False for p in self._REQUIRED_PACKAGES},
        ):
            stub.cmd_preflight()
            stub.ui.warning.assert_called()


class TestCmdTest:
    def test_both_pass(self, stub):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
            result = stub.cmd_test()
            assert result == 0
            stub.ui.success.assert_called()

    def test_l3build_fails(self, stub):
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return MagicMock(returncode=1, stdout="FAIL", stderr="err")
            return MagicMock(returncode=0, stdout="", stderr="")

        with patch("subprocess.run", side_effect=side_effect):
            result = stub.cmd_test()
            assert result == 1  # l3build failed -> overall failure

    def test_pytest_fails(self, stub):
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return MagicMock(returncode=0, stdout="", stderr="")
            return MagicMock(returncode=1, stdout="FAIL", stderr="")

        with patch("subprocess.run", side_effect=side_effect):
            result = stub.cmd_test()
            assert result == 1
