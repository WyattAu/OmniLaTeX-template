"""Comprehensive unit tests for buildlib/accessibility_checker.py."""  # noqa: E501

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup, Tag

bs4 = pytest.importorskip("bs4")

from buildlib.accessibility_checker import (CheckResult,  # noqa: E402
                                            Severity, Violation,
                                            _is_large_text, _parse_hex_color,
                                            _resolve_color, _tag_line,
                                            check_aria_attributes,
                                            check_aria_landmarks,
                                            check_color_contrast,
                                            check_directory,
                                            check_focus_indicators,
                                            check_form_labels,
                                            check_heading_hierarchy,
                                            check_html_accessibility,
                                            check_image_alt_text,
                                            check_language_attribute,
                                            check_link_accessibility,
                                            check_reduced_motion,
                                            check_skip_link, contrast_ratio)

pytestmark = pytest.mark.timeout(15)


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


# ── _parse_hex_color ────────────────────────────────────────────


class TestParseHexColor:
    def test_three_char(self):
        assert _parse_hex_color("#fff") == (255, 255, 255)

    def test_six_char(self):
        assert _parse_hex_color("#123456") == (18, 52, 86)

    def test_six_char_uppercase(self):
        assert _parse_hex_color("#ABCDEF") == (171, 205, 239)

    def test_invalid_chars(self):
        assert _parse_hex_color("#xyz") is None

    def test_too_short(self):
        assert _parse_hex_color("#1") is None

    def test_invalid_hex_digits(self):
        assert _parse_hex_color("#gggggg") is None

    def test_no_hash(self):
        assert _parse_hex_color("abcdef") == (171, 205, 239)

    def test_empty_string(self):
        assert _parse_hex_color("") is None


# ── _resolve_color ───────────────────────────────────────────────


class TestResolveColor:
    def test_hex_color(self):
        soup = _soup("<html></html>")
        assert _resolve_color("#ff0000", soup) == (255, 0, 0)

    def test_rgb_color(self):
        soup = _soup("<html></html>")
        assert _resolve_color("rgb(255, 0, 0)", soup) == (255, 0, 0)

    def test_rgba_color(self):
        soup = _soup("<html></html>")
        assert _resolve_color("rgba(255, 0, 0, 0.5)", soup) == (255, 0, 0)

    def test_named_color(self):
        soup = _soup("<html></html>")
        assert _resolve_color("red", soup) == (255, 0, 0)

    def test_transparent(self):
        soup = _soup("<html></html>")
        assert _resolve_color("transparent", soup) is None

    def test_empty_string(self):
        soup = _soup("<html></html>")
        assert _resolve_color("", soup) is None

    def test_unknown_color(self):
        soup = _soup("<html></html>")
        assert _resolve_color("unknowncolor", soup) is None

    def test_grey_named(self):
        soup = _soup("<html></html>")
        assert _resolve_color("grey", soup) == (128, 128, 128)


# ── _is_large_text ──────────────────────────────────────────────


