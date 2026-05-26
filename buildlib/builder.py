from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from buildlib.config import (
    BUILD_EXAMPLES_SUBDIR,
    FORCE_REBUILD_FLAG,
    INTERACTION_NONSTOP,
    LATEXMK_COMMAND,
    MAIN_TEX_FILENAME,
    MINTED_CACHE_SUBDIR,
    ProjectConfig,
    REPO_ROOT,
    SVG_INKSCAPE_CACHE,
)
from buildlib.runner import CommandRunner
from buildlib.ui import TerminalOutput

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
# Log Parsing for Package Timing
# -----------------------------------------------------------------------------

_PACKAGE_RE = re.compile(r"^Package:\s+(\S+)\s+(\d{4}/\d{2}/\d{2})\s*(.*)")
_LOAD_LUC_RE = re.compile(r"\(load luc:\s+(.+\.luc\))")
_TOTAL_TIME_RE = re.compile(r"([0-9.]+)\s+seconds?")


def parse_log_for_package_times(log_content: str) -> dict[str, dict]:
    """Parse LaTeX log content for per-package information and timing data."""
    packages: dict[str, dict] = {}
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


def extract_log_path(example_dir: Path) -> Path | None:
    """Find the main.log file for an example."""
    log_path = example_dir / "main.log"
    return log_path if log_path.exists() else None


