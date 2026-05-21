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


def compute_ssim(img1: Image.Image, img2: Image.Image, window_size: int = 7) -> float:
    """Compute SSIM using sliding-window approach (Wang et al. 2004).

    Uses Gaussian window with sigma=1.5, processing luminance channel.
    Falls back to global SSIM for very small images.
    """
    arr1 = np.array(img1.convert("L"), dtype=np.float64)
    arr2 = np.array(img2.convert("L"), dtype=np.float64)
    if arr1.shape != arr2.shape:
        return 0.0

    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2

    h, w = arr1.shape
    if h < window_size or w < window_size:
        mu1, mu2 = np.mean(arr1), np.mean(arr2)
        sigma1, sigma2 = np.var(arr1), np.var(arr2)
        sigma12 = np.mean((arr1 - mu1) * (arr2 - mu2))
        return ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / (
            (mu1**2 + mu2**2 + C1) * (sigma1 + sigma2 + C2)
        )

    sigma = 1.5
    coords = np.arange(window_size) - window_size // 2
    g1d = np.exp(-(coords**2) / (2 * sigma**2))
    g2d = np.outer(g1d, g1d)
    g2d /= g2d.sum()

    try:
        from scipy.ndimage import uniform_filter

        mu1 = uniform_filter(arr1, size=window_size, mode="constant")
        mu2 = uniform_filter(arr2, size=window_size, mode="constant")
        mu1_sq = mu1 * mu1
        mu2_sq = mu2 * mu2
        mu12 = mu1 * mu2
        sigma1_sq = (
            uniform_filter(arr1 * arr1, size=window_size, mode="constant") - mu1_sq
        )
        sigma2_sq = (
            uniform_filter(arr2 * arr2, size=window_size, mode="constant") - mu2_sq
        )
        sigma12 = uniform_filter(arr1 * arr2, size=window_size, mode="constant") - mu12
    except ImportError:

        def _conv2d(a, kernel):
            kh, kw = kernel.shape
            ph, pw = kh // 2, kw // 2
            padded = np.pad(a, ((ph, ph), (pw, pw)), mode="constant")
            out = np.zeros_like(a)
            for i in range(a.shape[0]):
                for j in range(a.shape[1]):
                    out[i, j] = np.sum(padded[i : i + kh, j : j + kw] * kernel)
            return out

        mu1 = _conv2d(arr1, g2d)
        mu2 = _conv2d(arr2, g2d)
        mu1_sq = mu1 * mu1
        mu2_sq = mu2 * mu2
        mu12 = mu1 * mu2
        sigma1_sq = _conv2d(arr1 * arr1, g2d) - mu1_sq
        sigma2_sq = _conv2d(arr2 * arr2, g2d) - mu2_sq
        sigma12 = _conv2d(arr1 * arr2, g2d) - mu12

    ssim_map = ((2 * mu12 + C1) * (2 * sigma12 + C2)) / (
        (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)
    )
    return float(np.mean(ssim_map))


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
    for name, info in examples.items():
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
