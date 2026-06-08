"""Plugin management commands mixin.

Provides commands for listing, searching, installing, removing,
validating, and inspecting OmniLaTeX plugins.
"""

from __future__ import annotations

import shutil

import buildlib.config as _cfg
from buildlib.plugin_manager import (
    discover_plugins,
    load_manifest,
    load_registry,
    search_plugins,
    validate_plugin,
)


class PluginMixin:
    """Mixin providing plugin management commands.

    Requires self.ui, self.runner, self.config to be set by the inheriting class.
    """

    def cmd_plugin_list(self, files: list[str] | None = None) -> None:
        """List installed plugins."""
        self.ui.header("Installed Plugins")
        plugins = discover_plugins()

        if not plugins:
            self.ui.info("No plugins installed.")
            self.ui.info("Place plugins in plugins/<name>/ with a manifest.toml file.")
            return

        for manifest in plugins:
            name = manifest.get("plugin", {}).get("name", "unknown")
            version = manifest.get("plugin", {}).get("version", "0.0.0")
            desc = manifest.get("plugin", {}).get("description", "")
            self.ui.info(f"  {name} v{version} - {desc}")

        self.ui.success(f"{len(plugins)} plugin(s) installed.")

    def cmd_plugin_search(
        self, files: list[str] | None = None, query: str = ""
    ) -> None:
        """Search the plugin registry."""
        self.ui.header("Plugin Registry Search")

        registry = load_registry()
        if not registry:
            self.ui.info("No plugins in registry.")
            return

        entries = registry.get("plugin", [])
        if query:
            entries = search_plugins(query)

        if not entries:
            self.ui.info(f"No plugins matching '{query}'.")
            return

        for entry in entries:
            name = entry.get("name", "unknown")
            version = entry.get("version", "0.0.0")
            desc = entry.get("description", "")
            status = entry.get("status", "unknown")
            self.ui.info(f"  {name} v{version} [{status}] - {desc}")

        self.ui.success(f"{len(entries)} plugin(s) found.")

    def cmd_plugin_install(
        self, files: list[str] | None = None, name: str = ""
    ) -> None:
        """Install a plugin from the registry."""
        if not name:
            self.ui.error("Usage: build.py plugin-install <name>")
            return

        self.ui.header(f"Installing Plugin: {name}")

        plugins_dir = _cfg.REPO_ROOT / "plugins"
        target_dir = plugins_dir / name

        if target_dir.exists():
            self.ui.warning(f"Plugin '{name}' already installed at {target_dir}")
            return

        # Check registry for the plugin
        registry = load_registry()
        entries = registry.get("plugin", []) if registry else []
        entry = None
        for e in entries:
            if e.get("name") == name:
                entry = e
                break

        if not entry:
            self.ui.error(f"Plugin '{name}' not found in registry.")
            return

        # Create plugin directory with basic manifest
        target_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = target_dir / "manifest.toml"

        manifest_content = f"""[plugin]
name = "{entry.get('name', name)}"
version = "{entry.get('version', '1.0.0')}"
description = "{entry.get('description', '')}"
author = "{entry.get('author', 'unknown')}"
license = "{entry.get('license', 'MIT')}"

[plugin.security]
shell_escape = false
file_write = false
network = false
"""
        manifest_path.write_text(manifest_content, encoding="utf-8")

        # Create placeholder .sty file
        sty_path = target_dir / f"omnilatex-plugin-{name}.sty"
        sty_content = f"""% OmniLaTeX Plugin: {name}
% Version: {entry.get('version', '1.0.0')}
% Description: {entry.get('description', '')}
%
% Place your plugin code here.

\\NeedsTeXFormat{{LaTeX2e}}
\\ProvidesPackage{{omnilatex-plugin-{name}}}"""
        f"""[{entry.get('version', '1.0.0')}"""
        f""" {entry.get('description', '')}]\n"""
        sty_path.write_text(sty_content, encoding="utf-8")

        # Validate the installed plugin
        manifest = load_manifest(manifest_path)
        if manifest:
            self.ui.success(f"Plugin '{name}' installed to {target_dir}")
        else:
            self.ui.warning(f"Plugin '{name}' installed but validation failed")

    def cmd_plugin_remove(self, files: list[str] | None = None, name: str = "") -> None:
        """Remove an installed plugin."""
        if not name:
            self.ui.error("Usage: build.py plugin-remove <name>")
            return

        self.ui.header(f"Removing Plugin: {name}")

        plugins_dir = _cfg.REPO_ROOT / "plugins"
        target_dir = plugins_dir / name

        if not target_dir.exists():
            self.ui.error(f"Plugin '{name}' not found at {target_dir}")
            return

        # Check for dependents
        all_plugins = discover_plugins()
        for manifest in all_plugins:
            deps = manifest.get("plugin", {}).get("dependencies", {})
            if name in deps:
                dep_name = manifest.get("plugin", {}).get("name", "unknown")
                self.ui.error(
                    f"Cannot remove '{name}': plugin '{dep_name}' depends on it"
                )
                return

        shutil.rmtree(target_dir)
        self.ui.success(f"Plugin '{name}' removed.")

    def cmd_plugin_validate(self, files: list[str] | None = None) -> None:
        """Validate plugin manifests."""
        self.ui.header("Plugin Validation")

        plugins = discover_plugins()
        if not plugins:
            self.ui.info("No plugins to validate.")
            return

        all_valid = True
        for manifest in plugins:
            name = manifest.get("plugin", {}).get("name", "unknown")
            is_valid, issues = validate_plugin(manifest)
            if is_valid:
                self.ui.info(f"  PASS: {name}")
            else:
                all_valid = False
                for issue in issues:
                    self.ui.warning(f"  FAIL: {name}: {issue}")

        if all_valid:
            self.ui.success("All plugins valid.")
        else:
            self.ui.warning("Some plugins have validation issues.")

    def cmd_plugin_info(self, files: list[str] | None = None, name: str = "") -> None:
        """Show detailed information about a plugin."""
        if not name:
            self.ui.error("Usage: build.py plugin-info <name>")
            return

        self.ui.header(f"Plugin Info: {name}")

        plugins_dir = _cfg.REPO_ROOT / "plugins" / name
        manifest_path = plugins_dir / "manifest.toml"

        if not manifest_path.exists():
            self.ui.error(f"Plugin '{name}' not found.")
            return

        manifest = load_manifest(manifest_path)
        if not manifest:
            self.ui.error(f"Failed to load manifest for '{name}'.")
            return

        plugin = manifest.get("plugin", {})
        self.ui.info(f"  Name:        {plugin.get('name', 'unknown')}")
        self.ui.info(f"  Version:     {plugin.get('version', '0.0.0')}")
        self.ui.info(f"  Description: {plugin.get('description', '')}")
        self.ui.info(f"  Author:      {plugin.get('author', 'unknown')}")
        self.ui.info(f"  License:     {plugin.get('license', 'unknown')}")
        self.ui.info(f"  Path:        {plugins_dir}")

        security = plugin.get("security", {})
        if security:
            self.ui.info("  Security:")
            for key, val in security.items():
                self.ui.info(f"    {key}: {val}")

        reqs = plugin.get("requirements", {})
        if reqs:
            self.ui.info("  Requirements:")
            for key, val in reqs.items():
                self.ui.info(f"    {key}: {val}")

        deps = plugin.get("dependencies", {})
        if deps:
            self.ui.info("  Dependencies:")
            for key, val in deps.items():
                self.ui.info(f"    {key}: {val}")
