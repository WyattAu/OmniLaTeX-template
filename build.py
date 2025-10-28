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
# Constants
# -----------------------------------------------------------------------------
READ_FIRST_CHARS = 5000
MAIN_TEX_FILENAME = "main.tex"
README_FILENAME = "README.md"
LATEXMK_COMMAND = "latexmk"
INTERACTION_NONSTOP = "-interaction=nonstopmode"
FORCE_REBUILD_FLAG = "-g"
MINTED_CACHE_SUBDIR = "_minted"
SVG_INKSCAPE_CACHE = "svg-inkscape"
BUILD_EXAMPLES_SUBDIR = "examples"

# -----------------------------------------------------------------------------
# Terminal Output
# -----------------------------------------------------------------------------
class TerminalOutput:
    """Handles formatted terminal messages with optional ANSI colors."""

    def __init__(self, use_color: bool = sys.stdout.isatty()) -> None:
        """Initialize TerminalOutput with optional ANSI color support.

        Args:
            use_color: Whether to use ANSI color codes in output.
        """
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
        """Announce a list of targets to the user.

        Args:
            title: Title for the announcement.
            targets: Iterable of target strings to display.
        """
        target_list = list(targets)
        if target_list:
            self.ui.info(f"{title}: {', '.join(target_list)}")
        else:
            self.ui.warning(f"{title}: none")

    def mode_label(self) -> str:
        """Get a human-readable label for the current build mode.

        Returns:
            String label for the build mode.
        """
        return {
            "dev": "DEVELOPMENT",
            "prod": "PRODUCTION",
            "ultra": "ULTRA-LITE",
        }.get(self.runner.build_mode, self.runner.build_mode.upper())

    def _example_description(self, example_dir: Path) -> str:
        """Extract the first non-header line from an example's README.md file.

        Args:
            example_dir: Path to the example directory.

        Returns:
            The first non-empty, non-header line from README.md, or empty string if not found.

        Raises:
            FileNotFoundError: If README.md does not exist.
            UnicodeDecodeError: If README.md cannot be decoded as UTF-8.
            OSError: If README.md cannot be read.
        """
        readme = example_dir / README_FILENAME
        if not readme.exists():
            raise FileNotFoundError(f"README.md not found in {example_dir}")
        try:
            with open(readme, "r", encoding="utf-8") as fh:
                for line in fh.readlines()[:10]:
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        return stripped
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(e.encoding, e.object, e.start, e.end, f"Failed to decode README.md in {example_dir}: {e.reason}")
        except OSError as e:
            raise OSError(f"Failed to read README.md in {example_dir}: {e}")
        return ""

    def build_tex(self, files: Optional[List[str]] = None) -> None:
        """Build LaTeX source files that contain \\documentclass.

        Scans the current directory recursively for .tex files and compiles those
        containing \\documentclass. If specific files are provided, builds only those.

        Args:
            files: Optional list of specific .tex files to build. If None, auto-discovers
                   all .tex files with \\documentclass.

        Returns:
            None

        Raises:
            No exceptions raised; warnings are issued for missing files or read errors.
        """
        mode_label = self.mode_label()
        self.ui.header(f"Building LaTeX Source Files ({mode_label})")
        cmd = self.runner.get_base_command(LATEXMK_COMMAND)
        flags = [INTERACTION_NONSTOP]

        if files:
            target_files = files
        else:
            # Only compile files with \documentclass (standalone documents)
            all_tex = [str(p) for p in Path(".").rglob("*.tex")]
            target_files: List[str] = []
            for tex_file in all_tex:
                try:
                    with open(tex_file, 'r', encoding='utf-8') as f:
                        content = f.read(READ_FIRST_CHARS)
                        if r'\documentclass' in content:
                            target_files.append(tex_file)
                except (OSError, UnicodeDecodeError):
                    continue

        if not target_files:
            self.ui.warning("No compilable .tex files found (files with \\documentclass).")
            return

        self._announce_targets("Targets", target_files)
        for tex in target_files:
            tex_path = Path(tex)
            if not tex_path.exists():
                self.ui.warning(f"Source not found: {tex}")
                continue
            self.runner.run(cmd + flags + [tex])
    
    def build_root(self, _files: Optional[List[str]] = None) -> None:
        """Build the root main.tex document.

        Compiles the main.tex file in the project root using latexmk with
        appropriate environment variables for minted caching.

        Args:
            _files: Ignored parameter for consistency with other methods.

        Returns:
            None

        Raises:
            No exceptions raised; warnings issued for missing files.
        """
        mode_label = self.mode_label()
        self.ui.header(f"Building Root Document ({mode_label})")

        main_tex = Path(MAIN_TEX_FILENAME)
        if not main_tex.exists():
            self.ui.warning("No main.tex found in root directory.")
            return

        cmd = self.runner.get_base_command(LATEXMK_COMMAND)
        flags = [INTERACTION_NONSTOP]

        # Ensure minted cache directory exists before building
        minted_cache_dir = self.config.build_dir / MINTED_CACHE_SUBDIR
        minted_cache_dir.mkdir(parents=True, exist_ok=True)
        extra_env = {
            "MINTED_CACHE_DIR": str((minted_cache_dir / "").resolve()),
        }

        self.runner.run(cmd + flags + [MAIN_TEX_FILENAME], extra_env=extra_env)
        self.ui.success("Root document build complete.")
    
    def build_all(self, _files: Optional[List[str]] = None) -> None:
        """Build the root document and all examples.

        First builds the root main.tex, then builds all discovered examples.

        Args:
            _files: Ignored parameter for consistency with other methods.

        Returns:
            None
        """
        self.ui.header("Building All Documents (Root + Examples)")

        # Build root first
        self.build_root()

        # Then build examples
        self.build_examples()

        self.ui.success("All documents built successfully.")

    def clean_aux(self, _files: Optional[List[str]] = None) -> None:
        """Clean LaTeX auxiliary files using latexmk -c.

        Removes all auxiliary files (.aux, .log, .fls, etc.) generated by LaTeX.

        Args:
            _files: Ignored parameter for consistency with other methods.

        Returns:
            None
        """
        self.ui.header("Cleaning auxiliary files")
        cmd = self.runner.get_base_command(LATEXMK_COMMAND)
        self.runner.run(cmd + ["-c"])
        self.ui.success("Auxiliary files cleaned.")

    def clean_pdf(self, _files: Optional[List[str]] = None) -> None:
        """Remove all PDF files from the build directory.

        Deletes all .pdf files in the configured build directory.

        Args:
            _files: Ignored parameter for consistency with other methods.

        Returns:
            None
        """
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
        """Perform a full cleanup of all build artifacts.

        Cleans auxiliary files, removes PDFs, and deletes the entire build directory.

        Args:
            _files: Ignored parameter for consistency with other methods.

        Returns:
            None
        """
        self.ui.header("Full clean")
        self.clean_aux()
        self.clean_pdf()
        # Remove entire build directory
        if self.config.build_dir.exists():
            shutil.rmtree(self.config.build_dir)
            self.ui.info(f"Removed build directory: {self.config.build_dir}")
        self.ui.success("Full cleanup finished.")

    def preflight(self, _files: Optional[List[str]] = None) -> None:
        """Run environment preflight checks.

        Performs various checks on the system environment, including library
        availability, user permissions, directory writability, and LaTeX installation.

        Args:
            _files: Ignored parameter for consistency with other methods.

        Returns:
            None
        """
        self.ui.header("Preflight checks")
        if sys.platform == "linux":
            try:
                output = self.runner.run(["ldconfig", "--print-cache"], capture_output=True)
                if output and "librsvg" in output:
                    self.ui.success("librsvg present.")
                else:
                    self.ui.warning("librsvg not detected.")
            except (subprocess.CalledProcessError, FileNotFoundError) as exc:
                self.ui.warning(f"Could not run ldconfig: {exc}")
        else:
            self.ui.info(f"Skipping Linux-only checks on {sys.platform}")

        # Check user permissions and environment
        self.ui.info("Checking user and permissions...")
        try:
            whoami = self.runner.run(["whoami"], capture_output=True)
            if whoami:
                self.ui.info(f"Current user: {whoami.strip()}")
            else:
                self.ui.warning("Could not determine current user")
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            self.ui.warning(f"Could not check user: {exc}")

        # Ensure minted cache directory exists and is writable
        minted_cache_dir = self.config.build_dir / MINTED_CACHE_SUBDIR
        minted_cache_dir.mkdir(parents=True, exist_ok=True)
        self.ui.info(f"Ensured minted cache directory: {minted_cache_dir}")
        try:
            # Check if we can write to minted cache directory
            test_file = minted_cache_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            self.ui.success("Minted cache directory is writable")
        except OSError as exc:
            self.ui.error(f"Minted cache directory not writable: {exc}")

        # Check environment variables
        self.ui.info("Checking environment variables...")
        env_vars = ["IS_OMNILATEX_CONTAINER", "BUILD_MODE", "TEXINPUTS", "MINTED_CACHE_DIR"]
        for var in env_vars:
            value = os.environ.get(var)
            if value:
                self.ui.info(f"{var}={value}")
            else:
                self.ui.info(f"{var} not set")

        cmd = self.runner.get_base_command(LATEXMK_COMMAND)
        self.runner.run(cmd + ["--version"])
        self.ui.success("Preflight complete.")

    def discover_examples(self) -> List[Path]:
        """Find all example directories containing main.tex.

        Scans the 'examples' directory for subdirectories that contain a main.tex file.

        Returns:
            Sorted list of Path objects for example directories with main.tex.
        """
        examples_dir = Path("examples")
        if not examples_dir.exists():
            return []

        examples: List[Path] = []
        for item in examples_dir.iterdir():
            if item.is_dir() and (item / MAIN_TEX_FILENAME).exists():
                examples.append(item)

        return sorted(examples)

    def list_examples(self, _files: Optional[List[str]] = None) -> None:
        """List all available examples with their descriptions.

        Discovers examples and displays their names along with descriptions
        extracted from README.md files.

        Args:
            _files: Ignored parameter for consistency with other methods.

        Returns:
            None
        """
        self.ui.header("Available Examples")
        examples = self.discover_examples()

        if not examples:
            self.ui.info("No examples found.")
            return

        for example in examples:
            try:
                description = self._example_description(example)
            except (FileNotFoundError, UnicodeDecodeError, OSError):
                description = ""
            self.ui.info(f"  {example.name}")
            if description:
                self.ui.info(f"    {description}")

        self.ui.success(f"Found {len(examples)} example(s).")

    def build_example(self, files: Optional[List[str]] = None) -> None:
        """Build one or more specific examples.

        Compiles the specified examples using latexmk with appropriate environment
        variables and copies resulting PDFs to the build directory.

        Args:
            files: List of example names to build.

        Returns:
            None

        Raises:
            No exceptions raised; errors are logged as warnings.
        """
        if not files:
            self.ui.error("No example name provided. Use: build.py build-example <name>")
            return

        examples_dir = Path("examples")
        if not examples_dir.exists():
            self.ui.error("Examples directory not found.")
            return

        # Build output directory
        build_examples_dir = self.config.build_dir / BUILD_EXAMPLES_SUBDIR
        build_examples_dir.mkdir(parents=True, exist_ok=True)

        root_latexmkrc = Path(__file__).resolve().parent / ".latexmkrc"

        repo_root = Path(__file__).resolve().parent

        for example_name in files:
            self.ui.header(f"Building example: {example_name}")
            example_dir = examples_dir / example_name

            if not example_dir.exists():
                self.ui.warning(f"Example not found: {example_name}")
                continue

            main_tex = example_dir / MAIN_TEX_FILENAME
            if not main_tex.exists():
                self.ui.warning(f"main.tex not found in {example_name}")
                continue

            # Build in the example directory
            try:
                with working_directory(example_dir):
                    # Ensure cache directories exist before building
                    for cache_dir in (Path(MINTED_CACHE_SUBDIR), Path(SVG_INKSCAPE_CACHE)):
                        cache_dir.mkdir(parents=True, exist_ok=True)

                    cmd = self.runner.get_base_command(LATEXMK_COMMAND)
                    latexmk_flags: List[str] = [INTERACTION_NONSTOP]
                    if os.environ.get("OMNILATEX_FORCE_REBUILD") == "1":
                        latexmk_flags.append(FORCE_REBUILD_FLAG)
                    current_texinputs = os.environ.get("TEXINPUTS", "")
                    texinputs_entries = [str(repo_root)]
                    if current_texinputs:
                        texinputs_entries.append(current_texinputs)
                    texinputs_entries.append("")
                    # Use build directory for minted cache to avoid permission issues
                    minted_cache_dir = self.config.build_dir / MINTED_CACHE_SUBDIR
                    minted_cache_dir.mkdir(parents=True, exist_ok=True)
                    extra_env = {
                        "MINTED_CACHE_DIR": str((minted_cache_dir / "").resolve()),
                        "OMNILATEX_EXAMPLE_ROOT": str(Path.cwd()),
                        "TEXINPUTS": os.pathsep.join(texinputs_entries),
                        "LC_ALL": "C.utf8",  # Set locale to avoid LuaLaTeX locale issues
                    }

                    invoke: List[str] = cmd + latexmk_flags
                    if root_latexmkrc.exists():
                        invoke.extend(["-r", str(root_latexmkrc)])
                    local_rc = Path(".latexmkrc")
                    if local_rc.exists():
                        invoke.extend(["-r", str(local_rc)])

                    invoke.append(MAIN_TEX_FILENAME)

                    self.runner.run(invoke, extra_env=extra_env)

                src_pdf = example_dir / "main.pdf"
                if src_pdf.exists():
                    dest_pdf = build_examples_dir / f"{example_name}.pdf"
                    shutil.copy(src_pdf, dest_pdf)
                    self.ui.success(f"Built {example_name} -> {dest_pdf}")
                else:
                    self.ui.warning(f"PDF not generated for {example_name}")

            except (OSError, subprocess.CalledProcessError, FileNotFoundError) as exc:
                self.ui.error(f"Failed to build {example_name}: {exc}")

    def build_examples(self, _files: Optional[List[str]] = None) -> None:
        """Build all discovered examples.

        Discovers all examples and builds them using build_example().

        Args:
            _files: Ignored parameter for consistency with other methods.

        Returns:
            None
        """
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
        """Run the test suite using Poetry and pytest.

        Sets up the test environment and runs pytest with provided arguments.

        Args:
            files: Optional list of pytest arguments/files to pass to pytest.

        Returns:
            None
        """
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
        """Clean auxiliary files from one or more examples.

        Runs latexmk -c in each specified example directory to remove
        auxiliary LaTeX files.

        Args:
            files: List of example names to clean.

        Returns:
            None
        """
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
                    cmd = self.runner.get_base_command(LATEXMK_COMMAND)
                    self.runner.run(cmd + ["-c"])

                self.ui.success(f"Cleaned {example_name}")

            except (OSError, subprocess.CalledProcessError, FileNotFoundError) as exc:
                self.ui.error(f"Failed to clean {example_name}: {exc}")

    def clean_examples(self, _files: Optional[List[str]] = None) -> None:
        """Clean all examples and their build outputs.

        Cleans auxiliary files from all examples and removes the build/examples directory.

        Args:
            _files: Ignored parameter for consistency with other methods.

        Returns:
            None
        """
        self.ui.header("Cleaning all examples")
        examples = self.discover_examples()

        if not examples:
            self.ui.warning("No examples found.")
            return

        example_names = [e.name for e in examples]
        self.clean_example(example_names)

        # Also clean build output
        build_examples_dir = self.config.build_dir / BUILD_EXAMPLES_SUBDIR
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
        ui.info(f"Build mode: {tasks.mode_label()}")
    
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
