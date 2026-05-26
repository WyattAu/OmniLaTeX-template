#!/usr/bin/env python3
"""
OmniLaTeX build entry point.

Key capabilities:
  • Explicit dev/prod/ultra modes with diagnostics
    announced up front.
  • Comprehensive logging of every subprocess invocation
    with elapsed timing.
  • Per-command verbose output toggled via
    --verbose / OMNILATEX_VERBOSE=1.
  • High-level commands for root builds, example builds,
    cleaning, preflight, and tests.
  • ALWAYS-CONCURRENT example building with a robust
    Rich UI or a simple TQDM-based fallback.
  • Meticulously preserved build logic from the original
    script to ensure correctness.
  • Robust success checking based on PDF existence,
    not exit codes.
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
from typing import Callable
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


def _compute_ssim_windowed(
    arr1: "np.ndarray", arr2: "np.ndarray", window_size: int = 7
) -> float:
    """Sliding-window SSIM (Wang et al. 2004). Returns mean SSIM index."""
    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2

    h, w = arr1.shape
    if h < window_size or w < window_size:
        mu1, mu2 = np.mean(arr1), np.mean(arr2)
        sigma1, sigma2 = np.var(arr1), np.var(arr2)
        sigma12 = np.mean((arr1 - mu1) * (arr2 - mu2))
        return ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / (
            (mu1**2 + mu2**2 + C1) * (sigma1 + sigma2 + C2)
        )

    sigma = 1.5
    coords = np.arange(window_size) - window_size // 2
    g1d = np.exp(-(coords**2) / (2 * sigma**2))
    kernel = np.outer(g1d, g1d)
    kernel /= kernel.sum()
    kh, kw = kernel.shape
    ph, pw = kh // 2, kw // 2

    try:
        from scipy.signal import fftconvolve as _scipy_fftconvolve

        def _conv2d(a, k):
            return _scipy_fftconvolve(a, k, mode="same")
    except ImportError:

        def _conv2d(a, k):
            padded = np.pad(a, ((ph, ph), (pw, pw)), mode="constant")
            windows = np.lib.stride_tricks.sliding_window_view(padded, (kh, kw))
            return np.einsum("ijkl,kl->ij", windows, k)

    mu1 = _conv2d(arr1, kernel)
    mu2 = _conv2d(arr2, kernel)
    mu1_sq, mu2_sq, mu12 = mu1 * mu1, mu2 * mu2, mu1 * mu2
    sigma1_sq = _conv2d(arr1 * arr1, kernel) - mu1_sq
    sigma2_sq = _conv2d(arr2 * arr2, kernel) - mu2_sq
    sigma12 = _conv2d(arr1 * arr2, kernel) - mu12

    ssim_map = ((2 * mu12 + C1) * (2 * sigma12 + C2)) / (
        (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)
    )
    return float(np.mean(ssim_map))


@dataclass
class ProjectConfig:
    build_dir: Path = Path("build")
    cnf_lines: list[str] = None

    def is_ci(self) -> bool:
        return any(
            os.environ.get(var)
            for var in ["CI", "GITHUB_ACTIONS", "GITLAB_CI"]
        )

    def verbose_enabled(self) -> bool:
        return os.environ.get(
            "OMNILATEX_VERBOSE", "0"
        ).lower() in {"1", "true", "yes"}


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
    """Default timeout for all subprocess invocations (seconds)."""
    DEFAULT_TIMEOUT = 3600  # 1 hour

    def __init__(self, ui: TerminalOutput, build_mode: str, verbose: bool):
        self.ui, self.build_mode, self.verbose = ui, build_mode, verbose

    def run(
        self,
        cmd_args: list[str],
        *,
        extra_env: dict[str, str] | None = None,
        cwd: Path | None = None,
        on_line: Callable[[str], None] | None = None,
        timeout: int | None = None,
    ) -> tuple[int, list[str]]:
        """Executes a command, streams output, and returns
        (exit_code, logs). Does NOT raise on failure."""
        if self.verbose:
            self.ui.debug(
                f"RUN in '{cwd or Path.cwd()}': "
                f"{' '.join(cmd_args)}"
            )
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
                    if on_line:
                        on_line(line.rstrip())
            return_code = process.wait(timeout=timeout or self.DEFAULT_TIMEOUT)
            return return_code, logs
        except FileNotFoundError as e:
            return -1, [f"Command not found: {cmd_args[0]}", str(e)]
        except PermissionError as e:
            return -1, [f"Permission denied: {cmd_args[0]}", str(e)]
        except OSError as e:
            return -1, [f"OS error running {cmd_args[0]}: {e}"]
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            return -1, [f"Command timed out after {timeout or self.DEFAULT_TIMEOUT}s: {cmd_args[0]}"]


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
        repo_root = Path(__file__).resolve().parent
        example_dir = repo_root / "examples" / example_name
        files: list[Path] = []
        tex_file = example_dir / MAIN_TEX_FILENAME
        if tex_file.exists():
            files.append(tex_file)
        for bib in example_dir.rglob("*.bib"):
            files.append(bib)
        files.extend(self._get_source_files(repo_root))
        return files

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
            repo_root = Path(__file__).resolve().parent
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
            repo_root = Path(__file__).resolve().parent
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

    def cmd_watch(self, files: list[str]):
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

    def _check_tool(self, tool: str, desc: str, required: bool = True) -> tuple[str, bool, str]:
        path = shutil.which(tool)
        if path:
            return (desc, True, f"Found at {path}")
        note = f"Not found" + ("" if not required else " (required)")
        return (desc, not required, note)

    def _get_texlive_version(self) -> int | None:
        try:
            result = subprocess.run(
                ["tex", "--version"], capture_output=True, text=True, timeout=5
            )
            for line in (result.stdout or "").splitlines():
                m = re.match(r".*TeX Live (\d{4})", line)
                if m:
                    return int(m.group(1))
        except (subprocess.TimeoutExpired, OSError, ValueError):
            pass
        return None

    def _check_latex_package(self, pkg: str) -> bool:
        try:
            result = subprocess.run(
                ["kpsewhich", f"{pkg}.sty"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            return False

    def _check_all_latex_packages(self, packages: list[str]) -> dict[str, bool]:
        try:
            result = subprocess.run(
                ["kpsewhich"] + [f"{pkg}.sty" for pkg in packages],
                capture_output=True,
                text=True,
                timeout=30,
            )
            found = set()
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.strip().splitlines():
                    stem = Path(line.strip()).stem
                    found.add(stem)
            elif result.returncode != 0 and result.stdout:
                for line in result.stdout.strip().splitlines():
                    if line.strip():
                        stem = Path(line.strip()).stem
                        found.add(stem)
            return {pkg: pkg in found for pkg in packages}
        except (subprocess.TimeoutExpired, OSError):
            return {pkg: False for pkg in packages}

    def cmd_preflight(self, files: list[str] | None = None) -> None:
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
        pkg_results = self._check_all_latex_packages(packages)
        for pkg in packages:
            found = pkg_results[pkg]
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

    def cmd_test(self, files: list[str] | None = None) -> int:
        """Run test suite (l3build + pytest)."""
        results = []
        self.ui.info("Running l3build check...")
        project_root = Path(__file__).resolve().parent
        result = subprocess.run(
            ["l3build", "check"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=600,
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
            timeout=600,
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

    def _is_git_ref(self, ref: str) -> bool:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--verify", ref],
                capture_output=True, text=True, timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            return False

    def _find_tex_for_pdf(self, pdf_path: str) -> Path | None:
        pdf = Path(pdf_path)
        tex = pdf.with_suffix(".tex")
        if tex.exists():
            return tex
        tex = pdf.parent / MAIN_TEX_FILENAME
        if tex.exists():
            return tex
        return None

    def _diff_two_pdfs(self, a: str, b: str, output: str = None):
        self.ui.header(f"Diff: {Path(a).name} vs {Path(b).name}")
        latexdiff_path = shutil.which("latexdiff")
        tex_a = self._find_tex_for_pdf(a)
        tex_b = self._find_tex_for_pdf(b)
        if latexdiff_path and tex_a and tex_b:
            self.ui.info("Using latexdiff to produce annotated diff PDF")
            self._run_latexdiff(tex_a, tex_b, output)
        else:
            if not latexdiff_path:
                self.ui.warning("latexdiff not available; falling back to basic comparison")
            else:
                self.ui.warning("Could not locate .tex sources for both PDFs; falling back to basic comparison")
            self._basic_pdf_compare(a, b)

    def _diff_git_refs(self, ref_a: str, ref_b: str, output: str = None):
        self.ui.header(f"Git Diff: {ref_a} vs {ref_b}")
        import tempfile
        tmpdir = Path(tempfile.mkdtemp(prefix="omnilatex-diff-"))
        try:
            old_tex = tmpdir / "old.tex"
            new_tex = tmpdir / "new.tex"
            for ref, dest in [(ref_a, old_tex), (ref_b, new_tex)]:
                result = subprocess.run(
                    ["git", "show", f"{ref}:{MAIN_TEX_FILENAME}"],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode != 0:
                    self.ui.error(f"Could not extract {MAIN_TEX_FILENAME} from ref '{ref}'")
                    self.ui.info(f"  git error: {result.stderr.strip()}")
                    return
                dest.write_text(result.stdout, encoding="utf-8")
            latexdiff_path = shutil.which("latexdiff")
            if latexdiff_path:
                self.ui.info("Using latexdiff to produce annotated diff PDF")
                self._run_latexdiff(old_tex, new_tex, output, cwd=tmpdir)
            else:
                self.ui.warning("latexdiff not available; showing textual diff")
                result = subprocess.run(
                    ["diff", "-u", str(old_tex), str(new_tex)],
                    capture_output=True, text=True, timeout=10,
                )
                if result.stdout:
                    print(result.stdout)
                if result.returncode != 0:
                    self.ui.info("Files differ")
                else:
                    self.ui.success("Files are identical")
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def _run_latexdiff(self, tex_a: Path, tex_b: Path, output: str = None, cwd: Path = None):
        import tempfile
        work_dir = cwd or Path(tempfile.mkdtemp(prefix="omnilatex-diff-"))
        cleanup = cwd is None
        try:
            diff_tex = work_dir / "diff.tex"
            result = subprocess.run(
                ["latexdiff", str(tex_a.resolve()), str(tex_b.resolve())],
                capture_output=True, text=True, timeout=30,
                cwd=work_dir,
            )
            if result.returncode != 0:
                self.ui.error(f"latexdiff failed: {result.stderr.strip()}")
                return
            diff_tex.write_text(result.stdout, encoding="utf-8")
            self.ui.info("Compiling diff PDF...")
            repo_root = Path(__file__).resolve().parent
            extra_env = {
                "TEXINPUTS": os.pathsep.join([".", str(repo_root), ""]),
            }
            root_latexmkrc = repo_root / ".latexmkrc"
            cmd = [LATEXMK_COMMAND, INTERACTION_NONSTOP]
            if root_latexmkrc.exists():
                cmd.extend(["-r", str(root_latexmkrc)])
            cmd.append(diff_tex.name)
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=120,
                cwd=work_dir, env={**os.environ, **extra_env},
            )
            diff_pdf = work_dir / "diff.pdf"
            if diff_pdf.exists():
                out_path = Path(output) if output else Path.cwd() / "diff.pdf"
                shutil.copy2(diff_pdf, out_path)
                self.ui.success(f"Annotated diff PDF: {out_path}")
            else:
                self.ui.error("Failed to compile diff PDF")
                if result.stdout:
                    for line in result.stdout.splitlines()[-20:]:
                        print(f"  {line}")
        finally:
            if cleanup:
                shutil.rmtree(work_dir, ignore_errors=True)

    def _basic_pdf_compare(self, a: str, b: str):
        size_a = Path(a).stat().st_size
        size_b = Path(b).stat().st_size
        self.ui.info(f"  {Path(a).name}: {size_a:,} bytes")
        self.ui.info(f"  {Path(b).name}: {size_b:,} bytes")
        try:
            import fitz
            doc_a = fitz.open(a)
            doc_b = fitz.open(b)
            if doc_a.page_count != doc_b.page_count:
                self.ui.warning(
                    f"Page count mismatch: {doc_a.page_count} vs {doc_b.page_count}"
                )
            else:
                self.ui.info(f"Page count: {doc_a.page_count} (match)")
            diff_pct = abs(size_a - size_b) / max(size_a, size_b, 1) * 100
            if diff_pct < 1:
                self.ui.success(f"File sizes nearly identical ({diff_pct:.1f}% diff)")
            else:
                self.ui.warning(f"File sizes differ by {diff_pct:.1f}%")
            doc_a.close()
            doc_b.close()
        except ImportError:
            if size_a == size_b:
                self.ui.success("Files are identical in size")
            else:
                self.ui.warning("File sizes differ")

    def cmd_diff(self, files: list[str], regenerate_references: bool = False, output: str = None):
        """Compare PDFs, git refs, or example references.

        Modes:
          - Two PDF paths: Direct comparison, with latexdiff if .tex sources are found.
          - Two git refs: Extract sources and produce an annotated diff PDF.
          - Example names: Visual regression against reference baselines.

        When *regenerate_references* is True, copies built PDFs to
        tests/references/ instead of comparing.
        """
        if files and len(files) == 2 and not regenerate_references:
            a, b = files[0], files[1]
            a_pdf = Path(a).exists() and a.lower().endswith(".pdf")
            b_pdf = Path(b).exists() and b.lower().endswith(".pdf")
            if a_pdf and b_pdf:
                return self._diff_two_pdfs(a, b, output)
            if self._is_git_ref(a) and self._is_git_ref(b):
                return self._diff_git_refs(a, b, output)

        self.ui.header("Visual Regression Diff")

        ref_dir = Path(__file__).resolve().parent / "tests" / "references"
        build_dir = self.config.build_dir / BUILD_EXAMPLES_SUBDIR
        repo_root = Path(__file__).resolve().parent

        if not files:
            self.ui.warning("No examples specified.")
            return

        if regenerate_references:
            self.ui.info("Regenerate mode: copying built PDFs to references/")
            ref_dir.mkdir(parents=True, exist_ok=True)
            copied = 0
            for name in files:
                build_copy = build_dir / f"{name}.pdf"
                pdf_path = repo_root / "examples" / name / "main.pdf"
                source = build_copy if build_copy.exists() else pdf_path
                if not source.exists():
                    self.ui.warning(f"SKIP: {name} -- PDF not found")
                    continue
                shutil.copy2(source, ref_dir / f"{name}.pdf")
                copied += 1
            self.ui.success(f"Copied {copied} reference PDF(s) to {ref_dir}")
            return

        try:
            from PIL import Image
            import numpy as np

            _has_ssim = True
        except ImportError:
            _has_ssim = False
            self.ui.info(
                "pillow/numpy not available; falling back to byte-level comparison"
            )

        all_pass = True
        for name in files:
            example_dir = repo_root / "examples" / name
            pdf_path = example_dir / "main.pdf"
            ref_path = ref_dir / f"{name}.pdf"
            build_copy = build_dir / f"{name}.pdf"

            # Prefer the build output (already post-build) if available
            source = build_copy if build_copy.exists() else pdf_path

            if not source.exists():
                self.ui.warning(f"SKIP: {name} \u2014 PDF not found")
                continue

            if not ref_path.exists():
                self.ui.info(
                    f"GENERATE: {name} \u2014 no reference, copying as baseline"
                )
                ref_path.parent.mkdir(parents=True, exist_ok=True)

                shutil.copy2(source, ref_path)
                continue

            # Compare using SSIM (requires pymupdf + pillow + numpy)
            if _has_ssim:
                try:
                    import fitz  # noqa: F401

                    ref_doc = fitz.open(str(ref_path))
                    test_doc = fitz.open(str(source))
                    try:
                        if ref_doc.page_count != test_doc.page_count:
                            self.ui.error(
                                f"FAIL: {name} — page count mismatch "
                                f"(ref={ref_doc.page_count}, test={test_doc.page_count})"
                            )
                            all_pass = False
                            continue

                        for i in range(ref_doc.page_count):
                            dpi = 150
                            mat = fitz.Matrix(dpi / 72, dpi / 72)
                            ref_pix = ref_doc[i].get_pixmap(matrix=mat)
                            test_pix = test_doc[i].get_pixmap(matrix=mat)
                            ref_img = Image.frombytes(
                                "RGB", [ref_pix.width, ref_pix.height], ref_pix.samples
                            )
                            test_img = Image.frombytes(
                                "RGB", [test_pix.width, test_pix.height], test_pix.samples
                            )

                            arr1 = np.array(ref_img.convert("L"), dtype=np.float64)
                            arr2 = np.array(test_img.convert("L"), dtype=np.float64)
                            if arr1.shape != arr2.shape:
                                self.ui.error(
                                    f"FAIL: {name} page {i + 1} — dimension mismatch"
                                )
                                all_pass = False
                                continue

                            ssim = _compute_ssim_windowed(arr1, arr2)

                            threshold = 0.95
                            page_pass = ssim >= threshold
                            status = "✅" if page_pass else "❌"
                            self.ui.info(f"  Page {i + 1}: SSIM={ssim:.4f} {status}")
                            if not page_pass:
                                all_pass = False
                    finally:
                        ref_doc.close()
                        test_doc.close()
                    continue  # SSIM comparison done, skip byte-level fallback

                except ImportError:
                    self.ui.info(
                        f"  pymupdf not available for {name}; falling back to byte-level"
                    )

            # Byte-level fallback (no SSIM deps available)
            import hashlib

            ref_hash = hashlib.sha256(source.read_bytes()).hexdigest()[:16]
            test_hash = hashlib.sha256(ref_path.read_bytes()).hexdigest()[:16]
            if ref_hash == test_hash:
                self.ui.info(f"\u2705 PASS: {name} (byte-identical)")
            else:
                self.ui.error(f"\u274c FAIL: {name} (content differs)")
                all_pass = False

        if all_pass:
            self.ui.success("All comparisons passed")
        else:
            self.ui.error("Visual regressions detected")

    def cmd_scaffold_institution(self, files: list[str]):
        """Create a new institution config from the generic template."""
        self.ui.header("Scaffold Institution")

        if not files:
            self.ui.warning("Usage: build.py scaffold-institution <name>")
            self.ui.info(
                "Creates config/institutions/<name>/<name>.sty from the generic template."
            )
            return

        name = files[0]
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            self.ui.error(
                f"Invalid institution name '{name}'. "
                "Use only alphanumeric characters, hyphens, and underscores."
            )
            return
        repo_root = Path(__file__).resolve().parent
        src = repo_root / "config" / "institutions" / "generic"
        dst = repo_root / "config" / "institutions" / name

        # Verify resolved path stays within expected directory
        if not dst.resolve().is_relative_to(repo_root / "config" / "institutions"):
            self.ui.error(f"Institution name '{name}' resolves outside institutions directory")
            return

        if not src.exists():
            self.ui.error(f"Generic template not found at {src}")
            return

        if dst.exists():
            self.ui.error(f"Institution '{name}' already exists at {dst}")
            return

        shutil.copytree(src, dst)

        # Rename generic.sty -> <name>.sty
        old_sty = dst / "generic.sty"
        new_sty = dst / f"{name}.sty"
        if old_sty.exists():
            old_sty.rename(new_sty)

        # Rename logo directory
        old_logo_dir = dst / "assets" / "logos" / "generic"
        new_logo_dir = dst / "assets" / "logos" / name
        if old_logo_dir.exists():
            old_logo_dir.rename(new_logo_dir)

        # Update ProvidesPackage and comments
        if new_sty.exists():
            content = new_sty.read_text(encoding="utf-8")
            content = content.replace(
                "config/institutions/generic/generic",
                f"config/institutions/{name}/{name}",
            )
            content = content.replace(
                "Generic Institution Configuration", f"{name} Institution Configuration"
            )
            content = content.replace("assets/logos/generic", f"assets/logos/{name}")
            content = content.replace("institution=generic]", f"institution={name}]")
            new_sty.write_text(content, encoding="utf-8")

        self.ui.success(f"Scaffolded institution: {name}")
        self.ui.info(f"  Config: {dst / f'{name}.sty'}")
        self.ui.info(f"  Assets: {dst / 'assets' / 'logos' / name}")
        self.ui.info(f"  Next: customize the .sty file, add your logo, update colors")
        self.ui.info(
            f"  Usage: \\documentclass[doctype=thesis,institution={name}]{{omnilatex}}"
        )

    def cmd_scaffold_language(self, files: list[str]):
        """Create a language addition guide with translation stubs."""
        self.ui.header("Scaffold Language")

        if not files:
            self.ui.warning("Usage: build.py scaffold-language <language-name>")
            self.ui.info(
                "Creates a guide file with translation stubs for adding a new language."
            )
            return

        lang = files[0].lower().strip()
        repo_root = Path(__file__).resolve().parent
        i18n_file = repo_root / "lib" / "language" / "omnilatex-i18n.sty"

        if not i18n_file.exists():
            self.ui.error(f"i18n module not found at {i18n_file}")
            return

        # Extract all translation keys from the i18n file

        content = i18n_file.read_text(encoding="utf-8")
        keys = sorted(set(re.findall(r"\\DeclareTranslation\{(?:english|german|french|spanish)\}\{(\w+)\}", content)))

        if not keys:
            self.ui.error("No translation keys found in i18n module")
            return

        # Check if language already exists
        escaped_lang = re.escape(lang)
        if re.search(r"\\DeclareTranslation\{" + escaped_lang + r"\}", content):
            self.ui.warning(f"Language '{lang}' already has translations in the i18n module")
            self.ui.info("Proceeding anyway to generate a fresh guide.")

        # Generate guide file
        guide_path = repo_root / "docs" / f"language-guide-{lang}.tex"

        lines = [
            f"% OmniLaTeX Language Addition Guide: {lang}",
            f"% Generated by build.py scaffold-language {lang}",
            f"% Date: {time.strftime('%Y-%m-%d')}",
            "%",
            "% This file contains translation stubs for all OmniLaTeX UI strings.",
            "% Fill in the translations and then integrate them into the i18n module.",
            "%",
            "% STEPS:",
            f"% 1. Translate all entries below (replace '???' with {lang} translations)",
            f"% 2. Add '{lang}' to \\setotherlanguages in lib/language/omnilatex-i18n.sty",
            "% 3. Copy each \\DeclareTranslation line into lib/language/omnilatex-i18n.sty",
            "%    next to the corresponding english/german/french/spanish entries",
            "% 4. Test with: \\documentclass[language=" + lang + "]{omnilatex}",
            "% 5. Remove this guide file when done",
            "",
            f"% === Translation stubs for '{lang}' ({len(keys)} keys) ===",
            "",
        ]

        for key in keys:
            lines.append(f"% TODO: Translate '{key}' to {lang}")
            lines.append(f"\\DeclareTranslation{{{lang}}}{{{key}}}{{???}}")

        lines.extend([
            "",
            "% === Integration Instructions ===",
            "%",
            "% In lib/language/omnilatex-i18n.sty:",
            "%",
            f"% 1. Add '{lang}' to the \\setotherlanguages list (line ~36):",
            f"%    \\setotherlanguages'{{'german,english,french,spanish,simplifiedchinese,japanese," + lang + "'}}'",
            "%",
            "% 2. For each key above, add the \\DeclareTranslation line after the",
            "%    existing translations for that key (after the spanish entry).",
            "%",
            f"% 3. If the 'translations' package doesn't support '{lang}':",
            "%    - Polyglossia will still handle standard captions (TOC, figures, tables)",
            "%    - OmniLaTeX-specific translations will work when language={lang} is active",
            "%    - See CONTRIBUTING.md for details on CJK language support",
        ])

        guide_path.parent.mkdir(parents=True, exist_ok=True)
        guide_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        self.ui.success(f"Language guide created: {guide_path}")
        self.ui.info(f"  Language: {lang}")
        self.ui.info(f"  Translation keys: {len(keys)}")
        self.ui.info(f"  Next steps:")
        self.ui.info(f"    1. Edit {guide_path.name} and fill in all '???' translations")
        self.ui.info(f"    2. Add '{lang}' to \\setotherlanguages in lib/language/omnilatex-i18n.sty")
        self.ui.info(f"    3. Copy \\DeclareTranslation lines into the i18n module")
        self.ui.info(f"    4. Test with \\documentclass[language={lang}]{{omnilatex}}")

    VALID_DOCTYPES = [
        "book",
        "thesis",
        "dissertation",
        "manual",
        "guide",
        "handbook",
        "report",
        "technicalreport",
        "standard",
        "patent",
        "article",
        "inlinepaper",
        "journal",
        "dictionary",
        "cv",
        "cover-letter",
        "poster",
        "presentation",
        "letter",
    ]

    VALID_LANGUAGES = [
        "english",
        "german",
        "french",
        "spanish",
        "polish",
        "dutch",
        "catalan",
        "brazilian",
        "italian",
        "portuguese",
        "romanian",
        "turkish",
        "greek",
        "russian",
        "ukrainian",
        "czech",
        "slovak",
        "slovenian",
        "serbian",
        "croatian",
        "bulgarian",
        "mongolian",
        "chinese",
        "japanese",
        "korean",
    ]

    def cmd_init(
        self,
        files: list[str],
        doctype: str = None,
        institution: str = None,
        language: str = None,
        thesis: bool = False,
    ):
        """Initialize a new OmniLaTeX project from a template."""
        self.ui.header("Initialize Project")

        if not files:
            self.ui.warning("Usage: build.py init [OPTIONS] <project-name>")
            self.ui.info(
                "Creates a new OmniLaTeX project from the minimal-starter template."
            )
            self.ui.info("Options:")
            self.ui.info("  --doctype TYPE      Set document type (default: book)")
            self.ui.info("  --institution NAME  Set institution (default: none)")
            self.ui.info("  --language LANG     Set language (default: english)")
            self.ui.info("  --thesis            Shortcut for --doctype thesis with full thesis structure")
            return

        if thesis and doctype is None:
            doctype = "thesis"

        project_name = files[0]
        if not re.match(r'^[a-zA-Z0-9_-]+$', project_name):
            self.ui.error(
                f"Invalid project name '{project_name}'. "
                "Use only alphanumeric characters, hyphens, and underscores."
            )
            return
        repo_root = Path(__file__).resolve().parent
        src = repo_root / "examples" / "minimal-starter"
        dst = Path.cwd() / project_name

        # Verify resolved path stays within current directory
        if not dst.resolve().is_relative_to(Path.cwd()):
            self.ui.error(f"Project name '{project_name}' resolves outside current directory")
            return

        if not src.exists():
            self.ui.error(f"Template not found at {src}")
            return

        if dst.exists():
            self.ui.error(f"Directory '{project_name}' already exists")
            return

        # Validate doctype
        if doctype is not None:
            if doctype.lower() not in self.VALID_DOCTYPES:
                self.ui.error(
                    f"Unknown doctype '{doctype}'. Valid options: "
                    + ", ".join(self.VALID_DOCTYPES)
                )
                return
            doctype = doctype.lower()

        # Validate language
        if language is not None:
            if language.lower() not in self.VALID_LANGUAGES:
                self.ui.error(
                    f"Unknown language '{language}'. Valid options: "
                    + ", ".join(self.VALID_LANGUAGES)
                )
                return
            language = language.lower()

        # Copy template (exclude build artifacts)
        ignore = shutil.ignore_patterns(
            "*.aux",
            "*.log",
            "*.out",
            "*.toc",
            "*.pdf",
            "*.fls",
            "*.fdb_latexmk",
            "*.synctex*",
            "*.bbl",
            "*.bcf",
            "*.blg",
            "*.run.xml",
            "*-blx.*",
            "*SAVE-ERROR",
            "*.glg",
            "*.glo",
            "*.gls",
            "*.acn",
            "*.acr",
            "*.glstex",
            "*.syi",
            "*.syg",
            "*.pyc",
            "__pycache__",
            "_minted*",
            "*.indent.log",
            "build/",
            ".git/",
            "node_modules/",
        )
        shutil.copytree(src, dst, ignore=ignore)

        # Create a .latexmkrc symlink pointing to the root
        latexmkrc_src = repo_root / ".latexmkrc"
        latexmkrc_dst = dst / ".latexmkrc"
        if latexmkrc_src.exists() and not latexmkrc_dst.exists():
            latexmkrc_dst.symlink_to(latexmkrc_src)

        # Patch main.tex if any options were specified
        main_tex = dst / "main.tex"
        if (doctype or institution or language) and main_tex.exists():

            content = main_tex.read_text(encoding="utf-8")

            # Multi-line regex: \documentclass[...options...]{class}
            m = re.search(r"(\\documentclass\s*\[)([\s\S]*?)(\]\{[^}]+\})", content)
            if m:
                prefix, opts_str, suffix = m.groups()
                existing_opts = [
                    o.strip()
                    for o in opts_str.replace("\n", " ").split(",")
                    if o.strip() and not o.strip().startswith("%")
                ]
                # Strip inline comments from option values
                cleaned_opts = []
                for o in existing_opts:
                    if "%" in o:
                        o = o[: o.index("%")].strip()
                    if o:
                        cleaned_opts.append(o)
                existing_opts = cleaned_opts
                # Remove options we're overriding
                existing_opts = [
                    o
                    for o in existing_opts
                    if not o.startswith("doctype=")
                    and not o.startswith("institution=")
                    and not o.startswith("language=")
                ]
                # Apply overrides
                if doctype:
                    existing_opts.insert(0, f"doctype={doctype}")
                if institution:
                    existing_opts.append(f"institution={institution}")
                if language:
                    existing_opts.append(f"language={language}")
                new_docclass = f"{prefix}{', '.join(existing_opts)}{suffix}"
                content = content[: m.start()] + new_docclass + content[m.end() :]
                main_tex.write_text(content, encoding="utf-8")

        if thesis:
            self._create_thesis_structure(dst, project_name, doctype, institution, language)

        self.ui.success(f"Initialized project: {project_name}")
        self.ui.info(f"  Location: {dst}")
        self.ui.info(f"  Template: minimal-starter")
        if doctype:
            self.ui.info(f"  Doctype: {doctype}")
        if institution:
            self.ui.info(f"  Institution: {institution}")
        if language:
            self.ui.info(f"  Language: {language}")
        if thesis:
            self.ui.info(f"  Structure: thesis (chapters, bib, figures)")
        self.ui.info(f"  Next steps:")
        self.ui.info(f"    1. cd {project_name}")
        if thesis:
            self.ui.info(f"    2. Edit chapters/ with your thesis content")
            self.ui.info(f"    3. Add references to bib/bibliography.bib")
            self.ui.info(f"    4. latexmk -lualatex main.tex")
        else:
            self.ui.info(f"    2. Edit main.tex to set your title, author, and content")
            self.ui.info(f"    3. python build.py build-root    (from repo root)")
            self.ui.info(f"       or latexmk -lualatex main.tex  (standalone)")

    def _create_thesis_structure(
        self, dst: Path, project_name: str, doctype: str, institution: str, language: str,
    ):
        chapters_dir = dst / "chapters"
        chapters_dir.mkdir(parents=True, exist_ok=True)

        chapter_templates = {
            "introduction.tex": (
                "\\chapter{Introduction}\n"
                "\n"
            ),
            "methodology.tex": (
                "\\chapter{Methodology}\n"
                "\n"
            ),
            "results.tex": (
                "\\chapter{Results}\n"
                "\n"
            ),
            "conclusion.tex": (
                "\\chapter{Conclusion}\n"
                "\n"
            ),
        }
        for filename, content in chapter_templates.items():
            (chapters_dir / filename).write_text(content, encoding="utf-8")

        bib_dir = dst / "bib"
        bib_dir.mkdir(parents=True, exist_ok=True)
        (bib_dir / "bibliography.bib").write_text(
            "@article{example2024,\n"
            "  author  = {Author, Example},\n"
            "  title   = {Example Article Title},\n"
            "  journal = {Journal of Examples},\n"
            "  year    = {2024},\n"
            "  volume  = {1},\n"
            "  pages   = {1--10},\n"
            "}\n",
            encoding="utf-8",
        )

        figures_dir = dst / "figures"
        figures_dir.mkdir(parents=True, exist_ok=True)
        (figures_dir / ".gitkeep").touch()

        repo_root = Path(__file__).resolve().parent
        latexmkrc_src = repo_root / ".latexmkrc"
        latexmkrc_dst = dst / ".latexmkrc"
        if latexmkrc_src.exists():
            if latexmkrc_dst.is_symlink():
                latexmkrc_dst.unlink()
            if not latexmkrc_dst.exists():
                latexmkrc_dst.symlink_to(latexmkrc_src)

        main_tex = dst / "main.tex"
        opts_parts = []
        if doctype:
            opts_parts.append(f"doctype={doctype}")
        else:
            opts_parts.append("doctype=thesis")
        if institution:
            opts_parts.append(f"institution={institution}")
        if language:
            opts_parts.append(f"language={language}")
        opts_str = ", ".join(opts_parts)
        main_tex.write_text(
            f"\\documentclass[{opts_str}]{{omnilatex}}\n"
            "\n"
            f"\\title{{{project_name.replace('-', ' ').replace('_', ' ').title()}}}\n"
            "\\author{Your Name}\n"
            "\\date{\\today}\n"
            "\n"
            "\\addbibresource{bib/bibliography.bib}\n"
            "\n"
            "\\graphicspath{{figures/}}\n"
            "\n"
            "\\begin{document}\n"
            "\\maketitle\n"
            "\\tableofcontents\n"
            "\n"
            "\\include{chapters/introduction}\n"
            "\\include{chapters/methodology}\n"
            "\\include{chapters/results}\n"
            "\\include{chapters/conclusion}\n"
            "\n"
            "\\printbibliography\n"
            "\\end{document}\n",
            encoding="utf-8",
        )

        (dst / "README.md").write_text(
            f"# {project_name}\n"
            "\n"
            "A thesis project built with [OmniLaTeX](https://github.com/WyattAu/OmniLaTeX-template).\n"
            "\n"
            "## Structure\n"
            "\n"
            "- `main.tex` — Main document file\n"
            "- `chapters/` — Thesis chapters (introduction, methodology, results, conclusion)\n"
            "- `bib/bibliography.bib` — Bibliography database\n"
            "- `figures/` — Figure assets\n"
            "- `.latexmkrc` — Build configuration (symlink to OmniLaTeX root)\n"
            "\n"
            "## Building\n"
            "\n"
            "```bash\n"
            "latexmk -lualatex main.tex\n"
            "```\n"
            "\n"
            "Or from the OmniLaTeX repo root:\n"
            "\n"
            "```bash\n"
            f"python build.py build-example {project_name}\n"
            "```\n",
            encoding="utf-8",
        )

    def cmd_doctor(self, files: list[str] | None = None) -> None:
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
                except (subprocess.TimeoutExpired, OSError, ValueError):
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

        font_names = [
            "Monaspace Neon",
            "Atkinson Hyperlegible Next",
            "Libertinus Serif",
        ]

        font_results: dict[str, tuple[bool, str]] = {}

        fc_list_output = ""
        try:
            result = subprocess.run(
                ["fc-list", ":family"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                fc_list_output = result.stdout.lower()
        except (subprocess.TimeoutExpired, OSError):
            pass

        lualatex_check_done = False

        for font_name in font_names:
            found = None

            if font_name.lower() in fc_list_output:
                found = True

            if found is None and not lualatex_check_done:
                try:
                    import tempfile
                    import os

                    tex_content = (
                        "\\RequirePackage{fontspec}\n"
                        "\\newcommand{\\checkfont}[1]{"
                        "\\IfFontExistsTF{#1}{\\typeout{FONTFOUND:#1}}"
                        "{\\typeout{FONTMISSING:#1}}}\n"
                    )
                    for fn in font_names:
                        if fn not in font_results:
                            tex_content += f"\\checkfont{{{fn}}}\n"
                    tex_content += "\\stop\n"

                    with tempfile.NamedTemporaryFile(
                        mode="w", suffix=".tex", delete=False
                    ) as tmp:
                        tmp.write(tex_content)
                        tmp_path = tmp.name

                    try:
                        result = subprocess.run(
                            ["lualatex", "--interaction=nonstopmode", tmp_path],
                            capture_output=True,
                            text=True,
                            timeout=30,
                        )
                        output = result.stdout + result.stderr
                        for fn in font_names:
                            if fn not in font_results:
                                if f"FONTFOUND:{fn}" in output:
                                    font_results[fn] = (
                                        True,
                                        "Found (via LuaLaTeX)",
                                    )
                                else:
                                    font_results[fn] = (
                                        False,
                                        "Not found (fallback font will be used)",
                                    )
                    finally:
                        os.unlink(tmp_path)

                    lualatex_check_done = True
                except (OSError, subprocess.SubprocessError):
                    lualatex_check_done = True

            if found is not None and font_name not in font_results:
                note = (
                    "Found" if found else "Not found (fallback font will be used)"
                )
                font_results[font_name] = (found, note)

            if font_name not in font_results:
                font_results[font_name] = (
                    False,
                    "Could not check (font tools unavailable)",
                )

        for font_name in font_names:
            ok, note = font_results[font_name]
            checks.append((f"Font: {font_name}", ok, note))

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

    def cmd_check(self, files: list[str] | None = None) -> int:
        """Cross-reference integrity check on LaTeX files."""
        from collections import defaultdict

        self.ui.header("Cross-Reference Integrity Check")

        scan_dir = Path(files[0]) if files and files else Path.cwd()

        if not scan_dir.is_dir():
            self.ui.error(f"Not a directory: {scan_dir}")
            return 1

        tex_files = sorted(
            f for f in scan_dir.rglob("*.tex")
            if self.config.build_dir not in f.parents
            and "_minted" not in str(f)
        )
        bib_files = sorted(
            f for f in scan_dir.rglob("*.bib")
            if self.config.build_dir not in f.parents
        )

        if not tex_files:
            self.ui.warning(f"No .tex files found in {scan_dir}")
            return 0

        self.ui.info(f"Scanning {len(tex_files)} .tex file(s), {len(bib_files)} .bib file(s)")

        _LABEL_RE = re.compile(r"\\label\{([^}]+)\}")
        _REF_RE = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref|pageref)\{([^}]+)\}")
        _CITE_RE = re.compile(r"\\(?:cite|nocite)\{([^}]+)\}")
        _BIB_ENTRY_RE = re.compile(r"@\w+\{([^,\s]+),")

        labels: dict[str, list[str]] = defaultdict(list)
        refs: dict[str, list[str]] = defaultdict(list)
        cites: dict[str, list[str]] = defaultdict(list)
        bib_keys: set[str] = set()

        for tex in tex_files:
            try:
                content = tex.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                self.ui.warning(f"Cannot read {tex}: {exc}")
                continue

            rel = tex.relative_to(scan_dir) if tex.is_relative_to(scan_dir) else tex

            for m in _LABEL_RE.finditer(content):
                labels[m.group(1)].append(str(rel))

            for m in _REF_RE.finditer(content):
                for key in m.group(1).split(","):
                    key = key.strip()
                    if key:
                        refs[key].append(str(rel))

            for m in _CITE_RE.finditer(content):
                for key in m.group(1).split(","):
                    key = key.strip()
                    if key:
                        cites[key].append(str(rel))

        for bib in bib_files:
            try:
                content = bib.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                self.ui.warning(f"Cannot read {bib}: {exc}")
                continue
            for m in _BIB_ENTRY_RE.finditer(content):
                bib_keys.add(m.group(1))

        label_set = set(labels.keys())
        ref_set = set(refs.keys())
        cite_set = set(cites.keys())

        undefined_refs = sorted(ref_set - label_set)
        unused_labels = sorted(label_set - ref_set)
        undefined_cites = sorted(cite_set - bib_keys)

        total_labels = len(label_set)
        total_refs = sum(len(v) for v in refs.values())
        total_cites = sum(len(v) for v in cites.values())

        self.ui.info(f"Labels: {total_labels}  |  References: {total_refs}  |  Citations: {total_cites}  |  Bib entries: {len(bib_keys)}")

        has_errors = False

        if undefined_refs:
            has_errors = True
            self.ui.warning(f"Undefined references ({len(undefined_refs)}):")
            for key in undefined_refs:
                locs = refs[key]
                self.ui.warning(f"  \\ref{{{key}}} referenced in: {', '.join(locs)}")

        if unused_labels:
            self.ui.info(f"Unused labels ({len(unused_labels)}):")
            for key in unused_labels:
                locs = labels[key]
                self.ui.info(f"  \\label{{{key}}} defined in: {', '.join(locs)}")

        if undefined_cites:
            has_errors = True
            self.ui.warning(f"Undefined citations ({len(undefined_cites)}):")
            for key in undefined_cites:
                locs = cites[key]
                self.ui.warning(f"  \\cite{{{key}}} referenced in: {', '.join(locs)}")

        if not undefined_refs and not unused_labels and not undefined_cites:
            self.ui.success("All cross-references and citations are valid.")
        elif not has_errors:
            self.ui.success("No errors found (unused labels are informational only).")
        else:
            self.ui.error("Cross-reference check failed: undefined references or citations found.")

        return 1 if has_errors else 0

    def cmd_lint(self, files: list[str] | None = None) -> int:
        """Lint .tex files with chktex and lacheck."""
        self.ui.header("Linting .tex files")

        repo_root = Path(__file__).resolve().parent

        if files:
            tex_files = [Path(f) for f in files if Path(f).exists()]
        else:
            tex_files = sorted(
                f for f in repo_root.rglob("*.tex")
                if self.config.build_dir not in f.parents
                and "_minted" not in str(f)
            )

        if not tex_files:
            self.ui.warning("No .tex files found")
            return 0

        has_chktex = shutil.which("chktex") is not None
        has_lacheck = shutil.which("lacheck") is not None

        if not has_chktex and not has_lacheck:
            self.ui.error("Neither chktex nor lacheck found.")
            self.ui.info("  Install with: tlmgr install chktex lacheck")
            return 1

        self.ui.info(f"Scanning {len(tex_files)} file(s) with {'chktex' if has_chktex else ''}{' and ' if has_chktex and has_lacheck else ''}{'lacheck' if has_lacheck else ''}")

        total_errors = 0
        total_warnings = 0
        error_re = re.compile(r"Error\s+\d+", re.IGNORECASE)

        for tex_file in tex_files:
            try:
                rel = tex_file.relative_to(repo_root)
            except ValueError:
                rel = tex_file

            if has_chktex:
                try:
                    result = subprocess.run(
                        ["chktex", "-q", "-f", "%f:%l:%c:%n:%m%n", str(tex_file)],
                        capture_output=True, text=True, timeout=30,
                    )
                    if result.stdout.strip():
                        self.ui.info(f"[chktex] {rel}:")
                        for line in result.stdout.strip().splitlines():
                            print(f"  {line}")
                            if error_re.search(line):
                                total_errors += 1
                            else:
                                total_warnings += 1
                except (subprocess.TimeoutExpired, OSError) as exc:
                    self.ui.warning(f"[chktex] Failed to process {rel}: {exc}")

            if has_lacheck:
                try:
                    result = subprocess.run(
                        ["lacheck", str(tex_file)],
                        capture_output=True, text=True, timeout=30,
                    )
                    if result.stdout.strip():
                        self.ui.info(f"[lacheck] {rel}:")
                        for line in result.stdout.strip().splitlines():
                            print(f"  {line}")
                            total_warnings += 1
                except (subprocess.TimeoutExpired, OSError) as exc:
                    self.ui.warning(f"[lacheck] Failed to process {rel}: {exc}")

        self.ui.info(
            f"\nLint summary: {total_errors} error(s), {total_warnings} warning(s) "
            f"across {len(tex_files)} file(s)"
        )

        if total_errors > 0:
            self.ui.error("Linting found errors")
            return 1
        if total_warnings > 0:
            self.ui.warning(f"Linting passed with {total_warnings} warning(s)")
        else:
            self.ui.success("Linting passed with no issues")
        return 0

    def cmd_export(self, files: list[str] | None = None, output_format: str = "html"):
        """Export LaTeX to alternative formats (html, epub, docx).

        Requires: latexml (for HTML), pandoc (for EPUB/DOCX)
        """
        import subprocess

        self.ui.header(f"Export to {output_format.upper()}")

        repo_root = Path(__file__).resolve().parent

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

            rc, _ = self.runner.run([
                "latexml",
                "--dest=" + str(output_dir / f"{stem}.xml"),
                str(source),
            ], cwd=source.parent)

            if rc == 0:
                rc, _ = self.runner.run([
                    "latexmlpost",
                    "--dest=" + str(html_file),
                    "--format=html",
                    str(output_dir / f"{stem}.xml"),
                ], cwd=source.parent)

            if rc == 0 and html_file.exists():
                self.ui.success(f"HTML exported: {html_file}")
            else:
                self.ui.error("HTML export failed")

        elif output_format in ("epub", "docx"):
            if not shutil.which("pandoc"):
                self.ui.error(f"pandoc not found. Install: apt-get install pandoc")
                return

            out_file = output_dir / f"{stem}.{output_format}"
            self.ui.info(f"Converting {source.name} -> {out_file}")

            xml_file = output_dir / f"{stem}.xml"
            html_file = output_dir / f"{stem}.html"

            if shutil.which("latexml"):
                rc, _ = self.runner.run([
                    "latexml",
                    f"--dest={xml_file}",
                    str(source),
                ], cwd=source.parent)
                if rc == 0:
                    rc, _ = self.runner.run([
                        "latexmlpost",
                        f"--dest={html_file}",
                        "--format=html",
                        str(xml_file),
                    ], cwd=source.parent)

            if html_file.exists():
                pandoc_from = "html"
                pandoc_input = str(html_file)
            else:
                pandoc_from = "latex"
                pandoc_input = str(source)

            rc, _ = self.runner.run([
                "pandoc",
                f"--from={pandoc_from}",
                f"--to={output_format}",
                "-o", str(out_file),
                pandoc_input,
            ], cwd=source.parent)

            if rc == 0 and out_file.exists():
                self.ui.success(f"{output_format.upper()} exported: {out_file}")
            else:
                self.ui.error(f"{output_format.upper()} export failed")
        else:
            self.ui.error(f"Unknown format: {output_format}. Use: html, epub, docx")


# -----------------------------------------------------------------------------
# Interactive Menu (TUI)
# -----------------------------------------------------------------------------
def interactive_menu(tasks: BuildTasks, commands: dict[str, tuple]) -> None:
    """Show an interactive terminal menu when no command is specified."""

    # Menu categories with their commands
    menu_sections = [
        (
            "Build",
            [
                ("build-all", "Build root + all examples"),
                ("build-root", "Build root document"),
                ("build-examples", "Build all examples"),
                ("build-example", "Build specific example(s)"),
            ],
        ),
        (
            "Clean",
            [
                ("clean", "Full cleanup"),
                ("clean-aux", "Clean auxiliary files"),
                ("clean-pdf", "Clean all PDFs"),
                ("clean-example", "Clean specific example(s)"),
            ],
        ),
        (
            "Quality",
            [
                ("test", "Run test suite"),
                ("preflight", "Run preflight checks"),
                ("doctor", "Health diagnostics"),
                ("diff", "Visual regression diff"),
                ("lint", "Lint .tex files (chktex/lacheck)"),
                ("check", "Cross-reference integrity check"),
            ],
        ),
        (
            "Utilities",
            [
                ("list-examples", "List all examples"),
                ("init", "New project from template"),
                ("scaffold-institution", "New institution config"),
                ("watch", "Watch files & rebuild"),
                ("export", "Export LaTeX to HTML/EPUB/DOCX"),
            ],
        ),
    ]

    # Build flat lookup: number -> (cmd_name, takes_files)
    flat_commands = {}
    idx = 1
    for _section, items in menu_sections:
        for cmd_name, desc in items:
            flat_commands[str(idx)] = (cmd_name, desc, commands[cmd_name][2])
            idx += 1

    if RICH_AVAILABLE:
        _rich_menu(tasks, commands, menu_sections, flat_commands)
    else:
        _simple_menu(tasks, commands, menu_sections, flat_commands)


def _rich_menu(tasks: BuildTasks, commands: dict[str, tuple], menu_sections: list[tuple[str, list[tuple[str, str]]]], flat_commands: dict[str, tuple[str, str, bool]]) -> None:
    """Render the interactive menu using rich."""
    from rich.console import Console
    from rich.table import Table as RichTable
    from rich.panel import Panel
    from rich.text import Text as RichText

    console = Console()

    while True:
        console.clear()
        console.print()
        title = RichText("OmniLaTeX Build System", style="bold cyan")
        subtitle = RichText(
            f"v2.1.0  •  {len(tasks.discover_examples())} examples  •  "
            f"{len([f for f in Path('.').rglob('*.sty')])} modules",
            style="dim",
        )
        console.print(
            Panel(title + "\n" + subtitle, border_style="blue", padding=(0, 1))
        )
        console.print()

        # Render each section
        for section_name, items in menu_sections:
            table = RichTable(show_header=False, box=None, padding=(0, 1))
            table.add_column("num", style="bold cyan", width=4, justify="right")
            table.add_column("command", style="bold white", width=22)
            table.add_column("description", style="dim")
            for i, (cmd_name, desc) in enumerate(items, 1):
                num = str(
                    sum(
                        len(s[1])
                        for s in menu_sections[
                            : menu_sections.index((section_name, items))
                        ]
                    )
                    + i
                )
                table.add_row(num + ".", cmd_name, desc)
            console.print(RichText(f"  [bold]{section_name}[/bold]", style=""))
            console.print(table)
            console.print()

        console.print(
            RichText(
                "  [dim]Enter command number or name, or [bold]q[/bold] to quit.[/dim]"
            )
        )

        try:
            choice = input("\n  Select > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/dim]")
            return

        if choice in ("q", "quit", "exit", ""):
            console.print("[dim]Goodbye![/dim]")
            return

        # Resolve the choice
        cmd_name = None
        takes_files = False

        # Check by number
        if choice in flat_commands:
            cmd_name, _, takes_files = flat_commands[choice]
        # Check by name
        elif choice in commands:
            cmd_name = choice
            takes_files = commands[choice][2]
        else:
            # Fuzzy match partial names
            for name in commands:
                if name.startswith(choice) or choice in name:
                    cmd_name = name
                    takes_files = commands[name][2]
                    break

        if not cmd_name:
            console.print(f"[red]  Unknown command: {choice}[/red]")
            time.sleep(1)
            continue

        # If command needs files, prompt for them
        files = None
        if takes_files:
            if cmd_name == "build-example":
                examples = [e.name for e in tasks.discover_examples()]
                console.print(
                    f"  [dim]Available: {', '.join(examples[:10])}{'...' if len(examples) > 10 else ''}[/dim]"
                )
            try:
                arg = input(f"  {cmd_name} > ").strip()
                files = arg.split() if arg else []
            except (EOFError, KeyboardInterrupt):
                console.print("\n[dim]Cancelled.[/dim]")
                time.sleep(0.5)
                continue

        # Execute
        console.print()
        handler = commands[cmd_name][0]
        try:
            handler(tasks, files)
        except SystemExit:
            pass
        except Exception as e:
            console.print(f"[red]  Error: {e}[/red]")

        console.print()
        try:
            input("  Press Enter to continue...")
        except (EOFError, KeyboardInterrupt):
            return


def _simple_menu(tasks: BuildTasks, commands: dict[str, tuple], menu_sections: list[tuple[str, list[tuple[str, str]]]], flat_commands: dict[str, tuple[str, str, bool]]) -> None:
    """Render the interactive menu using plain terminal output."""
    ui = tasks.ui

    while True:
        print()
        ui.info("OmniLaTeX Build System")
        print()

        for section_name, items in menu_sections:
            print(f"  {section_name}")
            for i, (cmd_name, desc) in enumerate(items, 1):
                offset = sum(
                    len(s[1])
                    for s in menu_sections[: menu_sections.index((section_name, items))]
                )
                print(f"    [{offset + i}] {cmd_name:<22} {desc}")
            print()

        print("  [q] Quit")
        print()

        try:
            choice = input("  Select > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            return

        if choice in ("q", "quit", "exit", ""):
            print("Goodbye!")
            return

        cmd_name = None
        takes_files = False

        if choice in flat_commands:
            cmd_name, _, takes_files = flat_commands[choice]
        elif choice in commands:
            cmd_name = choice
            takes_files = commands[choice][2]

        if not cmd_name:
            print(f"  Unknown command: {choice}")
            time.sleep(1)
            continue

        files = None
        if takes_files:
            try:
                arg = input(f"  {cmd_name} > ").strip()
                files = arg.split() if arg else []
            except (EOFError, KeyboardInterrupt):
                print("\nCancelled.")
                continue

        print()
        handler = commands[cmd_name][0]
        try:
            handler(tasks, files)
        except SystemExit:
            pass
        except Exception as e:
            ui.error(str(e))

        print()
        try:
            input("  Press Enter to continue...")
        except (EOFError, KeyboardInterrupt):
            return


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def main() -> None:
    ui, config = TerminalOutput(), ProjectConfig()
    default_jobs = 4 if config.is_ci() else (os.cpu_count() or 4)
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
    parser.add_argument(
        "--cnf-line",
        action="append",
        default=[],
        metavar="LINE",
        help="Extra TeX configuration line passed to lualatex via --cnf-line (can be repeated).",
    )

    subparsers = parser.add_subparsers(dest="command")
    # Note: subparsers are NOT required — running without a command shows the
    # interactive menu (in terminals) or prints help (in CI).
    commands = {
        "build": (BuildTasks.build_all, "Build root and all examples.", False),
        "build-root": (BuildTasks.build_root, "Build root document.", False),
        "build-all": (BuildTasks.build_all, "Alias for 'build'.", False),
        "clean": (BuildTasks.clean_all, "Full cleanup.", False),
        "clean-aux": (BuildTasks.clean_aux, "Clean aux files.", False),
        "clean-pdf": (BuildTasks.clean_pdf, "Clean all PDFs.", False),
        "preflight": (BuildTasks.preflight, "Run preflight checks.", False),
        "check": (BuildTasks.cmd_check, "Cross-reference integrity check on .tex files.", True),
        "lint": (BuildTasks.cmd_lint, "Lint .tex files with chktex/lacheck.", True),
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
        "diff": (
            BuildTasks.cmd_diff,
            "Compare PDFs against references for visual regression.",
            True,
        ),
        "scaffold-institution": (
            BuildTasks.cmd_scaffold_institution,
            "Create a new institution config from the generic template.",
            True,
        ),
        "scaffold-language": (
            BuildTasks.cmd_scaffold_language,
            "Create a language addition guide with translation stubs.",
            True,
        ),
        "init": (
            BuildTasks.cmd_init,
            "Initialize a new OmniLaTeX project from a template.",
            True,
        ),
        "export": (
            lambda tasks, files: tasks.cmd_export(files, output_format=getattr(args, "export_format", "html")),
            "Export LaTeX to HTML, EPUB, or DOCX",
            True,
        ),
    }
    diff_subparser = None
    init_subparser = None
    export_subparser = None
    list_examples_subparser = None
    for name, (handler, help_text, takes_files) in commands.items():
        sub = subparsers.add_parser(name, help=help_text)
        sub.set_defaults(handler=handler)
        if takes_files:
            sub.add_argument("files", nargs="*", default=None)
        if name == "diff":
            diff_subparser = sub
        if name == "init":
            init_subparser = sub
        if name == "export":
            export_subparser = sub
        if name == "list-examples":
            list_examples_subparser = sub
    if diff_subparser is not None:
        diff_subparser.add_argument(
            "--regenerate-references",
            action="store_true",
            dest="regenerate_references",
            default=False,
            help="Copy built PDFs to tests/references/ as new baselines instead of comparing.",
        )
        diff_subparser.add_argument(
            "--output", "-o",
            type=str,
            default=None,
            metavar="PATH",
            help="Output path for annotated diff PDF (used with two-PDF or git-ref mode).",
        )
    if init_subparser is not None:
        init_subparser.add_argument(
            "--doctype",
            type=str,
            default=None,
            help="Document type (e.g. book, thesis, article, poster, presentation, letter)",
        )
        init_subparser.add_argument(
            "--institution",
            type=str,
            default=None,
            help="Institution config name (e.g. tum, eth, none)",
        )
        init_subparser.add_argument(
            "--language",
            type=str,
            default=None,
            help="Document language (e.g. english, german, chinese)",
        )
        init_subparser.add_argument(
            "--thesis",
            action="store_true",
            default=False,
            help="Shortcut: set doctype=thesis and create full thesis project structure.",
        )
    if export_subparser is not None:
        export_subparser.add_argument(
            "--format", "-f",
            dest="export_format",
            type=str,
            default="html",
            choices=["html", "epub", "docx"],
            help="Output format (default: html)",
        )
    if list_examples_subparser is not None:
        list_examples_subparser.add_argument(
            "--format", "-f",
            dest="list_format",
            type=str,
            default="text",
            choices=["text", "json"],
            help="Output format (default: text)",
        )

    args = parser.parse_args()

    if args.source_date_epoch is not None:
        os.environ["SOURCE_DATE_EPOCH"] = str(args.source_date_epoch)
    config.cnf_lines = args.cnf_line
    if args.command and "build" in args.command:
        ui.info(f"Using up to {args.jobs} parallel jobs.")
    runner = CommandRunner(
        ui, build_mode=args.mode, verbose=(args.verbose or config.verbose_enabled())
    )
    tasks = BuildTasks(
        config, runner, ui, jobs=args.jobs, timings=args.timings, force=args.force
    )

    # No command given — show interactive menu (TTY) or help (CI)
    if not args.command:
        if config.is_ci() or not sys.stdout.isatty():
            parser.print_help()
            return
        interactive_menu(tasks, commands)
        return

    try:
        if args.command == "init":
            args.handler(
                tasks,
                getattr(args, "files", None),
                doctype=getattr(args, "doctype", None),
                institution=getattr(args, "institution", None),
                language=getattr(args, "language", None),
                thesis=getattr(args, "thesis", False),
            )
        elif args.command == "list-examples":
            args.handler(
                tasks,
                getattr(args, "files", None),
                output_format=getattr(args, "list_format", "text"),
            )
        elif args.command == "diff":
            args.handler(
                tasks,
                getattr(args, "files", None),
                regenerate_references=getattr(args, "regenerate_references", False),
                output=getattr(args, "output", None),
            )
        elif args.command == "lint":
            rc = args.handler(tasks, getattr(args, "files", None))
            if rc:
                sys.exit(rc)
        elif args.command == "check":
            rc = args.handler(tasks, getattr(args, "files", None))
            if rc:
                sys.exit(rc)
        elif args.command == "export":
            args.handler(tasks, getattr(args, "files", None))
        else:
            args.handler(tasks, getattr(args, "files", None))
    except Exception as e:
        ui.error(f"An unexpected top-level error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
