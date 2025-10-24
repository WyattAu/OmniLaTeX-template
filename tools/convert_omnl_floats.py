#!/usr/bin/env python3
"""Convert OmniLaTeX float environments to native LaTeX/KOMA floats.

This utility rewrites `\begin{omnlfigure}` / `\begin{omnltable}` blocks into
standard `figure` / `table` environments while preserving captions, labels,
optional short captions, caption widths, placements, and manual caption usage.

It is intentionally conservative and only processes the `content/` tree, which
is the portion built by `main.tex` in the root document.
"""
from __future__ import annotations

import argparse
import pathlib
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"


@dataclass
class FloatOptions:
    caption: Optional[str] = None
    short_caption: Optional[str] = None
    label: Optional[str] = None
    footnote: Optional[str] = None
    caption_width: Optional[str] = None
    align: Optional[str] = None
    placement: Optional[str] = None
    caption_position: Optional[str] = None


def strip_braces(value: str) -> str:
    """Remove a single pair of surrounding braces if present."""
    value = value.strip()
    if value.startswith("{") and value.endswith("}"):
        # Ensure braces are balanced; this is sufficient for our use case where
        # the outermost level is a single pair created by the key handler.
        depth = 0
        for ch in value:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0 and ch != value[-1]:
                    # Found closing brace before the end -> keep original
                    return value[1:-1]
        return value[1:-1]
    return value


def parse_options(option_string: str) -> FloatOptions:
    if not option_string:
        return FloatOptions()

    parts: List[str] = []
    current: List[str] = []
    brace_depth = 0
    bracket_depth = 0
    for ch in option_string:
        if ch == "{" and bracket_depth == 0:
            brace_depth += 1
        elif ch == "}" and bracket_depth == 0:
            brace_depth -= 1
        elif ch == "[":
            bracket_depth += 1
        elif ch == "]":
            bracket_depth -= 1
        if ch == "," and brace_depth == 0 and bracket_depth == 0:
            parts.append("".join(current))
            current = []
            continue
        current.append(ch)
    if current:
        parts.append("".join(current))

    data: Dict[str, str] = {}
    for raw_part in parts:
        part = raw_part.strip()
        if not part:
            continue
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        data[key.strip()] = value.strip()

    return FloatOptions(
        caption=data.get("caption"),
        short_caption=data.get("short-caption"),
        label=data.get("label"),
        footnote=data.get("footnote"),
        caption_width=data.get("caption-width"),
        align=data.get("align"),
        placement=data.get("placement"),
        caption_position=data.get("caption-position"),
    )


def find_matching_end(text: str, env: str, start_pos: int) -> int:
    token = f"\\end{{{env}}}"
    idx = start_pos
    while True:
        idx = text.find(token, idx)
        if idx == -1:
            return -1
        # ensure it's not escaped or part of a command name with trailing letters
        if idx == 0 or text[idx - 1] != "\\":
            return idx
        idx += len(token)


def build_caption_lines(opts: FloatOptions, base_env: str, indent: str) -> str:
    lines: List[str] = []
    if opts.caption_width:
        width = strip_braces(opts.caption_width)
        lines.append(f"{indent}\\captionsetup{{width={width}}}")
    if opts.caption:
        caption_content = strip_braces(opts.caption)
        caption_cmd = f"\\caption"
        if opts.short_caption:
            short = strip_braces(opts.short_caption)
            caption_cmd += f"[{short}]"
        caption_cmd += f"{{{caption_content}}}"
        lines.append(f"{indent}{caption_cmd}")
    if opts.label:
        label = strip_braces(opts.label)
        lines.append(f"{indent}\\label{{{label}}}")
    if opts.footnote:
        footnote = strip_braces(opts.footnote)
        lines.append(f"{indent}\\caption*{{{footnote}}}")
    if not lines:
        return ""
    return "\n".join(lines) + "\n"


def build_manual_caption_commands(opts: FloatOptions, base_env: str) -> List[str]:
    commands: List[str] = []
    if opts.caption_width:
        width = strip_braces(opts.caption_width)
        commands.append(f"\\captionsetup{{width={width}}}")
    if opts.caption:
        caption_content = strip_braces(opts.caption)
        caption_cmd = f"\\captionof{{{base_env}}}"
        if opts.short_caption:
            short = strip_braces(opts.short_caption)
            caption_cmd += f"[{short}]"
        caption_cmd += f"{{{caption_content}}}"
        commands.append(caption_cmd)
    if opts.label:
        label = strip_braces(opts.label)
        commands.append(f"\\label{{{label}}}")
    if opts.footnote:
        footnote = strip_braces(opts.footnote)
        commands.append(f"\\caption*{{{footnote}}}")
    return commands