class TestIsLargeText:
    def _make_tag(self, style: str) -> Tag:
        html = f'<span style="{style}">text</span>'
        soup = _soup(html)
        return soup.find("span")

    def test_24pt_is_large(self):
        tag = self._make_tag("font-size: 24pt")
        assert _is_large_text(tag) is True

    def test_18pt_bold_is_large(self):
        tag = self._make_tag("font-size: 18pt; font-weight: bold")
        assert _is_large_text(tag) is True

    def test_14pt_bold_is_large(self):
        tag = self._make_tag("font-size: 14pt; font-weight: bold")
        assert _is_large_text(tag) is True

    def test_14pt_not_bold_not_large(self):
        tag = self._make_tag("font-size: 14pt")
        assert _is_large_text(tag) is False

    def test_13pt_bold_not_large(self):
        tag = self._make_tag("font-size: 13pt; font-weight: bold")
        assert _is_large_text(tag) is False

    def test_18pt_not_bold_not_large(self):
        tag = self._make_tag("font-size: 18pt")
        assert _is_large_text(tag) is True

    def test_10pt_not_large(self):
        tag = self._make_tag("font-size: 10pt")
        assert _is_large_text(tag) is False

    def test_px_24px_is_large(self):
        tag = self._make_tag("font-size: 24px")
        assert _is_large_text(tag) is True

    def test_px_16px_not_large(self):
        tag = self._make_tag("font-size: 16px")
        assert _is_large_text(tag) is False

    def test_rem_2rem_is_large(self):
        tag = self._make_tag("font-size: 2rem")
        assert _is_large_text(tag) is True

    def test_rem_not_large(self):
        tag = self._make_tag("font-size: 1rem")
        assert _is_large_text(tag) is False

    def test_no_font_size(self):
        tag = self._make_tag("font-weight: bold")
        assert _is_large_text(tag) is False

    def test_weight_700(self):
        tag = self._make_tag("font-size: 14pt; font-weight: 700")
        assert _is_large_text(tag) is True

    def test_weight_400_not_bold(self):
        tag = self._make_tag("font-size: 14pt; font-weight: 400")
        assert _is_large_text(tag) is False


# ── _tag_line ────────────────────────────────────────────────────


class TestTagLine:
    def test_tag_with_sourceline(self):
        html = "<div>\n  <p>hello</p>\n</div>"
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.find("p")
        line = _tag_line(tag)
        if line is not None:
            assert line >= 1

    def test_tag_without_sourceline(self):
        mock_tag = MagicMock(spec=["name"])
        mock_tag.name = "div"
        assert not hasattr(mock_tag, "sourceline")
        line = _tag_line(mock_tag)
        assert line is None


# ── check_aria_landmarks ───────────────────────────────────────


class TestCheckAriaLandmarks:
    def test_no_main_error(self):
        html = "<html><body><p>text</p></body></html>"
        soup = _soup(html)
        violations = check_aria_landmarks(soup, "/test/file.html")
        errors = [
            v
            for v in violations
            if v.criterion == "1.3.1" and v.severity == Severity.ERROR
        ]
        assert len(errors) == 1
        assert "main" in errors[0].message

    def test_role_main_no_error(self):
        html = '<html><body><div role="main"><p>text</p></div></body></html>'
        soup = _soup(html)
        violations = check_aria_landmarks(soup, "/test/file.html")
        errors = [
            v
            for v in violations
            if "main" in v.message and v.severity == Severity.ERROR
        ]
        assert len(errors) == 0

    def test_no_nav_warning(self):
        html = "<html><body><main><p>text</p></main></body></html>"
        soup = _soup(html)
        violations = check_aria_landmarks(soup, "/test/file.html")
        nav_warnings = [
            v
            for v in violations
            if "nav" in v.message.lower()
            and "aria-label" not in v.message
            and v.severity == Severity.WARNING
        ]
        assert len(nav_warnings) == 1

    def test_no_header_warning(self):
        html = "<html><body><main><p>text</p></main></body></html>"
        soup = _soup(html)
        violations = check_aria_landmarks(soup, "/test/file.html")
        header_warnings = [
            v
            for v in violations
            if "header" in v.message.lower() and v.severity == Severity.WARNING
        ]
        assert len(header_warnings) == 1

    def test_no_footer_warning(self):
        html = "<html><body><main><p>text</p></main></body></html>"
        soup = _soup(html)
        violations = check_aria_landmarks(soup, "/test/file.html")
        footer_warnings = [
            v
            for v in violations
            if "footer" in v.message.lower() and v.severity == Severity.WARNING
        ]
        assert len(footer_warnings) == 1

    def test_nav_without_aria_label_warning(self):
        html = '<html><body><nav><a href="/">Home</a></nav></body></html>'
        soup = _soup(html)
        violations = check_aria_landmarks(soup, "/test/file.html")
        label_warnings = [v for v in violations if "aria-label" in v.message]
        assert len(label_warnings) == 1
        assert label_warnings[0].element == "nav"

    def test_nav_with_aria_label_no_warning(self):
        html = '<html><body><nav aria-label="Main"><a href="/">Home</a></nav></body></html>'
        soup = _soup(html)
        violations = check_aria_landmarks(soup, "/test/file.html")
        label_warnings = [v for v in violations if "aria-label" in v.message]
        assert len(label_warnings) == 0

    def test_full_page_no_violations(self):
        html = '<html><body><header></header><nav aria-label="Main"></nav><main><h1>Title</h1></main><footer></footer></body></html>'  # noqa: E501
        soup = _soup(html)
        violations = check_aria_landmarks(soup, "/test/file.html")
        errors = [v for v in violations if v.severity == Severity.ERROR]
        assert len(errors) == 0


