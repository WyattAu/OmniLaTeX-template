"""Check and lint commands mixin.

Provides cross-reference integrity checking and LaTeX linting.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path

import buildlib.config as _cfg


class CheckLintMixin:
    """Mixin providing check and lint commands.

    Requires self.ui, self.config to be set by the inheriting class.
    """

    def cmd_check(self, files: list[str] | None = None) -> int:
        """Cross-reference integrity check on LaTeX files."""
        self.ui.header("Cross-Reference Integrity Check")

        scan_dir = Path(files[0]) if files and files else Path.cwd()

        if not scan_dir.is_dir():
            self.ui.error(f"Not a directory: {scan_dir}")
            return 1

        tex_files = sorted(
            f
            for f in scan_dir.rglob("*.tex")
            if self.config.build_dir not in f.parents and "_minted" not in str(f)
        )
        bib_files = sorted(
            f for f in scan_dir.rglob("*.bib") if self.config.build_dir not in f.parents
        )

        if not tex_files:
            self.ui.warning(f"No .tex files found in {scan_dir}")
            return 0

        self.ui.info(
            f"Scanning {len(tex_files)} .tex file(s), {len(bib_files)} .bib file(s)"
        )

        _LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
        _REF_RE = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref|pageref)\{([^}]+)\}")
        _CITE_RE = re.compile(r"\\(?:cite|nocite)\{([^}]+)\}")
        _BIB_ENTRY_RE = re.compile(r"@\w+\{([^,\s]+),")

        labels: dict[str, list[str]] = defaultdict(list)
        refs: dict[str, list[str]] = defaultdict(list)
        cites: dict[str, list[str]] = defaultdict(list)
        bib_keys: set[str] = set()

        for tex in tex_files:
            try:
                content = tex.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                self.ui.warning(f"Cannot read {tex}: {exc}")
                continue

            rel = tex.relative_to(scan_dir) if tex.is_relative_to(scan_dir) else tex

            for m in _LABEL_RE.finditer(content):
                labels[m.group(1)].append(str(rel))

            for m in _REF_RE.finditer(content):
                for key in m.group(1).split(","):
                    key = key.strip()
                    if key:
                        refs[key].append(str(rel))

            for m in _CITE_RE.finditer(content):
                for key in m.group(1).split(","):
                    key = key.strip()
                    if key:
                        cites[key].append(str(rel))

        for bib in bib_files:
            try:
                content = bib.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                self.ui.warning(f"Cannot read {bib}: {exc}")
                continue
            for m in _BIB_ENTRY_RE.finditer(content):
                bib_keys.add(m.group(1))

        label_set = set(labels.keys())
        ref_set = set(refs.keys())
        cite_set = set(cites.keys())

        undefined_refs = sorted(ref_set - label_set)
        unused_labels = sorted(label_set - ref_set)
        undefined_cites = sorted(cite_set - bib_keys)

        total_labels = len(label_set)
        total_refs = sum(len(v) for v in refs.values())
        total_cites = sum(len(v) for v in cites.values())

        self.ui.info(
            f"Labels: {total_labels}  |  References: {total_refs}  |  "
            f"Citations: {total_cites}  |  Bib entries: {len(bib_keys)}"
        )

        has_errors = False

        if undefined_refs:
            has_errors = True
            self.ui.warning(f"Undefined references ({len(undefined_refs)}):")
            for key in undefined_refs:
                locs = refs[key]
                self.ui.warning(f"  \\ref{{{key}}} referenced in: {', '.join(locs)}")

        if unused_labels:
            self.ui.info(f"Unused labels ({len(unused_labels)}):")
            for key in unused_labels:
                locs = labels[key]
                self.ui.info(f"  \\label{{{key}}} defined in: {', '.join(locs)}")

        if undefined_cites:
            has_errors = True
            self.ui.warning(f"Undefined citations ({len(undefined_cites)}):")
            for key in undefined_cites:
                locs = cites[key]
                self.ui.warning(f"  \\cite{{{key}}} referenced in: {', '.join(locs)}")

        if not undefined_refs and not unused_labels and not undefined_cites:
            self.ui.success("All cross-references and citations are valid.")
        elif not has_errors:
            self.ui.success("No errors found (unused labels are informational only).")
        else:
            self.ui.error(
                "Cross-reference check failed: undefined references or citations found."
            )

        return 1 if has_errors else 0

    def cmd_lint(self, files: list[str] | None = None) -> int:
        """Lint .tex files with chktex and lacheck."""
        self.ui.header("Linting .tex files")

        repo_root = _cfg.REPO_ROOT

        if files:
            tex_files = [Path(f) for f in files if Path(f).exists()]
        else:
            tex_files = sorted(
                f
                for f in repo_root.rglob("*.tex")
                if self.config.build_dir not in f.parents and "_minted" not in str(f)
            )

        if not tex_files:
            self.ui.warning("No .tex files found")
            return 0

        has_chktex = shutil.which("chktex") is not None
        has_lacheck = shutil.which("lacheck") is not None

        if not has_chktex and not has_lacheck:
            self.ui.error("Neither chktex nor lacheck found.")
            self.ui.info("  Install with: tlmgr install chktex lacheck")
            return 1

        self.ui.info(
            f"Scanning {len(tex_files)} file(s) with"
            f"{'chktex' if has_chktex else ''}"
            f"{' and ' if has_chktex and has_lacheck else ''}"
            f"{'lacheck' if has_lacheck else ''}"
        )

        total_errors = 0
        total_warnings = 0
        error_re = re.compile(r"Error\s+\d+", re.IGNORECASE)

        for tex_file in tex_files:
            try:
                rel = tex_file.relative_to(repo_root)
            except ValueError:
                rel = tex_file

            if has_chktex:
                try:
                    result = subprocess.run(
                        ["chktex", "-q", "-f", "%f:%l:%c:%n:%m%n", str(tex_file)],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.stdout.strip():
                        self.ui.info(f"[chktex] {rel}:")
                        for line in result.stdout.strip().splitlines():
                            print(f"  {line}")
                            if error_re.search(line):
                                total_errors += 1
                            else:
                                total_warnings += 1
                except (subprocess.TimeoutExpired, OSError) as exc:
                    self.ui.warning(f"[chktex] Failed to process {rel}: {exc}")

            if has_lacheck:
                try:
                    result = subprocess.run(
                        ["lacheck", str(tex_file)],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if result.stdout.strip():
                        self.ui.info(f"[lacheck] {rel}:")
                        for line in result.stdout.strip().splitlines():
                            print(f"  {line}")
                            total_warnings += 1
                except (subprocess.TimeoutExpired, OSError) as exc:
                    self.ui.warning(f"[lacheck] Failed to process {rel}: {exc}")

        self.ui.info(
            f"\nLint summary: {total_errors} error(s), {total_warnings} warning(s) "
            f"across {len(tex_files)} file(s)"
        )

        if total_errors > 0:
            self.ui.error("Linting found errors")
            return 1
        if total_warnings > 0:
            self.ui.warning(f"Linting passed with {total_warnings} warning(s)")
        else:
            self.ui.success("Linting passed with no issues")
        return 0
