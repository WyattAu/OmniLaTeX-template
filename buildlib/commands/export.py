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
        """Export LaTeX to alternative formats.

        Supported formats:
          html     - High-fidelity HTML via LaTeXML
          html5    - Lightweight HTML5 via pandoc
          epub     - EPUB via pandoc (EPUB3 default)
          epub3    - EPUB3 with explicit pandoc flags
          docx     - DOCX via pandoc
          md       - Markdown via pandoc

        Requires: latexml (for html), pandoc (for all others)
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
            # High-fidelity HTML via LaTeXML
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

        elif output_format == "html5":
            # Lightweight HTML5 via pandoc
            if not shutil.which("pandoc"):
                self.ui.error("pandoc not found. Install: apt-get install pandoc")
                return

            out_file = output_dir / f"{stem}.html"
            self.ui.info(f"Converting {source.name} -> {out_file}")

            rc, _ = self.runner.run(
                [
                    "pandoc",
                    "--from=latex",
                    "--to=html5",
                    "--standalone",
                    "--self-contained",
                    "--toc",
                    "--mathjax",
                    "-o",
                    str(out_file),
                    str(source),
                ],
                cwd=source.parent,
            )

            if rc == 0 and out_file.exists():
                self.ui.success(f"HTML5 exported: {out_file}")
            else:
                self.ui.error("HTML5 export failed")

        elif output_format in ("epub", "epub3"):
            # EPUB/EPUB3 via pandoc (with optional LaTeXML intermediate)
            if not shutil.which("pandoc"):
                self.ui.error("pandoc not found. Install: apt-get install pandoc")
                return

            out_file = output_dir / f"{stem}.epub"
            self.ui.info(f"Converting {source.name} -> {out_file}")

            # Try LaTeXML intermediate for better fidelity
            xml_file = output_dir / f"{stem}.xml"
            html_file = output_dir / f"{stem}.html"

            if shutil.which("latexml"):
                rc, _ = self.runner.run(
                    ["latexml", f"--dest={xml_file}", str(source)],
                    cwd=source.parent,
                )
                if rc == 0:
                    self.runner.run(
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

            pandoc_to = "epub3" if output_format == "epub3" else "epub"
            epub_args = [
                "pandoc",
                f"--from={pandoc_from}",
                f"--to={pandoc_to}",
                "--toc",
                "--toc-depth=2",
                "-o",
                str(out_file),
                pandoc_input,
            ]

            # Inject metadata if export/metadata.xml exists
            meta_file = repo_root / "export" / "metadata.xml"
            if meta_file.exists():
                epub_args.insert(-2, f"--epub-metadata={meta_file}")

            # Inject CSS if export/epub.css exists
            css_file = repo_root / "export" / "epub.css"
            if css_file.exists():
                epub_args.insert(-2, f"--css={css_file}")

            rc, _ = self.runner.run(epub_args, cwd=source.parent)

            if rc == 0 and out_file.exists():
                self.ui.success(f"{output_format.upper()} exported: {out_file}")
            else:
                self.ui.error(f"{output_format.upper()} export failed")

        elif output_format in ("docx", "md", "markdown"):
            # DOCX/Markdown via pandoc
            if not shutil.which("pandoc"):
                self.ui.error("pandoc not found. Install: apt-get install pandoc")
                return

            ext = "md" if output_format in ("md", "markdown") else "docx"
            pandoc_to = "markdown" if ext == "md" else "docx"
            out_file = output_dir / f"{stem}.{ext}"
            self.ui.info(f"Converting {source.name} -> {out_file}")

            pandoc_args = [
                "pandoc",
                "--from=latex",
                f"--to={pandoc_to}",
                "-o",
                str(out_file),
                str(source),
            ]

            if ext == "md":
                pandoc_args.insert(3, "--wrap=none")

            rc, _ = self.runner.run(pandoc_args, cwd=source.parent)

            if rc == 0 and out_file.exists():
                self.ui.success(f"{output_format.upper()} exported: {out_file}")
            else:
                self.ui.error(f"{output_format.upper()} export failed")

        else:
            self.ui.error(
                f"Unknown format: {output_format}. "
                "Use: html, html5, epub, epub3, docx, md"
            )
