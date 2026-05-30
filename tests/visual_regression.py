#!/usr/bin/env python3
"""Visual regression testing for OmniLaTeX templates."""

import sys
from pathlib import Path

try:
    import fitz
    import numpy as np
    from PIL import Image
except ImportError:
    print("Install: poetry add pymupdf pillow numpy")
    sys.exit(1)


def pdf_to_images(pdf_path: Path, dpi: int = 150) -> list:
    doc = fitz.open(str(pdf_path))
    images = []
    for page in doc:
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    doc.close()
    return images


def compute_ssim(image_a, image_b) -> float:
    """Compute SSIM between two PIL Images."""
    from buildlib.diff import _compute_ssim_windowed

    arr_a = np.array(image_a.convert("L"), dtype=np.float64)
    arr_b = np.array(image_b.convert("L"), dtype=np.float64)
    return _compute_ssim_windowed(arr_a, arr_b)


def compare_pdfs(ref_path: Path, test_path: Path, threshold: float = 0.99) -> dict:
    ref_images = pdf_to_images(ref_path)
    test_images = pdf_to_images(test_path)
    if len(ref_images) != len(test_images):
        return {
            "pass": False,
            "reason": f"Page count: ref={len(ref_images)}, test={len(test_images)}",
        }
    results = []
    for i, (ref, test) in enumerate(zip(ref_images, test_images)):
        ssim = compute_ssim(ref, test)
        results.append({"page": i + 1, "ssim": ssim, "pass": ssim >= threshold})
    overall_pass = all(r["pass"] for r in results)
    return {"pass": overall_pass, "pages": results, "threshold": threshold}


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Visual regression for OmniLaTeX")
    parser.add_argument("--reference-dir", type=Path, default=Path("tests/references"))
    parser.add_argument("--build-dir", type=Path, default=Path("build/examples"))
    parser.add_argument("--threshold", type=float, default=0.99)
    parser.add_argument(
        "--generate", action="store_true", help="Generate reference images"
    )
    args = parser.parse_args()

    examples = {
        "accessibility-test": {},
        "article-color": {},
        "article": {},
        "book": {},
        "citation-styles": {},
        "cjk-chinese": {},
        "cjk-japanese": {},
        "cjk-korean": {},
        "color-themes": {},
        "cover-letter-formal": {},
        "cover-letter": {},
        "cv-twopage": {},
        "cv": {},
        "dictionary": {},
        "dissertation": {},
        "exam": {},
        "handout": {},
        "homework": {},
        "inline-paper": {},
        "journal": {},
        "lecture-notes": {},
        "letter": {},
        "lua-showcase": {},
        "manual": {},
        "memo": {},
        "minimal-custom": {},
        "minimal-starter": {},
        "multi-language": {},
        "patent": {},
        "poster": {},
        "presentation": {},
        "research-proposal": {},
        "recipe": {},
        "rtl-arabic": {},
        "rtl-hebrew": {},
        "standard": {},
        "syllabus": {},
        "technical-report": {},
        "thesis-spacing": {},
        "thesis-tuhh": {},
        "thesis": {},
        "white-paper": {},
        "invoice": {},
    }
    all_pass = True
    for name, _ in examples.items():
        pdf_path = args.build_dir / f"{name}.pdf"
        ref_path = args.reference_dir / f"{name}.pdf"
        if not pdf_path.exists():
            print(f"SKIP: {name} — PDF not found at {pdf_path}")
            continue
        if args.generate:
            ref_path.parent.mkdir(parents=True, exist_ok=True)
            ref_path.write_bytes(pdf_path.read_bytes())
            print(f"GENERATED: {ref_path}")
            continue
        if not ref_path.exists():
            print(f"SKIP: {name} — reference not found at {ref_path}")
            continue
        result = compare_pdfs(ref_path, pdf_path, args.threshold)
        status = "PASS" if result["pass"] else "FAIL"
        print(f"{status}: {name}")
        for page in result.get("pages", []):
            print(
                f"  Page {page['page']}: SSIM={page['ssim']:.4f} "
                f"({'PASS' if page['pass'] else 'FAIL'})"
            )
        if not result["pass"]:
            all_pass = False
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