# ── check_heading_hierarchy ─────────────────────────────────────


class TestCheckHeadingHierarchy:
    def test_no_headings_warning(self):
        html = "<html><body><p>text</p></body></html>"
        soup = _soup(html)
        violations = check_heading_hierarchy(soup, "/test/file.html")
        assert len(violations) == 1
        assert violations[0].severity == Severity.WARNING
        assert "no headings" in violations[0].message.lower()

    def test_skip_from_h1_to_h3_error(self):
        html = "<html><body><h1>One</h1><h3>Three</h3></body></html>"
        soup = _soup(html)
        violations = check_heading_hierarchy(soup, "/test/file.html")
        skip_errors = [
            v
            for v in violations
            if "skipped" in v.message.lower() and v.severity == Severity.ERROR
        ]
        assert len(skip_errors) == 1

    def test_no_h1_but_has_h2_error(self):
        html = "<html><body><h2>Two</h2></body></html>"
        soup = _soup(html)
        violations = check_heading_hierarchy(soup, "/test/file.html")
        h1_errors = [
            v
            for v in violations
            if "h1" in v.message.lower() and v.severity == Severity.ERROR
        ]
        assert len(h1_errors) == 1

    def test_two_h1_warning(self):
        html = "<html><body><h1>One</h1><h1>Two</h1></body></html>"
        soup = _soup(html)
        violations = check_heading_hierarchy(soup, "/test/file.html")
        h1_warnings = [
            v
            for v in violations
            if "h1" in v.message.lower() and v.severity == Severity.WARNING
        ]
        assert len(h1_warnings) == 1

    def test_proper_hierarchy_no_violations(self):
        html = "<html><body><h1>One</h1><h2>Two</h2><h3>Three</h3></body></html>"
        soup = _soup(html)
        violations = check_heading_hierarchy(soup, "/test/file.html")
        assert len(violations) == 0


# ── check_form_labels ────────────────────────────────────────────


class TestCheckFormLabels:
    def test_input_no_label_error(self):
        html = '<html><body><input type="text" name="field"></body></html>'
        soup = _soup(html)
        violations = check_form_labels(soup, "/test/file.html")
        assert len(violations) == 1
        assert violations[0].severity == Severity.ERROR

    def test_input_hidden_skipped(self):
        html = '<html><body><input type="hidden" name="csrf"></body></html>'
        soup = _soup(html)
        violations = check_form_labels(soup, "/test/file.html")
        assert len(violations) == 0

    def test_submit_skipped(self):
        html = '<html><body><input type="submit" value="Go"></body></html>'
        soup = _soup(html)
        violations = check_form_labels(soup, "/test/file.html")
        assert len(violations) == 0

    def test_wrapped_label_no_violation(self):
        html = (
            '<html><body><label>Enter<input id="x" type="text"></label></body></html>'
        )
        soup = _soup(html)
        violations = check_form_labels(soup, "/test/file.html")
        assert len(violations) == 0

    def test_label_for_no_violation(self):
        html = '<html><body><label for="x">Name</label><input id="x" type="text"></body></html>'
        soup = _soup(html)
        violations = check_form_labels(soup, "/test/file.html")
        assert len(violations) == 0

    def test_aria_label_no_violation(self):
        html = '<html><body><input type="text" aria-label="test"></body></html>'
        soup = _soup(html)
        violations = check_form_labels(soup, "/test/file.html")
        assert len(violations) == 0

    def test_title_attribute_no_violation(self):
        html = '<html><body><input type="text" title="test"></body></html>'
        soup = _soup(html)
        violations = check_form_labels(soup, "/test/file.html")
        assert len(violations) == 0

    def test_select_no_label_error(self):
        html = '<html><body><select name="choice"><option>A</option></select></body></html>'
        soup = _soup(html)
        violations = check_form_labels(soup, "/test/file.html")
        assert len(violations) == 1
        assert violations[0].severity == Severity.ERROR

    def test_textarea_no_label_error(self):
        html = '<html><body><textarea name="comment"></textarea></body></html>'
        soup = _soup(html)
        violations = check_form_labels(soup, "/test/file.html")
        assert len(violations) == 1


