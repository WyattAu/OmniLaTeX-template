"""Command mixin for BuildTasks --- watch, preflight, test, diff,
scaffold, init, doctor, check, lint, export."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import buildlib.config as _cfg
from buildlib.commands.check_lint import CheckLintMixin
from buildlib.commands.doctor import DoctorMixin
from buildlib.commands.export import ExportMixin
from buildlib.commands.plugin import PluginMixin
from buildlib.commands.scaffold import ScaffoldMixin
from buildlib.commands.watch import WatchMixin
from buildlib.config import (
    BUILD_EXAMPLES_SUBDIR,
    INTERACTION_NONSTOP,
    LATEXMK_COMMAND,
    MAIN_TEX_FILENAME,
)
from buildlib.diff import _compute_ssim_windowed


class _Commands(
    ScaffoldMixin, ExportMixin, WatchMixin, DoctorMixin, CheckLintMixin, PluginMixin
):
    # -- class-level constants used by cmd_init -----------------------------

    VALID_DOCTYPES = [
        "book",
        "thesis",
        "dissertation",
        "manual",
        "guide",
        "handbook",
        "report",
        "technicalreport",
        "standard",
        "patent",
        "article",
        "inlinepaper",
        "journal",
        "dictionary",
        "cv",
        "cover-letter",
        "poster",
        "presentation",
        "letter",
        "grant-proposal",
        "ieee",
        "book-chapter",
    ]

    VALID_LANGUAGES = [
        "english",
        "german",
        "french",
        "spanish",
        "polish",
        "dutch",
        "catalan",
        "brazilian",
        "italian",
        "portuguese",
        "romanian",
        "turkish",
        "greek",
        "russian",
        "ukrainian",
        "czech",
        "slovak",
        "slovenian",
        "serbian",
        "croatian",
        "bulgarian",
        "mongolian",
        "chinese",
        "japanese",
        "korean",
    ]

    # -- watch --------------------------------------------------------------

    # -- environment checks -------------------------------------------------

    def _check_tool(
        self, tool: str, desc: str, required: bool = True
    ) -> tuple[str, bool, str]:
        path = shutil.which(tool)
        if path:
            return (desc, True, f"Found at {path}")
        note = "Not found" + ("" if not required else " (required)")
        return (desc, not required, note)

    def _get_texlive_version(self) -> int | None:
        try:
            result = subprocess.run(
                ["tex", "--version"], capture_output=True, text=True, timeout=5
            )
            for line in (result.stdout or "").splitlines():
                m = re.match(r".*TeX Live (\d{4})", line)
                if m:
                    return int(m.group(1))
        except (subprocess.TimeoutExpired, OSError, ValueError):
            import logging

            logging.getLogger("omnilatex").debug(
                "Failed to detect TeX Live version", exc_info=True
            )
        return None

    def _check_latex_package(self, pkg: str) -> bool:
        try:
            result = subprocess.run(
                ["kpsewhich", f"{pkg}.sty"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            return False

    def _check_all_latex_packages(self, packages: list[str]) -> dict[str, bool]:
        try:
            result = subprocess.run(
                ["kpsewhich"] + [f"{pkg}.sty" for pkg in packages],
                capture_output=True,
                text=True,
                timeout=30,
            )
            found = set()
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.strip().splitlines():
                    stem = Path(line.strip()).stem
                    found.add(stem)
            elif result.returncode != 0 and result.stdout:
                for line in result.stdout.strip().splitlines():
                    if line.strip():
                        stem = Path(line.strip()).stem
                        found.add(stem)
            return {pkg: pkg in found for pkg in packages}
        except (subprocess.TimeoutExpired, OSError):
            return {pkg: False for pkg in packages}

    # -- preflight ----------------------------------------------------------

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

    # -- test ---------------------------------------------------------------

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

    # -- diff helpers -------------------------------------------------------

    def _compare_single_example(
        self, name: str, source: Path, ref_path: Path, has_ssim: bool
    ) -> bool:
        """Compare a single example PDF against its reference.

        Returns True if the example passes (no regression detected).
        """
        if not source.exists():
            self.ui.warning(f"SKIP: {name} \u2014 PDF not found")
            return True  # skip is not a failure

        if not ref_path.exists():
            self.ui.info(f"GENERATE: {name} \u2014 no reference, copying as baseline")
            ref_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, ref_path)
            return True

        if has_ssim:
            passed = self._compare_ssim(name, source, ref_path)
            if passed is not None:
                return passed

        return self._compare_bytes(name, source, ref_path)

    def _compare_ssim(self, name: str, source: Path, ref_path: Path) -> bool | None:
        """SSIM-based visual comparison. Returns None if pymupdf unavailable."""
        try:
            import fitz  # noqa: F401
            import numpy as np
            from PIL import Image

            ref_doc = fitz.open(str(ref_path))
            test_doc = fitz.open(str(source))
            try:
                if ref_doc.page_count != test_doc.page_count:
                    self.ui.error(
                        f"FAIL: {name} — page count mismatch "
                        f"(ref={ref_doc.page_count}, test={test_doc.page_count})"
                    )
                    return False

                for i in range(ref_doc.page_count):
                    dpi = 150
                    mat = fitz.Matrix(dpi / 72, dpi / 72)
                    ref_pix = ref_doc[i].get_pixmap(matrix=mat)
                    test_pix = test_doc[i].get_pixmap(matrix=mat)
                    ref_img = Image.frombytes(
                        "RGB", [ref_pix.width, ref_pix.height], ref_pix.samples
                    )
                    test_img = Image.frombytes(
                        "RGB",
                        [test_pix.width, test_pix.height],
                        test_pix.samples,
                    )

                    arr1 = np.array(ref_img.convert("L"), dtype=np.float64)
                    arr2 = np.array(test_img.convert("L"), dtype=np.float64)
                    if arr1.shape != arr2.shape:
                        self.ui.error(f"FAIL: {name} page {i + 1} — dimension mismatch")
                        return False

                    ssim = _compute_ssim_windowed(arr1, arr2)
                    threshold = 0.95
                    page_pass = ssim >= threshold
                    status = "PASS" if page_pass else "FAIL"
                    self.ui.info(f"  Page {i + 1}: SSIM={ssim:.4f} {status}")
                    if not page_pass:
                        return False
                return True
            finally:
                ref_doc.close()
                test_doc.close()

        except ImportError:
            self.ui.info(
                f"  pymupdf not available for {name}; falling back to byte-level"
            )
            return None

    def _compare_bytes(self, name: str, source: Path, ref_path: Path) -> bool:
        """Byte-level hash comparison fallback."""
        ref_hash = hashlib.sha256(source.read_bytes()).hexdigest()[:16]
        test_hash = hashlib.sha256(ref_path.read_bytes()).hexdigest()[:16]
        if ref_hash == test_hash:
            self.ui.info(f"\u2705 PASS: {name} (byte-identical)")
            return True
        else:
            self.ui.error(f"\u274c FAIL: {name} (content differs)")
            return False

    def _is_git_ref(self, ref: str) -> bool:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--verify", ref],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            return False

    def _find_tex_for_pdf(self, pdf_path: str) -> Path | None:
        pdf = Path(pdf_path)
        tex = pdf.with_suffix(".tex")
        if tex.exists():
            return tex
        tex = pdf.parent / MAIN_TEX_FILENAME
        if tex.exists():
            return tex
        return None

    def _diff_two_pdfs(self, a: str, b: str, output: str | None = None):
        self.ui.header(f"Diff: {Path(a).name} vs {Path(b).name}")
        latexdiff_path = shutil.which("latexdiff")
        tex_a = self._find_tex_for_pdf(a)
        tex_b = self._find_tex_for_pdf(b)
        if latexdiff_path and tex_a and tex_b:
            self.ui.info("Using latexdiff to produce annotated diff PDF")
            self._run_latexdiff(tex_a, tex_b, output)
        else:
            if not latexdiff_path:
                self.ui.warning(
                    "latexdiff not available; falling back to basic comparison"
                )
            else:
                self.ui.warning(
                    "Could not locate .tex sources for both PDFs; falling back to basic comparison"
                )
            self._basic_pdf_compare(a, b)

    def _diff_git_refs(self, ref_a: str, ref_b: str, output: str = None):
        self.ui.header(f"Git Diff: {ref_a} vs {ref_b}")
        import tempfile

        tmpdir = Path(tempfile.mkdtemp(prefix="omnilatex-diff-"))
        try:
            old_tex = tmpdir / "old.tex"
            new_tex = tmpdir / "new.tex"
            for ref, dest in [(ref_a, old_tex), (ref_b, new_tex)]:
                result = subprocess.run(
                    ["git", "show", f"{ref}:{MAIN_TEX_FILENAME}"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    self.ui.error(
                        f"Could not extract {MAIN_TEX_FILENAME} from ref '{ref}'"
                    )
                    self.ui.info(f"  git error: {result.stderr.strip()}")
                    return
                dest.write_text(result.stdout, encoding="utf-8")
            latexdiff_path = shutil.which("latexdiff")
            if latexdiff_path:
                self.ui.info("Using latexdiff to produce annotated diff PDF")
                self._run_latexdiff(old_tex, new_tex, output, cwd=tmpdir)
            else:
                self.ui.warning("latexdiff not available; showing textual diff")
                result = subprocess.run(
                    ["diff", "-u", str(old_tex), str(new_tex)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.stdout:
                    print(result.stdout)
                if result.returncode != 0:
                    self.ui.info("Files differ")
                else:
                    self.ui.success("Files are identical")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def _run_latexdiff(
        self,
        tex_a: Path,
        tex_b: Path,
        output: str | None = None,
        cwd: Path | None = None,
    ):
        import tempfile

        work_dir = cwd or Path(tempfile.mkdtemp(prefix="omnilatex-diff-"))
        cleanup = cwd is None
        try:
            diff_tex = work_dir / "diff.tex"
            result = subprocess.run(
                ["latexdiff", str(tex_a.resolve()), str(tex_b.resolve())],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=work_dir,
            )
            if result.returncode != 0:
                self.ui.error(f"latexdiff failed: {result.stderr.strip()}")
                return
            diff_tex.write_text(result.stdout, encoding="utf-8")
            self.ui.info("Compiling diff PDF...")
            repo_root = _cfg.REPO_ROOT
            extra_env = {
                "TEXINPUTS": os.pathsep.join([".", str(repo_root), ""]),
            }
            root_latexmkrc = repo_root / ".latexmkrc"
            cmd = [LATEXMK_COMMAND, INTERACTION_NONSTOP]
            if root_latexmkrc.exists():
                cmd.extend(["-r", str(root_latexmkrc)])
            cmd.append(diff_tex.name)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=work_dir,
                env={**os.environ, **extra_env},
            )
            diff_pdf = work_dir / "diff.pdf"
            if diff_pdf.exists():
                out_path = Path(output) if output else Path.cwd() / "diff.pdf"
                shutil.copy2(diff_pdf, out_path)
                self.ui.success(f"Annotated diff PDF: {out_path}")
            else:
                self.ui.error("Failed to compile diff PDF")
                if result.stdout:
                    for line in result.stdout.splitlines()[-20:]:
                        print(f"  {line}")
        finally:
            if cleanup:
                shutil.rmtree(work_dir, ignore_errors=True)

    def _basic_pdf_compare(self, a: str, b: str):
        size_a = Path(a).stat().st_size
        size_b = Path(b).stat().st_size
        self.ui.info(f"  {Path(a).name}: {size_a:,} bytes")
        self.ui.info(f"  {Path(b).name}: {size_b:,} bytes")
        try:
            import fitz

            doc_a = fitz.open(a)
            doc_b = fitz.open(b)
            if doc_a.page_count != doc_b.page_count:
                self.ui.warning(
                    f"Page count mismatch: {doc_a.page_count} vs {doc_b.page_count}"
                )
            else:
                self.ui.info(f"Page count: {doc_a.page_count} (match)")
            diff_pct = abs(size_a - size_b) / max(size_a, size_b, 1) * 100
            if diff_pct < 1:
                self.ui.success(f"File sizes nearly identical ({diff_pct:.1f}% diff)")
            else:
                self.ui.warning(f"File sizes differ by {diff_pct:.1f}%")
            doc_a.close()
            doc_b.close()
        except ImportError:
            if size_a == size_b:
                self.ui.success("Files are identical in size")
            else:
                self.ui.warning("File sizes differ")

    # -- cmd_diff -----------------------------------------------------------

    def cmd_diff(
        self,
        files: list[str],
        regenerate_references: bool = False,
        output: str | None = None,
    ):
        """Compare PDFs, git refs, or example references.

        Modes:
          - Two PDF paths: Direct comparison, with latexdiff if .tex sources are found.
          - Two git refs: Extract sources and produce an annotated diff PDF.
          - Example names: Visual regression against reference baselines.

        When *regenerate_references* is True, copies built PDFs to
        tests/references/ instead of comparing.
        """
        if files and len(files) == 2 and not regenerate_references:
            a, b = files[0], files[1]
            a_pdf = Path(a).exists() and a.lower().endswith(".pdf")
            b_pdf = Path(b).exists() and b.lower().endswith(".pdf")
            if a_pdf and b_pdf:
                return self._diff_two_pdfs(a, b, output)
            if self._is_git_ref(a) and self._is_git_ref(b):
                return self._diff_git_refs(a, b, output)

        self.ui.header("Visual Regression Diff")

        ref_dir = _cfg.REPO_ROOT / "tests" / "references"
        build_dir = self.config.build_dir / BUILD_EXAMPLES_SUBDIR
        repo_root = _cfg.REPO_ROOT

        if not files:
            self.ui.warning("No examples specified.")
            return

        if regenerate_references:
            self.ui.info("Regenerate mode: copying built PDFs to references/")
            ref_dir.mkdir(parents=True, exist_ok=True)
            copied = 0
            for name in files:
                build_copy = build_dir / f"{name}.pdf"
                pdf_path = repo_root / "examples" / name / "main.pdf"
                source = build_copy if build_copy.exists() else pdf_path
                if not source.exists():
                    self.ui.warning(f"SKIP: {name} -- PDF not found")
                    continue
                shutil.copy2(source, ref_dir / f"{name}.pdf")
                copied += 1
            self.ui.success(f"Copied {copied} reference PDF(s) to {ref_dir}")
            return

        try:
            import fitz  # noqa: F401

            _has_ssim = True
        except ImportError:
            _has_ssim = False
            self.ui.info(
                "pymupdf/numpy/pillow not available; "
                "falling back to byte-level comparison"
            )

        all_pass = True
        for name in files:
            example_dir = repo_root / "examples" / name
            pdf_path = example_dir / "main.pdf"
            ref_path = ref_dir / f"{name}.pdf"
            build_copy = build_dir / f"{name}.pdf"

            source = build_copy if build_copy.exists() else pdf_path

            if not self._compare_single_example(name, source, ref_path, _has_ssim):
                all_pass = False

        if all_pass:
            self.ui.success("All comparisons passed")
        else:
            self.ui.error("Visual regressions detected")

    # -- init ---------------------------------------------------------------

    def _validate_init_args(
        self, project_name: str, doctype: str | None, language: str | None
    ) -> tuple[str | None, str | None] | None:
        """Validate init arguments. Returns (doctype, language) or None on error."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", project_name):
            self.ui.error(
                f"Invalid project name '{project_name}'. "
                "Use only alphanumeric characters, hyphens, and underscores."
            )
            return None

        if doctype is not None:
            doctype = doctype.lower()
            if doctype not in self.VALID_DOCTYPES:
                self.ui.error(
                    f"Unknown doctype '{doctype}'. Valid options: "
                    + ", ".join(self.VALID_DOCTYPES)
                )
                return None

        if language is not None:
            language = language.lower()
            if language not in self.VALID_LANGUAGES:
                self.ui.error(
                    f"Unknown language '{language}'. Valid options: "
                    + ", ".join(self.VALID_LANGUAGES)
                )
                return None

        return doctype, language

    def _patch_documentclass(
        self,
        main_tex: Path,
        doctype: str | None,
        institution: str | None,
        language: str | None,
    ):
        """Patch \\documentclass options in main.tex with the given overrides."""
        content = main_tex.read_text(encoding="utf-8")

        m = re.search(r"(\\documentclass\s*\[)([\s\S]*?)(\]\{[^}]+\})", content)
        if not m:
            return

        prefix, opts_str, suffix = m.groups()
        existing_opts = [
            o.strip()
            for o in opts_str.replace("\n", " ").split(",")
            if o.strip() and not o.strip().startswith("%")
        ]
        # Strip inline comments from option values
        cleaned_opts = []
        for o in existing_opts:
            if "%" in o:
                o = o[: o.index("%")].strip()
            if o:
                cleaned_opts.append(o)
        existing_opts = cleaned_opts

        # Remove options we're overriding
        existing_opts = [
            o
            for o in existing_opts
            if not o.startswith("doctype=")
            and not o.startswith("institution=")
            and not o.startswith("language=")
        ]

        # Apply overrides
        if doctype:
            existing_opts.insert(0, f"doctype={doctype}")
        if institution:
            existing_opts.append(f"institution={institution}")
        if language:
            existing_opts.append(f"language={language}")

        new_docclass = f"{prefix}{', '.join(existing_opts)}{suffix}"
        content = content[: m.start()] + new_docclass + content[m.end() :]
        main_tex.write_text(content, encoding="utf-8")

    def cmd_init(
        self,
        files: list[str],
        doctype: str = None,
        institution: str = None,
        language: str = None,
        thesis: bool = False,
    ):
        """Initialize a new OmniLaTeX project from a template."""
        self.ui.header("Initialize Project")

        if not files:
            self.ui.warning("Usage: build.py init [OPTIONS] <project-name>")
            self.ui.info(
                "Creates a new OmniLaTeX project from the minimal-starter template."
            )
            self.ui.info("Options:")
            self.ui.info("  --doctype TYPE      Set document type (default: book)")
            self.ui.info("  --institution NAME  Set institution (default: none)")
            self.ui.info("  --language LANG     Set language (default: english)")
            self.ui.info(
                "  --thesis            Shortcut for --doctype thesis with full thesis structure"
            )
            return

        if thesis and doctype is None:
            doctype = "thesis"

        project_name = files[0]
        validated = self._validate_init_args(project_name, doctype, language)
        if validated is None:
            return
        doctype, language = validated

        repo_root = _cfg.REPO_ROOT
        src = repo_root / "examples" / "minimal-starter"
        dst = Path.cwd() / project_name

        if not dst.resolve().is_relative_to(Path.cwd()):
            self.ui.error(
                f"Project name '{project_name}' resolves outside current directory"
            )
            return

        if not src.exists():
            self.ui.error(f"Template not found at {src}")
            return

        if dst.exists():
            self.ui.error(f"Directory '{project_name}' already exists")
            return

        # Copy template (exclude build artifacts)
        ignore = shutil.ignore_patterns(
            "*.aux",
            "*.log",
            "*.out",
            "*.toc",
            "*.pdf",
            "*.fls",
            "*.fdb_latexmk",
            "*.synctex*",
            "*.bbl",
            "*.bcf",
            "*.blg",
            "*.run.xml",
            "*-blx.*",
            "*SAVE-ERROR",
            "*.glg",
            "*.glo",
            "*.gls",
            "*.acn",
            "*.acr",
            "*.glstex",
            "*.syi",
            "*.syg",
            "*.pyc",
            "__pycache__",
            "_minted*",
            "*.indent.log",
            "build/",
            ".git/",
            "node_modules/",
        )
        shutil.copytree(src, dst, ignore=ignore)

        # Create a .latexmkrc symlink pointing to the root
        latexmkrc_src = repo_root / ".latexmkrc"
        latexmkrc_dst = dst / ".latexmkrc"
        if latexmkrc_src.exists() and not latexmkrc_dst.exists():
            latexmkrc_dst.symlink_to(latexmkrc_src)

        # Patch main.tex if any options were specified
        main_tex = dst / "main.tex"
        if (doctype or institution or language) and main_tex.exists():
            self._patch_documentclass(main_tex, doctype, institution, language)

        if thesis:
            self._create_thesis_structure(
                dst, project_name, doctype, institution, language
            )

        self.ui.success(f"Initialized project: {project_name}")
        self.ui.info(f"  Location: {dst}")
        self.ui.info("  Template: minimal-starter")
        if doctype:
            self.ui.info(f"  Doctype: {doctype}")
        if institution:
            self.ui.info(f"  Institution: {institution}")
        if language:
            self.ui.info(f"  Language: {language}")
        if thesis:
            self.ui.info("  Structure: thesis (chapters, bib, figures)")
        self.ui.info("  Next steps:")
        self.ui.info(f"    1. cd {project_name}")
        if thesis:
            self.ui.info("    2. Edit chapters/ with your thesis content")
            self.ui.info("    3. Add references to bib/bibliography.bib")
            self.ui.info("    4. latexmk -lualatex main.tex")
        else:
            self.ui.info("    2. Edit main.tex to set your title, author, and content")
            self.ui.info("    3. python build.py build-root    (from repo root)")
            self.ui.info("       or latexmk -lualatex main.tex  (standalone)")

    # -- thesis structure helper --------------------------------------------

    def _create_thesis_structure(
        self,
        dst: Path,
        project_name: str,
        doctype: str,
        institution: str,
        language: str,
    ):
        chapters_dir = dst / "chapters"
        chapters_dir.mkdir(parents=True, exist_ok=True)

        chapter_templates = {
            "introduction.tex": ("\\chapter{Introduction}\n" "\n"),
            "methodology.tex": ("\\chapter{Methodology}\n" "\n"),
            "results.tex": ("\\chapter{Results}\n" "\n"),
            "conclusion.tex": ("\\chapter{Conclusion}\n" "\n"),
        }
        for filename, content in chapter_templates.items():
            (chapters_dir / filename).write_text(content, encoding="utf-8")

        bib_dir = dst / "bib"
        bib_dir.mkdir(parents=True, exist_ok=True)
        (bib_dir / "bibliography.bib").write_text(
            "@article{example2024,\n"
            "  author  = {Author, Example},\n"
            "  title   = {Example Article Title},\n"
            "  journal = {Journal of Examples},\n"
            "  year    = {2024},\n"
            "  volume  = {1},\n"
            "  pages   = {1--10},\n"
            "}\n",
            encoding="utf-8",
        )

        figures_dir = dst / "figures"
        figures_dir.mkdir(parents=True, exist_ok=True)
        (figures_dir / ".gitkeep").touch()

        repo_root = _cfg.REPO_ROOT
        latexmkrc_src = repo_root / ".latexmkrc"
        latexmkrc_dst = dst / ".latexmkrc"
        if latexmkrc_src.exists():
            if latexmkrc_dst.is_symlink():
                latexmkrc_dst.unlink()
            if not latexmkrc_dst.exists():
                latexmkrc_dst.symlink_to(latexmkrc_src)

        main_tex = dst / "main.tex"
        opts_parts = []
        if doctype:
            opts_parts.append(f"doctype={doctype}")
        else:
            opts_parts.append("doctype=thesis")
        if institution:
            opts_parts.append(f"institution={institution}")
        if language:
            opts_parts.append(f"language={language}")
        opts_str = ", ".join(opts_parts)
        main_tex.write_text(
            f"\\documentclass[{opts_str}]{{omnilatex}}\n"
            "\n"
            f"\\title{{{project_name.replace('-', ' ').replace('_', ' ').title()}}}\n"
            "\\author{Your Name}\n"
            "\\date{\\today}\n"
            "\n"
            "\\addbibresource{bib/bibliography.bib}\n"
            "\n"
            "\\graphicspath{{figures/}}\n"
            "\n"
            "\\begin{document}\n"
            "\\maketitle\n"
            "\\tableofcontents\n"
            "\n"
            "\\include{chapters/introduction}\n"
            "\\include{chapters/methodology}\n"
            "\\include{chapters/results}\n"
            "\\include{chapters/conclusion}\n"
            "\n"
            "\\printbibliography\n"
            "\\end{document}\n",
            encoding="utf-8",
        )

        (dst / "README.md").write_text(
            f"# {project_name}\n"
            "\n"
            "A thesis project built with"
            " [OmniLaTeX](https://github.com/WyattAu/OmniLaTeX-template).\n"
            "\n"
            "## Structure\n"
            "\n"
            "- `main.tex` — Main document file\n"
            "- `chapters/` — Thesis chapters (introduction, methodology, results, conclusion)\n"
            "- `bib/bibliography.bib` — Bibliography database\n"
            "- `figures/` — Figure assets\n"
            "- `.latexmkrc` — Build configuration (symlink to OmniLaTeX root)\n"
            "\n"
            "## Building\n"
            "\n"
            "```bash\n"
            "latexmk -lualatex main.tex\n"
            "```\n"
            "\n"
            "Or from the OmniLaTeX repo root:\n"
            "\n"
            "```bash\n"
            f"python build.py build-example {project_name}\n"
            "```\n",
            encoding="utf-8",
        )
