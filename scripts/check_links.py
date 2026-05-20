#!/usr/bin/env python3
"""Check internal and external links in Markdown documentation."""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"


def extract_links(content: str, filepath: Path) -> list[tuple[str, str, int]]:
    """Extract (link_target, context, line_number) from markdown content."""
    links = []
    for m in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', content):
        target = m.group(2)
        line = content[:m.start()].count('\n') + 1
        links.append((target, m.group(0), line))
    return links


def check_internal_link(target: str, source_file: Path) -> list[str]:
    """Check if an internal link resolves."""
    errors = []

    if '#' in target:
        target, anchor = target.split('#', 1)
    else:
        anchor = None

    if not target:
        if anchor:
            content = source_file.read_text(encoding='utf-8', errors='replace')
            heading = anchor.lower().replace('-', ' ')
            if heading not in content.lower():
                errors.append(f"Anchor #{anchor} not found in {source_file.name}")
        return errors

    target_path = (source_file.parent / target).resolve()

    if not target_path.exists():
        errors.append(f"File not found: {target} (from {source_file.name})")

    return errors


def main():
    errors = []
    warnings = []

    for md_file in DOCS_DIR.glob("*.md"):
        content = md_file.read_text(encoding='utf-8', errors='replace')
        links = extract_links(content, md_file)

        for target, context, line in links:
            if target.startswith('http://') or target.startswith('https://'):
                continue
            elif target.startswith('mailto:'):
                continue
            else:
                errs = check_internal_link(target, md_file)
                for e in errs:
                    errors.append(f"{md_file.name}:{line}: {e}")

    if errors:
        print("LINK ERRORS:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print(f"All internal links valid in {len(list(DOCS_DIR.glob('*.md')))} files")
        sys.exit(0)


if __name__ == "__main__":
    main()
