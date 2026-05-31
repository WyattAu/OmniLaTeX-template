#!/usr/bin/env python3
"""
Template DSL: Generate OmniLaTeX doctype .sty files from TOML definitions.

Usage:
    python scripts/doctype_generator.py <doctype.toml>
    python scripts/doctype_generator.py --all config/doctypes/*.toml

TOML schema:
    [doctype]
    name = "mydoctype"
    base_class = "scrartcl"       # scrartcl, scrreprt, scrbook, beamer
    description = "My custom document type"

    [doctype.geometry]
    paper_size = "a4"
    margin_left = "25mm"
    margin_right = "25mm"
    margin_top = "25mm"
    margin_bottom = "25mm"

    [doctype.features]
    math = true
    tikz = false
    code = true
    tables = true
    glossaries = false

    [doctype.typography]
    line_spacing = 1.5
    font_size = "12pt"
    paragraph_indent = "0pt"

    [doctype.aliases]
    short = ["mydoc", "mdt"]
"""

import sys
import tomllib
from pathlib import Path


TEMPLATE = r"""%\NeedsTeXFormat{{LaTeX2e}}
\ProvidesPackage{{config/document-types/{name}}}[2026/05/31 v2.2.3 {description}]

% Generated from doctype DSL: {name}
% Base class: {base_class}

% Geometry overrides
{geometry_block}

% Feature toggles
{feature_block}

% Typography settings
{typography_block}

% Alias definitions
{alias_block}

\endinput
"""


def generate_geometry_block(name: str, geo: dict) -> str:
    lines = []
    if "paper_size" in geo:
        lines.append(f"\\KOMAoption{{paper}}{{{geo['paper_size']}}}")
    for side in ["left", "right", "top", "bottom"]:
        key = f"margin_{side}"
        if key in geo:
            lines.append(f"\\newlength{{\\omnilatex@{name}@margin{side}}}")
            lines.append(f"\\setlength{{\\omnilatex@{name}@margin{side}}}{{{geo[key]}}}")
    return "\n".join(lines) if lines else "% No geometry overrides"


def generate_feature_block(features: dict) -> str:
    lines = []
    for feat, enabled in features.items():
        if feat == "math":
            lines.append(f"% Math: {'enabled' if enabled else 'disabled'}")
        elif feat == "tikz":
            lines.append(f"% TikZ: {'enabled' if enabled else 'disabled'}")
        elif feat == "code":
            lines.append(f"% Code listings: {'enabled' if enabled else 'disabled'}")
        elif feat == "tables":
            lines.append(f"% Tables: {'enabled' if enabled else 'disabled'}")
        elif feat == "glossaries":
            lines.append(f"% Glossaries: {'enabled' if enabled else 'disabled'}")
    return "\n".join(lines) if lines else "% No feature overrides"


def generate_typography_block(typo: dict) -> str:
    lines = []
    if "line_spacing" in typo:
        lines.append(f"\\linespread{{{typo['line_spacing']}}}")
    if "paragraph_indent" in typo:
        lines.append(f"\\setlength{{\\parindent}}{{{typo['paragraph_indent']}}}")
    return "\n".join(lines) if lines else "% No typography overrides"


def generate_alias_block(name: str, aliases: dict) -> str:
    lines = []
    for alias in aliases.get("short", []):
        lines.append(f"% Alias: {alias} -> {name}")
    return "\n".join(lines) if lines else "% No aliases"


def generate_doctype(toml_path: Path) -> str:
    with open(toml_path, "rb") as f:
        data = tomllib.load(f)

    dt = data["doctype"]
    name = dt["name"]
    base_class = dt.get("base_class", "scrartcl")
    description = dt.get("description", f"Custom doctype {name}")

    geo = dt.get("geometry", {})
    features = dt.get("features", {})
    typo = dt.get("typography", {})
    aliases = dt.get("aliases", {})

    return TEMPLATE.format(
        name=name,
        base_class=base_class,
        description=description,
        geometry_block=generate_geometry_block(name, geo),
        feature_block=generate_feature_block(features),
        typography_block=generate_typography_block(typo),
        alias_block=generate_alias_block(name, aliases),
    )


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate OmniLaTeX doctypes from TOML DSL")
    parser.add_argument("input", nargs="+", type=Path, help="TOML doctype definition file(s)")
    parser.add_argument("--output-dir", "-o", type=Path, default=Path("config/document-types"))
    parser.add_argument("--dry-run", action="store_true", help="Print generated .sty to stdout")
    args = parser.parse_args()

    for toml_path in args.input:
        if not toml_path.exists():
            print(f"ERROR: {toml_path} not found", file=sys.stderr)
            continue
        content = generate_doctype(toml_path)
        if args.dry_run:
            print(f"--- {toml_path.stem} ---")
            print(content)
        else:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            out = args.output_dir / f"{toml_path.stem}.sty"
            out.write_text(content)
            print(f"Generated: {out}")


if __name__ == "__main__":
    main()
