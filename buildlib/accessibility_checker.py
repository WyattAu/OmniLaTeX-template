"""WCAG 2.1 AA accessibility checker for HTML files.

Validates HTML pages against WCAG 2.1 AA criteria including:
- Color contrast ratios (4.5:1 normal, 3:1 large text)
- ARIA landmark roles
- Form labels and controls
- Heading hierarchy
- Image alt text
- Skip links
- Language attributes
- Keyboard navigation patterns
- prefers-reduced-motion support
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

try:
    from bs4 import BeautifulSoup, Tag

    _HAS_BS4 = True
except ImportError:
    _HAS_BS4 = False


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Violation:
    """A single accessibility violation."""

    criterion: str
    message: str
    severity: Severity
    element: str = ""
    line: int | None = None

    def __str__(self) -> str:
        loc = f" (line {self.line})" if self.line else ""
        elem = f" [{self.element}]" if self.element else ""
        return f"[{self.severity.value.upper()}] {self.criterion}: {self.message}{elem}{loc}"


def _tag_line(tag: Tag) -> int | None:
    """Extract source line number from a BeautifulSoup Tag, if available."""
    return getattr(tag, "sourceline", None)


@dataclass
class CheckResult:
    """Result of an accessibility check."""

    file: str
    violations: list[Violation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(
            v.severity in (Severity.ERROR, Severity.WARNING) for v in self.violations
        )

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == Severity.WARNING)

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        return (
            f"{status} {self.file}: "
            f"{self.error_count} errors, {self.warning_count} warnings"
        )


# ── Color Contrast Helpers ────────────────────────────────────────


def _parse_hex_color(hex_str: str) -> tuple[int, int, int] | None:
    """Parse a CSS hex color string to RGB tuple."""
    hex_str = hex_str.strip().lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join(c * 2 for c in hex_str)
    if len(hex_str) != 6:
        return None
    try:
        return (int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16))
    except ValueError:
        return None


def _relative_luminance(rgb: tuple[int, int, int]) -> float:
    """Calculate relative luminance per WCAG 2.1 definition."""
    r, g, b = [c / 255.0 for c in rgb]

    def linearize(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    """Calculate WCAG contrast ratio between two RGB colors."""
    l1 = _relative_luminance(fg)
    l2 = _relative_luminance(bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


_CSS_COLOR_MAP: dict[str, str] = {
    "white": "#ffffff",
    "black": "#000000",
    "red": "#ff0000",
    "green": "#008000",
    "blue": "#0000ff",
    "yellow": "#ffff00",
    "cyan": "#00ffff",
    "magenta": "#ff00ff",
    "gray": "#808080",
    "grey": "#808080",
    "orange": "#ffa500",
    "transparent": "#ffffff",
}


def _resolve_color(
    color_str: str, soup: BeautifulSoup, tag: Tag | None = None
) -> tuple[int, int, int] | None:
    """Resolve a CSS color string to RGB, handling hex, rgb(), and named colors."""
    color_str = color_str.strip().lower()
    if not color_str or color_str == "transparent":
        return None

    # Hex
    if color_str.startswith("#"):
        return _parse_hex_color(color_str)

    # rgb/rgba
    m = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", color_str)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # Named colors
    if color_str in _CSS_COLOR_MAP:
        return _parse_hex_color(_CSS_COLOR_MAP[color_str])

    return None


def _get_effective_bg(tag: Tag, soup: BeautifulSoup) -> tuple[int, int, int] | None:
    """Walk ancestors to find the effective background color."""
    current = tag
    while current and current.name != "[document]":
        if isinstance(current, Tag):
            style = current.get("style", "")
            m = re.search(r"background(?:-color)?\s*:\s*([^;]+)", style)
            if m:
                color = _resolve_color(m.group(1), soup, current)
                if color:
                    return color
        current = current.parent
    return (0, 0, 0)  # Default to black if no bg found (dark theme)


def _get_foreground_color(tag: Tag, soup: BeautifulSoup) -> tuple[int, int, int] | None:
    """Get the foreground color from a tag's style or computed defaults."""
    style = tag.get("style", "") if isinstance(tag, Tag) else ""
    m = re.search(r"color\s*:\s*([^;]+)", style)
    if m:
        return _resolve_color(m.group(1), soup, tag)
    return None


