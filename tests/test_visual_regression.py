"""Visual regression tests for OmniLaTeX PDF output.

Validates that built PDFs are well-formed (not pixel-diff regression,
which would require reference PDFs).
"""

from pathlib import Path

import pytest

try:
    import pymupdf as fitz
except ImportError:
    pytest.skip("pymupdf (fitz) not installed", allow_module_level=True)

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


@pytest.mark.slow
def test_pdf_page_counts_reasonable(example_pdfs):
    for pdf_path in example_pdfs:
        doc = fitz.open(str(pdf_path))
        try:
            assert doc.page_count <= 100, (
                f"{pdf_path.name} has {doc.page_count} pages (>100), "
                "possible infinite loop"
            )
        finally:
            doc.close()


@pytest.mark.slow
def test_root_pdf_exists():
    root_pdf = PROJECT_ROOT / "main.pdf"
    assert root_pdf.is_file(), "main.pdf not found at repo root"
    assert root_pdf.stat().st_size > 0, "main.pdf is empty"


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
