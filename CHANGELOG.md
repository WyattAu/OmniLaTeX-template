# OmniLaTeX Template -- Changelog

All notable changes to this project will be documented in per-version files.

The format is based on [Keep a Changelog](https://keepachangelog.com).
This project adheres to [Semantic versioning](https://semver.org).

## [v2.1.0] - 2026-05-24

See [CHANGELOG/v2.1.0.md](CHANGELOG/v2.1.0.md).

## [Unreleased]

### Fixed

- **Tests**: Fixed 15 failing slow tests (test_edge_cases.py, test_unicode.py) by switching
  from `latexmk` to `lualatex` for single-pass compilation. The `latexmk` return code
  was non-zero due to the biber/biblatex cycle even when PDF was generated successfully.
- **Tests**: Fixed `visual_regression.py` wrong PDF path (used subdirectory structure
  `build/examples/{name}/main.pdf` but `build.py` outputs flat `build/examples/{name}.pdf`).
- **Code quality**: Added timeout to `CommandRunner.run()` (default 3600s) and `cmd_test`
  subprocess calls to prevent indefinite CI hangs.
- **Code quality**: Added `encoding="utf-8"` to all `write_text`/`read_text` calls in `build.py`.
- **Code quality**: Narrowed broad `except Exception` blocks to specific exception types
  across `build.py` (12 occurrences).
- **Code quality**: Added `FileNotFoundError` handling for `inotifywait` fallback in watch mode.
- **CI/CD**: Fixed SBOM upload: replaced incorrect `github/codeql-action/upload-sarif`
  (expects SARIF format) with `anchore/sbom-action` `upload-sbom: true` (uses Dependency
  Snapshot API for SPDX JSON).
- **CI/CD**: Raised coverage threshold from 60% to 80%.
- **CI/CD**: Removed `continue-on-error: true` from edge case test step (tests now pass).
- **CI/CD**: Added `timeout-minutes: 10` to changelog job.
- **CI/CD**: Added top-level `permissions: contents: read` to `docker-ci.yml`.
- **CI/CD**: Removed dead git commit step in `visual-regression.yml` (handled by
  `create-pull-request` action).
- **CI/CD**: Fixed pre-commit config invalid `timeout` keys (unsupported by pre-commit).
- **Documentation**: Fixed stale dates in ROADMAP-v2.md, ROADMAP-DETAILED.md,
  ROADMAP-PRODUCTION.md to match VERSION.md (2026-05-17).

## Version History

| Version | Date | Summary |
|---------|------|---------|
| [2.0.0](CHANGELOG/v2.0.0.md) | 2026-05-17 | Beamer class, 5 institutions, CTAN TDS zip, manual expansion, CI hardening |
| [1.25.0](CHANGELOG/v1.25.0.md) | 2026-05-11 | Beamer support, pytest-cov CI, VS Code build-on-save |
| [1.24.0](CHANGELOG/v1.24.0.md) | 2026-05-11 | CrossReferenceConsistency proofs, deprecation mechanism, institution docs |
| [1.23.0](CHANGELOG/v1.23.0.md) | 2026-05-11 | DoctypePageGeometry proofs, institution tests, digest validation |
| [1.22.0](CHANGELOG/v1.22.0.md) | 2026-05-11 | Docker digest sync, visual regression CI, CHANGELOG split |
| [1.21.0](CHANGELOG/v1.21.0.md) | 2026-05-11 | ModuleIntegrity proofs, pre-commit Python 3.14 compat, audits |
| [1.20.0](CHANGELOG/v1.20.0.md) | 2026-05-11 | BuildModeStrictness proofs, build.py type hints |
| [1.19.0](CHANGELOG/v1.19.0.md) | 2026-05-10 | test_build_py.py, API stability doc, Nix packages, test coverage |
| [1.17.0](CHANGELOG/v1.17.0.md) | 2026-05-10 | 238-page manual, test constants, 14 bug fixes |
| [1.16.0](CHANGELOG/v1.16.0.md) | 2026-05-06 | TestLeanProofConsistency, language switch, 508 tests, CI fixes |
| [1.15.0](CHANGELOG/v1.15.0.md) | 2026-05-05 | Lean 4 expansion, visual regression, TikZ figures, VS Code rewrite, CTAN upload |
| [1.14.0](CHANGELOG/v1.14.0.md) | 2026-05-04 | Recipe/Harvard/Columbia doctypes, full i18n parity, CI hardening |
| [1.13.0](CHANGELOG/v1.13.0.md) | 2026-05-03 | White paper/invoice doctypes, 6 new languages, VS Code skeleton, Lean 4 theorems |
| [1.12.0](CHANGELOG/v1.12.0.md) | 2026-05-03 | Persian RTL, 5 new languages, performance docs, patent example |
| [1.11.0](CHANGELOG/v1.11.0.md) | 2026-05-02 | 18 polyglossia languages, 5 language translations, CTAN guide, 7 Lean proofs |
| [1.10.0](CHANGELOG/v1.10.0.md) | 2026-05-02 | Lecture notes/syllabus/handout/memo doctypes |
| [1.9.0](CHANGELOG/v1.9.0.md) | 2026-05-02 | CTAN CI, Overleaf zip, module integration tests |
| [1.8.0](CHANGELOG/v1.8.0.md) | 2026-05-02 | Exam/homework/research proposal doctypes, font setters, GitHub Pages gallery, CTAN packaging |
| [1.7.1](CHANGELOG/v1.7.1.md) | 2026-04-30 | 10 bug fixes (glossary load, KOMA colors, font defaults, build.py, CI) |
| [1.7.0](CHANGELOG/v1.7.0.md) | 2026-04-29 | Nix packages, Docker multi-arch CI, cross-platform CI, determinism, Lean 4 CI |
| [1.6.0](CHANGELOG/v1.6.0.md) | 2026-04-26 | TeX Live 2025, 20+ TL2025 compatibility fixes, security hardening |
| [1.5.0](CHANGELOG/v1.5.0.md) | 2026-04-24 | Color themes, 6 institutions, RTL support, accessibility |
| [1.4.0](CHANGELOG/v1.4.0.md) | 2026-04-24 | 4 institution configs, CJK support, citation styles, presentation overhaul, VS Code extension |
| [1.3.1](CHANGELOG/v1.3.1.md) | 2026-04-24 | Docker monorepo merge, cross-platform CI fix |
| [1.3.0](CHANGELOG/v1.3.0.md) | 2026-04-23 | Poster/presentation/letter doctypes, build.py init/scaffold, benchmarking |
| [1.2.0](CHANGELOG/v1.2.0.md) | 2026-04-23 | TUM/ETH institutions, cross-platform CI, Lean 4, omnilatex.cwl |
| [1.1.0](CHANGELOG/v1.1.0.md) | 2026-04-22 | README v2, CONTRIBUTING, CTAN/Overleaf packaging, TUI menu, Lua utilities |
| [1.0.0](CHANGELOG/v1.0.0.md) | 2026-04-03 | Nix flake, 20 examples, build.py orchestrator, CI/CD, testing infrastructure |