def _is_large_text(tag: Tag) -> bool:
    """Check if text qualifies as 'large' under WCAG (18pt+ or 14pt+ bold)."""
    style = tag.get("style", "") if isinstance(tag, Tag) else ""
    font_size_match = re.search(r"font-size\s*:\s*([\d.]+)(pt|px|rem|em)", style)
    font_weight_match = re.search(r"font-weight\s*:\s*(\d+|bold)", style)

    if not font_size_match:
        return False

    value = float(font_size_match.group(1))
    unit = font_size_match.group(2)
    if unit == "px":
        pt = value * 0.75
    elif unit == "pt":
        pt = value
    elif unit in ("rem", "em"):
        pt = value * 12  # approximate
    else:
        pt = 0

    is_bold = False
    if font_weight_match:
        w = font_weight_match.group(1)
        is_bold = w == "bold" or (w.isdigit() and int(w) >= 700)

    return pt >= 18 or (pt >= 14 and is_bold)


def check_color_contrast(soup: BeautifulSoup, file_path: str) -> list[Violation]:
    """Check color contrast ratios for text elements."""
    violations: list[Violation] = []

    text_tags = soup.find_all(
        [
            "p",
            "span",
            "a",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "li",
            "td",
            "th",
            "label",
            "button",
            "strong",
            "em",
            "code",
            "pre",
        ]
    )
    for tag in text_tags:
        fg = _get_foreground_color(tag, soup)
        bg = _get_effective_bg(tag, soup)

        if fg is None or bg is None:
            continue

        ratio = contrast_ratio(fg, bg)
        min_ratio = 3.0 if _is_large_text(tag) else 4.5

        if ratio < min_ratio:
            severity = Severity.ERROR if ratio < min_ratio - 1.0 else Severity.WARNING
            element_str = tag.name or "unknown"
            violations.append(
                Violation(
                    criterion="1.4.3",
                    message=f"Contrast ratio {ratio:.2f}:1 (need {min_ratio}:1)",
                    severity=severity,
                    element=element_str,
                    line=_tag_line(tag),
                )
            )

    return violations


# ── ARIA Landmark Checks ────────────────────────────────────────


def check_aria_landmarks(soup: BeautifulSoup, file_path: str) -> list[Violation]:
    """Check that page has proper ARIA landmark regions."""
    violations: list[Violation] = []

    has_main = soup.find("main") is not None
    has_nav = soup.find("nav") is not None
    has_header = soup.find("header") is not None
    has_footer = soup.find("footer") is not None

    # Also check for ARIA role attributes
    roles = {tag.get("role") for tag in soup.find_all(attrs={"role": True})}

    if not has_main and "main" not in roles:
        violations.append(
            Violation(
                criterion="1.3.1",
                message="Page missing <main> landmark",
                severity=Severity.ERROR,
            )
        )

    if not has_nav and "navigation" not in roles:
        violations.append(
            Violation(
                criterion="1.3.1",
                message="Page missing <nav> landmark",
                severity=Severity.WARNING,
            )
        )

    if not has_header and "banner" not in roles:
        violations.append(
            Violation(
                criterion="1.3.1",
                message="Page missing <header> landmark",
                severity=Severity.WARNING,
            )
        )

    if not has_footer and "contentinfo" not in roles:
        violations.append(
            Violation(
                criterion="1.3.1",
                message="Page missing <footer> landmark",
                severity=Severity.WARNING,
            )
        )

    # Check that nav elements have accessible names
    for nav in soup.find_all("nav"):
        if not nav.get("aria-label") and not nav.get("aria-labelledby"):
            violations.append(
                Violation(
                    criterion="1.3.1",
                    message="<nav> missing aria-label or aria-labelledby",
                    severity=Severity.WARNING,
                    element="nav",
                    line=_tag_line(nav),
                )
            )

    return violations


# ── Form Label Checks ────────────────────────────────────────────