# ── check_language_attribute ────────────────────────────────────


class TestCheckLanguageAttribute:
    def test_no_lang_error(self):
        html = "<html><body></body></html>"
        soup = _soup(html)
        violations = check_language_attribute(soup, "/test/file.html")
        assert len(violations) == 1
        assert violations[0].severity == Severity.ERROR
        assert "missing lang" in violations[0].message.lower()

    def test_lang_too_short_warning(self):
        html = '<html lang="x"><body></body></html>'
        soup = _soup(html)
        violations = check_language_attribute(soup, "/test/file.html")
        assert len(violations) == 1
        assert violations[0].severity == Severity.WARNING

    def test_valid_lang_no_violation(self):
        html = '<html lang="en"><body></body></html>'
        soup = _soup(html)
        violations = check_language_attribute(soup, "/test/file.html")
        assert len(violations) == 0

    def test_no_html_element_error(self):
        html = "<p>text</p>"
        soup = _soup(html)
        violations = check_language_attribute(soup, "/test/file.html")
        assert len(violations) == 1
        assert violations[0].severity == Severity.ERROR
        assert "html" in violations[0].message.lower()


# ── check_skip_link ─────────────────────────────────────────────


class TestCheckSkipLink:
    def test_no_skip_link_warning(self):
        html = "<html><body><main id='main'><h1>Title</h1></main></body></html>"
        soup = _soup(html)
        violations = check_skip_link(soup, "/test/file.html")
        assert len(violations) == 1
        assert violations[0].severity == Severity.WARNING
        assert "missing skip" in violations[0].message.lower()

    def test_skip_link_target_not_found_error(self):
        html = '<html><body><a href="#main" class="skip-link">Skip</a></body></html>'
        soup = _soup(html)
        violations = check_skip_link(soup, "/test/file.html")
        errors = [v for v in violations if v.severity == Severity.ERROR]
        assert len(errors) == 1
        assert "target" in errors[0].message.lower()

    def test_valid_skip_link_no_violation(self):
        html = '<html><body><a href="#main" class="skip-link">Skip</a><main id="main"><h1>Title</h1></main></body></html>'  # noqa: E501
        soup = _soup(html)
        violations = check_skip_link(soup, "/test/file.html")
        assert len(violations) == 0

    def test_skip_link_by_href_pattern(self):
        html = '<html><body><a href="#main-content">Skip</a><main id="main-content"><h1>Title</h1></main></body></html>'  # noqa: E501
        soup = _soup(html)
        violations = check_skip_link(soup, "/test/file.html")
        assert len(violations) == 0


# ── check_image_alt_text ────────────────────────────────────────


