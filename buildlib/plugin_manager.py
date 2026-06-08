"""OmniLaTeX plugin registry, validation, and sandbox enforcement."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from buildlib.config import REPO_ROOT

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PLUGINS_DIR = REPO_ROOT / "plugins"
REGISTRY_PATH = PLUGINS_DIR / "registry.toml"

SANDBOX_CAPABILITIES = frozenset({"shell_escape", "file_write", "network"})
ALWAYS_DENIED = frozenset({"network"})
REQUIRED_MANIFEST_SECTIONS = {"plugin"}
REQUIRED_PLUGIN_FIELDS = {"name", "version", "description", "author", "license"}
VERSION_PATTERN = re.compile(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?$")


# ---------------------------------------------------------------------------
# Version helpers (no packaging dependency)
# ---------------------------------------------------------------------------
def _parse_version(version_str: str) -> tuple[int, int, int]:
    """Parse a version string like '2.4.0' into a comparable tuple."""
    match = VERSION_PATTERN.match(version_str.strip())
    if not match:
        raise ValueError(f"Invalid version string: {version_str!r}")
    major = int(match.group(1))
    minor = int(match.group(2) or 0)
    patch = int(match.group(3) or 0)
    return (major, minor, patch)


def _version_satisfies(version: str, requirement: str) -> bool:
    """Check whether *version* satisfies a requirement like '>=2.4.0'."""
    requirement = requirement.strip()
    if requirement.startswith(">="):
        return _parse_version(version) >= _parse_version(requirement[2:])
    if requirement.startswith(">"):
        return _parse_version(version) > _parse_version(requirement[1:])
    if requirement.startswith("=="):
        return _parse_version(version) == _parse_version(requirement[2:])
    if requirement.startswith("<="):
        return _parse_version(version) <= _parse_version(requirement[2:])
    if requirement.startswith("<"):
        return _parse_version(version) < _parse_version(requirement[1:])
    return _parse_version(version) == _parse_version(requirement)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------
@dataclass
class PluginManifest:
    """Structured representation of a plugin manifest.toml."""

    name: str
    version: str
    description: str
    author: str
    license: str
    homepage: str = ""
    requirements: dict[str, Any] = field(default_factory=dict)
    dependencies: dict[str, str] = field(default_factory=dict)
    conflicts: dict[str, str] = field(default_factory=dict)
    files: dict[str, Any] = field(default_factory=dict)
    security: dict[str, bool] = field(default_factory=dict)

    # Convenience helpers -------------------------------------------------
    @property
    def main_sty(self) -> str:
        return self.files.get("main", f"omnilatex-plugin-{self.name}.sty")

    @property
    def shell_escape(self) -> bool:
        return self.security.get("shell_escape", False)

    @property
    def file_write(self) -> bool:
        return self.security.get("file_write", False)

    @property
    def network(self) -> bool:
        return self.security.get("network", False)


@dataclass
class RegistryEntry:
    """A single entry from the master registry.toml."""

    name: str
    version: str
    description: str
    author: str
    homepage: str
    license: str
    omnilatex_min: str
    tags: list[str] = field(default_factory=list)
    status: str = "active"


@dataclass
class PluginInfo:
    """Resolved information about a discovered plugin."""

    manifest: PluginManifest
    path: Path
    registry_entry: RegistryEntry | None = None


# ---------------------------------------------------------------------------
# Manifest loading & validation
# ---------------------------------------------------------------------------
def load_manifest(path: Path) -> PluginManifest:
    """Load and validate a manifest.toml from *path*.

    Raises ``ValueError`` if the manifest is invalid.
    """
    if not path.is_file():
        raise FileNotFoundError(f"Manifest not found: {path}")

    with open(path, "rb") as fh:
        raw = tomllib.load(fh)

    return _parse_manifest(raw, path.parent)


def _parse_manifest(raw: dict[str, Any], base_dir: Path) -> PluginManifest:
    """Parse raw TOML dict into a ``PluginManifest``, validating fields."""
    plugin_section = raw.get("plugin")
    if not isinstance(plugin_section, dict):
        raise ValueError("manifest.toml must contain a [plugin] section")

    # Required top-level fields
    missing = REQUIRED_PLUGIN_FIELDS - plugin_section.keys()
    if missing:
        raise ValueError(
            f"Missing required fields in [plugin]: {', '.join(sorted(missing))}"
        )

    manifest = PluginManifest(
        name=plugin_section["name"],
        version=str(plugin_section["version"]),
        description=plugin_section["description"],
        author=plugin_section["author"],
        license=plugin_section["license"],
        homepage=plugin_section.get("homepage", ""),
        requirements=plugin_section.get("requirements", {}),
        dependencies=plugin_section.get("dependencies", {}),
        conflicts=plugin_section.get("conflicts", {}),
        files=plugin_section.get("files", {}),
        security=plugin_section.get("security", {}),
    )

    # Validate version format
    try:
        _parse_version(manifest.version)
    except ValueError as exc:
        raise ValueError(f"Invalid plugin version {manifest.version!r}: {exc}") from exc

    # Validate main .sty exists
    sty_path = base_dir / manifest.main_sty
    if not sty_path.is_file():
        raise ValueError(
            f"Main style file '{manifest.main_sty}' not found in {base_dir}"
        )

    # Security validation
    _validate_security(manifest)

    return manifest


def _validate_security(manifest: PluginManifest) -> None:
    """Enforce sandbox capability rules."""
    for key in ALWAYS_DENIED:
        if manifest.security.get(key, False):
            raise ValueError(
                f"Security capability '{key}' is always denied for plugins"
            )

    for key in SANDBOX_CAPABILITIES - ALWAYS_DENIED:
        if key not in manifest.security:
            manifest.security[key] = False  # default to denied


# ---------------------------------------------------------------------------
# Registry management
# ---------------------------------------------------------------------------
def load_registry(path: Path | None = None) -> list[RegistryEntry]:
    """Load the master plugin registry from *path* (default: ``REGISTRY_PATH``)."""
    path = path or REGISTRY_PATH
    if not path.is_file():
        return []

    with open(path, "rb") as fh:
        raw = tomllib.load(fh)

    entries: list[RegistryEntry] = []
    for item in raw.get("plugin", []):
        entries.append(
            RegistryEntry(
                name=item["name"],
                version=str(item["version"]),
                description=item.get("description", ""),
                author=item.get("author", ""),
                homepage=item.get("homepage", ""),
                license=item.get("license", ""),
                omnilatex_min=item.get("omnilatex_min", ""),
                tags=item.get("tags", []),
                status=item.get("status", "active"),
            )
        )
    return entries


def _escape_toml_string(s: str) -> str:
    """Escape a string for TOML output."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _dump_toml_value(value: Any, indent: int = 0) -> str:
    """Format a TOML value as a string."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return f'"{_escape_toml_string(value)}"'
    if isinstance(value, list):
        items = ", ".join(_dump_toml_value(v) for v in value)
        return f"[{items}]"
    if isinstance(value, dict):
        return str(value)  # dicts are handled at section level
    return f'"{_escape_toml_string(str(value))}"'


def _dump_toml_section(data: dict[str, Any], prefix: str = "", indent: int = 0) -> str:
    """Recursively dump a dict as TOML sections."""
    lines: list[str] = []
    tab = "  " * indent
    # Top-level keys first
    for key, value in data.items():
        if isinstance(value, dict):
            continue
        lines.append(f"{tab}{key} = {_dump_toml_value(value)}")
    # Then sections
    for key, value in data.items():
        if not isinstance(value, dict):
            continue
        section = f"{prefix}.{key}" if prefix else key
        lines.append(f"\n{tab}[{section}]")
        lines.append(_dump_toml_section(value, section, indent))
    return "\n".join(lines)


def save_registry(entries: list[RegistryEntry], path: Path | None = None) -> None:
    """Write *entries* back to the registry file."""
    path = path or REGISTRY_PATH
    lines: list[str] = []

    lines.append("[registry]")
    lines.append('version = "1.0.0"')
    lines.append('last_updated = ""')
    lines.append('"description" = "Official OmniLaTeX plugin registry"')

    for entry in entries:
        lines.append("")
        lines.append("[[plugin]]")
        lines.append(f"name = {_dump_toml_value(entry.name)}")
        lines.append(f"version = {_dump_toml_value(entry.version)}")
        lines.append(f"description = {_dump_toml_value(entry.description)}")
        lines.append(f"author = {_dump_toml_value(entry.author)}")
        lines.append(f"homepage = {_dump_toml_value(entry.homepage)}")
        lines.append(f"license = {_dump_toml_value(entry.license)}")
        lines.append(f"omnilatex_min = {_dump_toml_value(entry.omnilatex_min)}")
        lines.append(f"tags = {_dump_toml_value(entry.tags)}")
        lines.append(f"status = {_dump_toml_value(entry.status)}")

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")


def search_plugins(
    entries: list[RegistryEntry],
    *,
    query: str = "",
    tag: str = "",
    status: str = "",
) -> list[RegistryEntry]:
    """Search the registry by name/description query, tag, or status."""
    results = entries
    if query:
        q = query.lower()
        results = [
            e for e in results if q in e.name.lower() or q in e.description.lower()
        ]
    if tag:
        results = [e for e in results if tag in e.tags]
    if status:
        results = [e for e in results if e.status == status]
    return results


def register_plugin(
    entries: list[RegistryEntry], manifest: PluginManifest
) -> list[RegistryEntry]:
    """Add or update a plugin in the registry from its manifest."""
    new_entry = RegistryEntry(
        name=manifest.name,
        version=manifest.version,
        description=manifest.description,
        author=manifest.author,
        homepage=manifest.homepage,
        license=manifest.license,
        omnilatex_min=manifest.requirements.get("omnilatex", ""),
        tags=[],
        status="active",
    )
    # Replace existing entry with the same name, or append
    updated = [e for e in entries if e.name != manifest.name]
    updated.append(new_entry)
    return updated


# ---------------------------------------------------------------------------
# Plugin discovery
# ---------------------------------------------------------------------------
def discover_plugins(plugins_dir: Path | None = None) -> list[PluginInfo]:
    """Discover all plugins under *plugins_dir* by scanning for manifest.toml files."""
    plugins_dir = plugins_dir or PLUGINS_DIR
    discovered: list[PluginInfo] = []

    if not plugins_dir.is_dir():
        return discovered

    for child in sorted(plugins_dir.iterdir()):
        if not child.is_dir():
            continue
        manifest_path = child / "manifest.toml"
        if manifest_path.is_file():
            try:
                manifest = load_manifest(manifest_path)
                discovered.append(PluginInfo(manifest=manifest, path=child))
            except (ValueError, FileNotFoundError):
                continue  # skip invalid plugins during discovery

    return discovered


# ---------------------------------------------------------------------------
# Sandbox capability checking
# ---------------------------------------------------------------------------
def check_capabilities(
    manifest: PluginManifest,
    *,
    allowed_shell_escape: bool = False,
    allowed_file_write: bool = False,
) -> dict[str, bool]:
    """Check whether a plugin's requested capabilities are permitted.

    Returns a dict mapping capability name to ``True`` (granted) or ``False``
    (denied).  Network is always denied.
    """
    caps: dict[str, bool] = {}

    caps["shell_escape"] = manifest.shell_escape and allowed_shell_escape
    caps["file_write"] = manifest.file_write and allowed_file_write
    caps["network"] = False  # always denied

    # Environment and process are always limited
    caps["env_vars"] = False
    caps["process_execution"] = False

    return caps


def get_denied_capabilities(
    manifest: PluginManifest,
    *,
    allowed_shell_escape: bool = False,
    allowed_file_write: bool = False,
) -> list[str]:
    """Return capability names that the plugin requests but are denied."""
    caps = check_capabilities(
        manifest,
        allowed_shell_escape=allowed_shell_escape,
        allowed_file_write=allowed_file_write,
    )
    requested = []
    if manifest.shell_escape:
        requested.append("shell_escape")
    if manifest.file_write:
        requested.append("file_write")
    return [cap for cap in requested if not caps.get(cap, False)]


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------
def detect_conflicts(
    plugin_infos: list[PluginInfo],
) -> list[tuple[PluginInfo, PluginInfo, str]]:
    """Detect conflicts between a set of plugins.

    Returns a list of ``(plugin_a, plugin_b, reason)`` tuples.
    """
    conflicts: list[tuple[PluginInfo, PluginInfo, str]] = []
    by_name = {info.manifest.name: info for info in plugin_infos}

    for info_a in plugin_infos:
        # Check explicit conflicts declared in manifests
        for conflict_name, conflict_spec in info_a.manifest.conflicts.items():
            if conflict_name in by_name:
                info_b = by_name[conflict_name]
                if conflict_spec == "*" or _version_satisfies(
                    info_b.manifest.version, conflict_spec
                ):
                    conflicts.append(
                        (
                            info_a,
                            info_b,
                            f"{info_a.manifest.name} conflicts with {conflict_name}",
                        )
                    )

        # Check reverse conflicts (B declares conflict with A)
        for info_b in plugin_infos:
            if info_b is info_a:
                continue
            for conflict_name, conflict_spec in info_b.manifest.conflicts.items():
                if conflict_name == info_a.manifest.name:
                    if conflict_spec == "*" or _version_satisfies(
                        info_a.manifest.version, conflict_spec
                    ):
                        # Avoid duplicates
                        if not any(
                            (a is info_b and b is info_a)
                            or (a is info_a and b is info_b)
                            for a, b, _ in conflicts
                        ):
                            conflicts.append(
                                (
                                    info_b,
                                    info_a,
                                    f"{info_b.manifest.name} conflicts with {conflict_name}",
                                )
                            )

    return conflicts


def check_dependencies(
    plugin_info: PluginInfo,
    available: dict[str, PluginInfo],
) -> list[str]:
    """Check that all dependencies of *plugin_info* are satisfied.

    Returns a list of unmet dependency descriptions.
    """
    unmet: list[str] = []
    for dep_name, dep_spec in plugin_info.manifest.dependencies.items():
        if dep_name not in available:
            unmet.append(f"Missing dependency: {dep_name} {dep_spec}")
            continue
        dep_version = available[dep_name].manifest.version
        if not _version_satisfies(dep_version, dep_spec):
            unmet.append(
                f"Dependency {dep_name} version {dep_version} does not satisfy {dep_spec}"
            )
    return unmet


# ---------------------------------------------------------------------------
# Full validation pipeline
# ---------------------------------------------------------------------------
@dataclass
class ValidationResult:
    """Result of validating a plugin against the registry and sandbox."""

    valid: bool
    manifest: PluginManifest | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    sandbox_caps: dict[str, bool] = field(default_factory=dict)
    denied_caps: list[str] = field(default_factory=list)
    conflicts: list[tuple[str, str, str]] = field(default_factory=list)
    unmet_deps: list[str] = field(default_factory=list)


def validate_plugin(
    manifest_path: Path,
    *,
    plugins_dir: Path | None = None,
    allowed_shell_escape: bool = False,
    allowed_file_write: bool = False,
) -> ValidationResult:
    """Run the full validation pipeline on a plugin.

    1. Load & validate the manifest
    2. Check sandbox capabilities
    3. Check for conflicts with other discovered plugins
    4. Check dependency satisfaction
    """
    plugins_dir = plugins_dir or PLUGINS_DIR
    result = ValidationResult(valid=False)

    # Step 1: load manifest
    try:
        manifest = load_manifest(manifest_path)
        result.manifest = manifest
    except (ValueError, FileNotFoundError) as exc:
        result.errors.append(str(exc))
        return result

    # Step 2: sandbox capabilities
    result.sandbox_caps = check_capabilities(
        manifest,
        allowed_shell_escape=allowed_shell_escape,
        allowed_file_write=allowed_file_write,
    )
    result.denied_caps = get_denied_capabilities(
        manifest,
        allowed_shell_escape=allowed_shell_escape,
        allowed_file_write=allowed_file_write,
    )
    if result.denied_caps:
        result.warnings.append(
            f"Plugin requests capabilities that will be denied: {', '.join(result.denied_caps)}"
        )

    # Step 3: conflicts
    plugin_info = PluginInfo(manifest=manifest, path=manifest_path.parent)
    all_plugins = discover_plugins(plugins_dir)
    # Exclude self from conflict detection
    other_plugins = [p for p in all_plugins if p.manifest.name != manifest.name]
    all_for_check = [plugin_info] + other_plugins
    raw_conflicts = detect_conflicts(all_for_check)
    result.conflicts = [
        (a.manifest.name, b.manifest.name, reason) for a, b, reason in raw_conflicts
    ]
    if result.conflicts:
        for a_name, b_name, reason in result.conflicts:
            result.errors.append(f"Conflict: {reason}")

    # Step 4: dependencies
    available = {p.manifest.name: p for p in all_plugins}
    result.unmet_deps = check_dependencies(plugin_info, available)
    if result.unmet_deps:
        for dep in result.unmet_deps:
            result.errors.append(dep)

    result.valid = len(result.errors) == 0
    return result


# ---------------------------------------------------------------------------
# Remote registry support
# ---------------------------------------------------------------------------
REGISTRY_REMOTE_URL = (
    "https://raw.githubusercontent.com/WyattAu/omnilatex-plugins" "/main/registry.toml"
)


def fetch_remote_registry(
    url: str = REGISTRY_REMOTE_URL, timeout: int = 10
) -> dict[str, Any] | None:
    """Fetch and parse the remote plugin registry.

    Returns the parsed TOML dict, or None on network/parse error.
    Uses stdlib urllib (no new dependencies).
    """
    import urllib.error
    import urllib.request

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "OmniLaTeX/2.5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read().decode("utf-8")
        return tomllib.loads(data)
    except (urllib.error.URLError, OSError, ValueError, tomllib.TOMLDecodeError):
        return None


def search_remote_plugins(
    query: str = "", url: str = REGISTRY_REMOTE_URL
) -> list[dict[str, Any]]:
    """Search the remote registry for plugins matching *query*.

    Falls back to the local registry if the remote is unreachable.
    """
    registry = fetch_remote_registry(url)
    if registry is None:
        registry = load_registry()

    entries = registry.get("plugin", []) if registry else []
    if not query:
        return entries

    query_lower = query.lower()
    return [
        e
        for e in entries
        if query_lower in e.get("name", "").lower()
        or query_lower in e.get("description", "").lower()
        or query_lower in " ".join(e.get("tags", [])).lower()
    ]
