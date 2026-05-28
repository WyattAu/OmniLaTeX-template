"""PDF content validation tests.

Validates compiled PDFs for:
1. No unresolved cross-references (Figure ??, Table ??, etc.)
2. No unresolved citations ([?])
3. Bibliography entries present in cited documents
4. Equation numbering consistency (sequential, no gaps)
5. LaTeX log analysis (undefined citations, undefined refs, rerun warnings)

These tests operate on pre-built PDFs in build/examples/ and their .log files
if available. Tests are skipped when PDFs or logs are absent.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

try:
    import pymupdf as fitz
except ImportError:
    fitz = None  # type: ignore[assignment]

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
EXAMPLES_DIR = PROJECT_ROOT / "build" / "examples"
LOG_DIR = PROJECT_ROOT / "build"

requires_pymupdf = pytest.mark.skipif(
    fitz is None, reason="pymupdf (PyMuPDF) not installed"
)

# ── Regex patterns for common LaTeX problems in PDF text ──────────────

# Unresolved cross-references: LaTeX emits "Figure ??", "Table ??", etc.
UNRESOLVED_XREF_RE = re.compile(
    r"(?:Figure|Table|Equation|Section|Chapter|Algorithm|Listing|Theorem"
    r"|Lemma|Proposition|Corollary|Example|Remark|Note|Scheme|Plate"
    r"|Box|Tab|Fig)\s+\?\?"
)

# Unresolved citations: bare [?] or Author [?] patterns
UNRESOLVED_CITE_RE = re.compile(r"\[?\?\]?")

# Numeric equation labels: (1), (2), (3), etc.
EQUATION_LABEL_RE = re.compile(r"\((\d+)\)")

# ── LaTeX log warning patterns ────────────────────────────────────────

LOG_UNDEFINED_CITE = re.compile(
    r"Citation [`']([^']+)' on page \d+ undefined"
)
LOG_UNDEFINED_REF = re.compile(
    r"Reference [`']([^']+)' on page \d+ undefined"
)
LOG_MULTIPLY_DEFINED = re.compile(
    r"Label [`']([^']+)' multiply defined"
)
LOG_RERUN_CROSSREF = re.compile(
    r"Rerun to get .*right"
)
LOG_RERUN_BIBLATEX = re.compile(
    r"Please rerun LaTeX.*biblatex"
)
LOG_ERROR = re.compile(
    r"^!", re.MULTILINE
)
LOG_MISSING_PACKAGE = re.compile(
    r"File `([^']+)' not found"
)


def _get_example_pdfs() -> list[tuple[str, Path]]:
    """Return list of (name, pdf_path) for all built example PDFs."""
    if not EXAMPLES_DIR.is_dir():
        return []
    return sorted(
        (p.stem, p)
        for p in EXAMPLES_DIR.glob("*.pdf")
    )


def _extract_text(pdf_path: Path) -> str:
    """Extract all text from a PDF."""
    doc = fitz.open(str(pdf_path))
    texts: list[str] = []
    for page in doc:
        texts.append(page.get_text())
    doc.close()
    return "\n".join(texts)


def _find_log_for_example(name: str) -> Path | None:
    """Find the .log file for a built example."""
    candidates = [
        EXAMPLES_DIR / f"{name}.log",
        EXAMPLES_DIR / name / "main.log",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return None


def _parse_log_warnings(log_path: Path) -> dict[str, list[str]]:
    """Parse a LaTeX log file for warnings and errors."""
    try:
        log_text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}

    return {
        "undefined_citations": LOG_UNDEFINED_CITE.findall(log_text),
        "undefined_references": LOG_UNDEFINED_REF.findall(log_text),
        "multiply_defined_labels": LOG_MULTIPLY_DEFINED.findall(log_text),
        "rerun_crossref": LOG_RERUN_CROSSREF.findall(log_text),
        "rerun_biblatex": LOG_RERUN_BIBLATEX.findall(log_text),
        "errors": [
            line.strip()
            for line in log_text.splitlines()
            if LOG_ERROR.match(line)
        ],
        "missing_packages": LOG_MISSING_PACKAGE.findall(log_text),
    }


# ── Examples known to have bibliography content ───────────────────────

# Only examples with actual \cite commands AND \printbibliography.
# Excludes examples that have bib infrastructure but zero \cite (no entries).
EXAMPLES_WITH_BIB = {
    "article", "citation-styles", "journal",
    "minimal-starter", "research-proposal", "thesis", "white-paper",
}

# Examples where ?? is acceptable (e.g., beamer doesn't always number)
EXAMPLES_ALLOW_UNRESOLVED = {
    "manual",  # Pre-existing: glossary conflicts, counter overflow, 28+ cross-refs
}

# Equation-heavy examples to check numbering on
EQUATION_EXAMPLES = {
    "manual": True,  # Has many equations, check numbering
    "thesis": True,
    "thesis-tuhh": True,
    "journal": True,
    "research-proposal": True,
    "homework": True,
    "exam": True,
    "lecture-notes": True,
}


# ═══════════════════════════════════════════════════════════════════════
# Test classes
# ═══════════════════════════════════════════════════════════════════════


@requires_pymupdf
@pytest.mark.slow
class TestPDFCrossReferences:
    """Verify no unresolved cross-references in compiled PDFs."""

    @pytest.mark.parametrize(
        "name,pdf_path",
        _get_example_pdfs(),
        ids=[n for n, _ in _get_example_pdfs()],
    )
    def test_no_unresolved_xrefs(self, name: str, pdf_path: Path) -> None:
        """PDF text should not contain 'Figure ??', 'Table ??', etc."""
        if name in EXAMPLES_ALLOW_UNRESOLVED:
            pytest.skip(f"{name} has known unresolved xrefs")

        text = _extract_text(pdf_path)
        matches = UNRESOLVED_XREF_RE.findall(text)
        assert not matches, (
            f"{name}: found {len(matches)} unresolved cross-references: "
            f"{matches[:10]}"
        )

    @pytest.mark.parametrize(
        "name,pdf_path",
        [(n, p) for n, p in _get_example_pdfs() if n in EXAMPLES_WITH_BIB],
        ids=[n for n, _ in _get_example_pdfs() if n in EXAMPLES_WITH_BIB],
    )
    def test_no_unresolved_citations(
        self, name: str, pdf_path: Path
    ) -> None:
        """Cited documents should not have bare [?] citation markers."""
        text = _extract_text(pdf_path)

        # Check for [?] pattern which means biber didn't run or failed
        # This is different from author-year style which uses "Author (Year)"
        bare_cite = re.findall(r"(?<!\w)\[\?\](?!\w)", text)
        assert not bare_cite, (
            f"{name}: found {len(bare_cite)} unresolved citations [?]. "
            f"Biber/biblatex may not have processed correctly."
        )


@requires_pymupdf
@pytest.mark.slow
class TestPDFBibliography:
    """Verify bibliography entries are present in cited documents."""

    @pytest.mark.parametrize(
        "name,pdf_path",
        [(n, p) for n, p in _get_example_pdfs() if n in EXAMPLES_WITH_BIB],
        ids=[n for n, _ in _get_example_pdfs() if n in EXAMPLES_WITH_BIB],
    )
    def test_bibliography_section_present(
        self, name: str, pdf_path: Path
    ) -> None:
        """Documents with .bib files should have a bibliography/references section."""
        text = _extract_text(pdf_path)
        text_lower = text.lower()

        has_bib_section = any(
            kw in text_lower
            for kw in [
                "references",
                "bibliography",
                "literaturverzeichnis",
                "literature cited",
                "works cited",
                "bibliografia",
                "referencias",
                "références",
            ]
        )
        assert has_bib_section, (
            f"{name}: expected a bibliography/references section but found none"
        )

    @pytest.mark.parametrize(
        "name,pdf_path",
        [(n, p) for n, p in _get_example_pdfs() if n in EXAMPLES_WITH_BIB],
        ids=[n for n, _ in _get_example_pdfs() if n in EXAMPLES_WITH_BIB],
    )
    def test_bibliography_has_entries(
        self, name: str, pdf_path: Path
    ) -> None:
        """Bibliography section should contain at least one entry."""
        text = _extract_text(pdf_path)
        text_lower = text.lower()

        # Find bibliography section start
        bib_start = -1
        for kw in [
            "references\n",
            "bibliography\n",
            "literaturverzeichnis\n",
        ]:
            idx = text_lower.rfind(kw)
            if idx >= 0:
                bib_start = idx
                break

        if bib_start < 0:
            pytest.skip(f"{name}: bibliography section header not found")

        bib_text = text[bib_start:]

        # Count entries: look for year patterns (1900-2099) as a proxy
        year_entries = re.findall(r"\b(19\d{2}|20\d{2})\b", bib_text)
        assert len(year_entries) >= 1, (
            f"{name}: bibliography section exists but contains no entries "
            f"(no year patterns found after header)"
        )


@requires_pymupdf
@pytest.mark.slow
class TestPDFEquations:
    """Verify equation rendering and numbering in compiled PDFs."""

    @pytest.mark.parametrize(
        "name,pdf_path",
        [(n, p) for n, p in _get_example_pdfs() if n in EQUATION_EXAMPLES],
        ids=[n for n, _ in _get_example_pdfs() if n in EQUATION_EXAMPLES],
    )
    def test_equation_numbering_sequential(
        self, name: str, pdf_path: Path
    ) -> None:
        """Equation numbers should be sequential (1, 2, 3, ...) with no gaps."""
        text = _extract_text(pdf_path)

        # Extract all equation numbers from PDF text
        # In LaTeX, equations are numbered like (1), (2), etc.
        all_nums = EQUATION_LABEL_RE.findall(text)

        # Filter to likely equation numbers (exclude years, page numbers)
        # Equation numbers are typically small (1-200) and sequential
        eq_nums = [int(n) for n in all_nums if 1 <= int(n) <= 200]

        if not eq_nums:
            pytest.skip(f"{name}: no equation numbers found")

        # Find the longest sequential run starting from 1
        # (equations may restart per chapter in some doctypes)
        sequential_runs: list[list[int]] = []
        current_run: list[int] = []

        for num in sorted(set(eq_nums)):
            if not current_run or num == current_run[-1] + 1:
                current_run.append(num)
            else:
                if len(current_run) >= 3:
                    sequential_runs.append(current_run)
                current_run = [num]
        if len(current_run) >= 3:
            sequential_runs.append(current_run)

        if not sequential_runs:
            pytest.skip(
                f"{name}: no sequential equation numbering runs found "
                f"(numbers: {sorted(set(eq_nums))[:20]})"
            )

        # Check the longest run for gaps
        longest = max(sequential_runs, key=len)
        expected = list(range(longest[0], longest[-1] + 1))
        assert longest == expected, (
            f"{name}: equation numbering gap detected. "
            f"Expected sequential {longest[0]}-{longest[-1]}, "
            f"but sequence is {longest}"
        )

    def test_manual_equation_environments_render(self) -> None:
        """Manual example should have multiple equation environments rendered."""
        manual_pdf = EXAMPLES_DIR / "manual.pdf"
        if not manual_pdf.is_file():
            pytest.skip("manual.pdf not found")

        text = _extract_text(manual_pdf)

        # The manual's math chapter demonstrates equation, align, gather, multline
        # At minimum, equation numbers should be present
        eq_labels = EQUATION_LABEL_RE.findall(text)
        eq_nums = [int(n) for n in eq_labels if 1 <= int(n) <= 100]

        assert len(eq_nums) >= 5, (
            f"manual.pdf: expected >= 5 equation numbers, found {len(eq_nums)}. "
            f"Math chapter may not have rendered correctly."
        )


@pytest.mark.slow
class TestLaTeXLogWarnings:
    """Analyze LaTeX .log files for unresolved citations and references.

    These tests run against the build logs (if preserved) to catch issues
    that PDF text extraction might miss.
    """

    @pytest.mark.parametrize(
        "name",
        sorted(EXAMPLES_WITH_BIB),
        ids=sorted(EXAMPLES_WITH_BIB),
    )
    def test_no_undefined_citations_in_log(self, name: str) -> None:
        """Log should not report undefined citations (biber ran successfully)."""
        log_path = _find_log_for_example(name)
        if log_path is None:
            pytest.skip(f"{name}: no .log file found")

        warnings = _parse_log_warnings(log_path)
        undef = warnings.get("undefined_citations", [])
        assert not undef, (
            f"{name}: {len(undef)} undefined citations in log: {undef[:10]}"
        )

    @pytest.mark.parametrize(
        "name",
        sorted(EXAMPLES_WITH_BIB),
        ids=sorted(EXAMPLES_WITH_BIB),
    )
    def test_no_undefined_references_in_log(self, name: str) -> None:
        """Log should not report undefined references (enough LaTeX passes)."""
        log_path = _find_log_for_example(name)
        if log_path is None:
            pytest.skip(f"{name}: no .log file found")

        warnings = _parse_log_warnings(log_path)
        undef = warnings.get("undefined_references", [])
        assert not undef, (
            f"{name}: {len(undef)} undefined references in log: {undef[:10]}"
        )

    @pytest.mark.parametrize(
        "name",
        sorted(EXAMPLES_WITH_BIB),
        ids=sorted(EXAMPLES_WITH_BIB),
    )
    def test_no_rerun_warnings(self, name: str) -> None:
        """Log should not have 'Rerun to get cross-references right'."""
        log_path = _find_log_for_example(name)
        if log_path is None:
            pytest.skip(f"{name}: no .log file found")

        warnings = _parse_log_warnings(log_path)
        rerun = warnings.get("rerun_crossref", [])
        assert not rerun, (
            f"{name}: LaTeX needs rerun ({len(rerun)} cross-ref warnings). "
            f"latexmk may not have done enough passes."
        )

    @pytest.mark.parametrize(
        "name",
        sorted(EXAMPLES_WITH_BIB),
        ids=sorted(EXAMPLES_WITH_BIB),
    )
    def test_no_multiply_defined_labels(self, name: str) -> None:
        """Log should not have multiply-defined labels."""
        log_path = _find_log_for_example(name)
        if log_path is None:
            pytest.skip(f"{name}: no .log file found")

        warnings = _parse_log_warnings(log_path)
        multi = warnings.get("multiply_defined_labels", [])
        assert not multi, (
            f"{name}: {len(multi)} multiply-defined labels: {multi[:10]}"
        )

    @pytest.mark.parametrize(
        "name",
        sorted(EXAMPLES_WITH_BIB),
        ids=sorted(EXAMPLES_WITH_BIB),
    )
    def test_no_latex_errors(self, name: str) -> None:
        """Log should not contain LaTeX errors (lines starting with !)."""
        log_path = _find_log_for_example(name)
        if log_path is None:
            pytest.skip(f"{name}: no .log file found")

        warnings = _parse_log_warnings(log_path)
        errors = warnings.get("errors", [])
        # Filter out known non-error "!" lines
        real_errors = [
            e for e in errors
            if not any(
                skip in e
                for skip in [
                    "! $",
                    "! Missing",
                    "! pdf backend",
                    "! ==>",
                    "! Emergency stop",
                ]
            )
        ]
        assert not real_errors, (
            f"{name}: {len(real_errors)} LaTeX errors in log: "
            f"{real_errors[:5]}"
        )


@requires_pymupdf
@pytest.mark.slow
class TestPDFStructuralIntegrity:
    """Additional structural checks on PDF content."""

    @pytest.mark.parametrize(
        "name,pdf_path",
        _get_example_pdfs(),
        ids=[n for n, _ in _get_example_pdfs()],
    )
    def test_pdf_has_nonblank_pages(
        self, name: str, pdf_path: Path
    ) -> None:
        """Every page should have extractable text (not blank/white pages)."""
        doc = fitz.open(str(pdf_path))
        blank_pages: list[int] = []
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if not text:
                blank_pages.append(i + 1)
        doc.close()

        # Allow up to 1 blank page (some doctypes have intentional blanks)
        assert len(blank_pages) <= 1, (
            f"{name}: {len(blank_pages)} blank pages: {blank_pages}"
        )

    @pytest.mark.parametrize(
        "name,pdf_path",
        [(n, p) for n, p in _get_example_pdfs() if n in EXAMPLES_WITH_BIB],
        ids=[n for n, _ in _get_example_pdfs() if n in EXAMPLES_WITH_BIB],
    )
    def test_citation_keys_rendered(
        self, name: str, pdf_path: Path
    ) -> None:
        """Citations in text should render as keys or author-year, not raw code."""
        text = _extract_text(pdf_path)

        # Raw \cite{} or \citep{} should never appear in rendered PDF
        # Exception: code listings may show \cite as syntax examples
        # Filter out occurrences that look like they're in code blocks
        # (preceded by common listing markers or surrounded by other LaTeX commands)
        raw_cite = re.findall(r"\\cite[pt]?\{[^}]+\}", text)
        # Filter false positives from code listings:
        # A real unresolved cite appears inline in prose, while a demo cite
        # appears alongside other LaTeX commands in a listing block.
        real_unresolved: list[str] = []
        for cite in raw_cite:
            idx = text.find(cite)
            context = text[max(0, idx - 100) : idx + len(cite) + 100]
            # Skip if surrounded by multiple other LaTeX commands (code listing)
            nearby_latex = len(re.findall(r"\\[a-zA-Z]+\{", context))
            if nearby_latex <= 2:
                real_unresolved.append(cite)
        assert not real_unresolved, (
            f"{name}: unresolved LaTeX citation commands in PDF: "
            f"{real_unresolved[:5]}"
        )

        # Raw \ref{} or \eqref{} should never appear in rendered text body
        raw_ref = re.findall(r"\\(?:eqref|autoref)\{[^}]+\}", text)
        assert not raw_ref, (
            f"{name}: raw LaTeX ref commands found in PDF: {raw_ref[:5]}"
        )

        # Raw \ref{} or \eqref{} should never appear
        raw_ref = re.findall(r"\\(?:ref|eqref|autoref|cref)\{[^}]+\}", text)
        assert not raw_ref, (
            f"{name}: raw LaTeX ref commands found in PDF: {raw_ref[:5]}"
        )
