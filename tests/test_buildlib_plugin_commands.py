"""Unit tests for buildlib.commands.plugin module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from buildlib.commands.plugin import PluginMixin
from buildlib.config import ProjectConfig
from buildlib.ui import TerminalOutput


@pytest.fixture
def plugin_cmd():
    ui = TerminalOutput(use_color=False)
    obj = object.__new__(PluginMixin)
    obj.ui = ui
    obj.runner = MagicMock()
    obj.config = ProjectConfig()
    return obj


@pytest.fixture
def tmp_plugins(tmp_path):
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    return plugins_dir


class TestCmdPluginList:
    def test_empty_plugins(self, plugin_cmd):
        with patch("buildlib.commands.plugin.discover_plugins", return_value=[]):
            plugin_cmd.cmd_plugin_list()

    def test_with_plugins(self, plugin_cmd):
        fake_manifests = [
            {
                "plugin": {
                    "name": "test-plugin",
                    "version": "1.0.0",
                    "description": "A test",
                }
            }
        ]
        with patch(
            "buildlib.commands.plugin.discover_plugins", return_value=fake_manifests
        ):
            plugin_cmd.cmd_plugin_list()

    def test_multiple_plugins(self, plugin_cmd):
        fake_manifests = [
            {"plugin": {"name": "a", "version": "1.0.0", "description": "A"}},
            {"plugin": {"name": "b", "version": "2.0.0", "description": "B"}},
        ]
        with patch(
            "buildlib.commands.plugin.discover_plugins", return_value=fake_manifests
        ):
            plugin_cmd.cmd_plugin_list()

    def test_missing_version_field(self, plugin_cmd):
        fake_manifests = [{"plugin": {"name": "incomplete"}}]
        with patch(
            "buildlib.commands.plugin.discover_plugins", return_value=fake_manifests
        ):
            plugin_cmd.cmd_plugin_list()


class TestCmdPluginSearch:
    def test_empty_results(self, plugin_cmd):
        with patch("buildlib.commands.plugin.search_remote_plugins", return_value=[]):
            plugin_cmd.cmd_plugin_search(query="nonexistent")

    def test_with_results(self, plugin_cmd):
        fake_entries = [
            {
                "name": "found",
                "version": "1.0.0",
                "description": "Found it",
                "status": "active",
            }
        ]
        with patch(
            "buildlib.commands.plugin.search_remote_plugins", return_value=fake_entries
        ):
            plugin_cmd.cmd_plugin_search(query="found")

    def test_empty_query(self, plugin_cmd):
        with patch("buildlib.commands.plugin.search_remote_plugins", return_value=[]):
            plugin_cmd.cmd_plugin_search(query="")


class TestCmdPluginInstall:
    def test_no_name_shows_error(self, plugin_cmd):
        plugin_cmd.cmd_plugin_install(name="")

    def test_already_installed(self, plugin_cmd, tmp_plugins):
        target = tmp_plugins / "existing"
        target.mkdir()
        with (patch("buildlib.commands.plugin._cfg") as mock_cfg,):
            mock_cfg.REPO_ROOT = tmp_plugins.parent
            plugin_cmd.cmd_plugin_install(name="existing")

    def test_not_in_registry(self, plugin_cmd, tmp_plugins):
        with (
            patch("buildlib.commands.plugin._cfg") as mock_cfg,
            patch("buildlib.commands.plugin.load_registry", return_value=None),
        ):
            mock_cfg.REPO_ROOT = tmp_plugins.parent
            plugin_cmd.cmd_plugin_install(name="nonexistent")

    def test_not_in_registry_entries(self, plugin_cmd, tmp_plugins):
        registry = {"plugin": [{"name": "other-plugin", "version": "1.0.0"}]}
        with (
            patch("buildlib.commands.plugin._cfg") as mock_cfg,
            patch("buildlib.commands.plugin.load_registry", return_value=registry),
        ):
            mock_cfg.REPO_ROOT = tmp_plugins.parent
            plugin_cmd.cmd_plugin_install(name="missing")

    def test_successful_install(self, plugin_cmd, tmp_plugins):
        registry = {
            "plugin": [
                {
                    "name": "new-plugin",
                    "version": "1.0.0",
                    "description": "New",
                    "author": "Test",
                    "license": "MIT",
                }
            ]
        }
        with (
            patch("buildlib.commands.plugin._cfg") as mock_cfg,
            patch("buildlib.commands.plugin.load_registry", return_value=registry),
            patch(
                "buildlib.commands.plugin.load_manifest",
                return_value={"plugin": {"name": "new-plugin"}},
            ),
        ):
            mock_cfg.REPO_ROOT = tmp_plugins.parent
            plugin_cmd.cmd_plugin_install(name="new-plugin")
            assert (tmp_plugins / "new-plugin" / "manifest.toml").exists()


class TestCmdPluginRemove:
    def test_no_name_shows_error(self, plugin_cmd):
        plugin_cmd.cmd_plugin_remove(name="")

    def test_not_found(self, plugin_cmd, tmp_plugins):
        with (patch("buildlib.commands.plugin._cfg") as mock_cfg,):
            mock_cfg.REPO_ROOT = tmp_plugins.parent
            plugin_cmd.cmd_plugin_remove(name="nonexistent")

    def test_has_dependents(self, plugin_cmd, tmp_plugins):
        target = tmp_plugins / "target"
        target.mkdir()
        dependent_manifest = {
            "plugin": {
                "name": "dependent",
                "version": "1.0.0",
                "dependencies": {"target": "*"},
            }
        }
        with (
            patch("buildlib.commands.plugin._cfg") as mock_cfg,
            patch(
                "buildlib.commands.plugin.discover_plugins",
                return_value=[dependent_manifest],
            ),
        ):
            mock_cfg.REPO_ROOT = tmp_plugins.parent
            plugin_cmd.cmd_plugin_remove(name="target")
            assert target.exists()  # not removed

    def test_successful_remove(self, plugin_cmd, tmp_plugins):
        target = tmp_plugins / "target"
        target.mkdir()
        (target / "manifest.toml").touch()
        with (
            patch("buildlib.commands.plugin._cfg") as mock_cfg,
            patch("buildlib.commands.plugin.discover_plugins", return_value=[]),
        ):
            mock_cfg.REPO_ROOT = tmp_plugins.parent
            plugin_cmd.cmd_plugin_remove(name="target")
            assert not target.exists()


class TestCmdPluginValidate:
    def test_no_plugins(self, plugin_cmd):
        with patch("buildlib.commands.plugin.discover_plugins", return_value=[]):
            plugin_cmd.cmd_plugin_validate()

    def test_all_valid(self, plugin_cmd):
        manifest = {"plugin": {"name": "valid", "version": "1.0.0"}}
        with (
            patch("buildlib.commands.plugin.discover_plugins", return_value=[manifest]),
            patch("buildlib.commands.plugin.validate_plugin", return_value=(True, [])),
        ):
            plugin_cmd.cmd_plugin_validate()

    def test_some_invalid(self, plugin_cmd):
        manifest = {"plugin": {"name": "bad", "version": "1.0.0"}}
        with (
            patch("buildlib.commands.plugin.discover_plugins", return_value=[manifest]),
            patch(
                "buildlib.commands.plugin.validate_plugin",
                return_value=(False, ["missing key"]),
            ),
        ):
            plugin_cmd.cmd_plugin_validate()

    def test_mixed_valid_invalid(self, plugin_cmd):
        m1 = {"plugin": {"name": "good", "version": "1.0.0"}}
        m2 = {"plugin": {"name": "bad", "version": "1.0.0"}}
        with (
            patch("buildlib.commands.plugin.discover_plugins", return_value=[m1, m2]),
            patch(
                "buildlib.commands.plugin.validate_plugin",
                side_effect=lambda m: (True, []) if m == m1 else (False, ["issue"]),
            ),
        ):
            plugin_cmd.cmd_plugin_validate()


class TestCmdPluginInfo:
    def test_no_name_shows_error(self, plugin_cmd):
        plugin_cmd.cmd_plugin_info(name="")

    def test_plugin_not_found(self, plugin_cmd):
        with patch("buildlib.commands.plugin._cfg") as mock_cfg:
            mock_cfg.REPO_ROOT = Path("/nonexistent")
            plugin_cmd.cmd_plugin_info(name="nonexistent")

    def test_plugin_found(self, plugin_cmd, tmp_plugins):
        pdir = tmp_plugins / "my-plugin"
        pdir.mkdir()
        fake_manifest = {
            "plugin": {
                "name": "my-plugin",
                "version": "1.0.0",
                "description": "Test",
                "author": "Test",
                "license": "MIT",
            }
        }
        with (
            patch("buildlib.commands.plugin._cfg") as mock_cfg,
            patch("buildlib.commands.plugin.load_manifest", return_value=fake_manifest),
        ):
            mock_cfg.REPO_ROOT = tmp_plugins.parent
            plugin_cmd.cmd_plugin_info(name="my-plugin")

    def test_plugin_with_security_section(self, plugin_cmd, tmp_plugins):
        pdir = tmp_plugins / "secure-plugin"
        pdir.mkdir()
        fake_manifest = {
            "plugin": {
                "name": "secure-plugin",
                "version": "1.0.0",
                "description": "Secure",
                "author": "Test",
                "license": "MIT",
                "security": {"shell_escape": False, "network": False},
            }
        }
        with (
            patch("buildlib.commands.plugin._cfg") as mock_cfg,
            patch("buildlib.commands.plugin.load_manifest", return_value=fake_manifest),
        ):
            mock_cfg.REPO_ROOT = tmp_plugins.parent
            plugin_cmd.cmd_plugin_info(name="secure-plugin")

    def test_plugin_with_requirements(self, plugin_cmd, tmp_plugins):
        pdir = tmp_plugins / "req-plugin"
        pdir.mkdir()
        fake_manifest = {
            "plugin": {
                "name": "req-plugin",
                "version": "1.0.0",
                "description": "Req",
                "author": "Test",
                "license": "MIT",
                "requirements": {"lualatex": "true"},
            }
        }
        with (
            patch("buildlib.commands.plugin._cfg") as mock_cfg,
            patch("buildlib.commands.plugin.load_manifest", return_value=fake_manifest),
        ):
            mock_cfg.REPO_ROOT = tmp_plugins.parent
            plugin_cmd.cmd_plugin_info(name="req-plugin")

    def test_plugin_with_dependencies(self, plugin_cmd, tmp_plugins):
        pdir = tmp_plugins / "dep-plugin"
        pdir.mkdir()
        fake_manifest = {
            "plugin": {
                "name": "dep-plugin",
                "version": "1.0.0",
                "description": "Dep",
                "author": "Test",
                "license": "MIT",
                "dependencies": {"base": ">=1.0.0"},
            }
        }
        with (
            patch("buildlib.commands.plugin._cfg") as mock_cfg,
            patch("buildlib.commands.plugin.load_manifest", return_value=fake_manifest),
        ):
            mock_cfg.REPO_ROOT = tmp_plugins.parent
            plugin_cmd.cmd_plugin_info(name="dep-plugin")

    def test_plugin_invalid_manifest(self, plugin_cmd, tmp_plugins):
        pdir = tmp_plugins / "bad-plugin"
        pdir.mkdir()
        (pdir / "manifest.toml").write_text("x", encoding="utf-8")
        with (
            patch("buildlib.commands.plugin._cfg") as mock_cfg,
            patch("buildlib.commands.plugin.load_manifest", return_value=None),
        ):
            mock_cfg.REPO_ROOT = tmp_plugins.parent
            plugin_cmd.cmd_plugin_info(name="bad-plugin")
