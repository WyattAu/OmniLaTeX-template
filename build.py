#!/usr/bin/env python3
"""
OmniLaTeX build entry point.

Key capabilities:
  • Explicit dev/prod/ultra modes with diagnostics announced up front.
  • Comprehensive logging of every subprocess invocation with elapsed timing.
  • Per-command verbose output toggled via --verbose / OMNILATEX_VERBOSE=1.
  • High-level commands for root builds, example builds, cleaning, preflight, and tests.

This script no longer shells out through Docker automatically. Instead, it assumes
execution inside the devcontainer or a prepared environment. Docker support can be
reintroduced by adjusting CommandRunner.get_base_command().
"""

from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional

# -----------------------------------------------------------------------------
# Terminal Output
# -----------------------------------------------------------------------------
class TerminalOutput:
    """Handles formatted terminal messages with optional ANSI colors."""

    def __init__(self, use_color: bool = sys.stdout.isatty()) -> None:
        palette = {
            "blue": "\033[94m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "bold": "\033[1m",
            "end": "\033[0m",
        }
        if use_color:
            self.blue = palette["blue"]
            self.green = palette["green"]
            self.yellow = palette["yellow"]
            self.red = palette["red"]
            self.bold = palette["bold"]
            self.end = palette["end"]
        else:
            self.blue = self.green = self.yellow = self.red = self.bold = self.end = ""

    def header(self, message: str) -> None:
        print(f"\n{self.bold}{self.blue}=== {message} ==={self.end}")

    def info(self, message: str) -> None:
        print(f"[INFO] {message}")

    def success(self, message: str) -> None:
        print(f"{self.green}[SUCCESS] {message}{self.end}")

    def warning(self, message: str) -> None:
        print(f"{self.yellow}[WARNING] {message}{self.end}")

    def error(self, message: str) -> None:
        print(f"{self.bold}{self.red}[ERROR] {message}{self.end}", file=sys.stderr)
        raise RuntimeError(message)

    def command(self, command: str) -> None:
        print(f"{self.bold}[RUN] {command}{self.end}")

    def debug(self, message: str) -> None:
        print(f"[DEBUG] {message}")

# -----------------------------------------------------------------------------
# Project configuration
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class ProjectConfig:
    build_dir: Path = Path("build")

    def is_ci(self) -> bool:
        return os.environ.get("CI", "").lower() in {"1", "true", "yes"}

    def verbose_enabled(self) -> bool:
        return os.environ.get("OMNILATEX_VERBOSE", "0").lower() in {"1", "true", "yes"}

    def get_git_short_sha(self) -> str:
        if self.is_ci():
            env_sha = os.environ.get("CI_COMMIT_SHORT_SHA")
            if env_sha:
                return env_sha
        try:
            return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
        except Exception:
            return "unknown-sha"
# -----------------------------------------------------------------------------
# Command execution
# -----------------------------------------------------------------------------
class CommandRunner:
    def __init__(self, config: ProjectConfig, ui: TerminalOutput, build_mode: str = "dev", verbose: bool = False) -> None:
        self.config = config
        self.ui = ui
        self.build_mode = build_mode
        self.verbose = verbose or config.verbose_enabled()

    def get_base_command(self, tool: str) -> List[str]:
        return [tool]

    def format_command(self, args: Iterable[str]) -> str:
        return " ".join(str(arg) for arg in args)

    def run(
        self,
        cmd_args: List[str],
        *,
        capture_output: bool = False,
        extra_env: Optional[Dict[str, str]] = None,
        cwd: Optional[Path] = None,
    ) -> Optional[str]:
        command_str = self.format_command(cmd_args)
        self.ui.command(command_str)
        env = os.environ.copy()
        env["BUILD_MODE"] = self.build_mode
        if extra_env:
            env.update(extra_env)
        start = time.perf_counter()
        try:
            if capture_output:
                result = subprocess.run(
                    cmd_args,
                    check=True,
                    text=True,
                    capture_output=True,
                    env=env,
                    cwd=str(cwd) if cwd else None,
                )
                elapsed = time.perf_counter() - start
                if self.verbose:
                    self.ui.debug(f"Completed in {elapsed:.2f}s: {command_str}")
                    if result.stdout:
                        self.ui.debug(result.stdout.strip())
                    if result.stderr:
                        self.ui.debug(result.stderr.strip())
                return result.stdout

            subprocess.run(cmd_args, check=True, env=env, cwd=str(cwd) if cwd else None)
            elapsed = time.perf_counter() - start
            if self.verbose:
                self.ui.debug(f"Completed in {elapsed:.2f}s: {command_str}")
            return None
        except subprocess.CalledProcessError as exc:
            elapsed = time.perf_counter() - start
            self.ui.error(
                f"Command failed ({elapsed:.2f}s, exit {exc.returncode}): {command_str}"
            )
        except FileNotFoundError:
            self.ui.error(f"Command not found: {cmd_args[0]}. Install it or adjust PATH.")
        return None

# -----------------------------------------------------------------------------
# Context managers
# -----------------------------------------------------------------------------
@contextmanager
def working_directory(path: Path):
    """Context manager to temporarily change working directory."""
    prev_cwd = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)

