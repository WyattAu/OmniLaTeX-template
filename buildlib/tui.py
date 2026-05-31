from __future__ import annotations

import time

from buildlib.builder import RICH_AVAILABLE


def interactive_menu(tasks, commands: dict[str, tuple]) -> None:
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
                ("cache-stats", "Show build cache statistics"),
                ("cache-clear", "Delete build cache"),
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


def _rich_menu(
    tasks,
    commands: dict[str, tuple],
    menu_sections: list[tuple[str, list[tuple[str, str]]]],
    flat_commands: dict[str, tuple[str, str, bool]],
) -> None:
    """Render the interactive menu using rich."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table as RichTable
    from rich.text import Text as RichText

    console = Console()

    while True:
        console.clear()
        console.print()
        title = RichText("OmniLaTeX Build System", style="bold cyan")
        subtitle = RichText(
            f"v{tasks.version}  •  {len(tasks.discover_examples())} examples  •  "
            f"{len(tasks.source_files)} modules",
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
                    f"  [dim]Available: {', '.join(examples[:10])}{'...' if len(examples) > 10 else ''}[/dim]"  # noqa: E501
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


def _simple_menu(
    tasks,
    commands: dict[str, tuple],
    menu_sections: list[tuple[str, list[tuple[str, str]]]],
    flat_commands: dict[str, tuple[str, str, bool]],
) -> None:
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