def check_form_labels(soup: BeautifulSoup, file_path: str) -> list[Violation]:
    """Check that all form controls have associated labels."""
    violations: list[Violation] = []

    inputs = soup.find_all(["input", "select", "textarea"])
    for inp in inputs:
        inp_type = inp.get("type", "text")
        if inp_type in ("hidden", "submit", "button", "reset", "image"):
            continue

        inp_id = inp.get("id")
        has_label = False

        # Check for <label for="id">
        if inp_id:
            label = soup.find("label", attrs={"for": inp_id})
            if label:
                has_label = True

        # Check for wrapping <label>
        if not has_label and inp.parent and inp.parent.name == "label":
            has_label = True

        # Check for aria-label or aria-labelledby
        if not has_label and (inp.get("aria-label") or inp.get("aria-labelledby")):
            has_label = True

        # Check for title attribute
        if not has_label and inp.get("title"):
            has_label = True

        if not has_label:
            element_str = f"<{inp.name}"
            if inp.get("type"):
                element_str += f' type="{inp["type"]}"'
            if inp.get("name"):
                element_str += f' name="{inp["name"]}"'
            element_str += ">"
            violations.append(
                Violation(
                    criterion="1.3.1",
                    message="Form control missing associated label",
                    severity=Severity.ERROR,
                    element=element_str,
                    line=_tag_line(inp),
                )
            )

    return violations


# ── Heading Hierarchy ────────────────────────────────────────────


def check_heading_hierarchy(soup: BeautifulSoup, file_path: str) -> list[Violation]:
    """Check that heading levels are properly nested (h1 -> h2 -> h3)."""
    violations: list[Violation] = []
    headings = soup.find_all(re.compile(r"^h[1-6]$"))

    if not headings:
        violations.append(
            Violation(
                criterion="1.3.1",
                message="Page has no headings",
                severity=Severity.WARNING,
            )
        )
        return violations

    prev_level = 0
    h1_count = 0

    for heading in headings:
        level = int(heading.name[1])

        if level == 1:
            h1_count += 1

        if prev_level > 0 and level > prev_level + 1:
            violations.append(
                Violation(
                    criterion="1.3.1",
                    message=f"Heading level skipped: h{prev_level} -> h{level}",
                    severity=Severity.ERROR,
                    element=heading.name,
                    line=_tag_line(heading),
                )
            )

        prev_level = level

    if h1_count == 0:
        violations.append(
            Violation(
                criterion="1.3.1",
                message="Page missing <h1> heading",
                severity=Severity.ERROR,
            )
        )
    elif h1_count > 1:
        violations.append(
            Violation(
                criterion="1.3.1",
                message=f"Page has {h1_count} <h1> headings (should have exactly 1)",
                severity=Severity.WARNING,
            )
        )

    return violations


# ── Image Alt Text ───────────────────────────────────────────────


def check_image_alt_text(soup: BeautifulSoup, file_path: str) -> list[Violation]:
    """Check that all images have alt text."""
    violations: list[Violation] = []

    images = soup.find_all("img")
    for img in images:
        alt = img.get("alt")
        src = img.get("src", "unknown")

        if alt is None:
            violations.append(
                Violation(
                    criterion="1.1.1",
                    message=f"Image missing alt attribute: {src[:50]}",
                    severity=Severity.ERROR,
                    element="img",
                    line=_tag_line(img),
                )
            )
        elif alt.strip() == "" and not img.get("role") == "presentation":
            # Empty alt is OK for decorative images, but flag for review
            pass

    # Check SVG elements used as content
    svgs = soup.find_all("svg")
    for svg in svgs:
        has_title = svg.find("title") is not None
        has_aria_label = svg.get("aria-label") is not None
        has_aria_hidden = svg.get("aria-hidden") == "true"
        has_role = svg.get("role") == "presentation"

        if not (has_title or has_aria_label or has_aria_hidden or has_role):
            violations.append(
                Violation(
                    criterion="1.1.1",
                    message="SVG missing accessible name (title, aria-label, or aria-hidden)",
                    severity=Severity.WARNING,
                    element="svg",
                    line=_tag_line(svg),
                )
            )

    return violations


# ── Skip Link ────────────────────────────────────────────────────


def check_skip_link(soup: BeautifulSoup, file_path: str) -> list[Violation]:
    """Check that page has a skip navigation link."""
    violations: list[Violation] = []

    skip_link = soup.find("a", class_="skip-link")
    if not skip_link:
        skip_link = soup.find(
            "a",
            href=re.compile(r"#(main-content|main|content|skip)", re.IGNORECASE),
        )

    if not skip_link:
        violations.append(
            Violation(
                criterion="2.4.1",
                message="Page missing skip navigation link",
                severity=Severity.WARNING,
            )
        )
    else:
        href = skip_link.get("href", "")
        if href.startswith("#"):
            target_id = href[1:]
            target = soup.find(id=target_id)
            if not target:
                violations.append(
                    Violation(
                        criterion="2.4.1",
                        message=f"Skip link target #{target_id} not found",
                        severity=Severity.ERROR,
                        element="a.skip-link",
                    )
                )

    return violations


