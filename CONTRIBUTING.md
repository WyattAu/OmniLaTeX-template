# Contributing to OmniLaTeX

Thank you for your interest in contributing. This guide covers setup, conventions, and the PR workflow.

## Prerequisites

- Python 3.10+ (3.13 recommended)
- LuaTeX (LuaHBTeX 1.21+) -- part of TeX Live 2025+
- Node.js 18+ (for web frontend development only)
- Lean 4 (for formal verification only)

## Setup

```bash
git clone https://github.com/WyattAu/OmniLaTeX-template.git
cd OmniLaTeX-template
python -m venv .venv
source .venv/bin/activate  # or .venv/bin/activate.fish on Fish
pip install -e ".[dev]"
bash scripts/setup-hooks.sh
```

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `omnilatex.cls` | Main document class |
| `lib/` | 31 Lua modules (layout, typography, language, etc.) |
| `config/` | Doctype profiles and institution configs |
| `examples/` | 50 example documents |
| `buildlib/` | Python build system (9 modules) |
| `tests/` | Python test suite |
| `lean/` | Lean 4 formal verification modules |
| `web/` | Astro documentation site |
| `extensions/` | VS Code extension |
| `scripts/` | CI and utility scripts |

## Coding Conventions

### Python

- **Formatter:** black (line length 100)
- **Import sort:** isort (profile black)
- **Linter:** flake8 (max-line-length 100, ignore E203, W503)
- **Type hints:** Use `from __future__ import annotations` and modern syntax (`X | None`, `list[str]`)
- **Tests:** pytest with descriptive names (`test_cache_hit_skips_build`)

### LaTeX

- **Module files:** `lib/*.sty` -- each handles one concern (typography, layout, language)
- **Config files:** `config/document-types/*.sty` -- doctype-specific settings
- **Naming:** lowercase, underscores for multi-word (`conditional-include.sty`)
- **Lua modules:** `lib/*.lua` -- complex logic requiring LuaTeX

### Web (Astro + SolidJS)

- **Components:** PascalCase (`BaseLayout.astro`, `GalleryGrid.tsx`)
- **Styling:** CSS custom properties in `global.css`, no inline styles
- **Design tokens:** Spatial Materialism + Amoebic UI (see `web/src/styles/global.css`)

## Running Tests

```bash
# Fast suite (no LaTeX compilation, ~30s)
python -m pytest tests/ -m "not slow"

# Full suite including build tests (~3min)
python -m pytest tests/

# Specific module
python -m pytest tests/test_buildlib_builder.py -v

# With coverage
python -m pytest tests/ --cov=buildlib --cov-report=term-missing
```

## Pre-Commit / Pre-Push Hooks

The repo uses pre-commit hooks for formatting and a pre-push hook for quality gates:

**Pre-commit** (runs on `git commit`):
- black, isort, flake8, markdownlint, YAML validation
- Fast pytest subset

**Pre-push** (runs on `git push`, blocks on failure):
- Full fast pytest suite
- Lint checks
- Docker digest consistency
- Semantic versioning consistency

Install hooks after cloning:

```bash
bash scripts/setup-hooks.sh
```

## Commit Messages

Follow Conventional Commits:

```
type(scope): description

feat(web): add table-of-contents sidebar to doc pages
fix(builder): resolve cache corruption on crash
refactor(config): centralize latexmk command construction
docs(README): add feature highlights section
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `ci`, `perf`

## PR Workflow

1. Create a feature branch from `main`
2. Make changes, commit with conventional messages
3. Push and open a PR
4. CI must pass: lint, build, test, determinism, performance, visual regression
5. One review approval required for merge

## Adding a New Document Type

1. Create `config/document-types/<name>.sty` with doctype-specific settings
2. Add the name to `omnilatex.cls` option parsing
3. Create an example in `examples/<name>/` with `main.tex`
4. Add structural tests in `tests/test_modules.py` (file existence, option registration)
5. Run `python build.py build-example <name>` to verify

## Adding a New Institution

1. Copy an existing institution from `config/institutions/`
2. Customize colors in the `.sty` file (`\definecolor` commands)
3. Add logo files if applicable
4. Add structural tests for file existence and color definitions
5. Update the institution list in README.md

## Adding a New Language

1. Create `config/languages/<lang>.sty` with polyglossia setup
2. Add UI translations in the appropriate module
3. Add test coverage for language file existence
4. Test with a minimal example using `language=<lang>`

## Reporting Issues

Use the [bug report](.github/ISSUE_TEMPLATE/bug_report.md) or [feature request](.github/ISSUE_TEMPLATE/feature_request.md) templates. Include:

- OmniLaTeX version (check `VERSION.md`)
- Build method (Docker / Nix / Native TeX Live)
- Minimal working example that reproduces the issue
- Relevant log output

## Questions?

Open a [GitHub Discussion](https://github.com/WyattAu/OmniLaTeX-template/discussions) or check the [documentation site](https://omnilatex-template.wyattau.com/).
