#!/usr/bin/env python3
"""
OmniLaTeX build entry point.

Key capabilities:
  • Explicit dev/prod/ultra modes with diagnostics announced up front.
  • Comprehensive logging of every subprocess invocation with elapsed timing.
  • Per-command verbose output toggled via --verbose / OMNILATEX_VERBOSE=1.
  • High-level commands for root builds, example builds, cleaning, preflight, and tests.
  • ALWAYS-CONCURRENT example building with a robust Rich UI or a simple TQDM-based fallback.
  • Meticulously preserved build logic from the original script to ensure correctness.
  • Robust success checking based on PDF existence, not exit codes.
"""

from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
import hashlib
import json
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import re
from typing import Callable, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# --- Rich library integration ---
try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import (
        Progress,
        BarColumn,
        TextColumn,
        TimeElapsedColumn,
        MofNCompleteColumn,
    )
    from rich.text import Text
    from collections import deque

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# --- TQDM fallback ---
try:
    from tqdm import tqdm
except ImportError:

    class TqdmFallback:
        def __init__(self, iterable, desc="", total=None):
            self.iterable = iterable
            self.desc = desc
            self.total = total or len(iterable)
            self.current = 0

        def __iter__(self):
            for item in self.iterable:
                self.current += 1
                percent = (
                    int((self.current / self.total) * 100) if self.total > 0 else 0
                )
                bar = "#" * (percent // 5) + "-" * (20 - (percent // 5))
                sys.stdout.write(f"\r{self.desc}: [{bar}] {self.current}/{self.total} ")
                sys.stdout.flush()
                yield item
            sys.stdout.write("\n")
            sys.stdout.flush()

    tqdm = TqdmFallback

# -----------------------------------------------------------------------------
# Constants & Config
# -----------------------------------------------------------------------------
MAIN_TEX_FILENAME = "main.tex"
LATEXMK_COMMAND = "latexmk"
INTERACTION_NONSTOP = "-interaction=nonstopmode"
FORCE_REBUILD_FLAG = "-g"
MINTED_CACHE_SUBDIR = "_minted"
SVG_INKSCAPE_CACHE = "svg-inkscape"
BUILD_EXAMPLES_SUBDIR = "examples"


@dataclass(frozen=True)
class ProjectConfig:
    build_dir: Path = Path("build")

    def is_ci(self) -> bool:
        return any(os.environ.get(var) for var in ["CI", "GITHUB_ACTIONS", "GITLAB_CI"])

    def verbose_enabled(self) -> bool:
        return os.environ.get("OMNILATEX_VERBOSE", "0").lower() in {"1", "true", "yes"}


# -----------------------------------------------------------------------------
# Terminal Output
# -----------------------------------------------------------------------------
class TerminalOutput:
    def __init__(self, use_color: bool = sys.stdout.isatty()):
        p = {
            "blue": "\033[94m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "cyan": "\033[96m",
            "gray": "\033[90m",
            "bold": "\033[1m",
            "end": "\033[0m",
        }
        if use_color:
            self.__dict__.update(p)
        else:
            self.__dict__.update({k: "" for k in p})

    def header(self, m: str):
        print(f"\n{self.bold}{self.blue}=== {m} ==={self.end}")

    def info(self, m: str):
        print(f"{self.cyan}[INFO]{self.end} {m}")

    def success(self, m: str):
        print(f"{self.green}[✓] {m}{self.end}")

    def warning(self, m: str):
        print(f"{self.yellow}[⚠] {m}{self.end}")

    def error(self, m: str):
        print(f"{self.bold}{self.red}[✗] {m}{self.end}", file=sys.stderr)

    def debug(self, m: str):
        print(f"{self.gray}[DEBUG] {m}{self.end}")


# -----------------------------------------------------------------------------
# Command Execution
# -----------------------------------------------------------------------------
class CommandRunner:
    def __init__(self, ui: TerminalOutput, build_mode: str, verbose: bool):
        self.ui, self.build_mode, self.verbose = ui, build_mode, verbose

    def run(
        self,
        cmd_args: List[str],
        *,
        extra_env: Optional[Dict[str, str]] = None,
        cwd: Optional[Path] = None,
    ) -> Tuple[int, List[str]]:
        """Executes a command, streams output, and returns (exit_code, logs). Does NOT raise on failure."""
        if self.verbose:
            self.ui.debug(f"RUN in '{cwd or Path.cwd()}': {' '.join(cmd_args)}")
        env = os.environ.copy()
        env["BUILD_MODE"] = self.build_mode
        if extra_env:
            env.update(extra_env)

        logs = []
        try:
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                cwd=cwd,
            )
            if process.stdout:
                for line in iter(process.stdout.readline, ""):
                    logs.append(line.rstrip())
            return_code = process.wait()
            return return_code, logs
        except FileNotFoundError as e:
            return -1, [f"Command not found: {cmd_args[0]}", str(e)]


@contextmanager
def working_directory(path: Path):
    prev = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev)