def replace_manual_caption(body: str, commands: List[str]) -> str:
    if not commands:
        # Remove placeholder entirely
        return body.replace("\\omnlFloatCaption", "")

    pattern = re.compile(r"(^\s*)\\omnlFloatCaption", re.MULTILINE)

    def repl(match: re.Match[str]) -> str:
        indent = match.group(1)
        lines = [indent + cmd for cmd in commands]
        return "\n".join(lines)

    return pattern.sub(repl, body)


def convert_environment(text: str, env: str) -> str:
    result = []
    idx = 0
    begin_token = f"\\begin{{{env}}}"
    base_env = "figure" if env == "omnlfigure" else "table"

    while True:
        start = text.find(begin_token, idx)
        if start == -1:
            result.append(text[idx:])
            break

        result.append(text[idx:start])

        line_start = text.rfind("\n", 0, start) + 1
        indent = text[line_start:start]

        pos = start + len(begin_token)
        # Skip whitespace before potential options
        while pos < len(text) and text[pos] in " \t\r\n":
            pos += 1

        options_str = ""
        if pos < len(text) and text[pos] == "[":
            bracket_depth = 0
            opt_start = pos + 1
            while pos < len(text):
                ch = text[pos]
                if ch == "[":
                    bracket_depth += 1
                elif ch == "]":
                    bracket_depth -= 1
                    if bracket_depth == 0:
                        options_str = text[opt_start:pos]
                        pos += 1
                        break
                pos += 1
        opts = parse_options(options_str)

        body_start = pos
        end = find_matching_end(text, env, body_start)
        if end == -1:
            # fallback: append rest and exit
            result.append(text[start:])
            break
        body = text[body_start:end]
        closing_token = f"\\end{{{env}}}"
        end_pos = end + len(closing_token)

        # Prepare new environment
        placement = strip_braces(opts.placement) if opts.placement else "tbp"
        placement_arg = f"[{placement}]" if placement else ""

        align_cmd = None
        if opts.align:
            align_key = strip_braces(opts.align)
            if align_key == "center":
                align_cmd = "\\centering"
            elif align_key == "left":
                align_cmd = "\\raggedright"
            elif align_key == "right":
                align_cmd = "\\raggedleft"

        caption_pos = (strip_braces(opts.caption_position) if opts.caption_position else "bottom").lower()

        body_processed = body
        caption_before = ""
        caption_after = ""

        if caption_pos == "manual":
            manual_cmds = build_manual_caption_commands(opts, base_env)
            body_processed = replace_manual_caption(body_processed, manual_cmds)
        else:
            caption_lines = build_caption_lines(opts, base_env, indent + "    ")
            if caption_pos == "top":
                caption_before = caption_lines
            else:
                caption_after = caption_lines

        # Ensure manual placeholder is removed if still present
        body_processed = body_processed.replace("\\omnlFloatCaption", "")

        new_block = indent + f"\\begin{{{base_env}}}{placement_arg}\n"
        if align_cmd:
            new_block += indent + "    " + align_cmd + "\n"
        if caption_before:
            new_block += caption_before

        new_block += body_processed
        if not new_block.endswith("\n"):
            new_block += "\n"
        if caption_after:
            if not new_block.endswith("\n"):
                new_block += "\n"
            new_block += caption_after
        new_block += indent + f"\\end{{{base_env}}}"

        result.append(new_block)
        idx = end_pos

    return "".join(result)


def process_file(path: pathlib.Path) -> None:
    original = path.read_text()
    updated = convert_environment(original, "omnlfigure")
    updated = convert_environment(updated, "omnltable")
    if updated != original:
        path.write_text(updated)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert OmniLaTeX floats to native LaTeX")
    parser.add_argument("paths", nargs="*", default=[str(CONTENT_DIR)], help="Paths to process (default: content/)")
    args = parser.parse_args()

    for target in args.paths:
        path = pathlib.Path(target)
        if path.is_file() and path.suffix == ".tex":
            process_file(path)
        elif path.is_dir():
            for tex_path in path.rglob("*.tex"):
                process_file(tex_path)


if __name__ == "__main__":
    main()
