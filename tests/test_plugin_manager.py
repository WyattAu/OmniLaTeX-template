"""Unit tests for buildlib.plugin_manager module."""

from __future__ import annotations

from pathlib import Path

import pytest

from buildlib.plugin_manager import (
    ALWAYS_DENIED,
    SANDBOX_CAPABILITIES,
    PluginInfo,
    PluginManifest,
    RegistryEntry,
    ValidationResult,
    _parse_version,
    _version_satisfies,
    check_capabilities,
    check_dependencies,
    detect_conflicts,
    discover_plugins,
    get_denied_capabilities,
    load_manifest,
    load_registry,
    register_plugin,
    save_registry,
    search_plugins,
    validate_plugin,
)


# ---------------------------------------------------------------------------
# Version helpers
# ---------------------------------------------------------------------------
class TestVersionHelpers:
    def test_parse_standard(self):
        assert _parse_version("2.4.0") == (2, 4, 0)

    def test_parse_major_minor(self):
        assert _parse_version("2.4") == (2, 4, 0)

    def test_parse_major_only(self):
        assert _parse_version("3") == (3, 0, 0)

    def test_parse_invalid(self):
        with pytest.raises(ValueError, match="Invalid version"):
            _parse_version("abc")

    def test_version_gte_satisfied(self):
        assert _version_satisfies("2.5.0", ">=2.4.0") is True

    def test_version_gte_exact(self):
        assert _version_satisfies("2.4.0", ">=2.4.0") is True

    def test_version_gte_not_satisfied(self):
        assert _version_satisfies("2.3.0", ">=2.4.0") is False

    def test_version_gt_satisfied(self):
        assert _version_satisfies("2.5.0", ">2.4.0") is True

    def test_version_gt_not_satisfied(self):
        assert _version_satisfies("2.4.0", ">2.4.0") is False

    def test_version_eq(self):
        assert _version_satisfies("2.4.0", "==2.4.0") is True

    def test_version_lte(self):
        assert _version_satisfies("2.3.0", "<=2.4.0") is True

    def test_version_lt(self):
        assert _version_satisfies("2.3.0", "<2.4.0") is True

    def test_version_lt_not_satisfied(self):
        assert _version_satisfies("2.4.0", "<2.4.0") is False


# ---------------------------------------------------------------------------
# PluginManifest
# ---------------------------------------------------------------------------
class TestPluginManifest:
    def test_main_sty_default(self):
        m = PluginManifest(
            name="foo", version="1.0.0", description="d", author="a", license="MIT"
        )
        assert m.main_sty == "omnilatex-plugin-foo.sty"

    def test_main_sty_explicit(self):
        m = PluginManifest(
            name="foo",
            version="1.0.0",
            description="d",
            author="a",
            license="MIT",
            files={"main": "custom.sty"},
        )
        assert m.main_sty == "custom.sty"

    def test_security_defaults(self):
        m = PluginManifest(
            name="foo", version="1.0.0", description="d", author="a", license="MIT"
        )
        assert m.shell_escape is False
        assert m.file_write is False
        assert m.network is False

    def test_security_explicit(self):
        m = PluginManifest(
            name="foo",
            version="1.0.0",
            description="d",
            author="a",
            license="MIT",
            security={"shell_escape": True, "file_write": True, "network": False},
        )
        assert m.shell_escape is True
        assert m.file_write is True
        assert m.network is False


