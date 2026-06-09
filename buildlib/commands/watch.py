"""Watch command mixin.

Provides the file watching command for automatic rebuilds.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path


class WatchMixin:
    """Mixin providing the watch command.

    Requires self.ui, self.runner to be set by the inheriting class.
    """

    def cmd_watch(self, files: list[str]):
        """Watch source files for changes and rebuild."""
        watch_dirs = [Path(".")]
        extensions = {".tex", ".sty", ".cls", ".bib", ".lua", ".toml"}
        ui = self.ui
        ui.info("Watching for changes... (Ctrl+C to stop)")

        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer

            class RebuildHandler(FileSystemEventHandler):
                def __init__(self, runner, extensions, files):
                    self.runner = runner
                    self.extensions = extensions
                    self.files = files
                    self._last_rebuild = 0

                def on_modified(self, event):
                    path = Path(event.src_path)
                    if path.suffix in self.extensions:
                        now = time.time()
                        if now - self._last_rebuild < 1.0:
                            return
                        self._last_rebuild = now
                        self.runner.ui.info(f"\nChange detected: {path}")
                        self.runner._rebuild_affected(path, self.files)

            handler = RebuildHandler(self, extensions, files)
            observer = Observer()
            for d in watch_dirs:
                observer.schedule(handler, str(d), recursive=True)
            observer.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()

        except ImportError:
            ui.info("watchdog not installed, using inotifywait fallback")
            cmd = [
                "inotifywait",
                "-r",
                "-e",
                "modify,create,delete",
                "--format",
                "%w%f",
            ]
            for d in watch_dirs:
                cmd.append(str(d))
            try:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
                if process.stdout is None:
                    ui.error("inotifywait stdout is None, cannot watch")
                    return
                for line in process.stdout:
                    path = Path(line.strip())
                    if path.suffix in extensions:
                        ui.info(f"\nChange detected: {path}")
                        self._rebuild_affected(path, files)
            except FileNotFoundError:
                ui.error(
                    "Neither watchdog nor inotifywait found. "
                    "Install one to use watch mode: pip install watchdog"
                )
            except KeyboardInterrupt:
                process.terminate()

    def _rebuild_affected(self, changed_path: Path, files: list[str]):
        """Rebuild documents affected by a changed file."""
        if files:
            self.build_example(files)
        else:
            self.build_examples([])
