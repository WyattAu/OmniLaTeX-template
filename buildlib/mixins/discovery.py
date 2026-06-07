"""Example discovery and source file management mixin.

Provides methods for finding examples, collecting source files,
and listing available examples.
"""

from __future__ import annotations

import json
from pathlib import Path

import buildlib.config as _cfg


class DiscoveryMixin:
    """Mixin providing example discovery and source file operations.

    Requires self.config, self.ui, self._source_files_cache
    to be set by the inheriting class.
    """

    def _get_source_files(self, repo_root: Path) -> list[Path]:
        """Find all .sty and .cls files, excluding non-source directories."""
        key = str(repo_root)
        if key not in self._source_files_cache:
            exclude = {
                ".git",
                "node_modules",
                "build",
                ".venv",
                ".direnv",
                "__pycache__",
                ".nix",
            }
            sty_files = [
                p
                for p in repo_root.rglob("*.sty")
                if not any(d in exclude for d in p.parts)
            ]
            cls_files = [
                p
                for p in repo_root.rglob("*.cls")
                if not any(d in exclude for d in p.parts)
            ]
            self._source_files_cache[key] = sty_files + cls_files
        return self._source_files_cache[key]

    def _collect_source_files(self, example_name: str) -> list[Path]:
        """Collect all source files relevant to an example (tex, bib, sty, cls)."""
        repo_root = _cfg.REPO_ROOT
        example_dir = repo_root / "examples" / example_name
        files: list[Path] = []
        tex_file = example_dir / _cfg.MAIN_TEX_FILENAME
        if tex_file.exists():
            files.append(tex_file)
        for bib in example_dir.rglob("*.bib"):
            files.append(bib)
        files.extend(self._get_source_files(repo_root))
        return files

    def discover_examples(self) -> list[Path]:
        """Find all example directories containing a main.tex file."""
        d = _cfg.REPO_ROOT / "examples"
        return (
            sorted(
                [
                    p
                    for p in d.iterdir()
                    if p.is_dir() and (p / _cfg.MAIN_TEX_FILENAME).is_file()
                ]
            )
            if d.is_dir()
            else []
        )

    def list_examples(
        self,
        _: object | None = None,
        *,
        output_format: str = "text",
    ) -> None:
        """List all available examples in text or JSON format."""
        examples = self.discover_examples()
        if output_format == "json":
            data = [
                {"name": ex.name, "path": str(ex)}
                for ex in sorted(examples, key=lambda e: e.name)
            ]
            print(json.dumps(data, indent=2))
        else:
            self.ui.header("Available Examples")
            for ex in examples:
                print(f"  {self.ui.bold}{ex.name}{self.ui.end}")
            self.ui.success(f"Found {len(examples)} example(s).")