# ---------------------------------------------------------------------------
# Load manifest
# ---------------------------------------------------------------------------
class TestLoadManifest:
    def test_load_example_manifest(self):
        manifest_path = (
            Path(__file__).resolve().parent.parent
            / "plugins"
            / "example-plugin"
            / "manifest.toml"
        )
        if not manifest_path.exists():
            pytest.skip("example-plugin manifest not found")
        manifest = load_manifest(manifest_path)
        assert manifest.name == "example-plugin"
        assert manifest.version == "1.0.0"
        assert manifest.shell_escape is False
        assert manifest.file_write is False

    def test_load_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_manifest(Path("/nonexistent/manifest.toml"))

    def test_load_missing_plugin_section(self, tmp_path):
        manifest_file = tmp_path / "manifest.toml"
        manifest_file.write_text("[notplugin]\nname = 'x'\n")
        with pytest.raises(ValueError, match="\\[plugin\\] section"):
            load_manifest(manifest_file)

    def test_load_missing_required_fields(self, tmp_path):
        sty = tmp_path / "omnilatex-plugin-test.sty"
        sty.write_text("\\ProvidesPackage{test}\n\\endinput\n")
        manifest_file = tmp_path / "manifest.toml"
        manifest_file.write_text("[plugin]\nname = 'test'\nversion = '1.0.0'\n")
        with pytest.raises(ValueError, match="Missing required fields"):
            load_manifest(manifest_file)

    def test_load_invalid_version(self, tmp_path):
        sty = tmp_path / "omnilatex-plugin-test.sty"
        sty.write_text("\\ProvidesPackage{test}\n\\endinput\n")
        manifest_file = tmp_path / "manifest.toml"
        manifest_file.write_text(
            '[plugin]\nname = "test"\nversion = "bad"\ndescription = "d"\n'
            'author = "a"\nlicense = "MIT"\n'
        )
        with pytest.raises(ValueError, match="Invalid plugin version"):
            load_manifest(manifest_file)

    def test_load_missing_main_sty(self, tmp_path):
        manifest_file = tmp_path / "manifest.toml"
        manifest_file.write_text(
            '[plugin]\nname = "test"\nversion = "1.0.0"\ndescription = "d"\n'
            'author = "a"\nlicense = "MIT"\n'
        )
        with pytest.raises(ValueError, match="Main style file"):
            load_manifest(manifest_file)

    def test_load_network_always_denied(self, tmp_path):
        sty = tmp_path / "omnilatex-plugin-test.sty"
        sty.write_text("\\ProvidesPackage{test}\n\\endinput\n")
        manifest_file = tmp_path / "manifest.toml"
        manifest_file.write_text(
            '[plugin]\nname = "test"\nversion = "1.0.0"\ndescription = "d"\n'
            'author = "a"\nlicense = "MIT"\n'
            "[plugin.security]\nnetwork = true\n"
        )
        with pytest.raises(ValueError, match="always denied"):
            load_manifest(manifest_file)

    def test_load_security_defaults_applied(self, tmp_path):
        sty = tmp_path / "omnilatex-plugin-test.sty"
        sty.write_text("\\ProvidesPackage{test}\n\\endinput\n")
        manifest_file = tmp_path / "manifest.toml"
        manifest_file.write_text(
            '[plugin]\nname = "test"\nversion = "1.0.0"\ndescription = "d"\n'
            'author = "a"\nlicense = "MIT"\n'
        )
        manifest = load_manifest(manifest_file)
        assert manifest.security.get("shell_escape") is False
        assert manifest.security.get("file_write") is False


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
class TestRegistry:
    def test_load_registry(self):
        entries = load_registry()
        assert isinstance(entries, list)
        if entries:
            assert isinstance(entries[0], RegistryEntry)

    def test_load_nonexistent_registry(self, tmp_path):
        entries = load_registry(tmp_path / "nope.toml")
        assert entries == []

    def test_search_by_query(self):
        entries = [
            RegistryEntry(
                name="foo",
                version="1.0.0",
                description="A foo plugin",
                author="a",
                homepage="",
                license="MIT",
                omnilatex_min="2.4.0",
            ),
            RegistryEntry(
                name="bar",
                version="1.0.0",
                description="A bar plugin",
                author="a",
                homepage="",
                license="MIT",
                omnilatex_min="2.4.0",
            ),
        ]
        results = search_plugins(entries, query="foo")
        assert len(results) == 1
        assert results[0].name == "foo"

    def test_search_by_tag(self):
        entries = [
            RegistryEntry(
                name="a",
                version="1.0.0",
                description="d",
                author="a",
                homepage="",
                license="MIT",
                omnilatex_min="2.4.0",
                tags=["formatting"],
            ),
            RegistryEntry(
                name="b",
                version="1.0.0",
                description="d",
                author="a",
                homepage="",
                license="MIT",
                omnilatex_min="2.4.0",
                tags=["utility"],
            ),
        ]
        results = search_plugins(entries, tag="formatting")
        assert len(results) == 1
        assert results[0].name == "a"

    def test_search_by_status(self):
        entries = [
            RegistryEntry(
                name="a",
                version="1.0.0",
                description="d",
                author="a",
                homepage="",
                license="MIT",
                omnilatex_min="2.4.0",
                status="active",
            ),
            RegistryEntry(
                name="b",
                version="1.0.0",
                description="d",
                author="a",
                homepage="",
                license="MIT",
                omnilatex_min="2.4.0",
                status="deprecated",
            ),
        ]
        results = search_plugins(entries, status="deprecated")
        assert len(results) == 1
        assert results[0].name == "b"

    def test_register_plugin(self):
        entries: list[RegistryEntry] = []
        manifest = PluginManifest(
            name="new-plugin",
            version="1.0.0",
            description="New",
            author="Test",
            license="MIT",
            requirements={"omnilatex": ">=2.4.0"},
        )
        entries = register_plugin(entries, manifest)
        assert len(entries) == 1
        assert entries[0].name == "new-plugin"
        assert entries[0].omnilatex_min == ">=2.4.0"

    def test_register_plugin_replaces_existing(self):
        entries = [
            RegistryEntry(
                name="foo",
                version="1.0.0",
                description="old",
                author="a",
                homepage="",
                license="MIT",
                omnilatex_min="",
            )
        ]
        manifest = PluginManifest(
            name="foo",
            version="2.0.0",
            description="new",
            author="a",
            license="MIT",
        )
        entries = register_plugin(entries, manifest)
        assert len(entries) == 1
        assert entries[0].version == "2.0.0"
        assert entries[0].description == "new"

    def test_save_and_reload_registry(self, tmp_path):
        reg_path = tmp_path / "registry.toml"
        entries = [
            RegistryEntry(
                name="test-plugin",
                version="1.0.0",
                description="Test",
                author="Test Author",
                homepage="https://example.com",
                license="MIT",
                omnilatex_min=">=2.4.0",
                tags=["test"],
                status="active",
            )
        ]
        save_registry(entries, reg_path)
        assert reg_path.is_file()

        reloaded = load_registry(reg_path)
        assert len(reloaded) == 1
        assert reloaded[0].name == "test-plugin"
        assert reloaded[0].version == "1.0.0"
        assert reloaded[0].tags == ["test"]

    def test_save_multiple_entries(self, tmp_path):
        reg_path = tmp_path / "registry.toml"
        entries = [
            RegistryEntry(
                name="a",
                version="1.0.0",
                description="A",
                author="a",
                homepage="",
                license="MIT",
                omnilatex_min="",
            ),
            RegistryEntry(
                name="b",
                version="2.0.0",
                description="B",
                author="b",
                homepage="",
                license="Apache-2.0",
                omnilatex_min=">=2.5.0",
            ),
        ]
        save_registry(entries, reg_path)
        reloaded = load_registry(reg_path)
        assert len(reloaded) == 2
        names = {e.name for e in reloaded}
        assert names == {"a", "b"}


