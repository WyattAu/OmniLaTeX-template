"""Tests for buildlib/commands/plugin.py mixin."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from buildlib.commands.plugin import PluginMixin


class _Stub(PluginMixin):
    def __init__(self):
        self.ui = MagicMock()
        self.runner = MagicMock()
        self.config = MagicMock()


@pytest.fixture
def stub():
    return _Stub()


class TestPluginList:
    def test_no_plugins(self, stub, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.commands.plugin._cfg", MagicMock(REPO_ROOT=tmp_path))
        with patch("buildlib.commands.plugin.discover_plugins", return_value=[]):
            stub.cmd_plugin_list()
            stub.ui.info.assert_called()

    def test_with_plugins(self, stub, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.commands.plugin._cfg", MagicMock(REPO_ROOT=tmp_path))
        manifest = {"plugin": {"name": "test", "version": "1.0.0", "description": "Test"}}
        with patch("buildlib.commands.plugin.discover_plugins", return_value=[manifest]):
            stub.cmd_plugin_list()
            stub.ui.success.assert_called()


class TestPluginSearch:
    def test_search_empty(self, stub):
        with patch("buildlib.commands.plugin.search_remote_plugins", return_value=[]):
            stub.cmd_plugin_search(query="nonexistent")
            stub.ui.info.assert_called()

    def test_search_results(self, stub):
        entries = [{"name": "test", "version": "1.0.0", "description": "Test", "status": "active"}]
        with patch("buildlib.commands.plugin.search_remote_plugins", return_value=entries):
            stub.cmd_plugin_search(query="test")
            stub.ui.success.assert_called()


class TestPluginInstall:
    def test_no_name(self, stub):
        stub.cmd_plugin_install(name="")
        stub.ui.error.assert_called()

    def test_already_installed(self, stub, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.commands.plugin._cfg", MagicMock(REPO_ROOT=tmp_path))
        (tmp_path / "plugins" / "test").mkdir(parents=True)
        stub.cmd_plugin_install(name="test")
        stub.ui.warning.assert_called()

    def test_not_in_registry(self, stub, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.commands.plugin._cfg", MagicMock(REPO_ROOT=tmp_path))
        with patch("buildlib.commands.plugin.load_registry", return_value={}):
            stub.cmd_plugin_install(name="nonexistent")
            stub.ui.error.assert_called()

    def test_install_success(self, stub, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.commands.plugin._cfg", MagicMock(REPO_ROOT=tmp_path))
        registry = {"plugin": [{"name": "test", "version": "1.0.0", "description": "Test", "author": "A", "license": "MIT"}]}
        with patch("buildlib.commands.plugin.load_registry", return_value=registry), \
             patch("buildlib.commands.plugin.load_manifest", return_value={"plugin": {"name": "test"}}):
            stub.cmd_plugin_install(name="test")
            stub.ui.success.assert_called()
            assert (tmp_path / "plugins" / "test" / "manifest.toml").exists()


class TestPluginRemove:
    def test_no_name(self, stub):
        stub.cmd_plugin_remove(name="")
        stub.ui.error.assert_called()

    def test_not_found(self, stub, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.commands.plugin._cfg", MagicMock(REPO_ROOT=tmp_path))
        stub.cmd_plugin_remove(name="nonexistent")
        stub.ui.error.assert_called()

    def test_has_dependents(self, stub, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.commands.plugin._cfg", MagicMock(REPO_ROOT=tmp_path))
        (tmp_path / "plugins" / "dep").mkdir(parents=True)
        dep_manifest = {"plugin": {"name": "dep", "dependencies": {"dep": ">=1.0"}}}
        with patch("buildlib.commands.plugin.discover_plugins", return_value=[dep_manifest]):
            stub.cmd_plugin_remove(name="dep")
            stub.ui.error.assert_called()

    def test_remove_success(self, stub, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.commands.plugin._cfg", MagicMock(REPO_ROOT=tmp_path))
        (tmp_path / "plugins" / "test").mkdir(parents=True)
        with patch("buildlib.commands.plugin.discover_plugins", return_value=[]):
            stub.cmd_plugin_remove(name="test")
            stub.ui.success.assert_called()
            assert not (tmp_path / "plugins" / "test").exists()


class TestPluginValidate:
    def test_no_plugins(self, stub):
        with patch("buildlib.commands.plugin.discover_plugins", return_value=[]):
            stub.cmd_plugin_validate()
            stub.ui.info.assert_called()

    def test_all_valid(self, stub):
        manifest = {"plugin": {"name": "test"}}
        with patch("buildlib.commands.plugin.discover_plugins", return_value=[manifest]), \
             patch("buildlib.commands.plugin.validate_plugin", return_value=(True, [])):
            stub.cmd_plugin_validate()
            stub.ui.success.assert_called()

    def test_some_invalid(self, stub):
        manifest = {"plugin": {"name": "test"}}
        with patch("buildlib.commands.plugin.discover_plugins", return_value=[manifest]), \
             patch("buildlib.commands.plugin.validate_plugin", return_value=(False, ["error"])):
            stub.cmd_plugin_validate()
            stub.ui.warning.assert_called()


class TestPluginInfo:
    def test_no_name(self, stub):
        stub.cmd_plugin_info(name="")
        stub.ui.error.assert_called()

    def test_not_found(self, stub, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.commands.plugin._cfg", MagicMock(REPO_ROOT=tmp_path))
        stub.cmd_plugin_info(name="nonexistent")
        stub.ui.error.assert_called()

    def test_info_display(self, stub, tmp_path, monkeypatch):
        monkeypatch.setattr("buildlib.commands.plugin._cfg", MagicMock(REPO_ROOT=tmp_path))
        plugin_dir = tmp_path / "plugins" / "test"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "manifest.toml").write_text(
            '[plugin]\nname="test"\nversion="1.0.0"\ndescription="Test"\nauthor="A"\nlicense="MIT"\n'
        )
        manifest = {"plugin": {"name": "test", "version": "1.0.0", "description": "Test", "author": "A", "license": "MIT", "security": {"network": False}}}
        with patch("buildlib.commands.plugin.load_manifest", return_value=manifest):
            stub.cmd_plugin_info(name="test")
            stub.ui.info.assert_called()
