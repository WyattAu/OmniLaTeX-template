"""Doctor command mixin.

Provides the health diagnostics command.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


class DoctorMixin:
    """Mixin providing the doctor command.

    Requires self.ui to be set by the inheriting class.
    """

    def cmd_doctor(self, _: list[str] | None = None) -> None:
        """Run comprehensive health diagnostics."""
        import platform as _platform

        self.ui.info("OmniLaTeX Doctor \u2014 Environment Health Check")
        self.ui.info("=" * 50)

        self.ui.info(f"Platform: {_platform.system()} {_platform.release()}")
        self.ui.info(f"Python: {sys.version}")
        self.ui.info(f"Architecture: {_platform.machine()}")

        checks = []

        for tool, desc in [
            ("lualatex", "LuaTeX engine"),
            ("latexmk", "Build orchestrator"),
            ("biber", "Bibliography processor"),
            ("bib2gls", "Glossary processor"),
            ("inkscape", "SVG converter"),
            ("git", "Version control"),
            ("pygmentize", "Code highlighting (Pygments)"),
        ]:
            path = shutil.which(tool)
            if path:
                try:
                    result = subprocess.run(
                        [tool, "--version"], capture_output=True, text=True, timeout=5
                    )
                    version = (result.stdout or result.stderr).split("\n")[0].strip()
                    checks.append((desc, True, f"{path}\n  {version}"))
                except (subprocess.TimeoutExpired, OSError, ValueError):
                    checks.append((desc, True, f"{path}"))
            else:
                remediation = {
                    "lualatex": "Install TeX Live: https://tug.org/texlive/",
                    "latexmk": "Install latexmk (usually bundled with TeX Live)",
                    "biber": "Install biber (usually bundled with TeX Live)",
                    "bib2gls": "Install bib2gls: tlmgr install bib2gls",
                    "inkscape": "Install Inkscape: https://inkscape.org/",
                    "git": "Install git: https://git-scm.com/",
                    "pygmentize": "pip install Pygments",
                }
                checks.append((desc, False, remediation.get(tool, "Install the tool")))

        font_names = [
            "Monaspace Neon",
            "Atkinson Hyperlegible Next",
            "Libertinus Serif",
        ]

        font_results: dict[str, tuple[bool, str]] = {}

        fc_list_output = ""
        try:
            result = subprocess.run(
                ["fc-list", ":family"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                fc_list_output = result.stdout.lower()
        except (subprocess.TimeoutExpired, OSError):
            import logging

            logging.getLogger("omnilatex").debug(
                "fc-list font detection failed", exc_info=True
            )

        lualatex_check_done = False

        for font_name in font_names:
            found = None

            if font_name.lower() in fc_list_output:
                found = True

            if found is None and not lualatex_check_done:
                try:
                    import tempfile

                    tex_content = (
                        "\\RequirePackage{fontspec}\n"
                        "\\newcommand{\\checkfont}[1]{"
                        "\\IfFontExistsTF{#1}{\\typeout{FONTFOUND:#1}}"
                        "{\\typeout{FONTMISSING:#1}}}\n"
                    )
                    for fn in font_names:
                        if fn not in font_results:
                            tex_content += f"\\checkfont{{{fn}}}\n"
                    tex_content += "\\stop\n"

                    with tempfile.TemporaryDirectory(
                        prefix="omnilatex-doctor-"
                    ) as tmpdir:
                        tmp_path = Path(tmpdir) / "check.tex"
                        tmp_path.write_text(tex_content, encoding="utf-8")

                        result = subprocess.run(
                            ["lualatex", "--interaction=nonstopmode", str(tmp_path)],
                            capture_output=True,
                            text=True,
                            timeout=30,
                            cwd=tmpdir,
                        )
                        output = result.stdout + result.stderr
                        for fn in font_names:
                            if fn not in font_results:
                                if f"FONTFOUND:{fn}" in output:
                                    font_results[fn] = (
                                        True,
                                        "Found (via LuaLaTeX)",
                                    )
                                else:
                                    font_results[fn] = (
                                        False,
                                        "Not found (fallback font will be used)",
                                    )

                    lualatex_check_done = True
                except (OSError, subprocess.SubprocessError):
                    lualatex_check_done = True

            if found is not None and font_name not in font_results:
                note = "Found" if found else "Not found (fallback font will be used)"
                font_results[font_name] = (found, note)

            if font_name not in font_results:
                font_results[font_name] = (
                    False,
                    "Could not check (font tools unavailable)",
                )

        for font_name in font_names:
            ok, note = font_results[font_name]
            checks.append((f"Font: {font_name}", ok, note))

        for name, ok, detail in checks:
            status = "PASS" if ok else "FAIL"
            self.ui.info(f"\n[{status}] {name}")
            self.ui.info(f"  {detail}")

        passed = sum(1 for _, ok, _ in checks if ok)
        total = len(checks)
        self.ui.info(f"\n{'=' * 50}")
        self.ui.info(f"Result: {passed}/{total} checks passed")

        failed = [(n, d) for n, ok, d in checks if not ok]
        if failed:
            self.ui.info("\nRemediation steps:")
            for name, detail in failed:
                self.ui.info(f"  \u2022 {name}: {detail}")
