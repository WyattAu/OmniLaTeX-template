"""Visual regression tests for OmniLaTeX PDF output.

Validates that built PDFs are well-formed (not pixel-diff regression,
which would require reference PDFs).
"""

from pathlib import Path

import pytest

try:
    import pymupdf as fitz

    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

requires_pymupdf = pytest.mark.skipif(
    not HAS_PYMUPDF, reason="pymupdf (fitz) not installed"
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def requires_build_dir():
    build_dir = PROJECT_ROOT / "build" / "examples"
    if not build_dir.is_dir():
        pytest.skip("build/examples/ directory not found (run make first)")
    return build_dir


@pytest.fixture
def example_pdfs(requires_build_dir):
    build_dir = PROJECT_ROOT / "build" / "examples"
    pdfs = sorted(build_dir.glob("*.pdf"))
    if not pdfs:
        pytest.skip("No PDF files found in build/examples/")
    return pdfs


@requires_pymupdf
@pytest.mark.slow
def test_all_pdfs_are_valid(example_pdfs):
    for pdf_path in example_pdfs:
        assert pdf_path.stat().st_size > 0, f"{pdf_path.name} is empty"
        header = pdf_path.read_bytes()[:5]
        assert header == b"%PDF-", f"{pdf_path.name} does not start with %PDF-"
        doc = fitz.open(str(pdf_path))
        try:
            assert doc.page_count >= 1, f"{pdf_path.name} has 0 pages"
        finally:
            doc.close()


@requires_pymupdf
@pytest.mark.slow
def test_pdf_page_counts_reasonable(example_pdfs):
    # manual.pdf is a full user manual (~240 pages); other examples should be concise.
    # The threshold guards against infinite-loop regressions, not legitimate long docs.
    PAGE_LIMIT = 300
    for pdf_path in example_pdfs:
        doc = fitz.open(str(pdf_path))
        try:
            assert doc.page_count <= PAGE_LIMIT, (
                f"{pdf_path.name} has {doc.page_count} pages (>{PAGE_LIMIT}), "
                "possible infinite loop"
            )
        finally:
            doc.close()


@pytest.mark.slow
def test_root_pdf_exists():
    root_pdf = PROJECT_ROOT / "main.pdf"
    assert root_pdf.is_file(), "main.pdf not found at repo root"
    assert root_pdf.stat().st_size > 0, "main.pdf is empty"


EXAMPLES: dict[str, int | None] = {
    "accessibility-test": 3,
    "article-color": 9,
    "article": 10,
    "beamer-academic": 4,
    "beamer-corporate": 3,
    "beamer-defense": None,
    "beamer-minimal": 2,
    "book": 17,
    "citation-styles": 7,
    "cjk-chinese": 9,
    "cjk-japanese": 8,
    "cjk-korean": 9,
    "color-themes": 18,
    "cover-letter-formal": 3,
    "cover-letter": 3,
    "cv-twopage": 3,
    "cv": 3,
    "dictionary": 11,
    "dissertation": 26,
    "exam": 4,
    "handout": 3,
    "homework": 5,
    "inline-paper": 3,
    "invoice": 3,
    "journal": 10,
    "lecture-notes": 7,
    "letter": 3,
    "lua-showcase": 9,
    "manual": 240,
    "memo": 3,
    "minimal-custom": 12,
    "minimal-starter": 27,
    "multi-language": 10,
    "patent": 5,
    "poster": 2,
    "presentation": 11,
    "recipe": 3,
    "research-proposal": 15,
    "rtl-arabic": 7,
    "rtl-hebrew": 7,
    "standard": 4,
    "syllabus": 5,
    "technical-report": 9,
    "thesis-spacing": 22,
    "thesis": 25,
    "white-paper": 7,
}


@requires_pymupdf
@pytest.mark.slow
@pytest.mark.parametrize(
    "name,expected_pages", list(EXAMPLES.items()), ids=list(EXAMPLES.keys())
)
def test_example_page_count(requires_build_dir, name, expected_pages):
    pdf_path = requires_build_dir / f"{name}.pdf"
    if not pdf_path.is_file():
        pytest.skip(f"{name}.pdf not found in build/examples/")
    ref_path = PROJECT_ROOT / "tests" / "references" / f"{name}.pdf"
    if not ref_path.is_file():
        pytest.skip(f"{name} reference PDF not yet generated")
    doc = fitz.open(str(pdf_path))
    try:
        assert (
            doc.page_count == expected_pages
        ), f"{name}: expected {expected_pages} pages, got {doc.page_count}"
    finally:
        doc.close()


@requires_pymupdf
@pytest.mark.slow
def test_pdf_metadata_consistent():
    root_pdf = PROJECT_ROOT / "main.pdf"
    if not root_pdf.is_file():
        pytest.skip("main.pdf not found")
    doc = fitz.open(str(root_pdf))
    try:
        metadata = doc.metadata
        title = metadata.get("title", "")
        assert title and title.strip(), "Root PDF metadata title is empty"
    finally:
        doc.close()