# -----------------------------------------------------------------------------
# Build Core Mixin
# -----------------------------------------------------------------------------
class _BuildCore:
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
        self.timings_data: list[dict] = []
        self._timings_lock = threading.Lock()
        self._cache_lock = threading.Lock()
        self._source_files_cache: dict[str, list[Path]] = {}
        self._shared_build_cache: dict | None = None

    @staticmethod
    def _hash_for_paths(paths: list[Path]) -> str:
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
        cache_path.write_text(
            json.dumps(cache, indent=2) + "\n",
            encoding="utf-8",
        )

    def _get_source_files(self, repo_root: Path) -> list[Path]:
        key = str(repo_root)
        if key not in self._source_files_cache:
            sty_files = list(repo_root.rglob("*.sty"))
            cls_files = list(repo_root.rglob("*.cls"))
            self._source_files_cache[key] = sty_files + cls_files
        return self._source_files_cache[key]

    def _collect_source_files(self, example_name: str) -> list[Path]:
        repo_root = REPO_ROOT
        example_dir = repo_root / "examples" / example_name
        files: list[Path] = []
        tex_file = example_dir / MAIN_TEX_FILENAME
        if tex_file.exists():
            files.append(tex_file)
        for bib in example_dir.rglob("*.bib"):
            files.append(bib)
        files.extend(self._get_source_files(repo_root))
        return files

    def cmd_cache_stats(self, _: object | None = None) -> None:
        self.ui.header("Build Cache Statistics")
        cache_path = REPO_ROOT / self.config.build_dir / "build_cache.json"
        if not cache_path.exists():
            self.ui.info("No build cache found.")
            return
        cache_data = self._load_build_cache()
        entries = {k: v for k, v in cache_data.items() if k.startswith("examples/")}
        total_examples = len(self.discover_examples())
        cached_examples = len(entries)
        file_size = cache_path.stat().st_size
        mtimes = [
            (k, v["build_time"])
            for k, v in entries.items()
            if "build_time" in v
        ]
        mtimes.sort(key=lambda x: x[1])
        self.ui.info(f"Cached entries:    {cached_examples}")
        self.ui.info(f"Cache file size:   {file_size:,} bytes")
        self.ui.info(f"Total examples:    {total_examples}")
        self.ui.info(f"Cached examples:   {cached_examples}/{total_examples}")
        if mtimes:
            self.ui.info(f"Oldest entry:      {mtimes[0][0]} ({mtimes[0][1]})")
            self.ui.info(f"Newest entry:      {mtimes[-1][0]} ({mtimes[-1][1]})")
        self.ui.success("Cache statistics complete.")

    def cmd_cache_clear(self, _: object | None = None) -> None:
        self.ui.header("Clearing Build Cache")
        cache_path = REPO_ROOT / self.config.build_dir / "build_cache.json"
        if cache_path.exists():
            cache_path.unlink()
            self.ui.success(f"Deleted build cache: {cache_path}")
        else:
            self.ui.info("No build cache file to delete.")

    def discover_examples(self) -> list[Path]:
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

    def list_examples(
        self,
        _: object | None = None,
        *,
        output_format: str = "text",
    ) -> None:
        examples = self.discover_examples()
        if output_format == "json":
            import json

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

    def _compile_example_worker(self, example_name: str) -> tuple[str, bool, list[str]]:
        """
        Worker function that faithfully reproduces the
        original script's logic. Success is determined ONLY
        by the existence of the final PDF.
        """
        all_logs = []
        start_time = time.perf_counter()
        _timing_success = False
        try:
            repo_root = REPO_ROOT
            example_dir = repo_root / "examples" / example_name

            if not self.force:
                source_files = self._collect_source_files(example_name)
                source_hash = self._hash_for_paths(source_files)
                with self._cache_lock:
                    if self._shared_build_cache is not None:
                        cache = self._shared_build_cache
                    else:
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
                        "[green]✓ Cache hit for "
                        f"{example_name}, skipping build.[/green]"
                    )
                    _timing_success = True
                    return example_name, True, all_logs

            # --- Start: EXACT reproduction of original script's core logic ---
            cmd = [LATEXMK_COMMAND]
            latexmk_flags: list[str] = [INTERACTION_NONSTOP]
            if os.environ.get("OMNILATEX_FORCE_REBUILD") == "1":
                latexmk_flags.append(FORCE_REBUILD_FLAG)

            invoke: list[str] = cmd + latexmk_flags

            root_latexmkrc = repo_root / ".latexmkrc"
            if root_latexmkrc.exists():
                invoke.extend(["-r", str(root_latexmkrc)])

            invoke.append(MAIN_TEX_FILENAME)

            # Use absolute paths to avoid thread-unsafe os.chdir().
            # The runner.run() call already sets cwd=example_dir.
            if self.force:
                self.runner.run([LATEXMK_COMMAND, "-C"], cwd=example_dir)

            for cache_dir in (
                Path(MINTED_CACHE_SUBDIR),
                Path(SVG_INKSCAPE_CACHE),
            ):
                (example_dir / cache_dir).mkdir(
                    parents=True, exist_ok=True
                )

            minted_cache_dir = example_dir / MINTED_CACHE_SUBDIR
            minted_cache_dir.mkdir(parents=True, exist_ok=True)

            extra_env = {
                "MINTED_CACHE_DIR": str(minted_cache_dir.resolve()),
                "OMNILATEX_EXAMPLE_ROOT": str(example_dir.resolve()),
                "TEXINPUTS": os.pathsep.join([".", str(repo_root), ""]),
                "LC_ALL": "C.utf8",
            }

            if self.config.cnf_lines:
                extra_env["OMNILATEX_CNF_LINES"] = ";".join(self.config.cnf_lines)

            # Run the command but do not raise an exception on failure
            exit_code, logs_from_run = self.runner.run(
                invoke, extra_env=extra_env, cwd=example_dir
            )
            all_logs.extend(logs_from_run)
            # --- End: EXACT reproduction of original script's core logic ---

            # Create build/examples directory early to
            # avoid race conditions in concurrent builds
            repo_root = REPO_ROOT
            build_examples_dir = (
                repo_root / self.config.build_dir
                / BUILD_EXAMPLES_SUBDIR
            )
            all_logs.append(
                f"[DEBUG] Build examples dir: "
                f"{build_examples_dir}"
            )
            build_examples_dir.mkdir(parents=True, exist_ok=True)

            # THE SOLE CRITERION FOR SUCCESS: Does the PDF exist?
            src_pdf = example_dir / "main.pdf"
            all_logs.append(f"[DEBUG] Checking for PDF at: {src_pdf}")
            if src_pdf.exists():
                all_logs.append(
                    "[DEBUG] PDF exists, size: "
                    f"{src_pdf.stat().st_size} bytes"
                )
                dest_pdf = build_examples_dir / f"{example_name}.pdf"
                all_logs.append(f"[DEBUG] Destination PDF: {dest_pdf}")
                try:
                    shutil.copy(src_pdf, dest_pdf)
                    # Preserve .log file for content validation tests
                    src_log = example_dir / "main.log"
                    if src_log.exists():
                        dest_log = build_examples_dir / f"{example_name}.log"
                        shutil.copy(src_log, dest_log)
                    all_logs.append(f"[DEBUG] Copy operation completed")
                    if dest_pdf.exists():
                        all_logs.append(
                            "[DEBUG] Destination PDF "
                            "confirmed, size: "
                            f"{dest_pdf.stat().st_size} bytes"
                        )
                        all_logs.append(
                            f"[green]✓ PDF found and copied to build directory.[/green]"
                        )
                    else:
                        all_logs.append(
                            "[bold red]✗ FAILURE: Copy reported "
                            "success but destination PDF not "
                            "found[/bold red]"
                        )
                        return example_name, False, all_logs
                except Exception as copy_exc:
                    all_logs.append(f"[DEBUG] Copy exception: {copy_exc}")
                    all_logs.append(
                        "[bold red]✗ FAILURE: Could not copy "
                        f"PDF: {copy_exc}[/bold red]"
                    )
                    return example_name, False, all_logs
                _timing_success = True
                source_files = self._collect_source_files(example_name)
                source_hash = self._hash_for_paths(source_files)
                with self._cache_lock:
                    if self._shared_build_cache is not None:
                        cache = self._shared_build_cache
                    else:
                        cache = self._load_build_cache()
                    cache[f"examples/{example_name}"] = {
                        "source_hash": source_hash,
                        "pdf_size": dest_pdf.stat().st_size,
                        "build_time": time.strftime(
                            "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                        ),
                    }
                    if self._shared_build_cache is None:
                        self._save_build_cache(cache)
                return example_name, True, all_logs
            else:
                all_logs.append(
                    "[bold red]✗ FAILURE: PDF not found at "
                    f"{src_pdf} after build attempt.[/bold red]"
                )
                return example_name, False, all_logs
        except Exception as exc:
            all_logs.append(
                "[bold red]✗ A critical error occurred in "
                f"worker for {example_name}: {exc}[/bold red]"
            )
            return example_name, False, all_logs
        finally:
            if self.timings:
                elapsed = time.perf_counter() - start_time
                repo_root = REPO_ROOT
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
                    except (OSError, UnicodeDecodeError, KeyError):
                        pass
                with self._timings_lock:
                    self.timings_data.append(timing_record)

    def _build_examples_rich_concurrent(self, example_names: list[str]):
        console = Console()
        log_lines, log_lock = deque(maxlen=200), threading.Lock()
        active_jobs: dict[str, float] = {}  # name -> start_time
        active_lock = threading.Lock()
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
            Layout(
                overall_progress, size=3
            ),
            Layout(
                Panel(
                    Text(""),
                    title="[b]Active Workers[/b]",
                ),
                name="jobs",
            ),
            Layout(
                Panel(
                    Text(""),
                    title="[b yellow]Logs[/b yellow]",
                    border_style="green",
                ),
                name="logs",
            ),
        )
        active_jobs_text, log_panel_text = Text(""), Text("")
        layout["jobs"].update(
            Panel(
                active_jobs_text,
                title="[b]Active Workers[/b]",
            )
        )
        layout["logs"].update(
            Panel(
                log_panel_text,
                title="[b yellow]Logs[/b yellow]",
                border_style="green",
            )
        )

        def _refresh_active():
            """Rebuild the active workers display from the dict."""
            lines = []
            for name, t0 in active_jobs.items():
                elapsed = time.perf_counter() - t0
                lines.append(
                    f"[cyan]⠋ {name}[/cyan]"
                    f"  [dim]{elapsed:.1f}s[/dim]"
                )
            active_jobs_text.plain = (
                "\n".join(lines)
                if lines
                else "[dim]—[/dim]"
            )

        results = []
        with Live(layout, console=console, screen=True, refresh_per_second=10):
            with ThreadPoolExecutor(max_workers=self.jobs) as executor:
                futures = {}
                for name in example_names:
                    future = executor.submit(
                        self._compile_example_worker, name
                    )
                    futures[future] = name
                    with active_lock:
                        active_jobs[name] = time.perf_counter()
                    _refresh_active()

                for future in as_completed(futures):
                    name = futures[future]
                    try:
                        _, success, logs = future.result()
                        results.append(success)
                        with log_lock:
                            log_lines.extend(logs)
                    except Exception as exc:
                        results.append(False)
                        log_lines.append(
                            f"[b red]FATAL ERROR: "
                            f"{name}: {exc}[/b red]"
                        )
                    finally:
                        with active_lock:
                            active_jobs.pop(name, None)
                            _refresh_active()
                            log_panel_text.plain = "\n".join(log_lines)
                        overall_progress.update(
                            overall_task, advance=1
                        )
        self.ui.header(
            "Build Summary: "
            f"{sum(1 for r in results if r)}"
            f"/{len(example_names)} successful"
        )

    def _build_examples_simple_concurrent(self, example_names: list[str]):
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
                        self.ui.info(
                            f"Finished: {name} "
                            f"({status}{self.ui.end})"
                        )
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

    def build_examples(self, files: list[str] | None = None):
        self.ui.header(f"Building examples (up to {self.jobs} in parallel)")
        all_names = [e.name for e in self.discover_examples()]
        names = all_names if not files else [n for n in files if n in all_names]
        if not names:
            self.ui.warning("No valid examples to build.")
            return

        self.ui.info(f"Queued {len(names)} example(s) for build.")

        self._shared_build_cache = self._load_build_cache()
        try:
            if RICH_AVAILABLE:
                self._build_examples_rich_concurrent(names)
            else:
                self.ui.warning(
                    "`rich` not found. Falling back to simple concurrent display."
                )
                self._build_examples_simple_concurrent(names)
        finally:
            with self._cache_lock:
                self._save_build_cache(self._shared_build_cache)
            self._shared_build_cache = None

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
            metrics_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
            self.ui.success(f"Timing metrics written to {metrics_path}")

            history_dir = self.config.build_dir / "metrics_history"
            history_dir.mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
            history_path = history_dir / f"metrics_{timestamp}.json"
            history_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
            self.ui.success(f"Metrics history written to {history_path}")

    # --- ALL ORIGINAL COMMANDS ---
    def build_example(self, files: list[str]):
        self.build_examples(files)

    def build_all(self, _: object | None = None) -> None:
        self.build_root()
        self.build_examples()

    def build_root(self, _: object | None = None) -> None:
        self.ui.header("Building Root")
        pdf_path = Path(MAIN_TEX_FILENAME).with_suffix(".pdf")

        if RICH_AVAILABLE and not self.config.is_ci():
            exit_code, logs = self._run_with_dashboard(
                [LATEXMK_COMMAND, INTERACTION_NONSTOP, MAIN_TEX_FILENAME],
                title="Building Root",
            )
        else:
            exit_code, logs = self.runner.run(
                [LATEXMK_COMMAND, INTERACTION_NONSTOP, MAIN_TEX_FILENAME]
            )

        if pdf_path.exists():
            self.ui.success("Root build complete.")
            build_dir = self.config.build_dir
            build_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(pdf_path, build_dir / pdf_path.name)
            self.ui.success(f"Copied {pdf_path.name} to {build_dir}")
        else:
            self.ui.error("Build failure: PDF not generated.")
            if exit_code != 0:
                self.ui.error(f"latexmk exited with code {exit_code}")
            # Print captured logs for debugging (especially in CI)
            tail = logs[-50:] if len(logs) > 50 else logs
            for line in tail:
                print(line)
            raise SystemExit(1)

    def _run_with_dashboard(
        self, cmd_args: list[str], *, title: str = "Building"
    ) -> tuple[int, list[str]]:
        """Run a command with a rich live dashboard showing progress and logs."""
        console = Console()
        log_lines: deque = deque(maxlen=50)
        start_time = time.perf_counter()

        # Build status table
        from rich.table import Table as RichTable

        status_table = RichTable(show_header=False, expand=True, box=None)
        status_table.add_column("Key", style="bold cyan", width=12)
        status_table.add_column("Value")
        status_table.add_row("Status", "[yellow]⏳ Running...[/yellow]")
        status_table.add_row("Elapsed", "0.0s")
        status_table.add_row("Engine", "lualatex")

        log_panel_text = Text("")

        layout = Layout()
        layout.split(
            Layout(
                Panel(status_table, title=f"[b]{title}[/b]", border_style="blue"),
                size=5,
            ),
            Layout(
                Panel(
                    log_panel_text,
                    title="[b dim]Build Log[/b dim]",
                    border_style="dim",
                ),
                name="logs",
            ),
        )

        def on_line(line: str):
            log_lines.append(line)
            log_panel_text.plain = "\n".join(log_lines)
            elapsed = time.perf_counter() - start_time
            status_table.rows[1].cells[1] = Text(f"{elapsed:.1f}s")

        exit_code = 0
        logs: list[str] = []
        try:
            with Live(layout, console=console, refresh_per_second=5):
                exit_code, logs = self.runner.run(cmd_args, on_line=on_line)
                elapsed = time.perf_counter() - start_time
                if exit_code == 0:
                    status_table.rows[0].cells[1] = Text("[green]✓ Complete[/green]")
                else:
                    status_table.rows[0].cells[1] = Text(
                        f"[red]✗ Failed (exit {exit_code})[/red]"
                    )
                status_table.rows[1].cells[1] = Text(f"{elapsed:.1f}s")
        except Exception as exc:
            # Dashboard failed, fall back to simple run
            self.ui.warning(f"Dashboard error ({exc}), falling back to simple output.")
            return self.runner.run(cmd_args)

        return exit_code, logs

    def clean_all(self, _: object | None = None) -> None:
        self.ui.header("Full cleanup")
        self.clean_aux()
        shutil.rmtree(self.config.build_dir, ignore_errors=True)
        self.ui.success("Full cleanup finished.")

    def clean_aux(self, _: object | None = None) -> None:
        self.ui.header("Cleaning auxiliary files")
        self.runner.run([LATEXMK_COMMAND, "-C"])
        self.clean_example([e.name for e in self.discover_examples()])

    def clean_example(self, files: list[str]):
        if files:
            self.ui.info(f"Cleaning {len(files)} example(s)")
            for name in files:
                try:
                    self.runner.run(
                        [LATEXMK_COMMAND, "-c"], cwd=Path("examples") / name
                    )
                except (OSError, subprocess.SubprocessError):
                    self.ui.warning(f"Could not clean example {name}")

    def clean_pdf(self, _: object | None = None) -> None:
        self.ui.header("Cleaning PDF files")
        count = 0
        for pdf in Path(".").rglob("*.pdf"):
            if self.config.build_dir in pdf.parents or "examples" in [
                d.name for d in pdf.parents
            ]:
                pdf.unlink(missing_ok=True)
                count += 1
        self.ui.success(f"Removed {count} PDF(s).")

    def preflight(self, _: object | None = None) -> None:
        self.cmd_preflight()

    def run_tests(self, _: object | None = None) -> object:
        return self.cmd_test()