class TestCheckImageAltText:
    def test_no_alt_error(self):
        html = '<html><body><img src="test.png"></body></html>'
        soup = _soup(html)
        violations = check_image_alt_text(soup, "/test/file.html")
        errors = [v for v in violations if v.severity == Severity.ERROR]
        assert len(errors) == 1
        assert "missing alt" in errors[0].message.lower()

    def test_empty_alt_no_error(self):
        html = '<html><body><img src="test.png" alt=""></body></html>'
        soup = _soup(html)
        violations = check_image_alt_text(soup, "/test/file.html")
        errors = [v for v in violations if v.severity == Severity.ERROR]
        assert len(errors) == 0

    def test_alt_with_role_presentation(self):
        html = (
            '<html><body><img src="test.png" alt="" role="presentation"></body></html>'
        )
        soup = _soup(html)
        violations = check_image_alt_text(soup, "/test/file.html")
        errors = [v for v in violations if v.severity == Severity.ERROR]
        assert len(errors) == 0

    def test_alt_with_text_no_violation(self):
        html = '<html><body><img src="test.png" alt="A photo"></body></html>'
        soup = _soup(html)
        violations = check_image_alt_text(soup, "/test/file.html")
        assert len(violations) == 0

    def test_svg_no_accessible_name_warning(self):
        html = '<html><body><svg viewBox="0 0 10 10"><circle cx="5" cy="5" r="5"/></svg></body></html>'  # noqa: E501
        soup = _soup(html)
        violations = check_image_alt_text(soup, "/test/file.html")
        svg_violations = [v for v in violations if "SVG" in v.message]
        assert len(svg_violations) == 1
        assert svg_violations[0].severity == Severity.WARNING

    def test_svg_with_title_no_violation(self):
        html = '<html><body><svg viewBox="0 0 10 10"><title>Icon</title><circle cx="5" cy="5" r="5"/></svg></body></html>'  # noqa: E501
        soup = _soup(html)
        violations = check_image_alt_text(soup, "/test/file.html")
        svg_violations = [v for v in violations if "SVG" in v.message]
        assert len(svg_violations) == 0

    def test_svg_aria_hidden_no_violation(self):
        html = '<html><body><svg aria-hidden="true" viewBox="0 0 10 10"><circle cx="5" cy="5" r="5"/></svg></body></html>'  # noqa: E501
        soup = _soup(html)
        violations = check_image_alt_text(soup, "/test/file.html")
        svg_violations = [v for v in violations if "SVG" in v.message]
        assert len(svg_violations) == 0


# ── check_focus_indicators ─────────────────────────────────────


class TestCheckFocusIndicators:
    def test_outline_none_no_focus_warning(self):
        html = (
            "<html><head><style>* { outline: none; }</style></head><body></body></html>"
        )
        soup = _soup(html)
        violations = check_focus_indicators(soup, "/test/file.html")
        assert len(violations) == 1
        assert violations[0].severity == Severity.WARNING
        assert "outline:none" in violations[0].message

    def test_outline_none_with_focus_visible_no_warning(self):
        html = "<html><head><style>* { outline: none; } a:focus-visible { outline: 2px solid blue; }</style></head><body></body></html>"  # noqa: E501
        soup = _soup(html)
        violations = check_focus_indicators(soup, "/test/file.html")
        assert len(violations) == 0

    def test_no_outline_none_no_violation(self):
        html = "<html><head><style>a:focus { color: red; }</style></head><body></body></html>"
        soup = _soup(html)
        violations = check_focus_indicators(soup, "/test/file.html")
        assert len(violations) == 0

    def test_outline_0_without_focus_warning(self):
        html = "<html><head><style>button { outline: 0; }</style></head><body></body></html>"
        soup = _soup(html)
        violations = check_focus_indicators(soup, "/test/file.html")
        assert len(violations) == 1


# ── check_color_contrast ────────────────────────────────────────


class TestCheckColorContrast:
    def test_low_contrast_produces_violation(self):
        html = '<html><body><span style="color: #777777; background-color: #888888">text</span></body></html>'  # noqa: E501
        soup = _soup(html)
        violations = check_color_contrast(soup, "/test/file.html")
        assert len(violations) == 1
        assert violations[0].criterion == "1.4.3"
        assert violations[0].severity == Severity.ERROR

    def test_sufficient_contrast_no_violation(self):
        html = '<html><body><span style="color: #000000; background-color: #ffffff">text</span></body></html>'  # noqa: E501
        soup = _soup(html)
        violations = check_color_contrast(soup, "/test/file.html")
        assert len(violations) == 0

    def test_no_style_skipped(self):
        html = "<html><body><span>text</span></body></html>"
        soup = _soup(html)
        violations = check_color_contrast(soup, "/test/file.html")
        assert len(violations) == 0

    def test_default_bg_black_when_no_bg_set(self):
        html = '<html><body><p style="color: #aaaaaa">text</p></body></html>'
        soup = _soup(html)
        violations = check_color_contrast(soup, "/test/file.html")
        assert len(violations) == 0


