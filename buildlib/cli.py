from __future__ import annotations

import argparse
import os
import sys

from buildlib import BuildTasks
from buildlib.config import ProjectConfig
from buildlib.ui import TerminalOutput
from buildlib.runner import CommandRunner
from buildlib.tui import interactive_menu


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