# ── Language Attribute ───────────────────────────────────────────


def check_language_attribute(soup: BeautifulSoup, file_path: str) -> list[Violation]:
    """Check that html element has a lang attribute."""
    violations: list[Violation] = []

    html_tag = soup.find("html")
    if html_tag:
        lang = html_tag.get("lang")
        if not lang:
            violations.append(
                Violation(
                    criterion="3.1.1",
                    message="<html> missing lang attribute",
                    severity=Severity.ERROR,
                )
            )
        elif len(lang) < 2:
            violations.append(
                Violation(
                    criterion="3.1.1",
                    message=f"Invalid lang attribute value: '{lang}'",
                    severity=Severity.WARNING,
                )
            )
    else:
        violations.append(
            Violation(
                criterion="3.1.1",
                message="Document missing <html> element",
                severity=Severity.ERROR,
            )
        )

    return violations


# ── Focus Indicators ─────────────────────────────────────────────


def check_focus_indicators(soup: BeautifulSoup, file_path: str) -> list[Violation]:
    """Check that focus styles are defined (in <style> blocks)."""
    violations: list[Violation] = []

    # Collect all inline style content
    style_blocks = soup.find_all("style")
    all_css = "\n".join(s.string or "" for s in style_blocks)

    # Check for outline:none or outline:0 without a replacement
    outline_none_count = len(re.findall(r"outline\s*:\s*(?:none|0)\b", all_css))
    focus_visible_count = len(re.findall(r":focus-visible|:focus\b", all_css))

    if outline_none_count > 0 and focus_visible_count == 0:
        violations.append(
            Violation(
                criterion="2.4.7",
                message=(
                    f"outline:none found {outline_none_count} time(s) "
                    "without :focus-visible replacement"
                ),
                severity=Severity.WARNING,
            )
        )

    return violations


# ── prefers-reduced-motion ───────────────────────────────────────


def check_reduced_motion(soup: BeautifulSoup, file_path: str) -> list[Violation]:
    """Check that prefers-reduced-motion is handled."""
    violations: list[Violation] = []

    style_blocks = soup.find_all("style")
    all_css = "\n".join(s.string or "" for s in style_blocks)

    has_reduced_motion = "prefers-reduced-motion" in all_css

    if not has_reduced_motion:
        violations.append(
            Violation(
                criterion="2.3.3",
                message="No prefers-reduced-motion media query found",
                severity=Severity.INFO,
            )
        )

    return violations


# ── ARIA Attributes ──────────────────────────────────────────────


def check_aria_attributes(soup: BeautifulSoup, file_path: str) -> list[Violation]:
    """Check for valid ARIA attribute usage."""
    violations: list[Violation] = []

    # Check aria-live regions for proper usage
    live_regions = soup.find_all(attrs={"aria-live": True})
    for region in live_regions:
        value = region.get("aria-live", "")
        if value not in ("polite", "assertive", "off"):
            violations.append(
                Violation(
                    criterion="4.1.3",
                    message=f"Invalid aria-live value: '{value}'",
                    severity=Severity.ERROR,
                    element=region.name or "unknown",
                )
            )

    # Check role attributes
    valid_roles = {
        "alert",
        "alertdialog",
        "application",
        "article",
        "banner",
        "button",
        "cell",
        "checkbox",
        "columnheader",
        "combobox",
        "complementary",
        "contentinfo",
        "definition",
        "dialog",
        "directory",
        "document",
        "feed",
        "figure",
        "form",
        "grid",
        "gridcell",
        "group",
        "heading",
        "img",
        "link",
        "list",
        "listbox",
        "listitem",
        "log",
        "main",
        "marquee",
        "math",
        "menu",
        "menubar",
        "menuitem",
        "menuitemcheckbox",
        "menuitemradio",
        "navigation",
        "none",
        "note",
        "option",
        "presentation",
        "progressbar",
        "radio",
        "radiogroup",
        "region",
        "row",
        "rowgroup",
        "rowheader",
        "scrollbar",
        "search",
        "searchbox",
        "separator",
        "slider",
        "spinbutton",
        "status",
        "switch",
        "tab",
        "table",
        "tablist",
        "tabpanel",
        "term",
        "textbox",
        "timer",
        "toolbar",
        "tooltip",
        "tree",
        "treegrid",
        "treeitem",
    }

    role_tags = soup.find_all(attrs={"role": True})
    for tag in role_tags:
        role = tag.get("role", "")
        if role not in valid_roles:
            violations.append(
                Violation(
                    criterion="4.1.2",
                    message=f"Invalid ARIA role: '{role}'",
                    severity=Severity.ERROR,
                    element=tag.name or "unknown",
                )
            )

    return violations