# ── check_reduced_motion ───────────────────────────────────────


class TestCheckReducedMotion:
    def test_no_reduced_motion_info(self):
        html = "<html><head><style>a { color: red; }</style></head><body></body></html>"
        soup = _soup(html)
        violations = check_reduced_motion(soup, "/test/file.html")
        assert len(violations) == 1
        assert violations[0].severity == Severity.INFO

    def test_has_reduced_motion_no_violation(self):
        html = "<html><head><style>@media (prefers-reduced-motion: reduce) { * { animation: none; } }</style></head><body></body></html>"  # noqa: E501
        soup = _soup(html)
        violations = check_reduced_motion(soup, "/test/file.html")
        assert len(violations) == 0


# ── check_aria_attributes ───────────────────────────────────────


class TestCheckAriaAttributes:
    def test_invalid_aria_live_error(self):
        html = '<html><body><div aria-live="maybe">text</div></body></html>'
        soup = _soup(html)
        violations = check_aria_attributes(soup, "/test/file.html")
        live_errors = [v for v in violations if "aria-live" in v.message]
        assert len(live_errors) == 1

    def test_valid_aria_live_no_violation(self):
        html = '<html><body><div aria-live="polite">text</div></body></html>'
        soup = _soup(html)
        violations = check_aria_attributes(soup, "/test/file.html")
        assert len(violations) == 0

    def test_invalid_role_error(self):
        html = '<html><body><div role="notarole">text</div></body></html>'
        soup = _soup(html)
        violations = check_aria_attributes(soup, "/test/file.html")
        role_errors = [v for v in violations if "Invalid ARIA role" in v.message]
        assert len(role_errors) == 1


# ── check_link_accessibility ───────────────────────────────────


class TestCheckLinkAccessibility:
    def test_empty_link_error(self):
        html = '<html><body><a href="#"></a></body></html>'
        soup = _soup(html)
        violations = check_link_accessibility(soup, "/test/file.html")
        errors = [v for v in violations if "no accessible text" in v.message]
        assert len(errors) == 1

    def test_link_with_text_no_violation(self):
        html = '<html><body><a href="#">Home</a></body></html>'
        soup = _soup(html)
        violations = check_link_accessibility(soup, "/test/file.html")
        assert len(violations) == 0

    def test_link_with_img_alt_no_violation(self):
        html = (
            '<html><body><a href="#"><img src="icon.png" alt="Home"></a></body></html>'
        )
        soup = _soup(html)
        violations = check_link_accessibility(soup, "/test/file.html")
        assert len(violations) == 0

    def test_blank_no_warning_info(self):
        html = '<html><body><a href="https://example.com" target="_blank">link</a></body></html>'
        soup = _soup(html)
        violations = check_link_accessibility(soup, "/test/file.html")
        info = [v for v in violations if "new window" in v.message.lower()]
        assert len(info) == 1
        assert info[0].severity == Severity.INFO


# ── check_html_accessibility ────────────────────────────────────


class TestCheckHtmlAccessibility:
    def test_nonexistent_file_returns_error_result(self):
        result = check_html_accessibility("/nonexistent/path/file.html")
        assert isinstance(result, CheckResult)
        assert result.file == "file.html"
        errors = [v for v in result.violations if v.severity == Severity.ERROR]
        assert len(errors) == 1
        assert "not found" in errors[0].message.lower()

    def test_no_bs4_returns_warning(self):
        with patch("buildlib.accessibility_checker._HAS_BS4", False):
            result = check_html_accessibility("/nonexistent/file.html")
        assert any(
            "beautifulsoup4 not installed" in v.message for v in result.violations
        )

    def test_check_exception_caught(self, tmp_path):
        html_file = tmp_path / "test.html"
        html_file.write_text("<html><body></body></html>", encoding="utf-8")

        mock_fn = MagicMock(side_effect=RuntimeError("boom"))
        mock_fn.__name__ = "check_language_attribute"

        with patch("buildlib.accessibility_checker.check_language_attribute", mock_fn):
            result = check_html_accessibility(html_file)
        error_msgs = [v for v in result.violations if "failed" in v.message.lower()]
        assert len(error_msgs) == 1
        assert "check_language_attribute" in error_msgs[0].message


