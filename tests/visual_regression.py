#!/usr/bin/env python3
"""Visual regression testing for OmniLaTeX templates."""

import sys
from pathlib import Path

try:
    import fitz
    from PIL import Image
    import numpy as np
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


def compute_ssim(img1: Image.Image, img2: Image.Image) -> float:
    arr1 = np.array(img1.convert("L"), dtype=np.float64)
    arr2 = np.array(img2.convert("L"), dtype=np.float64)
    if arr1.shape != arr2.shape:
        return 0.0
    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mu1 = np.mean(arr1)
    mu2 = np.mean(arr2)
    sigma1 = np.var(arr1)
    sigma2 = np.var(arr2)
    sigma12 = np.mean((arr1 - mu1) * (arr2 - mu2))
    ssim = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / (
        (mu1**2 + mu2**2 + C1) * (sigma1 + sigma2 + C2)
    )
    return ssim


def compare_pdfs(ref_path: Path, test_path: Path, threshold: float = 0.95) -> dict:
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
    parser.add_argument("--threshold", type=float, default=0.95)
    parser.add_argument(
        "--generate", action="store_true", help="Generate reference images"
    )
    args = parser.parse_args()

    examples = {
        "thesis": "thesis/main.pdf",
        "article": "article/main.pdf",
        "cv": "cv-twopage/main.pdf",
    }
    all_pass = True
    for name, rel_path in examples.items():
        pdf_path = args.build_dir / rel_path
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
                f"  Page {page['page']}: SSIM={page['ssim']:.4f} ({'PASS' if page['pass'] else 'FAIL'})"
            )
        if not result["pass"]:
            all_pass = False
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