# ---------------------------------------------------------------------------
# Sandbox capability checking
# ---------------------------------------------------------------------------
class TestSandboxCapabilities:
    def test_all_denied_by_default(self):
        m = PluginManifest(
            name="x", version="1.0.0", description="d", author="a", license="MIT"
        )
        caps = check_capabilities(m)
        assert caps["shell_escape"] is False
        assert caps["file_write"] is False
        assert caps["network"] is False
        assert caps["env_vars"] is False
        assert caps["process_execution"] is False

    def test_shell_escape_granted_when_allowed(self):
        m = PluginManifest(
            name="x",
            version="1.0.0",
            description="d",
            author="a",
            license="MIT",
            security={"shell_escape": True},
        )
        caps = check_capabilities(m, allowed_shell_escape=True)
        assert caps["shell_escape"] is True

    def test_shell_escape_denied_when_not_allowed(self):
        m = PluginManifest(
            name="x",
            version="1.0.0",
            description="d",
            author="a",
            license="MIT",
            security={"shell_escape": True},
        )
        caps = check_capabilities(m, allowed_shell_escape=False)
        assert caps["shell_escape"] is False

    def test_file_write_granted_when_allowed(self):
        m = PluginManifest(
            name="x",
            version="1.0.0",
            description="d",
            author="a",
            license="MIT",
            security={"file_write": True},
        )
        caps = check_capabilities(m, allowed_file_write=True)
        assert caps["file_write"] is True

    def test_network_always_denied(self):
        m = PluginManifest(
            name="x",
            version="1.0.0",
            description="d",
            author="a",
            license="MIT",
            security={"network": True},
        )
        caps = check_capabilities(m)
        assert caps["network"] is False

    def test_denied_capabilities_list(self):
        m = PluginManifest(
            name="x",
            version="1.0.0",
            description="d",
            author="a",
            license="MIT",
            security={"shell_escape": True, "file_write": True},
        )
        denied = get_denied_capabilities(m)
        assert "shell_escape" in denied
        assert "file_write" in denied

    def test_no_denied_when_allowed(self):
        m = PluginManifest(
            name="x",
            version="1.0.0",
            description="d",
            author="a",
            license="MIT",
            security={"shell_escape": True, "file_write": True},
        )
        denied = get_denied_capabilities(
            m, allowed_shell_escape=True, allowed_file_write=True
        )
        assert denied == []


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------
class TestConflictDetection:
    def _make_info(
        self, name: str, conflicts: dict[str, str] | None = None
    ) -> PluginInfo:
        m = PluginManifest(
            name=name,
            version="1.0.0",
            description="d",
            author="a",
            license="MIT",
            conflicts=conflicts or {},
        )
        return PluginInfo(manifest=m, path=Path(f"/tmp/{name}"))

    def test_no_conflicts(self):
        a = self._make_info("a")
        b = self._make_info("b")
        conflicts = detect_conflicts([a, b])
        assert conflicts == []

    def test_explicit_conflict(self):
        a = self._make_info("a", conflicts={"b": "*"})
        b = self._make_info("b")
        conflicts = detect_conflicts([a, b])
        assert len(conflicts) == 1
        assert (
            "a" in conflicts[0][0].manifest.name or "a" in conflicts[0][1].manifest.name
        )

    def test_versioned_conflict(self):
        a = self._make_info("a", conflicts={"b": ">=2.0.0"})
        b = self._make_info("b")
        b.manifest.version = "1.5.0"
        conflicts = detect_conflicts([a, b])
        assert conflicts == []

    def test_self_not_conflicting(self):
        a = self._make_info("a", conflicts={"b": "*"})
        conflicts = detect_conflicts([a])
        assert conflicts == []