# -----------------------------------------------------------------------------
# Log Parsing for Package Timing
# -----------------------------------------------------------------------------

_PACKAGE_RE = re.compile(r"^Package:\s+(\S+)\s+(\d{4}/\d{2}/\d{2})\s*(.*)")
_LOAD_LUC_RE = re.compile(r"\(load luc:\s+(.+\.luc\))")
_CPU_TIME_RE = re.compile(
    r"^(\d+)\s+bytes\s+written.*\(([0-9.]+)\s+seconds\)", re.DOTALL
)
_LATEX_RUN_TIME_RE = re.compile(
    r" Transcript written on .*?\.\n.*?\(([^)]+)\)\s*$", re.DOTALL
)
_TOTAL_TIME_RE = re.compile(r"([0-9.]+)\s+seconds?")


def parse_log_for_package_times(log_content: str) -> Dict[str, dict]:
    """Parse LaTeX log content for per-package information and timing data."""
    packages: Dict[str, dict] = {}
    for line in log_content.splitlines():
        m = _PACKAGE_RE.match(line.strip())
        if m:
            name, date_str, rest = m.group(1), m.group(2), m.group(3)
            packages[name] = {
                "name": name,
                "date": date_str,
                "info": rest.strip(),
            }
        m = _LOAD_LUC_RE.search(line)
        if m:
            luc_path = Path(m.group(1))
            luc_name = luc_path.stem
            if luc_name not in packages:
                packages[luc_name] = {
                    "name": luc_name,
                    "source": "luc_cache",
                    "path": str(luc_path),
                }
    total_time = None
    for line in log_content.splitlines():
        m = _TOTAL_TIME_RE.search(line)
        if m and "seconds" in line.lower():
            val = float(m.group(1))
            if val > 0.5:
                total_time = val
    return {
        "packages": packages,
        "package_count": len(packages),
        "total_time_s": total_time,
    }


def extract_log_path(example_dir: Path) -> Optional[Path]:
    """Find the main.log file for an example."""
    log_path = example_dir / "main.log"
    return log_path if log_path.exists() else None


