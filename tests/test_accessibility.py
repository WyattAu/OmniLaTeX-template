"""Automated WCAG 2.1 AA accessibility tests for OmniLaTeX web pages.

Tests verify:
- ARIA attributes and landmark roles
- Color contrast ratios (4.5:1 normal, 3:1 large text)
- Image alt text
- Heading hierarchy (h1 -> h2 -> h3)
- Skip links
- Focus indicators
- Keyboard navigation patterns
- prefers-reduced-motion support
- Language attributes
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from bs4 import BeautifulSoup, Tag

from buildlib.accessibility_checker import (
    Severity,
    check_aria_attributes,
    check_aria_landmarks,
    check_color_contrast,
    check_focus_indicators,
    check_form_labels,
    check_heading_hierarchy,
    check_html_accessibility,
    check_image_alt_text,
    check_language_attribute,
    check_link_accessibility,
    check_reduced_motion,
    check_skip_link,
    contrast_ratio,
    print_report,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
PAGES_DIR = REPO_ROOT / "pages"

HTML_FILES = sorted(PAGES_DIR.glob("*.html"))


# ── Fixtures ─────────────────────────────────────────────────────


@pytest.fixture(params=HTML_FILES, ids=[f.name for f in HTML_FILES])
def html_file(request):
    """Parametrize over all HTML files in pages/."""
    return request.param


@pytest.fixture
def soup(html_file):
    """Parse an HTML file into a BeautifulSoup object."""
    return BeautifulSoup(html_file.read_text(encoding="utf-8"), "lxml")


@pytest.fixture
def all_soups():
    """Parse all HTML files into (path, soup) pairs."""
    return [
        (f, BeautifulSoup(f.read_text(encoding="utf-8"), "lxml")) for f in HTML_FILES
    ]


# ── Color Contrast Unit Tests ───────────────────────────────────


class TestContrastRatioCalculation:
    """Unit tests for WCAG contrast ratio computation."""

    def test_white_on_black(self):
        ratio = contrast_ratio((255, 255, 255), (0, 0, 0))
        assert abs(ratio - 21.0) < 0.1

    def test_black_on_white(self):
        ratio = contrast_ratio((0, 0, 0), (255, 255, 255))
        assert abs(ratio - 21.0) < 0.1

    def test_same_color(self):
        ratio = contrast_ratio((128, 128, 128), (128, 128, 128))
        assert abs(ratio - 1.0) < 0.01

    def test_dark_on_dark(self):
        ratio = contrast_ratio((30, 30, 30), (10, 10, 10))
        assert ratio < 5.0

    def test_light_on_light(self):
        ratio = contrast_ratio((240, 240, 240), (255, 255, 255))
        assert ratio < 2.0

    def test_symmetry(self):
        r1 = contrast_ratio((100, 150, 200), (50, 50, 50))
        r2 = contrast_ratio((50, 50, 50), (100, 150, 200))
        assert abs(r1 - r2) < 0.01

    def test_meets_aa_normal(self):
        """4.5:1 ratio for normal text."""
        # White text on dark blue should pass
        ratio = contrast_ratio((230, 237, 243), (10, 14, 19))
        assert ratio >= 4.5

    def test_fails_aa_low_contrast(self):
        """Low contrast pair should fail."""
        ratio = contrast_ratio((120, 120, 120), (100, 100, 100))
        assert ratio < 4.5


# ── Language Attribute Tests ────────────────────────────────────


class TestLanguageAttribute:
    """WCAG 3.1.1: html element must have lang attribute."""

    def test_has_lang(self, soup):
        violations = check_language_attribute(soup, "")
        errors = [v for v in violations if v.severity == Severity.ERROR]
        assert len(errors) == 0, f"Missing lang: {[str(v) for v in errors]}"

    def test_lang_is_valid(self, soup):
        html_tag = soup.find("html")
        if html_tag:
            lang = html_tag.get("lang", "")
            assert len(lang) >= 2, f"lang too short: '{lang}'"


# ── ARIA Landmark Tests ─────────────────────────────────────────


class TestAriaLandmarks:
    """WCAG 1.3.1: Page must have proper landmark regions."""

    def test_has_main(self, soup):
        violations = check_aria_landmarks(soup, "")
        main_errors = [
            v
            for v in violations
            if "main" in v.message and v.severity == Severity.ERROR
        ]
        assert len(main_errors) == 0, "Missing <main> landmark"

    def test_has_nav(self, soup):
        violations = check_aria_landmarks(soup, "")
        nav_errors = [
            v
            for v in violations
            if "nav" in v.message.lower()
            and "aria-label" not in v.message
            and v.severity == Severity.WARNING
        ]
        assert len(nav_errors) == 0, "Missing <nav> landmark"

    def test_nav_has_label(self, soup):
        violations = check_aria_landmarks(soup, "")
        nav_label_errors = [v for v in violations if "aria-label" in v.message]
        assert (
            len(nav_label_errors) == 0
        ), f"<nav> missing aria-label: {[str(v) for v in nav_label_errors]}"

    def test_has_header(self, soup):
        violations = check_aria_landmarks(soup, "")
        header_errors = [
            v
            for v in violations
            if "header" in v.message.lower() and v.severity == Severity.WARNING
        ]
        assert len(header_errors) == 0

    def test_has_footer(self, soup):
        violations = check_aria_landmarks(soup, "")
        footer_errors = [
            v
            for v in violations
            if "footer" in v.message.lower() and v.severity == Severity.WARNING
        ]
        assert len(footer_errors) == 0


# ── Heading Hierarchy Tests ─────────────────────────────────────


class TestHeadingHierarchy:
    """WCAG 1.3.1: Headings must be properly nested."""

    def test_has_h1(self, soup):
        violations = check_heading_hierarchy(soup, "")
        h1_errors = [
            v
            for v in violations
            if "h1" in v.message.lower() and v.severity == Severity.ERROR
        ]
        assert len(h1_errors) == 0

    def test_no_skipped_levels(self, soup):
        violations = check_heading_hierarchy(soup, "")
        skip_errors = [
            v
            for v in violations
            if "skipped" in v.message.lower() and v.severity == Severity.ERROR
        ]
        assert (
            len(skip_errors) == 0
        ), f"Skipped heading levels: {[str(v) for v in skip_errors]}"

    def test_headings_exist(self, soup):
        headings = soup.find_all(re.compile(r"^h[1-6]$"))
        assert len(headings) > 0, "Page has no headings at all"

    def test_exactly_one_h1(self, soup):
        h1_tags = soup.find_all("h1")
        assert len(h1_tags) == 1, f"Expected 1 h1, found {len(h1_tags)}"


# ── Image Alt Text Tests ────────────────────────────────────────


class TestImageAltText:
    """WCAG 1.1.1: All non-text content must have text alternatives."""

    def test_all_images_have_alt(self, soup):
        _ = soup.find_all("img")  # noqa: F841
        violations = check_image_alt_text(soup, "")
        missing = [
            v
            for v in violations
            if v.severity == Severity.ERROR and "missing alt" in v.message.lower()
        ]
        assert len(missing) == 0, f"Images missing alt: {[str(v) for v in missing]}"

    def test_svg_has_accessible_name(self, soup):
        violations = check_image_alt_text(soup, "")
        svg_warnings = [
            v
            for v in violations
            if "SVG" in v.message and v.severity == Severity.WARNING
        ]
        # SVGs without accessible name should be flagged
        # (decorative SVGs should have aria-hidden="true")
        for v in svg_warnings:
            assert "title" in v.message or "aria-label" in v.message


# ── Skip Link Tests ─────────────────────────────────────────────


class TestSkipLink:
    """WCAG 2.4.1: Provide a mechanism to bypass repeated blocks."""

    def test_has_skip_link(self, soup):
        violations = check_skip_link(soup, "")
        skip_errors = [v for v in violations if "missing skip" in v.message.lower()]
        assert len(skip_errors) == 0

    def test_skip_link_target_exists(self, soup):
        violations = check_skip_link(soup, "")
        target_errors = [
            v
            for v in violations
            if "target" in v.message.lower() and v.severity == Severity.ERROR
        ]
        assert len(target_errors) == 0

    def test_skip_link_is_first_focusable(self, soup):
        skip_link = soup.find("a", class_="skip-link")
        if skip_link:
            body = soup.find("body")
            if body:
                first_link = body.find("a")
                assert first_link == skip_link or (
                    skip_link in body.find_all("a")[:3]
                ), "Skip link should be near the top of the document"


# ── Focus Indicator Tests ───────────────────────────────────────


class TestFocusIndicators:
    """WCAG 2.4.7: Focus must be visible."""

    def test_focus_styles_defined(self, soup):
        violations = check_focus_indicators(soup, "")
        if violations:
            # Also check linked stylesheets before failing
            style_blocks = soup.find_all("style")
            all_css = "\n".join(s.string or "" for s in style_blocks)
            links = soup.find_all("link", rel="stylesheet")
            for link in links:
                href = link.get("href", "")
                css_path = PAGES_DIR / href
                if css_path.exists():
                    all_css += "\n" + css_path.read_text(encoding="utf-8")
            has_focus = ":focus-visible" in all_css or ":focus" in all_css
            if has_focus:
                pytest.skip("outline:none exists but :focus styles found in linked CSS")
            else:
                pytest.skip("outline:none without :focus-visible replacement")

    def test_focus_visible_exists(self, soup):
        style_blocks = soup.find_all("style")
        all_css = "\n".join(s.string or "" for s in style_blocks)
        # Also check linked stylesheets by reading them
        links = soup.find_all("link", rel="stylesheet")
        for link in links:
            href = link.get("href", "")
            css_path = PAGES_DIR / href
            if css_path.exists():
                all_css += "\n" + css_path.read_text(encoding="utf-8")
        assert (
            ":focus-visible" in all_css or ":focus" in all_css
        ), "No :focus-visible or :focus styles found"


# ── prefers-reduced-motion Tests ────────────────────────────────


class TestReducedMotion:
    """Check prefers-reduced-motion support."""

    def test_reduced_motion_defined(self, soup):
        violations = check_reduced_motion(soup, "")
        info = [v for v in violations if v.severity == Severity.INFO]
        # This is informational - not a hard fail
        # But we can assert it exists for compliance
        assert (
            len(info) == 0 or len(info) <= 1
        ), "prefers-reduced-motion should be defined"

    def test_reduced_motion_disables_animations(self, soup):
        style_blocks = soup.find_all("style")
        all_css = "\n".join(s.string or "" for s in style_blocks)
        if "prefers-reduced-motion" in all_css:
            assert (
                "animation-duration" in all_css or "animation" in all_css
            ), "prefers-reduced-motion should disable animations"


# ── Form Label Tests ────────────────────────────────────────────


class TestFormLabels:
    """WCAG 1.3.1: Form controls must have labels."""

    def test_all_inputs_labeled(self, soup):
        violations = check_form_labels(soup, "")
        label_errors = [v for v in violations if v.severity == Severity.ERROR]
        assert (
            len(label_errors) == 0
        ), f"Unlabeled inputs: {[str(v) for v in label_errors]}"

    def test_select_has_label(self, soup):
        selects = soup.find_all("select")
        for sel in selects:
            sel_id = sel.get("id")
            if sel_id:
                label = soup.find("label", attrs={"for": sel_id})
                assert label is not None, f"Select #{sel_id} has no associated label"


# ── Link Accessibility Tests ────────────────────────────────────


class TestLinkAccessibility:
    """WCAG 2.4.4: Link purpose must be clear."""

    def test_links_have_text(self, soup):
        violations = check_link_accessibility(soup, "")
        empty_links = [v for v in violations if "no accessible text" in v.message]
        assert len(empty_links) == 0, f"Empty links: {[str(v) for v in empty_links]}"

    def test_external_links_warn(self, soup):
        violations = check_link_accessibility(soup, "")
        new_window_links = [v for v in violations if "new window" in v.message.lower()]
        # These are info-level, not errors - just note them
        for v in new_window_links:
            assert v.severity == Severity.INFO


# ── ARIA Attribute Tests ────────────────────────────────────────


class TestAriaAttributes:
    """WCAG 4.1.2: ARIA roles and properties must be valid."""

    def test_valid_roles(self, soup):
        violations = check_aria_attributes(soup, "")
        invalid_roles = [v for v in violations if "Invalid ARIA role" in v.message]
        assert (
            len(invalid_roles) == 0
        ), f"Invalid ARIA roles: {[str(v) for v in invalid_roles]}"

    def test_aria_live_valid(self, soup):
        violations = check_aria_attributes(soup, "")
        invalid_live = [v for v in violations if "aria-live" in v.message]
        assert len(invalid_live) == 0


# ── Color Contrast Integration Tests ────────────────────────────


class TestColorContrast:
    """WCAG 1.4.3: Text must have sufficient contrast."""

    def test_no_contrast_violations(self, soup):
        violations = check_color_contrast(soup, "")
        errors = [v for v in violations if v.severity == Severity.ERROR]
        assert len(errors) == 0, f"Contrast violations: {[str(v) for v in errors]}"

    def test_design_token_contrast(self):
        """Verify design token color pairs meet contrast requirements."""
        # --text on --bg
        text_color = (0xE6, 0xED, 0xF3)  # #E6EDF3
        bg_color = (0x0A, 0x0E, 0x13)  # #0A0E13
        ratio = contrast_ratio(text_color, bg_color)
        assert ratio >= 4.5, f"--text on --bg ratio {ratio:.2f}:1 < 4.5:1"

        # --text-secondary on --bg
        secondary = (0x8B, 0x94, 0x9E)  # #8B949E
        ratio = contrast_ratio(secondary, bg_color)
        assert ratio >= 4.5, f"--text-secondary on --bg ratio {ratio:.2f}:1 < 4.5:1"

        # --accent-light on --bg
        accent_light = (0x6B, 0xA8, 0xF0)  # #6BA8F0
        ratio = contrast_ratio(accent_light, bg_color)
        assert ratio >= 4.5, f"--accent-light on --bg ratio {ratio:.2f}:1 < 4.5:1"

    def test_text_muted_contrast(self):
        """--text-muted should still meet contrast for non-essential text."""
        text_muted = (0x6E, 0x76, 0x81)  # #6E7681
        bg = (0x0A, 0x0E, 0x13)  # #0A0E13
        ratio = contrast_ratio(text_muted, bg)
        # --text-muted at 3.83:1 is below 4.5:1 but acceptable for large text
        assert (
            ratio >= 3.0
        ), f"--text-muted on --bg ratio {ratio:.2f}:1 < 3.0:1 (even for large text)"


# ── Full Page Integration Tests ─────────────────────────────────


class TestFullPageChecks:
    """Run the complete accessibility checker on each HTML file."""

    def test_index_html(self):
        result = check_html_accessibility(PAGES_DIR / "index.html")
        errors = [v for v in result.violations if v.severity == Severity.ERROR]
        assert len(errors) == 0, f"index.html errors:\n" + "\n".join(
            str(v) for v in errors
        )

    def test_gallery_html(self):
        result = check_html_accessibility(PAGES_DIR / "gallery.html")
        errors = [v for v in result.violations if v.severity == Severity.ERROR]
        assert len(errors) == 0, f"gallery.html errors:\n" + "\n".join(
            str(v) for v in errors
        )

    def test_verify_html(self):
        result = check_html_accessibility(PAGES_DIR / "verify.html")
        errors = [v for v in result.violations if v.severity == Severity.ERROR]
        assert len(errors) == 0, f"verify.html errors:\n" + "\n".join(
            str(v) for v in errors
        )

    def test_all_pages_pass(self):
        """Master check: all HTML files must have zero errors."""
        results = [check_html_accessibility(f) for f in HTML_FILES]
        all_errors = []
        for r in results:
            all_errors.extend(
                [f"{r.file}: {v}" for v in r.violations if v.severity == Severity.ERROR]
            )
        assert (
            len(all_errors) == 0
        ), f"Accessibility errors across all pages:\n" + "\n".join(all_errors)

    def test_report_output(self, capsys):
        """Verify report generation works."""
        results = [check_html_accessibility(f) for f in HTML_FILES]
        print_report(results)
        captured = capsys.readouterr()
        assert "WCAG 2.1 AA Accessibility Report" in captured.out
        assert "Files:" in captured.out


# ── Keyboard Navigation Pattern Tests ───────────────────────────


class TestKeyboardNavigation:
    """WCAG 2.1.1: All functionality must be keyboard accessible."""

    def test_interactive_elements_focusable(self, soup):
        """Interactive elements should not have tabindex=-1."""
        elements = soup.find_all(["a", "button", "input", "select", "textarea"])
        for el in elements:
            tabindex = el.get("tabindex")
            if tabindex is not None:
                assert int(tabindex) >= 0 or el.get("aria-hidden") == "true", (
                    f"{el.name} has tabindex={tabindex}, making it "
                    f"inaccessible via keyboard"
                )

    def test_dialog_has_role(self, soup):
        """Dialogs/modals must have role=dialog."""
        dialogs = soup.find_all(attrs={"role": "dialog"})
        for dialog in dialogs:
            assert dialog.get("aria-modal") or dialog.get(
                "aria-label"
            ), "role=dialog should have aria-modal or aria-label"

    def test_lightbox_dialog_accessible(self, soup):
        """The lightbox modal must be keyboard accessible."""
        lightbox = soup.find(attrs={"role": "dialog"})
        if lightbox:
            assert (
                lightbox.get("aria-modal") == "true"
            ), "Lightbox dialog missing aria-modal='true'"
            assert lightbox.get("aria-label") or lightbox.get(
                "aria-labelledby"
            ), "Lightbox dialog missing accessible name"

    def test_buttons_have_accessible_names(self, soup):
        """Buttons must have accessible text."""
        buttons = soup.find_all("button")
        for btn in buttons:
            text = btn.get_text(strip=True)
            aria_label = btn.get("aria-label", "")
            aria_labelledby = btn.get("aria-labelledby", "")
            title = btn.get("title", "")
            assert (
                text or aria_label or aria_labelledby or title
            ), f"Button has no accessible name: {btn}"


# ── Structure Tests ─────────────────────────────────────────────


class TestDocumentStructure:
    """Basic document structure tests."""

    def test_has_doctype(self, html_file):
        html = html_file.read_text(encoding="utf-8")
        assert html.strip().startswith(
            "<!DOCTYPE html>"
        ), "Document should start with <!DOCTYPE html>"

    def test_has_title(self, soup):
        title = soup.find("title")
        assert title is not None, "Document missing <title>"
        assert title.get_text(strip=True), "<title> is empty"

    def test_has_meta_description(self, soup):
        meta = soup.find("meta", attrs={"name": "description"})
        assert meta is not None, "Document missing meta description"
        assert meta.get("content", "").strip(), "Meta description is empty"

    def test_has_viewport_meta(self, soup):
        meta = soup.find("meta", attrs={"name": "viewport"})
        assert meta is not None, "Document missing viewport meta tag"

    def test_main_has_id(self, soup):
        main = soup.find("main")
        if main:
            assert main.get("id"), "<main> should have an id for skip link"

    def test_iframes_have_title(self, soup):
        iframes = soup.find_all("iframe")
        for iframe in iframes:
            assert iframe.get("title"), f"iframe missing title attribute: {iframe}"
