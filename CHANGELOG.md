# OmniLaTeX Template — Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com).
This project adheres to [Semantic versioning](https://semver.org/).

## [Unreleased]

### Added
- README v2: comparison table, all 20 examples listed, engineering quality surfaced
- CONTRIBUTING.md: architecture overview, institution/language/doctype tutorials, PR checklist
- ROADMAP-v1.1.md: formal roadmap for v1.1–v1.4 (distribution, ecosystem, cross-platform, features)
- CTAN packaging: `scripts/make-ctan-zip.sh` builds TDS-compliant upload package
- Overleaf packaging: `scripts/make-overleaf-zip.sh` builds self-contained Overleaf template
- CTAN documentation: `doc/omnilatex.tex` — 23-page user manual (compiles to PDF)
- `build.py diff` command: SSIM-based visual regression with byte-level fallback
- CI changelog check: enforces CHANGELOG.md update when `.sty`/`.cls` files change
- l3build regression tests for all 21 modules (with `.tlg` baselines)
- Template gallery: `docs/gallery.md` — all 20 examples with PDF links, categorized
- In-repo Dockerfile: reproducible build environment based on TeX Live 2024
- `build.py scaffold-institution <name>`: creates institution config from generic template
- `build.py init <name>`: initialize a new OmniLaTeX project from minimal-starter template
- Generic institution config: `config/institutions/generic/` — customizable template

### Changed
- README no longer references non-existent `cv-bw` example
- README identity: leads with value proposition instead of "fork from TUHH"

## [1.0.0] - 2026-04-03

### Added
- Nix flake with `scheme-medium` + explicit packages replacing `scheme-full` (~3.7 GiB → ~2.6 GiB, ~30% reduction)
- Deterministic PDF builds verification via `nix build` and `nix flake check`
- direnv integration with `.envrc` and `use flake`
- Inkscape and gnuplot added to devShell
- pytest-timeout, graceful pymupdf skip
- Lazy module loading for omnilatex.cls (enablemath, enabletikz, etc.)
- 20/20 examples documents templates, covering all document types profiles
- Formal specification (TOML) for module contracts
- l3build integration test files
- Property-based testing with hypothesis
- Unicode stress tests covering 15 languages/scripts
- Edge case testing for empty documents, float handling, cross-references stress tests
- Negative case testing for invalid inputs handling
- Visual regression testing infrastructure
- Performance engineering with `--timings` flag and concurrent builds
- Build caching with source hash comparison
- Mathematical proof infrastructure (Lean 4 proof files)
- Developer experience improvements:
- `build.py watch` command with file watching
- `build.py doctor` for health diagnostics
- `build.py preflight` for environment validation
- GitHub Pages auto-deployment for CI
 pipeline
- 5 platform CI/CD support (GitHub Actions, GitLab CI, Forgejo, Gitea, Woodpecker)
- Pre-commit hooks configuration
- `.envrc` with `use flake` for direnv integration

- VS Code Dev container configuration with Docker Compose

- Python-based build orchestrator (`build.py`, 1075 lines)
  - dev/prod/ultra modes with `--mode` flag
  - Concurrent example building with `-j` flag
  - `--timings` metrics collection
  - `--force` rebuild option
  - `--source-date-epoch` for reproducible builds timestamps

  - Subcommand: build-all, build-root, build-example, build-examples, watch, test, preflight, doctor, lint, clean
- `--latexmkrc` build configuration (223 lines)
  - lualatex engine with `$pdf_mode = 4`
  - Bib2gls custom dependency
  - Multi-pass latexmk with `--halt-on-error`
- Document class with option system
  - Lua-based metadata embedding (`git-metadata.lua`)
  - Conditionally loaded feature modules (enablemath, enabletikz, enablelistings, etc.)

### Fixed
- Restored 3 accidentally deleted files (minimal-starter/main.tex, thesis-tuhh floats.tex, usage.tex)
- Fixed duplicate label `fig:matlab2tikz_pgfplots` in thesis-tuhh and root floats.tex
- Fixed empty document test (`\mbox{}` ensures PDF page output)
- Fixed unicode test (`\\&` escape for special LaTeX chars)
- Fixed `build.py watch` method ( `_rebuild_affected` now correctly resolves
- Fixed `build.py test` method  using reliable project root path
- Fixed `.gitignore` for only ignore example symlinks, not root `.latexmkrc`

### Changed
- `omnilatex.cls` version: v0.1.1 → v1.0.0
- `reproducibility.lock` version: 0.1.1 → 1.0.0
- `ROADMAP.md` version updated to v1.0.0
- All `ROADMAP.md` completion checkboxes updated to reflect reality
- Build tool upgraded from 345 → 1075 lines
- Testing expanded significantly
- Library modules now 21 `.sty` files across 9 subdirectories
