"""Command mixin for BuildTasks --- watch, preflight, test, diff,
scaffold, init, doctor, check, lint, export."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from buildlib.commands.export import ExportMixin
from buildlib.commands.scaffold import ScaffoldMixin
from buildlib.config import (
    BUILD_EXAMPLES_SUBDIR,
    INTERACTION_NONSTOP,
    LATEXMK_COMMAND,
    MAIN_TEX_FILENAME,
    REPO_ROOT,
)
from buildlib.diff import _compute_ssim_windowed


class _Commands(ScaffoldMixin, ExportMixin):
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

    def cmd_watch(self, files: list[str]):
        """Watch source files for changes and rebuild."""
        watch_dirs = [Path(".")]
        extensions = {".tex", ".sty", ".cls", ".bib", ".lua", ".toml"}
        ui = self.ui
        ui.info("Watching for changes... (Ctrl+C to stop)")

        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            class RebuildHandler(FileSystemEventHandler):
                def __init__(self, runner, extensions, files):
                    self.runner = runner
                    self.extensions = extensions
                    self.files = files
                    self._last_rebuild = 0

                def on_modified(self, event):
                    path = Path(event.src_path)
                    if path.suffix in self.extensions:
                        import time as _time

                        now = _time.time()
                        if now - self._last_rebuild < 1.0:
                            return
                        self._last_rebuild = now
                        self.runner.ui.info(f"\nChange detected: {path}")
                        self.runner._rebuild_affected(path, self.files)

            handler = RebuildHandler(self, extensions, files)
            observer = Observer()
            for d in watch_dirs:
                observer.schedule(handler, str(d), recursive=True)
            observer.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()

        except ImportError:
            ui.info("watchdog not installed, using inotifywait fallback")
            cmd = [
                "inotifywait",
                "-r",
                "-e",
                "modify,create,delete",
                "--format",
                "%w%f",
            ]
            for d in watch_dirs:
                cmd.append(str(d))
            try:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
                if process.stdout is None:
                    ui.error("inotifywait stdout is None, cannot watch")
                    return
                for line in process.stdout:
                    path = Path(line.strip())
                    if path.suffix in extensions:
                        ui.info(f"\nChange detected: {path}")
                        self._rebuild_affected(path, files)
            except FileNotFoundError:
                ui.error(
                    "Neither watchdog nor inotifywait found. "
                    "Install one to use watch mode: pip install watchdog"
                )
            except KeyboardInterrupt:
                process.terminate()

    def _rebuild_affected(self, changed_path: Path, files: list[str]):
        """Rebuild documents affected by a changed file."""
        if files:
            self.build_example(files)
        else:
            self.build_examples([])

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
        project_root = REPO_ROOT
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
        self, tex_a: Path, tex_b: Path, output: str | None = None, cwd: Path | None = None
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
            repo_root = REPO_ROOT
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
        self, files: list[str], regenerate_references: bool = False, output: str | None = None
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

        ref_dir = REPO_ROOT / "tests" / "references"
        build_dir = self.config.build_dir / BUILD_EXAMPLES_SUBDIR
        repo_root = REPO_ROOT

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
            import numpy as np
            from PIL import Image

            _has_ssim = True
        except ImportError:
            _has_ssim = False
            self.ui.info(
                "pillow/numpy not available; falling back to byte-level comparison"
            )

        all_pass = True
        for name in files:
            example_dir = repo_root / "examples" / name
            pdf_path = example_dir / "main.pdf"
            ref_path = ref_dir / f"{name}.pdf"
            build_copy = build_dir / f"{name}.pdf"

            # Prefer the build output (already post-build) if available
            source = build_copy if build_copy.exists() else pdf_path

            if not source.exists():
                self.ui.warning(f"SKIP: {name} \u2014 PDF not found")
                continue

            if not ref_path.exists():
                self.ui.info(
                    f"GENERATE: {name} \u2014 no reference, copying as baseline"
                )
                ref_path.parent.mkdir(parents=True, exist_ok=True)

                shutil.copy2(source, ref_path)
                continue

            # Compare using SSIM (requires pymupdf + pillow + numpy)
            if _has_ssim:
                try:
                    import fitz  # noqa: F401

                    ref_doc = fitz.open(str(ref_path))
                    test_doc = fitz.open(str(source))
                    try:
                        if ref_doc.page_count != test_doc.page_count:
                            self.ui.error(
                                f"FAIL: {name} — page count mismatch "
                                f"(ref={ref_doc.page_count}, test={test_doc.page_count})"
                            )
                            all_pass = False
                            continue

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
                                self.ui.error(
                                    f"FAIL: {name} page {i + 1} — dimension mismatch"
                                )
                                all_pass = False
                                continue

                            ssim = _compute_ssim_windowed(arr1, arr2)

                            threshold = 0.95
                            page_pass = ssim >= threshold
                            status = "✅" if page_pass else "❌"
                            self.ui.info(f"  Page {i + 1}: SSIM={ssim:.4f} {status}")
                            if not page_pass:
                                all_pass = False
                    finally:
                        ref_doc.close()
                        test_doc.close()
                    continue  # SSIM comparison done, skip byte-level fallback

                except ImportError:
                    self.ui.info(
                        f"  pymupdf not available for {name}; falling back to byte-level"
                    )

            # Byte-level fallback (no SSIM deps available)
            # Import hashlib at module level (line 5)

            ref_hash = hashlib.sha256(source.read_bytes()).hexdigest()[:16]
            test_hash = hashlib.sha256(ref_path.read_bytes()).hexdigest()[:16]
            if ref_hash == test_hash:
                self.ui.info(f"\u2705 PASS: {name} (byte-identical)")
            else:
                self.ui.error(f"\u274c FAIL: {name} (content differs)")
                all_pass = False

        if all_pass:
            self.ui.success("All comparisons passed")
        else:
            self.ui.error("Visual regressions detected")

    # -- init ---------------------------------------------------------------

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
        if not re.match(r"^[a-zA-Z0-9_-]+$", project_name):
            self.ui.error(
                f"Invalid project name '{project_name}'. "
                "Use only alphanumeric characters, hyphens, and underscores."
            )
            return
        repo_root = REPO_ROOT
        src = repo_root / "examples" / "minimal-starter"
        dst = Path.cwd() / project_name

        # Verify resolved path stays within current directory
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

        # Validate doctype
        if doctype is not None:
            if doctype.lower() not in self.VALID_DOCTYPES:
                self.ui.error(
                    f"Unknown doctype '{doctype}'. Valid options: "
                    + ", ".join(self.VALID_DOCTYPES)
                )
                return
            doctype = doctype.lower()

        # Validate language
        if language is not None:
            if language.lower() not in self.VALID_LANGUAGES:
                self.ui.error(
                    f"Unknown language '{language}'. Valid options: "
                    + ", ".join(self.VALID_LANGUAGES)
                )
                return
            language = language.lower()

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

            content = main_tex.read_text(encoding="utf-8")

            # Multi-line regex: \documentclass[...options...]{class}
            m = re.search(r"(\\documentclass\s*\[)([\s\S]*?)(\]\{[^}]+\})", content)
            if m:
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

        repo_root = REPO_ROOT
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

    # -- doctor -------------------------------------------------------------

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

    # -- check --------------------------------------------------------------

    def cmd_check(self, files: list[str] | None = None) -> int:
        """Cross-reference integrity check on LaTeX files."""
        from collections import defaultdict

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

    # -- lint ---------------------------------------------------------------

    def cmd_lint(self, files: list[str] | None = None) -> int:
        """Lint .tex files with chktex and lacheck."""
        self.ui.header("Linting .tex files")

        repo_root = REPO_ROOT

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
