"""Export commands mixin.

Provides commands for exporting LaTeX to alternative formats.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import buildlib.config as _cfg


class ExportMixin:
    """Mixin providing export commands.

    Requires self.ui, self.runner, self.config to be set by the inheriting class.
    """

    def cmd_export(self, files: list[str] | None = None, output_format: str = "html"):
        """Export LaTeX to alternative formats (html, epub, docx).

        Requires: latexml (for HTML), pandoc (for EPUB/DOCX)
        """
        self.ui.header(f"Export to {output_format.upper()}")

        repo_root = _cfg.REPO_ROOT

        if files:
            source = Path(files[0])
            if not source.is_absolute():
                source = repo_root / source
        else:
            source = repo_root / "main.tex"

        if not source.exists():
            self.ui.error(f"Source file not found: {source}")
            return

        output_dir = repo_root / self.config.build_dir / "export" / output_format
        output_dir.mkdir(parents=True, exist_ok=True)

        stem = source.stem

        if output_format == "html":
            if not shutil.which("latexml"):
                self.ui.error("latexml not found. Install: apt-get install latexml")
                return

            html_file = output_dir / f"{stem}.html"
            self.ui.info(f"Converting {source.name} -> {html_file}")

            rc, _ = self.runner.run(
                [
                    "latexml",
                    "--dest=" + str(output_dir / f"{stem}.xml"),
                    str(source),
                ],
                cwd=source.parent,
            )

            if rc == 0:
                rc, _ = self.runner.run(
                    [
                        "latexmlpost",
                        "--dest=" + str(html_file),
                        "--format=html",
                        str(output_dir / f"{stem}.xml"),
                    ],
                    cwd=source.parent,
                )

            if rc == 0 and html_file.exists():
                self.ui.success(f"HTML exported: {html_file}")
            else:
                self.ui.error("HTML export failed")

        elif output_format in ("epub", "docx"):
            if not shutil.which("pandoc"):
                self.ui.error("pandoc not found. Install: apt-get install pandoc")
                return

            out_file = output_dir / f"{stem}.{output_format}"
            self.ui.info(f"Converting {source.name} -> {out_file}")

            xml_file = output_dir / f"{stem}.xml"
            html_file = output_dir / f"{stem}.html"

            if shutil.which("latexml"):
                rc, _ = self.runner.run(
                    [
                        "latexml",
                        f"--dest={xml_file}",
                        str(source),
                    ],
                    cwd=source.parent,
                )
                if rc == 0:
                    rc, _ = self.runner.run(
                        [
                            "latexmlpost",
                            f"--dest={html_file}",
                            "--format=html",
                            str(xml_file),
                        ],
                        cwd=source.parent,
                    )

            if html_file.exists():
                pandoc_from = "html"
                pandoc_input = str(html_file)
            else:
                pandoc_from = "latex"
                pandoc_input = str(source)

            rc, _ = self.runner.run(
                [
                    "pandoc",
                    f"--from={pandoc_from}",
                    f"--to={output_format}",
                    "-o",
                    str(out_file),
                    pandoc_input,
                ],
                cwd=source.parent,
            )

            if rc == 0 and out_file.exists():
                self.ui.success(f"{output_format.upper()} exported: {out_file}")
            else:
                self.ui.error(f"{output_format.upper()} export failed")
        else:
            self.ui.error(f"Unknown format: {output_format}. Use: html, epub, docx")