# ── Link Accessibility ───────────────────────────────────────────


def check_link_accessibility(soup: BeautifulSoup, file_path: str) -> list[Violation]:
    """Check that links are accessible."""
    violations: list[Violation] = []

    links = soup.find_all("a")
    for link in links:
        href = link.get("href", "")
        text = link.get_text(strip=True)
        aria_label = link.get("aria-label", "")

        if not text and not aria_label:
            # Check for img with alt inside link
            img = link.find("img")
            if img and img.get("alt"):
                continue
            violations.append(
                Violation(
                    criterion="2.4.4",
                    message="Link has no accessible text",
                    severity=Severity.ERROR,
                    element="a",
                    line=_tag_line(link),
                )
            )

        # Check for new window without warning
        if link.get("target") == "_blank":
            if not aria_label and "new window" not in text.lower():
                violations.append(
                    Violation(
                        criterion="3.2.5",
                        message="External link opens new window without warning",
                        severity=Severity.INFO,
                        element="a",
                        line=_tag_line(link),
                    )
                )

    return violations


# ── Main Checker ─────────────────────────────────────────────────


def check_html_accessibility(
    file_path: str | Path,
) -> CheckResult:
    """Run all WCAG 2.1 AA checks on an HTML file.

    Args:
        file_path: Path to the HTML file to check.

    Returns:
        CheckResult with all violations found.
    """
    file_path = Path(file_path)
    result = CheckResult(file=file_path.name)

    if not _HAS_BS4:
        result.violations.append(
            Violation(
                criterion="N/A",
                message="beautifulsoup4 not installed; cannot check accessibility",
                severity=Severity.WARNING,
            )
        )
        return result

    if not file_path.exists():
        result.violations.append(
            Violation(
                criterion="N/A",
                message=f"File not found: {file_path}",
                severity=Severity.ERROR,
            )
        )
        return result

    html = file_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    checks = [
        check_language_attribute,
        check_aria_landmarks,
        check_heading_hierarchy,
        check_image_alt_text,
        check_form_labels,
        check_skip_link,
        check_focus_indicators,
        check_reduced_motion,
        check_aria_attributes,
        check_link_accessibility,
        check_color_contrast,
    ]

    for check_fn in checks:
        try:
            violations = check_fn(soup, str(file_path))
            result.violations.extend(violations)
        except Exception as e:
            result.violations.append(
                Violation(
                    criterion="N/A",
                    message=f"Check {check_fn.__name__} failed: {e}",
                    severity=Severity.WARNING,
                )
            )

    return result


def check_directory(
    directory: str | Path,
    pattern: str = "*.html",
) -> list[CheckResult]:
    """Check all HTML files in a directory.

    Args:
        directory: Directory to scan.
        pattern: Glob pattern for HTML files.

    Returns:
        List of CheckResult, one per file.
    """
    directory = Path(directory)
    results: list[CheckResult] = []

    for html_file in sorted(directory.glob(pattern)):
        results.append(check_html_accessibility(html_file))

    return results


def print_report(results: list[CheckResult]) -> None:
    """Print a formatted accessibility report."""
    total_errors = sum(r.error_count for r in results)
    total_warnings = sum(r.warning_count for r in results)
    passed = sum(1 for r in results if r.passed)

    print(f"\n{'=' * 60}")
    print("  WCAG 2.1 AA Accessibility Report")
    print(f"{'=' * 60}")

    for result in results:
        print(f"\n  {result.summary()}")
        for v in result.violations:
            if v.severity in (Severity.ERROR, Severity.WARNING):
                print(f"    {v}")

    print(f"\n{'─' * 60}")
    print(
        f"  Files: {len(results)} | "
        f"Passed: {passed} | "
        f"Errors: {total_errors} | "
        f"Warnings: {total_warnings}"
    )
    print(f"{'=' * 60}\n")
