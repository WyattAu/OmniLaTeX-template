"""Preflight and test commands mixin.

Provides commands for validating the build environment and running tests.
"""

from __future__ import annotations

import subprocess
import sys

import buildlib.config as _cfg


class PreflightTestMixin:
    """Mixin providing preflight and test commands.

    Requires self.ui, self.runner to be set by the inheriting class.
    """

    def _check_tool(
        self, name: str, description: str, required: bool = True
    ) -> tuple[str, bool, str]:
        """Check if a tool is available on PATH."""
        import shutil

        path = shutil.which(name)
        if path:
            return (description, True, f"Found at {path}")
        if required:
            return (description, False, "NOT FOUND")
        return (description, True, "Not found (optional)")

    def _get_texlive_version(self) -> int | None:
        """Get the TeX Live year version."""
        try:
            result = subprocess.run(
                ["lualatex", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            import re

            m = re.search(r"TeX Live (\d{4})", result.stdout)
            if m:
                return int(m.group(1))
        except (subprocess.SubprocessError, OSError):
            pass
        return None

    def _check_latex_package(self, pkg: str) -> bool:
        """Check if a LaTeX package is available."""
        try:
            result = subprocess.run(
                ["lualatex", "--interaction=nonstopmode", f"\\RequirePackage{{{pkg}}}\\stop"],
                capture_output=True,
                text=True,
                timeout=15,
                cwd=_cfg.REPO_ROOT,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, OSError):
            return False

    def _check_all_latex_packages(self, packages: list[str]) -> dict[str, bool]:
        """Check multiple LaTeX packages."""
        return {pkg: self._check_latex_package(pkg) for pkg in packages}

    def cmd_preflight(self, files: list[str] | None = None) -> None:
        """Validate build environment readiness."""
        checks = []

        checks.append(self._check_tool("lualatex", "LuaTeX engine"))
        checks.append(self._check_tool("latexmk", "latexmk build tool"))

        checks.append(
            ("Python >= 3.10", sys.version_info >= (3, 10), f"Found {sys.version}")
        )

        checks.append(
            self._check_tool("inkscape", "Inkscape (SVG support)", required=False)
        )
        checks.append(self._check_tool("git", "Git CLI"))

        tex_version = self._get_texlive_version()
        checks.append(
            (
                "TeX Live >= 2024",
                tex_version is not None and tex_version >= 2024,
                f"Found TeX Live {tex_version or 'unknown'}",
            )
        )

        packages = [
            "fontspec",
            "unicode-math",
            "hyperref",
            "minted",
            "biblatex",
            "siunitx",
            "circuitikz",
            "forest",
        ]
        pkg_results = self._check_all_latex_packages(packages)
        for pkg in packages:
            found = pkg_results[pkg]
            checks.append((f"Package {pkg}", found, "Found" if found else "Missing"))

        passed = sum(1 for _, ok, _ in checks if ok)
        total = len(checks)
        for name, ok, detail in checks:
            status = "\u2713" if ok else "\u2717"
            self.ui.info(f"  {status} {name}: {detail}")

        if passed == total:
            self.ui.success(f"All {total} checks passed")
        else:
            self.ui.warning(f"{passed}/{total} checks passed")

    def cmd_test(self, files: list[str] | None = None) -> int:
        """Run test suite (l3build + pytest)."""
        results = []
        self.ui.info("Running l3build check...")
        project_root = _cfg.REPO_ROOT
        result = subprocess.run(
            ["l3build", "check"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=600,
        )
        results.append(("l3build check", result.returncode == 0))
        if result.returncode != 0:
            self.ui.warning(f"l3build check FAILED:\n{result.stdout}\n{result.stderr}")
        else:
            self.ui.success("l3build check passed")

        self.ui.info("Running pytest...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=600,
        )
        results.append(("pytest", result.returncode == 0))
        if result.returncode != 0:
            self.ui.warning(f"pytest FAILED:\n{result.stdout}")
        else:
            self.ui.success("pytest passed")

        passed = sum(1 for _, ok in results if ok)
        total = len(results)
        self.ui.info(f"\nTest Results: {passed}/{total} suites passed")
        if passed < total:
            return 1
        return 0
