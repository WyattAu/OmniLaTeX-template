#!/usr/bin/env python3
"""Generate API documentation from OmniLaTeX module contracts."""

import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTRACTS_DIR = REPO_ROOT / "specs" / "module_contracts"
OUTPUT_FILE = REPO_ROOT / "docs" / "API_REFERENCE.md"


def load_contracts() -> list[dict]:
    """Load all module contracts sorted by name."""
    contracts = []
    for toml_file in sorted(CONTRACTS_DIR.glob("*.toml")):
        with open(toml_file, "rb") as f:
            data = tomllib.load(f)
        data["_source"] = toml_file.name
        contracts.append(data)
    return contracts


def generate_markdown(contracts: list[dict]) -> str:
    lines = [
        "# OmniLaTeX API Reference",
        "",
        "> Auto-generated from `specs/module_contracts/*.toml`",
        "> Run `python scripts/generate_api_docs.py` to regenerate.",
        "",
        f"**Modules:** {len(contracts)}",
        "",
    ]

    lines.append("## Module Index")
    lines.append("")
    lines.append("| Module | File | Version | Exports |")
    lines.append("|--------|------|---------|---------|")
    for c in contracts:
        mod = c.get("module", {})
        name = mod.get("name", "unknown")
        exports = c.get("exports", [])
        lines.append(f"| [{name}](#{name.replace('-', '')}) | `{mod.get('file', '')}` | {mod.get('version', '')} | {len(exports)} |")
    lines.append("")

    lines.append("## Detailed Reference")
    lines.append("")

    for c in contracts:
        mod = c.get("module", {})
        name = mod.get("name", "unknown")
        lines.append(f"### {name}")
        lines.append("")
        lines.append(f"**File:** `{mod.get('file', '')}`")
        lines.append(f"**Version:** {mod.get('version', '')}")
        lines.append(f"**Description:** {mod.get('description', '')}")
        lines.append(f"**Line count:** {mod.get('line_count', 'N/A')}")
        lines.append("")

        deps = c.get("dependencies", {})
        req = deps.get("requires", [])
        opt = deps.get("optionally_requires", [])
        if req or opt:
            lines.append("**Dependencies:**")
            if req:
                lines.append(f"- Required: {', '.join(f'`{r}`' for r in req)}")
            if opt:
                lines.append(f"- Optional: {', '.join(f'`{o}`' for o in opt)}")
            lines.append("")

        opts = c.get("options", {})
        if opts:
            lines.append("**Options:**")
            lines.append("")
            lines.append("| Option | Description |")
            lines.append("|--------|-------------|")
            for k, v in opts.items():
                lines.append(f"| `{k}` | {v} |")
            lines.append("")

        exports = c.get("exports", [])
        if exports:
            lines.append("**Exports:**")
            lines.append("")
            lines.append("| Name | Type | Signature | Description |")
            lines.append("|------|------|-----------|-------------|")
            for exp in exports:
                lines.append(f"| `{exp.get('name', '')}` | {exp.get('type', '')} | `{exp.get('signature', '')}` | {exp.get('description', '')} |")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    contracts = load_contracts()
    if not contracts:
        print("No contracts found in", CONTRACTS_DIR)
        sys.exit(1)

    md = generate_markdown(contracts)
    OUTPUT_FILE.write_text(md)
    print(f"Generated API reference: {OUTPUT_FILE} ({len(contracts)} modules)")


if __name__ == "__main__":
    main()