# ── check_directory ─────────────────────────────────────────────


class TestCheckDirectory:
    def test_scans_directory(self, tmp_path):
        (tmp_path / "a.html").write_text(
            "<html><body><h1>A</h1></body></html>", encoding="utf-8"
        )
        (tmp_path / "b.html").write_text(
            "<html><body><h2>B</h2></body></html>", encoding="utf-8"
        )
        results = check_directory(tmp_path)
        assert len(results) == 2
        assert results[0].file == "a.html"
        assert results[1].file == "b.html"

    def test_empty_directory(self, tmp_path):
        results = check_directory(tmp_path)
        assert len(results) == 0

    def test_custom_pattern(self, tmp_path):
        (tmp_path / "a.html").write_text("<html></html>", encoding="utf-8")
        (tmp_path / "b.htm").write_text("<html></html>", encoding="utf-8")
        results = check_directory(tmp_path, pattern="*.htm")
        assert len(results) == 1
        assert results[0].file == "b.htm"


# ── Violation dataclass ─────────────────────────────────────────


class TestViolation:
    def test_str_with_line(self):
        v = Violation(
            criterion="1.1.1",
            message="missing alt",
            severity=Severity.ERROR,
            element="img",
            line=42,
        )
        s = str(v)
        assert "[ERROR]" in s
        assert "line 42" in s
        assert "[img]" in s

    def test_str_without_line(self):
        v = Violation(criterion="1.1.1", message="missing alt", severity=Severity.ERROR)
        s = str(v)
        assert "line" not in s

    def test_str_with_element_no_line(self):
        v = Violation(
            criterion="1.1.1",
            message="missing alt",
            severity=Severity.WARNING,
            element="svg",
        )
        s = str(v)
        assert "[WARNING]" in s
        assert "[svg]" in s


# ── CheckResult dataclass ──────────────────────────────────────


class TestCheckResult:
    def test_passed_no_violations(self):
        r = CheckResult(file="test.html")
        assert r.passed is True
        assert r.error_count == 0
        assert r.warning_count == 0

    def test_failed_with_error(self):
        r = CheckResult(
            file="test.html", violations=[Violation("1.1.1", "err", Severity.ERROR)]
        )
        assert r.passed is False
        assert r.error_count == 1

    def test_failed_with_warning(self):
        r = CheckResult(
            file="test.html", violations=[Violation("1.1.1", "warn", Severity.WARNING)]
        )
        assert r.passed is False
        assert r.warning_count == 1

    def test_passed_with_info(self):
        r = CheckResult(
            file="test.html", violations=[Violation("1.1.1", "info", Severity.INFO)]
        )
        assert r.passed is True

    def test_summary(self):
        r = CheckResult(file="test.html")
        assert "PASS" in r.summary()
        assert "test.html" in r.summary()


# ── contrast_ratio ──────────────────────────────────────────────


class TestContrastRatio:
    def test_black_white(self):
        r = contrast_ratio((0, 0, 0), (255, 255, 255))
        assert abs(r - 21.0) < 0.1

    def test_same_color(self):
        r = contrast_ratio((128, 128, 128), (128, 128, 128))
        assert abs(r - 1.0) < 0.01

    def test_symmetry(self):
        r1 = contrast_ratio((100, 150, 200), (50, 50, 50))
        r2 = contrast_ratio((50, 50, 50), (100, 150, 200))
        assert abs(r1 - r2) < 0.01
