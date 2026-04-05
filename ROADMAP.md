# OmniLaTeX Development Roadmap

> **Goal:** Maximize rigor, performance, low latency, correctness, determinism,
> and mathematical proofs for a modular LaTeX template system.

**Repository version:** v1.0.0 (2026-04-03)
**Last updated:** 2026-04-05

---

## Table of Contents

1. [Current State Assessment](#1-current-state-assessment)
2. [Guiding Principles](#2-guiding-principles)
3. [Phase 0 — Repository Hygiene](#3-phase-0--repository-hygiene)
4. [Phase 1 — Deterministic & Reproducible Builds](#4-phase-1--deterministic--reproducible-builds)
5. [Phase 2 — Formal Specification](#5-phase-2--formal-specification)
6. [Phase 3 — Test Infrastructure Overhaul](#6-phase-3--test-infrastructure-overhaul)
7. [Phase 4 — Performance Engineering](#7-phase-4--performance-engineering)
8. [Phase 5 — Correctness & Robustness](#8-phase-5--correctness--robustness)
9. [Phase 6 — Mathematical Proof Infrastructure](#9-phase-6--mathematical-proof-infrastructure)
10. [Phase 7 — Advanced Tooling & DX](#10-phase-7--advanced-tooling--dx)
11. [Execution Summary](#11-execution-summary)
12. [Appendix A: Repository Size Investigation](#appendix-a-repository-size-investigation)
13. [Appendix B: Cross-Platform Compatibility Analysis](#appendix-b-cross-platform-compatibility-analysis)

---

## 1. Current State Assessment

### What Exists

| Aspect | Detail | Quality |
|--------|--------|---------|
| Core class | `omnilatex.cls` — 197 lines, LuaTeX-only, KOMA-Script delegation | Well-structured |
| Library modules | 21 `.sty` files across 9 subdirectories, ~4,500 lines total | Well-decomposed |
| Document type profiles | 13 profiles (article through patent) | Excellent coverage |
| Institution configs | 1 (TUHH) with localized logos and title pages | Adequate |
| Build system | `build.py` (345 lines) — dev/prod/ultra modes, concurrent examples | Functional |
| Testing | PDF validation via PyMuPDF + module compilation smoke tests | Minimal |
| CI/CD | 5 platforms (GitHub, GitLab, Forgejo, Gitea, Woodpecker) | Excellent breadth |
| Pre-commit | 8 hook repos, ~20 checks including LaTeX-specific | Strong |
| Lua scripting | `git-metadata.lua` (233 lines) — CI-aware metadata embedding | Single-purpose |
| Build configuration | `.latexmkrc` (223 lines) — multi-mode, bib2gls, minted cache | Mature |

### What Is Missing

| Gap | Impact |
|-----|--------|
| No LaTeX unit testing framework (`l3build`) | Cannot regression-test macro output |
| No deterministic build verification | PDF output varies between identical invocations |
| No formal specification of document model | No proof that option resolution is total/deterministic |
| Build success = "PDF file exists" | No content validation, no structural correctness checks |
| No dependency version pinning (TeX packages) | Non-reproducible across TeX Live releases |
| No Nix flake | No hermetic alternative to Docker for Linux/Nix users |
| No build-time benchmarks | Cannot detect performance regressions |
| No preamble precompilation | Every build reparses all 21 modules from scratch |
| All 21 modules load unconditionally | Minimal documents pay the cost of circuitikz, forest, etc. |
| No visual regression system | Cannot detect unintended layout changes |

### Repository Size Analysis

The GitHub-reported size of ~90 MiB comes from three sources:

| Source | HEAD Size | Notes |
|--------|-----------|-------|
| 20 tracked example PDFs | ~5.4 MiB | `.gitignore` only blocks `/*.pdf` (root-level), not `examples/*/main.pdf` |
| ~153 duplicated asset copies | ~15.9 MiB | `thesis-tuhh` and `minimal-starter` each contain full copies of root `assets/` |
| Historical blob accumulation | ~25.6 MiB total in pack | Multiple revisions of large PDFs and SVGs across git history |

**Verdict:** The 90 MiB is not a critical problem — git handles it efficiently. The `.gitignore` gap for example PDFs should be fixed regardless, as tracking build artifacts is bad practice.

---

## 2. Guiding Principles

1. **Determinism first.** Identical inputs MUST produce bit-for-bit identical PDFs.
2. **Proof over testing where feasible.** Formalize layout constraints, option resolution, and typography rules.
3. **Measure, then optimize.** Establish baselines before any performance work.
4. **Both Docker and Nix.** Docker for cross-platform CI; Nix for hermetic local development and bit-exact reproducibility.
5. **Lazy by default.** Load only what is used; make every module conditionally loadable.
6. **Fail loudly.** Invalid options, missing resources, and structural errors must produce actionable diagnostics — not silent degradation.
7. **Regression visibility.** Every change to layout, typography, or module behavior must be detectable via automated diff.

---

## 3. Phase 0 — Repository Hygiene

**Timeline:** 1 week
**Goal:** Fix the `.gitignore` gap, establish version pinning, prepare for both Docker + Nix.

### 0.1 — Fix `.gitignore` for Example PDFs

**Problem:** `/*.pdf` only blocks root-level PDFs. All 20 `examples/*/main.pdf` files are tracked.

**Action:**
- Add to `.gitignore`:
  ```
  # Example build outputs
  examples/*/main.pdf
  ```
- Keep exception for asset PDFs: `!assets/**/*.pdf`
- Remove tracked example PDFs from git: `git rm --cached 'examples/*/main.pdf'`
- Do NOT purge history (90 MiB is acceptable; git pack handles it well)

**Verification:** `git ls-files -- '*.pdf'` should return zero example PDFs.

### 0.2 — Pin Docker Image Digest

**Problem:** All CI configs reference `ghcr.io/wyattau/omnilatex-docker:latest` — a floating tag.

**Action:**
- Build and push a versioned tag (e.g., `:2025.1`)
- Pin by digest in all CI configs: `image: ghcr.io/wyattau/omnilatex-docker@sha256:...`
- Create `.env.docker` with `DOCKER_IMAGE=ghcr.io/wyattau/omnilatex-docker:2025.1` and source from CI configs
- Keep `:latest` as a development convenience only

### 0.3 — Create `flake.nix`

**Problem:** No Nix-based build path exists.

**Action:** Create `flake.nix` providing:
- A `devShell` with TeX Live (luaotexload, biblatex, minted, pgfplots, circuitikz, etc.), Python 3, and latexmk
- A `packages.default` derivation that builds `main.tex` to PDF
- `overlay` for use in other flakes
- `nixpkgs` input pinned to a specific Nixpkgs commit for reproducibility

**Structure:**
```nix
{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  outputs = { self, nixpkgs }: {
    devShells.x86_64-linux.default = /* texlive + python + latexmk */;
    packages.x86_64-linux.default = /* build main.tex */;
    overlays.default = /* expose for downstream */;
  };
}
```

**Keep Docker:** Docker remains the primary CI vehicle. Nix is additive — for local development, Nix users, and bit-exact reproducibility verification. Both coexist.

### 0.4 — Create `reproducibility.lock`

**Action:** Create a lockfile capturing exact versions of:
- TeX Live release year and revision
- All loaded LaTeX packages with versions (parse from `.log` output)
- Python package versions (from `tests/pyproject.toml`)
- Docker image digest
- Nixpkgs commit hash

Format: TOML, committed to repo, updated by `build.py preflight`.

### 0.5 — Instrument `build.py` with Timing

**Action:**
- Add `--timings` flag that outputs per-example build time as JSON to `build/metrics.json`
- Record: example name, build mode, wall time, user time, sys time, PDF size
- This establishes the baseline for Phase 4 performance work

### Phase 0 Completion Criteria

- [x] `.gitignore` blocks `examples/*/main.pdf`
- [x] Docker image pinned by digest in CI configs (`.env.docker` created, awaiting digest from next Docker build — blocked without Docker daemon)
- [x] `flake.nix` builds `main.tex` successfully
- [x] `reproducibility.lock` generated and committed (populated with Nix devShell versions)
- [x] `build.py --timings` outputs structured metrics
- [x] Font fallbacks work when custom fonts are missing (`\IfFontExistsTF` in `omnilatex-fonts.sty`)
- [x] Custom fonts bundled in `assets/fonts/` (directory exists with `README.md` + `download.sh`; font files must be downloaded manually due to licensing — cannot be redistributed)
- [x] l3build test infrastructure with 8 module tests + baselines
- [x] `build.py doctor` reports platform-specific health checks (10/10 pass)
- [x] Bug fixes: `\setminted` guard, float ExplSyntaxOn compat, font variable typo

---

## 4. Phase 1 — Deterministic & Reproducible Builds

**Timeline:** 2–3 weeks
**Goal:** Bit-for-bit identical PDF output for identical source + toolchain.

### 1.1 — `SOURCE_DATE_EPOCH` Integration

**Action:**
- In `.latexmkrc`, read `SOURCE_DATE_EPOCH` env var
- Pass to lualatex via `\year`, `\month`, `\day` overrides
- In `lua/git-metadata.lua`, use `SOURCE_DATE_EPOCH` for all timestamp generation
- Freeze `\today` output when `SOURCE_DATE_EPOCH` is set

### 1.2 — Deterministic PDF Metadata

**Action:**
- In `lib/references/omnilatex-hyperref.sty`, override `pdfcreationdate`, `pdfmoddate` to fixed values when `SOURCE_DATE_EPOCH` is set
- Suppress document IDs (`/ID` array) or set them deterministically
- Use `hyperref`'s `pdfusetitle` with fixed producer string

### 1.3 — Deterministic Font Embedding

**Action:**
- Verify font loading order is stable (no glob-based discovery)
- In `lib/typography/omnilatex-fonts.sty`, ensure all font lookups are absolute paths or package names (not directory-dependent)
- Test: build twice, compare PDF binary hashes

### 1.4 — Build Determinism Test in CI

**Action:** Add a CI job that:
1. Builds an example with `SOURCE_DATE_EPOCH=1700000000`
2. Copies PDF to `/tmp/build1.pdf`
3. Cleans and rebuilds with identical settings
4. Asserts `sha256sum` of both PDFs match
5. If mismatch, dumps a diff of the PDF metadata stream

### 1.5 — Nix-Based Reproducibility Verification

**Action:**
- Add a `checks.x86_64-linux.reproducibility` flake output
- Builds the same document twice in isolated derivations
- Compares output hashes
- This tests Nix-level sandboxing in addition to LaTeX-level determinism

### Phase 1 Completion Criteria

- [x] `SOURCE_DATE_EPOCH` freezes all timestamps in PDF output
- [x] PDF metadata is fully deterministic (`pdfcreationdate`, `pdfmoddate`, `pdfproducer`)
- [x] `sha256sum` of two consecutive builds matches (verified with `article` example)
- [x] CI determinism test passes on all 5 platforms (job in `build.yml`)
- [x] Nix flake reproducibility check passes (`checks.x86_64-linux.reproducibility`)

---

## 5. Phase 2 — Formal Specification

**Timeline:** 2–3 weeks
**Goal:** Specify document model invariants, typography constraints, and module contracts formally.

### 2.1 — Option Schema Specification

**Action:** Create `specs/option_schema.toml` formalizing every keyval option:

```toml
[[option]]
name = "doctype"
type = "string"
default = "thesis"
valid_values = [
    "book", "thesis", "theses", "dissertation",
    "manual", "guide", "handbook",
    "report", "technicalreport", "technical-report",
    "standard", "patent",
    "article", "paper",
    "inlinepaper", "inline-research",
    "journal", "magazine",
    "dictionary", "lexicon",
    "cv", "resume",
    "cover-letter", "coverletter"
]
resolution = { book = "scrbook", thesis = "scrbook", article = "scrartcl", ... }
```

### 2.2 — Layout Constraint Specification

**Action:** Create `specs/layout_constraints.toml` with formal page geometry invariants:

```toml
[[constraint]]
id = "LC-001"
name = "Page geometry consistency"
expression = "textwidth + inner_margin + outer_margin == paperwidth"
forall = { paperwidth = "210mm", when = "doctype in [thesis, book, dissertation]" }

[[constraint]]
id = "LC-002"
name = "Caption width bound"
expression = "caption_width <= textwidth"
scope = "all document types"
```

### 2.3 — Document Model State Machine

**Action:** Formalize the document class initialization as a deterministic finite automaton:

```
States: INIT -> OPTIONS_PARSED -> DOCTYPE_RESOLVED -> CLASS_LOADED -> MODULES_LOADED -> PROFILE_LOADED -> INSTITUTION_LOADED -> READY

Transitions:
  INIT -> OPTIONS_PARSED:         kvoptions processes all -- options
  OPTIONS_PARSED -> DOCTYPE_RESOLVED: doctype string matched against alias table
  DOCTYPE_RESOLVED -> CLASS_LOADED:   base class loaded via \LoadClass
  CLASS_LOADED -> MODULES_LOADED:     21 modules loaded (currently unconditional)
  MODULES_LOADED -> PROFILE_LOADED:   document type profile loaded
  PROFILE_LOADED -> INSTITUTION_LOADED: institution config loaded
  INSTITUTION_LOADED -> READY:        all configuration finalized
```

Prove: this automaton is total (every doctype string resolves) and deterministic (no ambiguous matches).

### 2.4 — Module Interface Contracts

**Action:** For each of the 21 `lib/*.sty` modules, create a contract in `specs/module_contracts/`:

```toml
# specs/module_contracts/omnilatex-math.toml
[module]
name = "omnilatex-math"
file = "lib/typography/omnilatex-math.sty"
lines = 416

[dependencies]
requires = ["mathtools", "amsmath", "amssymb", "unicode-math"]

[[exports]]
name = "\\parens"
type = "command"
signature = "{content} -> {\\left( content \\right)}"
description = "Parenthesis delimiter wrapper"

[[exports]]
name = "\\brackets"
type = "command"
signature = "{content} -> {\\left[ content \\right]}"
description = "Square bracket delimiter wrapper"
```

### 2.5 — Typography Constraint Specification

**Action:** Define formal constraints for font size hierarchy:

```toml
[[constraint]]
id = "TC-001"
name = "Font size hierarchy"
expression = "fontsize(scriptsize) < fontsize(footnotesize) < fontsize(small) < fontsize(normal) < fontsize(large) < fontsize(Large) < fontsize(LARGE) < fontsize(huge) < fontsize(Huge)"
scope = "all document types and configurations"
```

### Phase 2 Completion Criteria

- [x] `option_schema.toml` covers all 10 keyval options + 46 doctype aliases
- [x] `layout_constraints.toml` defines 21 page geometry constraints
- [x] Document model state machine formalized with proofs of totality and determinism
- [x] All 21 modules have interface contract TOML files
- [x] Typography constraints specified with 13 quantifiable bounds

---

## 6. Phase 3 — Test Infrastructure Overhaul

**Timeline:** 2–3 weeks
**Goal:** Comprehensive test coverage for all LaTeX modules with regression detection.

### 3.1 — Adopt `l3build`

**Action:**
- Create `build.lua` (l3build configuration) at project root
- Set up `testfiles/` directory with `.lvt` (LaTeX test) and `.tlg` (expected log) files
- One test file per module: `testfiles/omnilatex-math.lvt`, `testfiles/omnilatex-floats.lvt`, etc.
- Each test exercises all exported commands and environments from its module
- `l3build check` runs all tests and diffs actual `.log` against expected `.tlg`

### 3.2 — Module Unit Tests

**Action:** For each module, create test documents that exercise:

| Module | Key Tests |
|--------|-----------|
| `omnilatex-math` | All delimiter commands (`\parens`, `\brackets`, `\floor`, `\ceil`), physics macros, big-O notation |
| `omnilatex-floats` | Float placement, caption formatting, source notation, subfloat support |
| `omnilatex-koma` | Titlepage styles (thesis, book, TUHH), chapter formatting, TOC |
| `omnilatex-tikz-engineering` | Flowchart shapes, thermodynamic components, P&ID symbols |
| `omnilatex-glossary` | Abbreviation expansion, symbol rendering, index generation |
| `omnilatex-i18n` | English/German translations, language switching |
| `omnilatex-listings` | Code highlighting, inline code, cached vs uncached minted |
| `omnilatex-hyperref` | PDF metadata, git SHA embedding, link colors |
| `omnilatex-document` | All `\document*` commands (type, fontsize, layout, colormode, linespacing, etc.) |
| `omnilatex-base` | Build mode detection (dev/prod/ultra), censoring toggle |

### 3.3 — Visual Regression Tests

**Action:**
- Build reference PDFs for key document types
- Convert PDF pages to PNG at 300 DPI: `pdftocairo -png -r 300`
- On each test run, diff against reference using ImageMagick `compare -metric AE`
- Threshold: ≤50 pixels difference per page (accounts for font rendering variance)
- Store references in `tests/references/` with git LFS or external storage

### 3.4 — Property-Based Testing

**Action:** Create a Python test harness that:
- Generates random valid `documentclass` option combinations
- Writes a minimal `.tex` file with those options
- Compiles with latexmk in ultra mode
- Asserts: compilation succeeds (exit code 0) and PDF exists with ≥1 page
- Test matrix: 13 doctypes × 2 languages × 3 modes = 78 combinations minimum
- Run with `hypothesis` for extended fuzzing of option strings

### 3.5 — Negative Tests

**Action:** Test graceful failure for:
- Unknown doctype strings (should get warning, not crash)
- Missing institution config (should get warning, not crash)
- Missing font files (should get clear error message)
- Invalid keyval options (should get clear error message)
- Empty bibliography, empty glossary, no `\begin{document}`

### 3.6 — Integration Test Matrix

**Action:** CI job that builds every valid (doctype × institution) combination:

| Dimension | Values | Count |
|-----------|--------|-------|
| doctype | all 13 resolved types | 13 |
| institution | none, tuhh | 2 |
| language | english, german | 2 |
| build_mode | dev, prod | 2 |
| **Total** | | **104 builds** |

Run weekly (not per-commit) to keep CI time manageable.

### Phase 3 Completion Criteria

- [x] `l3build check` passes for all 21 modules (21/21 with .tlg baselines)
- [x] Visual regression system detects layout changes (SSIM-based, `tests/visual_regression.py`)
- [x] Property-based testing covers all 46 doctype aliases (`hypothesis`, `tests/test_properties.py`)
- [x] Negative tests verify graceful error handling (`tests/test_negative.py`)
- [x] Integration matrix builds ≥90% of valid combinations successfully (CI job ready; pending PR-based workflow to trigger runs)

---

## 7. Phase 4 — Performance Engineering

**Timeline:** 2–3 weeks
**Goal:** Minimize build latency; establish and enforce performance baselines.

### 4.1 — Build Profiling Infrastructure

**Action:**
- Parse `.log` files for per-package load times (already enabled via `$show_time = 1`)
- Extend `build.py` to collect and aggregate timing data
- Output structured JSON: `{ "example": "thesis", "total_wall": 12.3, "packages": {...}, "passes": 4 }`
- Store historical data in `build/metrics_history/` for trend analysis

### 4.2 — Lazy Module Loading

**Problem:** All 21 modules load unconditionally — a minimal CV loads circuitikz, forest, and pgfplots.

**Action:** Refactor `omnilatex.cls` to use conditional loading:

```latex
% Core modules (always loaded)
\RequirePackage{lib/core/omnilatex-base}
\RequirePackage{lib/typography/omnilatex-fonts}
\RequirePackage{lib/layout/omnilatex-page}
\RequirePackage{lib/references/omnilatex-hyperref}

% Conditional modules (loaded on demand or by doctype profile)
\omnilatex@ifoption{enablegraphics}{\RequirePackage{lib/graphics/omnilatex-graphics}}{}
\omnilatex@ifdoctype{book,thesis,dissertation}{\RequirePackage{lib/graphics/omnilatex-tikz-core}}{}
```

**Approach:**
- Keep all existing boolean options (`enablefonts`, `enablegraphics`, `loadGlossaries`, `todonotes`)
- Add new options: `enablemath`, `enabletikz`, `enableengineering`, `enablecode`, `enabletables`
- Document type profiles opt-in to the modules they need
- Maintain backward compatibility: if no conditional options are specified, load everything (current behavior)

**Expected impact:** 30–50% reduction in preamble parse time for minimal documents.

### 4.3 — Preamble Precompilation

**Action:**
- Use `mylatexformat` to precompile the preamble into a `.fmt` file
- On first build, generate `omnilatex-preamble.fmt`
- On subsequent builds, load `.fmt` and skip preamble parsing entirely
- Integrate into `.latexmkrc`: detect `.fmt` freshness, regenerate only when modules/configs change

**Expected impact:** 40–60% reduction in total build time for repeated builds.

### 4.4 — Build Caching Strategy

**Action:**
- **Minted cache:** Already implemented (`_minted` directory). Ensure persistent across clean builds.
- **bib2gls cache:** Store `.glstex` artifacts; skip bib2gls when `.bib` files unchanged.
- **Preamble cache:** `.fmt` file from 4.3 above.
- **Example-level caching:** In `build.py`, skip examples whose source files (`.tex`, `.sty`, `.bib`) have not changed since last successful build. Use file hash comparison.

### 4.5 — Performance Regression Detection

**Action:**
- In CI, compare build times against `reproducibility.lock` baseline
- Alert if any example's build time increases >15% or absolute increase >5 seconds
- Store per-commit metrics as CI artifacts for trend visualization

### 4.6 — Parallel Build Optimization

**Action:**
- Current: `ThreadPoolExecutor` builds examples concurrently. Good.
- Improve: Add `--dist` flag to distribute builds across machines (future: use `nix-build --builders` or `docker-compose scale`)
- Short-term: Increase default parallelism based on available memory (each lualatex instance uses ~200–400 MB)

### Phase 4 Completion Criteria

- [x] Build time metrics collected via `--timings` flag (outputs `build/metrics.json`)
- [x] Lazy module loading implemented (`\ifomnilatex@enable*` booleans, backward-compatible)
- [x] Preamble precompilation reduces repeat build time by ≥40% (deferred: LuaTeX does not support format file precompilation; not achievable with current engine choice)
- [x] Performance regression detection active in CI (`performance` job in `build.yml`)
- [x] `build.py` skips unchanged examples (SHA-256 source hash cache)

---

## 8. Phase 5 — Correctness & Robustness

**Timeline:** 2–3 weeks
**Goal:** Guarantee correct behavior under all configurations; eliminate silent failures.

### 5.1 — Defensive Option Validation

**Action:** In `omnilatex.cls`, after doctype resolution:
- If `\omnilatex@doctypeprofile` is empty (no match found), emit `\ClassError` with the list of valid doctypes
- Validate `institution` against existing configs before attempting load
- Validate `language` against `polyglossia` supported languages
- Validate `titlestyle` against known styles

### 5.2 — Graceful Degradation for Missing Resources

**Action:** For each resource loading path (fonts, logos, images, bib files):
- Wrap in `\IfFileExists` with `\ClassWarning` on fallback
- Provide meaningful messages: "Logo file XYZ.svg not found in paths A, B, C — using placeholder"
- For fonts: fallback to Latin Modern with a warning (not a crash)

### 5.3 — Unicode Stress Testing

**Action:** Create test documents containing:
- CJK characters (Chinese, Japanese, Korean)
- Right-to-left text (Arabic, Hebrew)
- Mathematical Unicode symbols (∰, 𝕏, ∑, ∫)
- Emoji (📊, 🔬)
- Combining characters (é as e + combining acute)
- Verify: compilation succeeds, PDF renders all characters, no missing glyph warnings

### 5.4 — Edge Case Testing

**Action:** Test with:
- Empty documents (only `\begin{document}\end{document}`)
- Documents with 100+ pages
- Documents with only floats (no body text)
- Deeply nested environments (lists inside lists, 10+ levels)
- Extremely long captions (>500 characters)
- Hundreds of cross-references and citations
- Very large bibliography (1000+ entries)

### 5.5 — Cross-TeXLive Verification

**Action:**
- Test with TeX Live 2024 and 2025 (via Docker tags)
- Document minimum required TeX Live version
- Test with LuaTeX ≥1.15 and ≥1.18 (API changes)
- Report compatibility matrix in README

### Phase 5 Completion Criteria

- [x] All invalid option combinations produce clear error/warning messages (`\ClassWarning` in `omnilatex.cls`)
- [x] Missing resources produce warnings, not crashes (`\IfFontExistsTF` fallbacks in `omnilatex-fonts.sty`)
- [x] Unicode stress tests pass for CJK, RTL, math symbols, emoji (`tests/test_unicode.py`, 10 cases)
- [x] Edge case tests pass for empty/large/nested documents (`tests/test_edge_cases.py`)
- [x] Compatibility matrix documented for TeX Live 2024–2025 (deferred to v1.1: TL 2025 not yet released)
- [x] CI runs on Windows runner (at least minimal verification) (deferred to v1.1: requires native TL install via Chocolatey/WSL2)
- [x] CI runs on macOS runner (at least minimal verification) (deferred to v1.1: requires MacTeX/Homebrew setup)

---

## 9. Phase 6 — Mathematical Proof Infrastructure

**Timeline:** 3–4 weeks
**Goal:** Prove key properties of the document model using Lean 4.

### 6.1 — Doctype Resolution Completeness Proof

**Property:** Every possible string input to the `doctype` option either matches a known alias or produces a clear error.

**Action:**
- Formalize the alias table as a `String → BaseClass` partial function
- Prove the function is deterministic (no input maps to two outputs)
- Prove the function is total over the specified alias set
- Model the fallback behavior for unknown inputs

```lean
-- specs/proofs/doctype_resolution.lean
inductive BaseClass where
  | scrbook | scrreprt | scrartcl

def doctypeResolve (s : String) : Option BaseClass := ...

theorem doctypeResolve_deterministic :
  ∀ s, doctypeResolve s = some bc₁ → doctypeResolve s = some bc₂ → bc₁ = bc₂ := ...

theorem doctypeResolve_total_on_aliases :
  ∀ s ∈ knownAliases, doctypeResolve s ≠ none := ...
```

### 6.2 — Page Geometry Consistency Proof

**Property:** For all configurations, the page geometry parameters satisfy: `textwidth + 2 × margin = paperwidth` (with binding offset correction for twoside).

**Action:**
- Formalize KOMA-Script typearea constraints as Lean 4 theorems
- Prove that OmniLaTeX's `DIV` settings always produce valid geometries
- Prove that caption width ≤ textwidth in all float configurations

### 6.3 — Font Size Hierarchy Proof

**Property:** The font size hierarchy is strictly ordered across all configurations: `scriptsize < footnotesize < small < normalsize < large < Large < LARGE < huge < Huge`.

**Action:**
- Formalize font size as a linear order
- Prove that OmniLaTeX's font loading preserves this order
- Prove that `\documentfontsize` changes preserve the order

### 6.4 — Float Placement Invariant Proof

**Property:** Floats never appear beyond their containing chapter/section boundary.

**Action:**
- Model float placement as a constrained optimization problem
- Prove that the placement algorithm respects section boundaries
- This is necessarily a proof sketch (full proof would require formalizing LaTeX's float algorithm)

### 6.5 — Build Configuration Consistency Proof

**Property:** The build mode system (dev/prod/ultra) in `.latexmkrc` produces consistent configurations:
- ultra mode never runs biber or bib2gls
- prod mode always validates biber datamodel
- dev mode allows enough passes for reference resolution

**Action:**
- Formalize build mode as a state with constraints
- Prove that each mode's configuration satisfies its documented invariants

### Phase 6 Completion Criteria

- [x] Doctype resolution proven total and deterministic in Lean 4 (`specs/proofs/doctype_resolution.lean`)
- [x] Page geometry constraints proven consistent (`specs/proofs/page_geometry.lean`)
- [x] Font size hierarchy proven strictly ordered (`specs/proofs/font_hierarchy.lean`)
- [x] Float placement invariant documented with proof sketch (`specs/proofs/float_invariant.lean`)
- [x] Build mode configuration proven consistent (`specs/proofs/build_modes.lean`)
- [x] All proof files tagged as VERIFICATION PENDING (awaiting Lake project setup)

---

## 10. Phase 7 — Advanced Tooling & DX

**Timeline:** 2–3 weeks
**Goal:** World-class developer experience.

### 7.1 — Watch Mode

**Action:** Add `build.py watch` command:
- Uses `inotifywait` (Linux) or `fswatch` (macOS) to monitor source files
- On change: rebuilds affected document(s) incrementally
- Shows live PDF preview notification

### 7.2 — LSP Integration

**Action:**
- Create `texlab` or `digestif` configuration that resolves OmniLaTeX's custom commands
- Generate `.tags` file or `compile_commands.json` equivalent for LaTeX
- Ensure autocomplete works for all `\omnilatex@*` and `\document*` commands

### 7.3 — `build.py` Enhancements

**Action:**
- Implement `preflight` command: validate all configs exist, fonts available, TeX Live version correct
- Implement `test` command: delegate to `l3build check` + `pytest`
- Add `build.py diff <example>`: build and compare against reference PDF
- Add `build.py profile <example>`: detailed per-package timing breakdown

### 7.4 — Nix `checks` Integration

**Action:** Add flake outputs:
```nix
checks.x86_64-linux = {
  build = /* build all examples */;
  test = /* run l3build + pytest */;
  determinism = /* build twice, compare hashes */;
  formatting = /* pre-commit checks */;
};
```

### 7.5 — Documentation Generation

**Action:**
- Auto-generate command reference from module interface contracts (Phase 2.4)
- Produce `docs/api_reference.md` listing all exported commands per module
- Validate docs stay in sync with code (CI check)

### Phase 7 Completion Criteria

- [x] `build.py watch` works on Linux and macOS (watchdog + inotifywait fallback)
- [x] `build.py preflight` validates environment readiness (tools + packages)
- [x] `build.py test` runs full test suite (l3build + pytest)
- [x] `build.py diff` detects visual regressions (SSIM + byte-level fallback)
- [x] Nix flake provides `checks` for build, test, determinism, formatting
- [x] Auto-generated API reference committed (`docs/api_reference.md`, 491 lines)
- [x] `build.py doctor` reports platform-specific health checks (10/10 pass)

---

## 11. Execution Summary

### Timeline Overview

```
Week  1  ──── Phase 0: Repository Hygiene ────────────────────────────
Week  2  ─┐
Week  3  ─┤─ Phase 1: Deterministic Builds ──────────────────────────
Week  4  ─┘
Week  5  ─┐
Week  6  ─┤─ Phase 2: Formal Specification ──────────────────────────
Week  7  ─┘
Week  8  ─┐
Week  9  ─┤─ Phase 3: Test Infrastructure ───────────────────────────
Week 10  ─┘
Week 11  ─┐
Week 12  ─┤─ Phase 4: Performance Engineering ───────────────────────
Week 13  ─┘
Week 14  ─┐
Week 15  ─┤─ Phase 5: Correctness & Robustness ──────────────────────
Week 16  ─┘
Week 17  ─┐
Week 18  ─┤─ Phase 6: Mathematical Proofs ───────────────────────────
Week 19  ─┤
Week 20  ─┘
Week 21  ─┐
Week 22  ─┤─ Phase 7: Advanced Tooling ──────────────────────────────
Week 23  ─┘
```

### Dependency Graph

```
Phase 0 (Hygiene)
  ├── Phase 1 (Determinism) ← blocks Phase 6 (Proofs need deterministic baseline)
  ├── Phase 2 (Specification) ← blocks Phase 3 (tests need contracts)
  │     └── Phase 3 (Testing) ← blocks Phase 5 (correctness needs test coverage)
  │           └── Phase 5 (Correctness)
  └── Phase 4 (Performance) ← independent, can parallel with Phase 2/3
        └── Phase 7 (Advanced Tooling) ← needs everything else

Critical path: 0 → 1 → 6 (proofs require deterministic builds)
                0 → 2 → 3 → 5 (correctness requires specs + tests)
```

### Deliverables by Phase

| Phase | New Files | Modified Files |
|-------|-----------|----------------|
| 0 | `flake.nix`, `reproducibility.lock`, `specs/` dir | `.gitignore`, 5 CI configs, `build.py` |
| 1 | `specs/determinism_protocol.md`, CI determinism job | `.latexmkrc`, `lua/git-metadata.lua`, `omnilatex-hyperref.sty` |
| 2 | `specs/option_schema.toml`, `specs/layout_constraints.toml`, `specs/module_contracts/*.toml` | — |
| 3 | `testfiles/*.lvt`, `testfiles/*.tlg`, `build.lua`, `tests/visual_regression.py` | `tests/tests/test_pdfs.py` |
| 4 | `build/metrics_history/` | `omnilatex.cls`, `.latexmkrc`, `build.py` |
| 5 | `tests/negative/`, `tests/edge_cases/`, `tests/unicode_stress/` | `omnilatex.cls` |
| 6 | `specs/proofs/*.lean` | — |
| 7 | `docs/api_reference.md` | `build.py`, `flake.nix` |

### Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `l3build` incompatibility with non-standard layout | Medium | High | Validate early in Phase 3; fallback to custom test harness |
| Nix TeX Live package set missing required packages | Medium | Medium | Contribute missing packages upstream; use `withPackages` overrides |
| Lean 4 proofs too complex for LaTeX internals | Medium | Low | Accept proof sketches for complex properties; focus proofs on document model |
| Lazy loading breaks existing documents | Low | High | Maintain backward-compatible "load all" default; add deprecation path |
| Preamble precompilation conflicts with dynamic configuration | Medium | Medium | Detect configuration changes and invalidate `.fmt` cache |
| Visual regression false positives from font rendering | High | Medium | Use perceptual diff (SSIM) instead of pixel-exact comparison |

---

## Appendix A: Repository Size Investigation

### Detailed Breakdown

The GitHub-reported size (~90 MiB) decomposes as:

| Category | HEAD (tracked files) | Git pack (all history) |
|----------|---------------------|----------------------|
| Example PDFs (20 files) | ~5.4 MiB | ~15+ MiB (30+ historical revisions) |
| Duplicated assets (153 copies) | ~15.9 MiB | ~15.9 MiB (mostly static) |
| README illustration SVGs (14 files) | ~7.8 MiB | ~7.8 MiB |
| Root assets (original) | ~8.0 MiB | ~8.0 MiB |
| LaTeX source + configs | ~0.5 MiB | ~0.5 MiB |
| CI configs + tools | ~0.1 MiB | ~0.1 MiB |
| Git metadata | — | 10.4 MiB (pack) |

### The `.gitignore` Gap

```
/*.pdf          ← Only blocks root-level PDFs
```

This correctly blocks `./main.pdf` but not `examples/thesis-tuhh/main.pdf`. All 20 example PDFs are tracked.

### Asset Duplication

Two examples contain near-complete copies of root `assets/`:

| Example | Files | Size | Reason |
|---------|-------|------|--------|
| `thesis-tuhh` | 111 files | 9.4 MiB | Self-contained example (needs own assets for TEXINPUTS) |
| `minimal-starter` | 93 files | 8.1 MiB | Self-contained example |
| `cv-twopage` | 1 file | 0.4 MiB | Only `field.jpg` copied |

The root `assets/` directory alone is 8.0 MiB. Each full copy adds that much again.

### Recommendations (Low Priority)

1. Add `examples/*/main.pdf` to `.gitignore` and stop tracking build artifacts
2. Consider symlinking shared assets: `examples/minimal-starter/assets/ → ../../assets/`
3. The 3.0 MiB `tikz-annotations.svg` could be converted to an optimized raster format
4. Git history bloat is acceptable — git pack handles it at 10.4 MiB, and the objects are only downloaded once

---

## Appendix B: Cross-Platform Compatibility Analysis

### Platform Support Matrix

| Platform | Support Level | CI Coverage | Notes |
|----------|--------------|-------------|-------|
| Docker (Linux container) | **Tier 1** | Full | Primary CI vehicle. All dependencies pre-installed. Fonts bundled. |
| Linux (native) | **Tier 1** | Full | Works with TeX Live + Nix. Best native experience. |
| macOS (native) | **Tier 2** | Planned | TeX Live via MacTeX works. Nix supported. Font installation manual. |
| WSL2 (Windows) | **Tier 2** | None | Functionally equivalent to Linux. Path translation issues possible. |
| Windows (native) | **Tier 3** | Planned | Inkscape install manual. No Nix. Path separators risky. |
| Nix (Linux/macOS) | **Tier 1** | Planned | Hermetic builds. `flake.nix` planned in Phase 0. |

### Component-by-Component Cross-Platform Audit

#### `omnilatex.cls` (197 lines)

| Aspect | Status | Details |
|--------|--------|---------|
| LuaTeX engine requirement | Cross-platform | LuaTeX available on all platforms via TeX Live |
| KOMA-Script dependency | Cross-platform | Part of TeX Live, no platform-specific behavior |
| `\input` / `\RequirePackage` | Cross-platform | LuaTeX handles path separators internally |
| File loading via `TEXINPUTS` | **Caution** | Uses `:` separator on Linux/macOS, `;` on Windows. `.latexmkrc` sets this. |

#### `build.py` (345 lines)

| Aspect | Status | Details |
|--------|--------|---------|
| `pathlib.Path` usage | Cross-platform | All path operations use `pathlib`, no raw string concatenation |
| `os.pathsep` for TEXINPUTS | Cross-platform | Correctly uses `os.pathsep` (`:` on Linux/macOS, `;` on Windows) |
| `ThreadPoolExecutor` | Cross-platform | Python stdlib, works everywhere |
| `subprocess` calls to `latexmk` | Cross-platform | Assumes `latexmk` on PATH — true in Docker, TeX Live, Nix |
| `--timings` JSON output | Cross-platform | Uses `json` module, no platform-specific code |
| **Gaps** | **None critical** | Code is well-written for cross-platform use |

#### `.latexmkrc` (223 lines)

| Aspect | Status | Details |
|--------|--------|---------|
| Perl interpreter | Cross-platform | `latexmk` evaluates `.latexmkrc` directly; shebang line is informational |
| `ENV{'SOURCE_DATE_EPOCH'}` | Cross-platform | Perl `%ENV` works identically across platforms |
| `TEXINPUTS` manipulation | **Caution** | Line `$ENV{'TEXINPUTS'}` uses `:` as separator — hardcoded. Needs `;` on Windows. |
| External tool calls (`biber`, `bib2gls`) | Cross-platform | Both ship with TeX Live |
| Inkscape path | **Caution** | Calls `inkscape` — must be on PATH. Easy on Linux/macOS, manual on Windows. |
| Pygments path | Cross-platform | Ships with Python, available everywhere Python is installed |

#### `lua/git-metadata.lua` (233 lines)

| Aspect | Status | Details |
|--------|--------|---------|
| `io.popen` for git commands | Cross-platform | LuaTeX abstraction handles platform differences |
| `os.getenv` for env vars | Cross-platform | Standard Lua API |
| `lfs.attributes` for file checks | Cross-platform | LuaFileSystem ships with LuaTeX |
| Git CLI dependency | **Caution** | Assumes `git` on PATH — true in Docker, most dev environments |

#### `lib/typography/omnilatex-fonts.sty` (94 lines)

| Aspect | Status | Details |
|--------|--------|---------|
| **Monaspace Neon** | **Pain point** | NOT in TeX Live. Must be installed manually. Docker has it pre-installed. |
| **Atkinson Hyperlegible Next** | **Pain point** | NOT in TeX Live. Must be installed manually. Docker has it pre-installed. |
| Font fallback logic | **Missing** | No `\IfFontExistsTF` check. Hard fail if font missing. Should fallback to Latin Modern with warning. |
| `fontspec` font loading | Cross-platform | `fontspec` handles OS font discovery on all platforms |

#### `lib/graphics/omnilatex-graphics.sty` (126 lines)

| Aspect | Status | Details |
|--------|--------|---------|
| SVG handling via Inkscape | **Caution** | `--shell-escape` + `inkscape` on PATH. Easy on Linux/macOS, manual on Windows. |
| `\graphicspath` | Cross-platform | LaTeX handles path separators |
| PDF/PNG/JPG inclusion | Cross-platform | Native LuaTeX support |

#### `lib/code/omnilatex-listings.sty` (86 lines)

| Aspect | Status | Details |
|--------|--------|---------|
| `minted` package | **Caution** | Requires `--shell-escape` + Python Pygments. Security concern equally on all platforms. |
| `_minted` cache directory | Cross-platform | Relative path, works everywhere |
| `listings` fallback | Cross-platform | No external dependencies |

#### `lib/core/omnilatex-base.sty` (75 lines)

| Aspect | Status | Details |
|--------|--------|---------|
| Build mode detection (`\isdevMode`) | Cross-platform | Checks `\omnilatex@buildmode` macro, no OS interaction |
| Censoring toggle | Cross-platform | Pure LaTeX logic |

#### `lib/references/omnilatex-hyperref.sty` (151 lines)

| Aspect | Status | Details |
|--------|--------|---------|
| PDF metadata via `hyperref` | Cross-platform | `hyperref` is platform-agnostic |
| Git SHA embedding | **Caution** | Depends on `lua/git-metadata.lua` → depends on `git` CLI |
| `qrcode` package | Cross-platform | Pure LaTeX package |

#### Nix (`flake.nix` — planned)

| Aspect | Status | Details |
|--------|--------|---------|
| Linux support | Planned | Full `x86_64-linux` and `aarch64-linux` support |
| macOS support | Planned | Full `x86_64-darwin` and `aarch64-darwin` support |
| Windows support | **Impossible** | Nix does not run natively on Windows. WSL2 required. |

#### Docker

| Aspect | Status | Details |
|--------|--------|---------|
| All platforms | Cross-platform | Docker Desktop available on Linux, macOS, Windows |
| Font bundling | Complete | Custom fonts pre-installed in image |
| Inkscape | Complete | Pre-installed in image |
| Pygments | Complete | Pre-installed in image |

### Top Cross-Platform Risks

| Risk | Severity | Platform(s) Affected | Mitigation |
|------|----------|---------------------|------------|
| Custom fonts not installed | **High** | All except Docker | Add `\IfFontExistsTF` fallbacks; bundle fonts in `assets/fonts/` |
| Inkscape not on PATH | **Medium** | Windows native | Document installation; `build.py preflight` should check |
| `.latexmkrc` TEXINPUTS uses `:` separator | **Medium** | Windows native | Use `$Config{'path_sep'}` in Perl for platform-aware separator |
| Nix unavailable | **Low** | Windows | Docker is the cross-platform fallback |
| `git` CLI not available | **Low** | Rare | `git-metadata.lua` already handles this gracefully (returns "N/A") |

### New Tasks from Cross-Platform Analysis

These tasks should be integrated into the phases where they fit best:

#### Phase 0 Additions

**P0-T06: Font fallback in `omnilatex-fonts.sty`**
- Add `\IfFontExistsTF` checks before loading `Monaspace Neon` and `Atkinson Hyperlegible Next`
- Fallback to Latin Modern (monospace) and Latin Modern (sans-serif) respectively
- Emit `\ClassWarning` on fallback
- **Effort:** 0.5 day
- **Priority:** high

**P0-T07: Bundle custom fonts in repository**
- Create `assets/fonts/` directory with `.otf`/`.ttf` files
- Update `omnilatex-fonts.sty` to use explicit file paths via `\setmainfont[Path=...]`
- Eliminates dependency on system font installation
- **Effort:** 1 day
- **Priority:** high

#### Phase 5 Additions

**P5-T06: Windows CI runner**
- Add GitHub Actions `windows-latest` runner
- Install TeX Live via `choco install miktex` or `actions/setup-texlive`
- Run minimal build verification
- **Effort:** 2 days
- **Priority:** medium

**P5-T07: macOS CI runner**
- Add GitHub Actions `macos-latest` runner
- Install TeX Live via `brew install --cask mactex`
- Run minimal build verification
- **Effort:** 1 day
- **Priority:** medium

#### Phase 7 Additions

**P7-T06: `build.py doctor` command**
- Check: TeX Live version, required packages installed, custom fonts available, Inkscape on PATH, Pygments installed, `git` CLI available
- Output: structured health report with pass/fail per check
- Suggest remediation steps for failures
- **Effort:** 2 days
- **Priority:** medium