# -----------------------------------------------------------------------------
# Build tasks
# -----------------------------------------------------------------------------
class BuildTasks:
    def __init__(self, config: ProjectConfig, runner: CommandRunner, ui: TerminalOutput) -> None:
        self.config = config
        self.runner = runner
        self.ui = ui

    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------
    def _announce_targets(self, title: str, targets: Iterable[str]) -> None:
        target_list = list(targets)
        if target_list:
            self.ui.info(f"{title}: {', '.join(target_list)}")
        else:
            self.ui.warning(f"{title}: none")

    def _mode_label(self) -> str:
        return {
            "dev": "DEVELOPMENT",
            "prod": "PRODUCTION",
            "ultra": "ULTRA-LITE",
        }.get(self.runner.build_mode, self.runner.build_mode.upper())

    def _example_description(self, example_dir: Path) -> str:
        readme = example_dir / "README.md"
        if not readme.exists():
            return ""
        try:
            with open(readme, "r", encoding="utf-8") as fh:
                for line in fh.readlines()[:10]:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        return stripped
        except Exception:
            return ""
        return ""

    def build_tex(self, files: Optional[List[str]] = None) -> None:
        mode_label = self._mode_label()
        self.ui.header(f"Building LaTeX Source Files ({mode_label})")
        cmd = self.runner.get_base_command("latexmk")
        flags = ["-interaction=nonstopmode"]

        if files:
            target_files = files
        else:
            # Only compile files with \documentclass (standalone documents)
            all_tex = [str(p) for p in Path(".").rglob("*.tex")]
            target_files = []
            for tex_file in all_tex:
                try:
                    with open(tex_file, 'r', encoding='utf-8') as f:
                        content = f.read(5000)  # Read first 5000 chars
                        if r'\documentclass' in content:
                            target_files.append(tex_file)
                except Exception:
                    continue
        
        if not target_files:
            self.ui.warning("No compilable .tex files found (files with \\documentclass).")
            return

        self._announce_targets("Targets", target_files)
        for tex in target_files:
            if not Path(tex).exists():
                self.ui.warning(f"Source not found: {tex}")
                continue
            self.runner.run(cmd + flags + [tex])
    
    def build_root(self, _files: Optional[List[str]] = None) -> None:
        """Build the root main.tex document."""
        mode_label = self._mode_label()
        self.ui.header(f"Building Root Document ({mode_label})")
        
        main_tex = Path("main.tex")
        if not main_tex.exists():
            self.ui.warning("No main.tex found in root directory.")
            return
        
        cmd = self.runner.get_base_command("latexmk")
        flags = ["-interaction=nonstopmode"]
        self.runner.run(cmd + flags + ["main.tex"])
        self.ui.success("Root document build complete.")
    
    def build_all(self, _files: Optional[List[str]] = None) -> None:
        self.ui.header("Building All Documents (Root + Examples)")
        
        # Build root first
        self.build_root()
        
        # Then build examples
        self.build_examples()
        
        self.ui.success("All documents built successfully.")

    def clean_aux(self, _files: Optional[List[str]] = None) -> None:
        self.ui.header("Cleaning auxiliary files")
        cmd = self.runner.get_base_command("latexmk")
        self.runner.run(cmd + ["-c"])
        self.ui.success("Auxiliary files cleaned.")

    def clean_pdf(self, _files: Optional[List[str]] = None) -> None:
        self.ui.header("Cleaning PDF files")
        if not self.config.build_dir.exists():
            self.ui.info("Build directory does not exist.")
            return
        pdfs = list(self.config.build_dir.glob("*.pdf"))
        if not pdfs:
            self.ui.info("No PDF files found in build directory.")
            return
        for p in pdfs:
            p.unlink(missing_ok=True)
            self.ui.info(f"Removed {p}")
        self.ui.success("PDF cleaning complete.")

    def clean_all(self, _files: Optional[List[str]] = None) -> None:
        self.ui.header("Full clean")
        self.clean_aux()
        self.clean_pdf()
        # Remove entire build directory
        if self.config.build_dir.exists():
            shutil.rmtree(self.config.build_dir)
            self.ui.info(f"Removed build directory: {self.config.build_dir}")
        self.ui.success("Full cleanup finished.")

    def preflight(self, _files: Optional[List[str]] = None) -> None:
        self.ui.header("Preflight checks")
        if sys.platform == "linux":
            try:
                output = self.runner.run(["ldconfig", "--print-cache"], capture_output=True)
                if output and "librsvg" in output:
                    self.ui.success("librsvg present.")
                else:
                    self.ui.warning("librsvg not detected.")
            except Exception as exc:
                self.ui.warning(f"Could not run ldconfig: {exc}")
        else:
            self.ui.info(f"Skipping Linux-only checks on {sys.platform}")

        cmd = self.runner.get_base_command("latexmk")
        self.runner.run(cmd + ["--version"])
        self.ui.success("Preflight complete.")

    def discover_examples(self) -> List[Path]:
        """Find all example directories with main.tex."""
        examples_dir = Path("examples")
        if not examples_dir.exists():
            return []
        
        examples = []
        for item in examples_dir.iterdir():
            if item.is_dir() and (item / "main.tex").exists():
                examples.append(item)
        
        return sorted(examples)

    def list_examples(self, _files: Optional[List[str]] = None) -> None:
        """List all available examples."""
        self.ui.header("Available Examples")
        examples = self.discover_examples()

        if not examples:
            self.ui.info("No examples found.")
            return

        for example in examples:
            description = self._example_description(example)
            self.ui.info(f"  {example.name}")
            if description:
                self.ui.info(f"    {description}")

        self.ui.success(f"Found {len(examples)} example(s).")

    def build_example(self, files: Optional[List[str]] = None) -> None:
        """Build one or more specific examples."""
        if not files:
            self.ui.error("No example name provided. Use: build.py build-example <name>")
            return
        
        examples_dir = Path("examples")
        if not examples_dir.exists():
            self.ui.error("Examples directory not found.")
            return
        
        # Build output directory
        build_examples_dir = self.config.build_dir / "examples"
        build_examples_dir.mkdir(parents=True, exist_ok=True)
        
        root_latexmkrc = Path(__file__).resolve().parent / ".latexmkrc"

        repo_root = Path(__file__).resolve().parent

        for example_name in files:
            self.ui.header(f"Building example: {example_name}")
            example_dir = examples_dir / example_name
            
            if not example_dir.exists():
                self.ui.warning(f"Example not found: {example_name}")
                continue
            
            main_tex = example_dir / "main.tex"
            if not main_tex.exists():
                self.ui.warning(f"main.tex not found in {example_name}")
                continue
            
            # Build in the example directory
            try:
                with working_directory(example_dir):
                    for cache_dir in (Path("_minted"), Path("svg-inkscape")):
                        cache_dir.mkdir(parents=True, exist_ok=True)

                    cmd = self.runner.get_base_command("latexmk")
                    latexmk_flags: List[str] = ["-interaction=nonstopmode"]
                    if os.environ.get("OMNILATEX_FORCE_REBUILD") == "1":
                        latexmk_flags.append("-g")
                    current_texinputs = os.environ.get("TEXINPUTS", "")
                    texinputs_entries = [str(repo_root)]
                    if current_texinputs:
                        texinputs_entries.append(current_texinputs)
                    texinputs_entries.append("")
                    extra_env = {
                        "MINTED_CACHE_DIR": str((Path("_minted") / "").resolve()),
                        "OMNILATEX_EXAMPLE_ROOT": str(Path.cwd()),
                        "TEXINPUTS": os.pathsep.join(texinputs_entries),
                    }

                    invoke: List[str] = cmd + latexmk_flags
                    if root_latexmkrc.exists():
                        invoke.extend(["-r", str(root_latexmkrc)])
                    local_rc = Path(".latexmkrc")
                    if local_rc.exists():
                        invoke.extend(["-r", str(local_rc)])

                    invoke.append("main.tex")

                    self.runner.run(invoke, extra_env=extra_env)

                src_pdf = example_dir / "main.pdf"
                if src_pdf.exists():
                    dest_pdf = build_examples_dir / f"{example_name}.pdf"
                    shutil.copy(src_pdf, dest_pdf)
                    self.ui.success(f"Built {example_name} -> {dest_pdf}")
                else:
                    self.ui.warning(f"PDF not generated for {example_name}")

            except Exception as exc:
                self.ui.error(f"Failed to build {example_name}: {exc}")

    def build_examples(self, _files: Optional[List[str]] = None) -> None:
        """Build all examples."""
        self.ui.header("Building all examples")
        examples = self.discover_examples()
        
        if not examples:
            self.ui.warning("No examples found.")
            return
        
        example_names = [e.name for e in examples]
        self.ui.info(f"Found {len(example_names)} example(s): {', '.join(example_names)}")
        
        # Use build_example to build each
        self.build_example(example_names)
        
        self.ui.success("All examples built.")

    def run_tests(self, files: Optional[List[str]] = None) -> None:
        self.ui.header("Running test suite")

        tests_dir = Path("tests")
        if not tests_dir.exists():
            self.ui.warning("Tests directory not found.")
            return

        pytest_args = files or []

        with working_directory(tests_dir):
            self.runner.run(["python3", "-m", "pip", "install", "--upgrade", "pip"])
            self.runner.run(["python3", "-m", "pip", "install", "poetry"])
            self.runner.run(["poetry", "config", "virtualenvs.in-project", "true"])
            self.runner.run(["poetry", "install", "--no-interaction"])

            pytest_cmd = ["poetry", "run", "pytest", "-v", "--tb=short"]
            if pytest_args:
                pytest_cmd.extend(pytest_args)

            self.runner.run(pytest_cmd)

        self.ui.success("Test suite finished.")

    def clean_example(self, files: Optional[List[str]] = None) -> None:
        """Clean auxiliary files from one or more examples."""
        if not files:
            self.ui.error("No example name provided. Use: build.py clean-example <name>")
            return
        
        examples_dir = Path("examples")
        for example_name in files:
            self.ui.header(f"Cleaning example: {example_name}")
            example_dir = examples_dir / example_name
            
            if not example_dir.exists():
                self.ui.warning(f"Example not found: {example_name}")
                continue
            
            try:
                with working_directory(example_dir):
                    cmd = self.runner.get_base_command("latexmk")
                    self.runner.run(cmd + ["-c"])
                
                self.ui.success(f"Cleaned {example_name}")
            
            except Exception as exc:
                self.ui.error(f"Failed to clean {example_name}: {exc}")

    def clean_examples(self, _files: Optional[List[str]] = None) -> None:
        """Clean all examples."""
        self.ui.header("Cleaning all examples")
        examples = self.discover_examples()
        
        if not examples:
            self.ui.warning("No examples found.")
            return
        
        example_names = [e.name for e in examples]
        self.clean_example(example_names)
        
        # Also clean build output
        build_examples_dir = self.config.build_dir / "examples"
        if build_examples_dir.exists():
            shutil.rmtree(build_examples_dir)
            self.ui.info(f"Removed {build_examples_dir}")
        
        self.ui.success("All examples cleaned.")

# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
Handler = Callable[[Optional[List[str]]], None]

def main() -> None:
    ui = TerminalOutput()
    config = ProjectConfig()

    parser = argparse.ArgumentParser(description="OmniLaTeX build tool")
    parser.add_argument(
        "--mode",
        choices=["dev", "prod", "ultra"],
        default="dev",
        help="Build mode: 'dev' for fast iteration (default), 'prod' for full validation, 'ultra' for minimal rebuild",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose command output (or set OMNILATEX_VERBOSE=1)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Define commands structure (without handlers yet)
    command_specs: Dict[str, tuple[str, str, bool]] = {
        "build": ("build_all", "Build root document and all examples", False),
        "build-tex": ("build_tex", "Build .tex files (auto-discover)", True),
        "build-root": ("build_root", "Build root main.tex document", False),
        "build-all": ("build_all", "Build root document and all examples", False),
        "clean": ("clean_all", "Full cleanup", False),
        "clean-aux": ("clean_aux", "Remove LaTeX auxiliary files", False),
        "clean-pdf": ("clean_pdf", "Remove generated PDFs", False),
        "preflight": ("preflight", "Run environment preflight checks", False),
        "lint": ("preflight", "Run linting and environment checks", False),
        "list-examples": ("list_examples", "List all available examples", False),
        "build-example": ("build_example", "Build specific example(s)", True),
        "build-examples": ("build_examples", "Build all examples", False),
        "clean-example": ("clean_example", "Clean specific example(s)", True),
        "clean-examples": ("clean_examples", "Clean all examples", False),
        "test": ("run_tests", "Run test suite (pass extra pytest args)", True),
    }

    # Register subparsers
    for name, (method_name, help_text, accepts_files) in command_specs.items():
        sub = subparsers.add_parser(name, help=help_text)
        sub.set_defaults(method=method_name)
        if accepts_files:
            sub.add_argument("files", nargs="*", help="Target files (optional)")

    # Parse arguments
    args = parser.parse_args()
    
    # Initialize runner and tasks with build mode
    runner = CommandRunner(config, ui, build_mode=args.mode, verbose=args.verbose)
    tasks = BuildTasks(config, runner, ui)
    
    # Show build mode for build commands
    if args.command.startswith("build"):
        ui.info(f"Build mode: {tasks._mode_label()}")
    
    # Get and call the appropriate handler method
    method_name: str = getattr(args, "method")
    handler: Handler = getattr(tasks, method_name)
    files: Optional[List[str]] = getattr(args, "files", None)
    handler(files)

if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        sys.exit(f"Error: {exc}")