# -----------------------------------------------------------------------------
# Build Tasks
# -----------------------------------------------------------------------------
class BuildTasks:
    def __init__(
        self,
        config: ProjectConfig,
        runner: CommandRunner,
        ui: TerminalOutput,
        jobs: int,
        timings: bool = False,
        force: bool = False,
    ):
        self.config, self.runner, self.ui, self.jobs = config, runner, ui, jobs
        self.timings = timings
        self.force = force
        self.timings_data: List[dict] = []
        self._timings_lock = threading.Lock()
        self._cache_lock = threading.Lock()

    @staticmethod
    def _hash_for_paths(paths: List[Path]) -> str:
        h = hashlib.sha256()
        for p in sorted(paths):
            if p.exists():
                h.update(p.read_bytes())
        return h.hexdigest()

    def _load_build_cache(self) -> dict:
        cache_path = self.config.build_dir / "build_cache.json"
        if cache_path.exists():
            try:
                return json.loads(cache_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _save_build_cache(self, cache: dict) -> None:
        cache_path = self.config.build_dir / "build_cache.json"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, indent=2) + "\n", encoding="utf-8")

    def _collect_source_files(self, example_name: str) -> List[Path]:
        repo_root = Path(__file__).resolve().parent
        example_dir = repo_root / "examples" / example_name
        files: List[Path] = []
        tex_file = example_dir / MAIN_TEX_FILENAME
        if tex_file.exists():
            files.append(tex_file)
        for bib in example_dir.rglob("*.bib"):
            files.append(bib)
        for sty in repo_root.rglob("*.sty"):
            files.append(sty)
        for cls in repo_root.rglob("*.cls"):
            files.append(cls)
        return files

    def discover_examples(self) -> List[Path]:
        d = Path("examples")
        return (
            sorted(
                [
                    p
                    for p in d.iterdir()
                    if p.is_dir() and (p / MAIN_TEX_FILENAME).is_file()
                ]
            )
            if d.is_dir()
            else []
        )

    def list_examples(self, _=None):
        self.ui.header("Available Examples")
        for ex in self.discover_examples():
            print(f"  {self.ui.bold}{ex.name}{self.ui.end}")
        self.ui.success(f"Found {len(self.discover_examples())} example(s).")

    def _compile_example_worker(self, example_name: str) -> Tuple[str, bool, List[str]]:
        """
        Worker function that faithfully reproduces the original script's logic.
        Success is determined ONLY by the existence of the final PDF.
        """
        all_logs = []
        start_time = time.perf_counter()
        _timing_success = False
        try:
            repo_root = Path(__file__).resolve().parent
            example_dir = repo_root / "examples" / example_name

            if not self.force:
                source_files = self._collect_source_files(example_name)
                source_hash = self._hash_for_paths(source_files)
                cache = self._load_build_cache()
                cached = cache.get(f"examples/{example_name}")
                dest_pdf = (
                    repo_root / self.config.build_dir / BUILD_EXAMPLES_SUBDIR
                ) / f"{example_name}.pdf"
                if (
                    cached
                    and cached.get("source_hash") == source_hash
                    and dest_pdf.exists()
                ):
                    all_logs.append(
                        f"[green]✓ Cache hit for {example_name}, skipping build.[/green]"
                    )
                    _timing_success = True
                    return example_name, True, all_logs

            # --- Start: EXACT reproduction of original script's core logic ---
            cmd = [LATEXMK_COMMAND]
            latexmk_flags: List[str] = [INTERACTION_NONSTOP]
            if os.environ.get("OMNILATEX_FORCE_REBUILD") == "1":
                latexmk_flags.append(FORCE_REBUILD_FLAG)

            invoke: List[str] = cmd + latexmk_flags

            root_latexmkrc = repo_root / ".latexmkrc"
            if root_latexmkrc.exists():
                invoke.extend(["-r", str(root_latexmkrc)])

            invoke.append(MAIN_TEX_FILENAME)

            with working_directory(example_dir):
                # When --force is used, clean auxiliary files first to avoid
                # stale artifacts from different package versions (e.g. .glstex
                # from a different glossaries-extra version).
                if self.force:
                    self.runner.run([LATEXMK_COMMAND, "-C"])

                for cache_dir in (Path(MINTED_CACHE_SUBDIR), Path(SVG_INKSCAPE_CACHE)):
                    cache_dir.mkdir(parents=True, exist_ok=True)

                minted_cache_dir = self.config.build_dir / MINTED_CACHE_SUBDIR
                minted_cache_dir.mkdir(parents=True, exist_ok=True)

                extra_env = {
                    "MINTED_CACHE_DIR": str(minted_cache_dir.resolve()),
                    "OMNILATEX_EXAMPLE_ROOT": str(Path.cwd()),
                    "TEXINPUTS": os.pathsep.join([".", str(repo_root), ""]),
                    "LC_ALL": "C.utf8",
                }

                # Run the command but do not raise an exception on failure
                exit_code, logs_from_run = self.runner.run(
                    invoke, extra_env=extra_env, cwd=example_dir
                )
                all_logs.extend(logs_from_run)
            # --- End: EXACT reproduction of original script's core logic ---

            # Create build/examples directory early to avoid race conditions in concurrent builds
            repo_root = Path(__file__).resolve().parent
            build_examples_dir = (
                repo_root / self.config.build_dir / BUILD_EXAMPLES_SUBDIR
            )
            all_logs.append(f"[DEBUG] Build examples dir: {build_examples_dir}")
            build_examples_dir.mkdir(parents=True, exist_ok=True)

            # THE SOLE CRITERION FOR SUCCESS: Does the PDF exist?
            src_pdf = example_dir / "main.pdf"
            all_logs.append(f"[DEBUG] Checking for PDF at: {src_pdf}")
            if src_pdf.exists():
                all_logs.append(
                    f"[DEBUG] PDF exists, size: {src_pdf.stat().st_size} bytes"
                )
                dest_pdf = build_examples_dir / f"{example_name}.pdf"
                all_logs.append(f"[DEBUG] Destination PDF: {dest_pdf}")
                try:
                    shutil.copy(src_pdf, dest_pdf)
                    all_logs.append(f"[DEBUG] Copy operation completed")
                    if dest_pdf.exists():
                        all_logs.append(
                            f"[DEBUG] Destination PDF confirmed, size: {dest_pdf.stat().st_size} bytes"
                        )
                        all_logs.append(
                            f"[green]✓ PDF found and copied to build directory.[/green]"
                        )
                    else:
                        all_logs.append(
                            f"[bold red]✗ FAILURE: Copy reported success but destination PDF not found[/bold red]"
                        )
                        return example_name, False, all_logs
                except Exception as copy_exc:
                    all_logs.append(f"[DEBUG] Copy exception: {copy_exc}")
                    all_logs.append(
                        f"[bold red]✗ FAILURE: Could not copy PDF: {copy_exc}[/bold red]"
                    )
                    return example_name, False, all_logs
                _timing_success = True
                source_files = self._collect_source_files(example_name)
                source_hash = self._hash_for_paths(source_files)
                with self._cache_lock:
                    cache = self._load_build_cache()
                    cache[f"examples/{example_name}"] = {
                        "source_hash": source_hash,
                        "pdf_size": dest_pdf.stat().st_size,
                        "build_time": time.strftime(
                            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                        ),
                    }
                    self._save_build_cache(cache)
                return example_name, True, all_logs
            else:
                all_logs.append(
                    f"[bold red]✗ FAILURE: PDF not found at {src_pdf} after build attempt.[/bold red]"
                )
                return example_name, False, all_logs
        except Exception as exc:
            all_logs.append(
                f"[bold red]✗ A critical error occurred in worker for {example_name}: {exc}[/bold red]"
            )
            return example_name, False, all_logs
        finally:
            if self.timings:
                elapsed = time.perf_counter() - start_time
                repo_root = Path(__file__).resolve().parent
                example_dir = repo_root / "examples" / example_name
                pdf_size = (
                    (example_dir / "main.pdf").stat().st_size
                    if (example_dir / "main.pdf").exists()
                    else 0
                )
                timing_record = {
                    "name": example_name,
                    "mode": self.runner.build_mode,
                    "wall_time_s": round(elapsed, 3),
                    "pdf_size_bytes": pdf_size,
                    "success": _timing_success,
                }
                log_path = extract_log_path(example_dir)
                if log_path:
                    try:
                        log_content = log_path.read_text(
                            encoding="utf-8", errors="replace"
                        )
                        package_info = parse_log_for_package_times(log_content)
                        timing_record["package_timing"] = package_info
                    except Exception:
                        pass
                with self._timings_lock:
                    self.timings_data.append(timing_record)

    def _build_examples_rich_concurrent(self, example_names: List[str]):
        console = Console()
        log_lines, log_lock, active_jobs = deque(maxlen=200), threading.Lock(), []
        overall_progress = Progress(
            TextColumn("[b blue]Overall"),
            MofNCompleteColumn(),
            BarColumn(),
            TimeElapsedColumn(),
        )
        overall_task = overall_progress.add_task(
            "Building...", total=len(example_names)
        )

        layout = Layout()
        layout.split(
            Layout(overall_progress, size=3),
            Layout(Panel(Text(""), title="[b]Active Workers[/b]"), name="jobs"),
            Layout(
                Panel(
                    Text(""), title="[b yellow]Logs[/b yellow]", border_style="green"
                ),
                name="logs",
            ),
        )
        active_jobs_text, log_panel_text = Text(""), Text("")
        layout["jobs"].update(Panel(active_jobs_text, title="[b]Active Workers[/b]"))
        layout["logs"].update(
            Panel(
                log_panel_text, title="[b yellow]Logs[/b yellow]", border_style="green"
            )
        )

        results = []
        with Live(layout, console=console, screen=True, refresh_per_second=10):
            with ThreadPoolExecutor(max_workers=self.jobs) as executor:
                futures = {
                    executor.submit(self._compile_example_worker, name): name
                    for name in example_names
                }
                for future in as_completed(futures):
                    name = futures[future]
                    with log_lock:
                        active_jobs.append(name)
                    try:
                        _, success, logs = future.result()
                        results.append(success)
                        with log_lock:
                            log_lines.extend(logs)
                    except Exception as exc:
                        results.append(False)
                        log_lines.append(f"[b red]FATAL ERROR: {name}: {exc}[/b red]")
                    finally:
                        with log_lock:
                            active_jobs.remove(name)
                            active_jobs_text.plain = "\n".join(
                                f"[yellow]• Compiling {j}...[/yellow]"
                                for j in active_jobs
                            )
                            log_panel_text.plain = "\n".join(log_lines)
                        overall_progress.update(overall_task, advance=1)
        self.ui.header(
            f"Build Summary: {sum(1 for r in results if r)}/{len(example_names)} successful"
        )

    def _build_examples_simple_concurrent(self, example_names: List[str]):
        results, print_lock = [], threading.Lock()
        with ThreadPoolExecutor(max_workers=self.jobs) as executor:
            futures = {
                executor.submit(self._compile_example_worker, name): name
                for name in example_names
            }
            for future in tqdm(
                as_completed(futures),
                total=len(example_names),
                desc="Building Examples",
            ):
                try:
                    name, success, logs = future.result()
                    results.append(success)
                    with print_lock:
                        status = (
                            self.ui.green + "✓ Success"
                            if success
                            else self.ui.red + "✗ Failed"
                        )
                        self.ui.info(f"Finished: {name} ({status}{self.ui.end})")
                        if self.runner.verbose or not success:
                            self.ui.debug(f"--- Logs for {name} ---")
                            for line in logs:
                                print(f"  {line}")
                except Exception as exc:
                    name = futures[future]
                    results.append(False)
                    with print_lock:
                        self.ui.error(f"Exception in future for {name}: {exc}")
        self.ui.header(
            f"Build Summary: {sum(1 for r in results if r)}/{len(example_names)} successful"
        )

    def build_examples(self, files: Optional[List[str]] = None):
        self.ui.header(f"Building examples (up to {self.jobs} in parallel)")
        all_names = [e.name for e in self.discover_examples()]
        names = all_names if not files else [n for n in files if n in all_names]
        if not names:
            self.ui.warning("No valid examples to build.")
            return

        self.ui.info(f"Queued {len(names)} example(s) for build.")
        if RICH_AVAILABLE:
            self._build_examples_rich_concurrent(names)
        else:
            self.ui.warning(
                "`rich` not found. Falling back to simple concurrent display."
            )
            self._build_examples_simple_concurrent(names)

        if self.timings and self.timings_data:
            metrics_path = self.config.build_dir / "metrics.json"
            metrics_path.parent.mkdir(parents=True, exist_ok=True)
            summary = {
                "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "build_mode": self.runner.build_mode,
                "examples": sorted(self.timings_data, key=lambda x: x["name"]),
                "summary": {
                    "total": len(self.timings_data),
                    "successful": sum(1 for t in self.timings_data if t["success"]),
                    "total_time_s": round(
                        sum(t["wall_time_s"] for t in self.timings_data), 3
                    ),
                },
            }
            metrics_path.write_text(json.dumps(summary, indent=2) + "\n")
            self.ui.success(f"Timing metrics written to {metrics_path}")

            history_dir = self.config.build_dir / "metrics_history"
            history_dir.mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
            history_path = history_dir / f"metrics_{timestamp}.json"
            history_path.write_text(json.dumps(summary, indent=2) + "\n")
            self.ui.success(f"Metrics history written to {history_path}")

    # --- ALL ORIGINAL COMMANDS ---
    def build_example(self, files: List[str]):
        self.build_examples(files)

    def build_all(self, _=None):
        self.build_root()
        self.build_examples()

    def build_root(self, _=None):
        self.ui.header("Building Root")
        exit_code, logs = self.runner.run(
            [LATEXMK_COMMAND, INTERACTION_NONSTOP, MAIN_TEX_FILENAME]
        )
        pdf_path = Path(MAIN_TEX_FILENAME).with_suffix(".pdf")
        if pdf_path.exists():
            self.ui.success("Root build complete.")
            build_dir = self.config.build_dir
            build_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(pdf_path, build_dir / pdf_path.name)
            self.ui.success(f"Copied {pdf_path.name} to {build_dir}")
        else:
            self.ui.error("Build failure: PDF not generated.")
            raise SystemExit(1)

    def clean_all(self, _=None):
        self.ui.header("Full clean"), self.clean_aux()
        (
            shutil.rmtree(self.config.build_dir, ignore_errors=True),
            self.ui.success("Full cleanup finished."),
        )

    def clean_aux(self, _=None):
        self.ui.header("Cleaning auxiliary files")
        self.runner.run([LATEXMK_COMMAND, "-C"])
        self.clean_example([e.name for e in self.discover_examples()])

    def clean_example(self, files: List[str]):
        if files:
            self.ui.info(f"Cleaning {len(files)} example(s)")
            for name in files:
                try:
                    self.runner.run(
                        [LATEXMK_COMMAND, "-c"], cwd=Path("examples") / name
                    )
                except Exception:
                    self.ui.warning(f"Could not clean example {name}")

    def clean_pdf(self, _=None):
        self.ui.header("Cleaning PDF files")
        count = 0
        for pdf in Path(".").rglob("*.pdf"):
            if self.config.build_dir in pdf.parents or "examples" in [
                d.name for d in pdf.parents
            ]:
                pdf.unlink(missing_ok=True)
                count += 1
        self.ui.success(f"Removed {count} PDF(s).")

    def preflight(self, _=None):
        self.cmd_preflight()

    def build_tex(self, _=None):
        self.ui.header("Building TeX... (Not implemented)")

    def run_tests(self, _=None):
        return self.cmd_test()

    def cmd_watch(self, files: List[str]):
        """Watch source files for changes and rebuild."""
        watch_dirs = [Path(".")]
        extensions = {".tex", ".sty", ".cls", ".bib", ".lua", ".toml"}
        ui = self.ui
        ui.info("Watching for changes... (Ctrl+C to stop)")

        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class RebuildHandler(FileSystemEventHandler):
                def __init__(self, runner, extensions, files):
                    self.runner = runner
                    self.extensions = extensions
                    self.files = files
                    self._last_rebuild = 0

                def on_modified(self, event):
                    path = Path(event.src_path)
                    if path.suffix in self.extensions:
                        import time as _time

                        now = _time.time()
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
                for line in process.stdout:
                    path = Path(line.strip())
                    if path.suffix in extensions:
                        ui.info(f"\nChange detected: {path}")
                        self._rebuild_affected(path, files)
            except KeyboardInterrupt:
                process.terminate()

    def _rebuild_affected(self, changed_path: Path, files: List[str]):
        """Rebuild documents affected by a changed file."""
        if files:
            self.build_example(files)
        else:
            self.build_examples([])

    def _check_tool(self, tool: str, desc: str, required: bool = True):
        path = shutil.which(tool)
        if path:
            return (desc, True, f"Found at {path}")
        note = f"Not found" + ("" if not required else " (required)")
        return (desc, not required, note)

    def _get_texlive_version(self):
        try:
            result = subprocess.run(
                ["tex", "--version"], capture_output=True, text=True, timeout=5
            )
            for line in (result.stdout or "").splitlines():
                m = re.match(r".*TeX Live (\d{4})", line)
                if m:
                    return int(m.group(1))
        except Exception:
            pass
        return None

    def _check_latex_package(self, pkg: str) -> bool:
        try:
            result = subprocess.run(
                ["kpsewhich", f"{pkg}.sty"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def cmd_preflight(self, files=None):
        """Validate build environment readiness."""
        checks = []

        checks.append(self._check_tool("lualatex", "LuaTeX engine"))
        checks.append(self._check_tool("latexmk", "latexmk build tool"))

        checks.append(
            ("Python >= 3.10", sys.version_info >= (3, 10), f"Found {sys.version}")
        )

        checks.append(
            self._check_tool("inkscape", "Inkscape (SVG support)", required=False)
        )
        checks.append(self._check_tool("git", "Git CLI"))

        tex_version = self._get_texlive_version()
        checks.append(
            (
                "TeX Live >= 2024",
                tex_version is not None and tex_version >= 2024,
                f"Found TeX Live {tex_version or 'unknown'}",
            )
        )

        packages = [
            "fontspec",
            "unicode-math",
            "hyperref",
            "minted",
            "biblatex",
            "siunitx",
            "circuitikz",
            "forest",
        ]
        for pkg in packages:
            found = self._check_latex_package(pkg)
            checks.append((f"Package {pkg}", found, "Found" if found else "Missing"))

        passed = sum(1 for _, ok, _ in checks if ok)
        total = len(checks)
        for name, ok, detail in checks:
            status = "\u2713" if ok else "\u2717"
            self.ui.info(f"  {status} {name}: {detail}")

        if passed == total:
            self.ui.success(f"All {total} checks passed")
        else:
            self.ui.warning(f"{passed}/{total} checks passed")

    def cmd_test(self, files=None):
        """Run test suite (l3build + pytest)."""
        results = []
        self.ui.info("Running l3build check...")
        project_root = Path(__file__).resolve().parent.parent
        result = subprocess.run(
            ["l3build", "check"],
            capture_output=True,
            text=True,
            cwd=project_root,
        )
        results.append(("l3build check", result.returncode == 0))
        if result.returncode != 0:
            self.ui.warning(f"l3build check FAILED:\n{result.stdout}\n{result.stderr}")
        else:
            self.ui.success("l3build check passed")

        self.ui.info("Running pytest...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=project_root,
        )
        results.append(("pytest", result.returncode == 0))
        if result.returncode != 0:
            self.ui.warning(f"pytest FAILED:\n{result.stdout}")
        else:
            self.ui.success("pytest passed")

        passed = sum(1 for _, ok in results if ok)
        total = len(results)
        self.ui.info(f"\nTest Results: {passed}/{total} suites passed")
        if passed < total:
            return 1
        return 0

    def cmd_doctor(self, files=None):
        """Run comprehensive health diagnostics."""
        import platform as _platform

        self.ui.info("OmniLaTeX Doctor \u2014 Environment Health Check")
        self.ui.info("=" * 50)

        self.ui.info(f"Platform: {_platform.system()} {_platform.release()}")
        self.ui.info(f"Python: {sys.version}")
        self.ui.info(f"Architecture: {_platform.machine()}")

        checks = []

        for tool, desc in [
            ("lualatex", "LuaTeX engine"),
            ("latexmk", "Build orchestrator"),
            ("biber", "Bibliography processor"),
            ("bib2gls", "Glossary processor"),
            ("inkscape", "SVG converter"),
            ("git", "Version control"),
            ("pygmentize", "Code highlighting (Pygments)"),
        ]:
            path = shutil.which(tool)
            if path:
                try:
                    result = subprocess.run(
                        [tool, "--version"], capture_output=True, text=True, timeout=5
                    )
                    version = (result.stdout or result.stderr).split("\n")[0].strip()
                    checks.append((desc, True, f"{path}\n  {version}"))
                except Exception:
                    checks.append((desc, True, f"{path}"))
            else:
                remediation = {
                    "lualatex": "Install TeX Live: https://tug.org/texlive/",
                    "latexmk": "Install latexmk (usually bundled with TeX Live)",
                    "biber": "Install biber (usually bundled with TeX Live)",
                    "bib2gls": "Install bib2gls: tlmgr install bib2gls",
                    "inkscape": "Install Inkscape: https://inkscape.org/",
                    "git": "Install git: https://git-scm.com/",
                    "pygmentize": "pip install Pygments",
                }
                checks.append((desc, False, remediation.get(tool, "Install the tool")))

        for font_name in [
            "Monaspace Neon",
            "Atkinson Hyperlegible Next",
            "Libertinus Serif",
        ]:
            try:
                result = subprocess.run(
                    ["fc-list", ":family", font_name],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                found = font_name.lower() in result.stdout.lower()
                note = "Found" if found else "Not found (fallback font will be used)"
                checks.append((f"Font: {font_name}", found or True, note))
            except Exception:
                checks.append(
                    (
                        f"Font: {font_name}",
                        True,
                        "Could not check (fc-list unavailable)",
                    )
                )

        for name, ok, detail in checks:
            status = "PASS" if ok else "FAIL"
            self.ui.info(f"\n[{status}] {name}")
            self.ui.info(f"  {detail}")

        passed = sum(1 for _, ok, _ in checks if ok)
        total = len(checks)
        self.ui.info(f"\n{'=' * 50}")
        self.ui.info(f"Result: {passed}/{total} checks passed")

        failed = [(n, d) for n, ok, d in checks if not ok]
        if failed:
            self.ui.info("\nRemediation steps:")
            for name, detail in failed:
                self.ui.info(f"  \u2022 {name}: {detail}")


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def main() -> None:
    ui, config = TerminalOutput(), ProjectConfig()
    default_jobs = 2 if config.is_ci() else (os.cpu_count() or 2)
    parser = argparse.ArgumentParser(
        description="OmniLaTeX build tool.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--mode", choices=["dev", "prod", "ultra"], default="dev", help="Build mode."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose log output."
    )
    parser.add_argument(
        "--timings",
        action="store_true",
        help="Record per-example build metrics to build/metrics.json.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force rebuild, ignoring incremental build cache.",
    )
    parser.add_argument(
        "--source-date-epoch",
        type=int,
        default=None,
        metavar="TIMESTAMP",
        help="Set SOURCE_DATE_EPOCH for reproducible builds (Unix timestamp).",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=default_jobs,
        help=f"Parallel jobs. Default: {default_jobs}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    commands = {
        "build": (BuildTasks.build_all, "Build root and all examples.", False),
        "build-tex": (BuildTasks.build_tex, "Build specific .tex files.", True),
        "build-root": (BuildTasks.build_root, "Build root document.", False),
        "build-all": (BuildTasks.build_all, "Alias for 'build'.", False),
        "clean": (BuildTasks.clean_all, "Full cleanup.", False),
        "clean-aux": (BuildTasks.clean_aux, "Clean aux files.", False),
        "clean-pdf": (BuildTasks.clean_pdf, "Clean all PDFs.", False),
        "preflight": (BuildTasks.preflight, "Run preflight checks.", False),
        "lint": (BuildTasks.preflight, "Alias for 'preflight'.", False),
        "list-examples": (BuildTasks.list_examples, "List all examples.", False),
        "build-example": (
            BuildTasks.build_example,
            "Build specific example(s) concurrently.",
            True,
        ),
        "build-examples": (
            BuildTasks.build_examples,
            "Build all examples concurrently.",
            False,
        ),
        "clean-example": (BuildTasks.clean_example, "Clean specific example(s).", True),
        "clean-examples": (BuildTasks.clean_aux, "Clean all examples.", False),
        "test": (BuildTasks.run_tests, "Run test suite.", True),
        "watch": (BuildTasks.cmd_watch, "Watch files for changes and rebuild.", True),
        "doctor": (
            BuildTasks.cmd_doctor,
            "Comprehensive environment health diagnostics.",
            False,
        ),
    }
    for name, (handler, help_text, takes_files) in commands.items():
        sub = subparsers.add_parser(name, help=help_text)
        sub.set_defaults(handler=handler)
        if takes_files:
            sub.add_argument("files", nargs="*", default=None)

    args = parser.parse_args()
    if args.source_date_epoch is not None:
        os.environ["SOURCE_DATE_EPOCH"] = str(args.source_date_epoch)
    if "build" in args.command:
        ui.info(f"Using up to {args.jobs} parallel jobs.")
    runner = CommandRunner(
        ui, build_mode=args.mode, verbose=(args.verbose or config.verbose_enabled())
    )
    tasks = BuildTasks(
        config, runner, ui, jobs=args.jobs, timings=args.timings, force=args.force
    )

    try:
        args.handler(tasks, getattr(args, "files", None))
    except Exception as e:
        ui.error(f"An unexpected top-level error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