# ---------------------------------------------------------------------------
# Dependency checking
# ---------------------------------------------------------------------------
class TestDependencyChecking:
    def test_all_deps_met(self):
        m = PluginManifest(
            name="a",
            version="1.0.0",
            description="d",
            author="a",
            license="MIT",
            dependencies={"b": ">=1.0.0"},
        )
        info = PluginInfo(manifest=m, path=Path("/tmp/a"))
        b = PluginManifest(
            name="b", version="1.2.0", description="d", author="a", license="MIT"
        )
        available = {"b": PluginInfo(manifest=b, path=Path("/tmp/b"))}
        unmet = check_dependencies(info, available)
        assert unmet == []

    def test_missing_dep(self):
        m = PluginManifest(
            name="a",
            version="1.0.0",
            description="d",
            author="a",
            license="MIT",
            dependencies={"missing": ">=1.0.0"},
        )
        info = PluginInfo(manifest=m, path=Path("/tmp/a"))
        unmet = check_dependencies(info, {})
        assert len(unmet) == 1
        assert "Missing dependency" in unmet[0]

    def test_version_not_satisfied(self):
        m = PluginManifest(
            name="a",
            version="1.0.0",
            description="d",
            author="a",
            license="MIT",
            dependencies={"b": ">=2.0.0"},
        )
        info = PluginInfo(manifest=m, path=Path("/tmp/a"))
        b = PluginManifest(
            name="b", version="1.5.0", description="d", author="a", license="MIT"
        )
        available = {"b": PluginInfo(manifest=b, path=Path("/tmp/b"))}
        unmet = check_dependencies(info, available)
        assert len(unmet) == 1
        assert "does not satisfy" in unmet[0]


# ---------------------------------------------------------------------------
# Plugin discovery
# ---------------------------------------------------------------------------
class TestPluginDiscovery:
    def test_discover_example_plugin(self):
        plugins = discover_plugins()
        names = {p.manifest.name for p in plugins}
        if (
            Path(__file__).resolve().parent.parent / "plugins" / "example-plugin"
        ).is_dir():
            assert "example-plugin" in names

    def test_discover_empty_dir(self, tmp_path):
        plugins = discover_plugins(tmp_path)
        assert plugins == []

    def test_discover_nonexistent_dir(self, tmp_path):
        plugins = discover_plugins(tmp_path / "nonexistent")
        assert plugins == []


# ---------------------------------------------------------------------------
# Full validation pipeline
# ---------------------------------------------------------------------------
class TestValidationPipeline:
    def test_validate_example_plugin(self):
        manifest_path = (
            Path(__file__).resolve().parent.parent
            / "plugins"
            / "example-plugin"
            / "manifest.toml"
        )
        if not manifest_path.exists():
            pytest.skip("example-plugin manifest not found")
        result = validate_plugin(manifest_path)
        assert result.valid is True
        assert result.manifest is not None
        assert result.manifest.name == "example-plugin"

    def test_validate_missing_manifest(self, tmp_path):
        result = validate_plugin(tmp_path / "nope.toml")
        assert result.valid is False
        assert len(result.errors) > 0

    def test_validate_warns_on_denied_caps(self, tmp_path):
        sty = tmp_path / "omnilatex-plugin-test.sty"
        sty.write_text("\\ProvidesPackage{test}\n\\endinput\n")
        manifest_file = tmp_path / "manifest.toml"
        manifest_file.write_text(
            '[plugin]\nname = "test"\nversion = "1.0.0"\ndescription = "d"\n'
            'author = "a"\nlicense = "MIT"\n'
            "[plugin.security]\nshell_escape = true\n"
        )
        result = validate_plugin(manifest_file)
        assert result.valid is True
        assert len(result.warnings) > 0
        assert "shell_escape" in result.warnings[0]


# ---------------------------------------------------------------------------
# Data class constants
# ---------------------------------------------------------------------------
class TestConstants:
    def test_always_denied(self):
        assert "network" in ALWAYS_DENIED

    def test_sandbox_capabilities(self):
        assert "shell_escape" in SANDBOX_CAPABILITIES
        assert "file_write" in SANDBOX_CAPABILITIES
        assert "network" in SANDBOX_CAPABILITIES
