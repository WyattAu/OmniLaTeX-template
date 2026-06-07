"""Build cleanup mixin.

Provides methods for cleaning auxiliary files, PDFs, and build artifacts.
"""

from __future__ import annotations

import shutil

import buildlib.config as _cfg


class CleanupMixin:
    """Mixin providing cleanup operations.

    Requires self.config, self.runner, self.ui
    to be set by the inheriting class.
    """

    def clean_all(self, _: object | None = None) -> None:
        """Full cleanup: remove auxiliary files and build directory."""
        self.ui.header("Full cleanup")
        self.clean_aux()
        shutil.rmtree(self.config.build_dir, ignore_errors=True)
        self.ui.success("Full cleanup finished.")

    def clean_aux(self, _: object | None = None) -> None:
        """Clean auxiliary files from all examples."""
        self.ui.header("Cleaning auxiliary files")
        self.runner.run([_cfg.LATEXMK_COMMAND, "-C"], cwd=_cfg.REPO_ROOT)
        self.clean_example([e.name for e in self.discover_examples()])

    def clean_example(self, files: list[str]):
        """Clean auxiliary files from specific examples."""
        if files:
            self.ui.info(f"Cleaning {len(files)} example(s)")
            for name in files:
                example_dir = _cfg.REPO_ROOT / "examples" / name
                try:
                    exit_code, _ = self.runner.run(
                        [_cfg.LATEXMK_COMMAND, "-c"], cwd=example_dir
                    )
                    if exit_code != 0:
                        self.ui.warning(f"Could not clean example {name}")
                except OSError:
                    self.ui.warning(f"Could not clean example {name}")

    def clean_pdf(self, _: object | None = None) -> None:
        """Remove all generated PDFs from build and examples directories."""
        self.ui.header("Cleaning PDF files")
        count = 0
        build_examples = self.config.build_dir / "examples"
        if build_examples.is_dir():
            for pdf in build_examples.glob("*.pdf"):
                pdf.unlink(missing_ok=True)
                count += 1
        examples_dir = _cfg.REPO_ROOT / "examples"
        if examples_dir.is_dir():
            for pdf in examples_dir.rglob("*.pdf"):
                pdf.unlink(missing_ok=True)
                count += 1
        self.ui.success(f"Removed {count} PDF(s).")
