# OmniLaTeX Comprehensive Manual — Plan

## Overview

A comprehensive reference manual covering every functionality of modern LaTeX through the lens of OmniLaTeX. Structured as a book (KOMA `scrbook`, ~30 chapters, ~800-1000 pages). Not a TUHH clone — a **superset** that covers everything TUHH demonstrates plus all 25 features it misses.

**Audience:** Graduate students, researchers, engineers, and technical writers who want a single authoritative reference for modern LaTeX practices.

**Compile target:** `doctype=manual` (KOMA scrreprt), bilingual index, glossary, full bibliography.

---

## Scope Comparison: TUHH Book vs. This Manual

| Category | TUHH Book | This Manual |
|---|---|---|
| Chapters | 6 (+ front/back matter) | ~30 (+ front/back matter) |
| Approximate pages | ~300 | ~800-1000 |
| Font showcase | YES | YES (expanded: CJK, RTL fonts) |
| Math macros | YES | YES (expanded: all statistical/physical/derivative macros) |
| Chemistry | YES | YES |
| Units (siunitx) | YES | YES (expanded: custom SI units, qualifiers) |
| Bibliography | YES | YES (expanded: 9 citation styles) |
| Glossaries | YES | YES (expanded: all glossary types) |
| SVG graphics | YES | YES |
| TikZ/pgfplots | YES | YES (expanded: all custom shapes, engineering diagrams) |
| Code listings | YES | YES (expanded: Lua, Modelica, CJK code) |
| Tables | YES | YES (expanded: longtblr, siunitx columns) |
| Floats | YES | YES |
| Landscape | YES | YES |
| Censoring | YES | YES |
| Git integration | YES | YES |
| Docker/build | YES | YES |
| **Color themes** | NO | YES |
| **Dark mode** | NO | YES |
| **Presentations** | NO | YES (full slide system) |
| **Posters** | NO | YES |
| **CVs** | NO | YES |
| **RTL (Arabic/Hebrew/Persian)** | NO | YES |
| **CJK (Chinese/Japanese/Korean)** | NO | YES |
| **PDF accessibility** | NO | YES |
| **All 26 doctypes** | NO (thesis only) | YES (dedicated chapter per category) |
| **All 16 institutions** | NO (TUHH only) | YES (institution branding chapter) |
| **9 citation styles** | NO | YES |
| **Custom SI units** | NO | YES |
| **Lua scripting** | NO | YES |
| **Cross-language documents** | NO | YES |
| **Invoice/recipe/letter** | NO | YES |
| **Homework/exam/syllabus** | NO | YES |
| **Patent/standard/white-paper** | NO | YES |
| **Engineering TikZ shapes** | NO | YES (valves, pumps, heat exchangers, radiators) |
| **Build modes** | NO | YES (dev/prod/ultra) |
| **Formal verification** | NO | YES (Lean 4 proofs) |

---

## Structure

### Front Matter

```
00_FRONTMATTER.md        — Title page, copyright, colophon
01_PREFACE.md           — Purpose, audience, how to use this book
02_NOTATION.md           — Typographic conventions used in the book itself
```

### Part I: Foundations (Getting Started)

```
10_INSTALLATION.md       — Docker, Nix, TeX Live, DevContainer, CI/CD
11_QUICKSTART.md         — 5-minute first document (minimal-starter example)
12_BUILD_SYSTEM.md       — build.py commands, latexmk, incremental builds, caching
13_CLASS_OPTIONS.md      — All 15 class options explained with examples
14_DOCTYPE_SYSTEM.md     — How doctype aliases work, KOMA class mapping, alias table
```

### Part II: Document Types (26 Profiles)

```
20_ARTICLES.md           — article, journal, inline-paper, white-paper, letter
21_REPORTS.md            — report, technical-report, research-proposal, standard, patent
22_THESES.md             — thesis, dissertation, manual, dictionary, thesis-tuhh
23_ACADEMIC.md           — homework, exam, lecture-notes, syllabus, handout
24_BUSINESS.md           — cv, cover-letter, invoice, memo, recipe
25_VISUAL.md             — presentation (slides), poster
```

### Part III: Typography & Content

```
30_FONTS.md              — fontspec, unicode-math, all 5 font families (roman/sans/mono/math/CJK)
31_TEXT_FORMATTING.md    — microtype, extdash, csquotes, ragged2e, blindtext
32_MATH.md               — amsmath, unicode-math, auto-scaling delimiters, all math macros
33_PHYSICAL_MATH.md      — siunitx, custom SI units/qualifiers, chemmacros, reaction equations
34_DERIVATIVES.md        — All derivative macros, vector calculus, thermodynamic notation
35_CJK_MATHEMATICS.md    — CJK math fonts, ruby/furigana annotations, vertical math
```

### Part IV: Language & Internationalization

```
40_I18N_SYSTEM.md        — polyglossia, translation keys, language fallback chain
41_MULTILINGUAL.md       — Switching languages mid-document, cross-language references
42_RTL_SCRIPTS.md        — Arabic, Hebrew, Persian: bidi layout, font fallback, Arabic-Indic digits
43_CJK_SCRIPTS.md        — Chinese, Japanese, Korean: luatexja, ruby, vertical writing, CJK-Latin spacing
44_TRANSLATION_KEYS.md   — Complete reference of all 47 keys × 18 languages
```

### Part V: Layout & Structure

```
50_PAGE_LAYOUT.md        — KOMA page geometry, BCOR, twoside, custom margins, headers/footers
51_SECTIONING.md         — KOMA sectioning hierarchy, paragraph, TOC customization
52_TITLE_PAGES.md        — 4 title styles (book/thesis/simple/tuhh), custom title pages
53_INSTITUTIONS.md       — All 16 institution configs, how to create your own
```

### Part VI: Figures, Tables & Floats

```
60_FLOATS.md             — Float placement, continued floats, float footnotes, side captions
61_FIGURES.md            — SVG (includesvg), TikZ basics, images, subfigures
62_TABLES.md             — booktabs, longtblr, siunitx S-columns, multi-column tables
63_PGFLOTS.md            — Line/scatter/bar plots, contour plots, date plots, CSV import, custom styles
64_TIKZ_ENGINEERING.md   — Flowcharts, circuit diagrams, 3D drawings, custom thermodynamic shapes
```

### Part VII: References & Glossaries

```
70_BIBLIOGRAPHY.md       — biblatex/biber setup, citation commands, backref, per-chapter bib
71_CITATION_STYLES.md    — All 9 styles (IEEE, ACM, APA, Chicago, Nature, Science, Harvard, Vancouver, MLA)
72_GLOSSARIES.md         — Symbols, abbreviations, numbers, subscripts, index, custom glossary fields
73_CROSS_REFERENCES.md   — cleveref, autoref, custom crefnames, PDF bookmarks
```

### Part VIII: Code & Listings

```
80_CODE_LISTINGS.md      — minted, inline/block/long listings, language support, Simulink icons
81_LUA_SCRIPTING.md      — Lua in LaTeX, git metadata, conditional compilation, custom commands
```

### Part IX: Advanced Features

```
90_COLOR_THEMES.md       — 7 palettes, dark/light mode, per-slot overrides, theme switching
91_BOXES_ENVS.md         — tcolorbox: example, callout, keyconcept, alert/definition/note blocks
92_CENSORING.md          — Censoring, TODO notes, blind text, censor boxes
93_ACCESSIBILITY.md      — PDF/UA-1, alt text, accessible links, heading validation, contrast checking
94_PRESENTATIONS.md     — Full slide system: frames, progress bar, section dividers, block envs
95_POSTERS.md            — Conference posters: A1 landscape, posterblock, column breaks
```

### Part X: Build & Automation

```
100_BUILD_MODES.md       — dev/prod/ultra modes, BUILD_MODE env var, mode-specific behavior
101_GIT_INTEGRATION.md    — Git SHA, ref name, verification box, build date
102_DOCKER_WORKFLOW.md   — Docker image, build commands, CI/CD pipeline, cross-platform
103_NIX_WORKFLOW.md      — flake.nix, dev shell, reproducible builds
104_CI_CD.md             — 9 GitHub Actions workflows, CTAN auto-upload, release automation
```

### Part XI: Formal Verification

```
110_LEAN4_PROOFS.md       — 53 theorems across 10 modules, proof structure, how to read/extend
111_ARCHITECTURE.md      — 27 modules, dependency graph, module responsibilities
```

### Back Matter

```
B0_APPENDIX_COMMANDS.md — Quick-reference: every OmniLaTeX command alphabetically
B1_APPENDIX_OPTIONS.md   — Quick-reference: every class option
B2_APPENDIX_DOCTYPES.md  — Quick-reference: all 26 doctypes with aliases
B3_APPENDIX_MODULES.md   — Quick-reference: all 27 lib modules
B4_APPENDIX_SIUNITS.md   — Quick-reference: all custom SI units and qualifiers
```

---

## Implementation Plan

### Phase 1: Scaffold (chapters 00-02, 10-14)
- Create the `examples/manual/` directory structure
- `config/document-types/manual.sty` already exists
- Write front matter + Part I (foundations)
- Establish consistent formatting conventions

### Phase 2: Core Content (chapters 30-34, 50-53, 60-63, 70-72)
- Typography, math, layout, floats, references
- These have the most overlap with TUHH book — can adapt
- Most valuable chapters for daily use

### Phase 3: Extended Content (chapters 20-25, 40-44, 80-81, 90-95)
- All 26 doctypes, i18n, code, advanced features
- CJK/RTL coverage (unique selling point)
- Presentation/poster/CV chapters

### Phase 4: Automation & Verification (chapters 100-104, 110-111)
- Build system, CI/CD, Lean proofs
- Architecture documentation

### Phase 5: Back Matter & Polish (chapters B0-B4)
- Quick-reference appendices
- Index compilation
- Final proofread

### Estimated Content

| Part | Chapters | Est. Pages |
|---|---|---|
| Front Matter | 3 | 15 |
| Part I: Foundations | 5 | 60 |
| Part II: Document Types | 6 | 150 |
| Part III: Typography | 6 | 120 |
| Part IV: Language | 5 | 100 |
| Part V: Layout | 4 | 60 |
| Part VI: Figures & Tables | 5 | 120 |
| Part VII: References | 4 | 60 |
| Part VIII: Code | 2 | 40 |
| Part IX: Advanced | 6 | 100 |
| Part X: Build & Automation | 5 | 50 |
| Part XI: Verification | 2 | 30 |
| Back Matter | 5 | 40 |
| **Total** | **58 sections** | **~945** |

---

## Writing Conventions

1. **Every command shown with a compilable example** — no bare syntax snippets
2. **Cross-reference doctypes** — "see Chapter 22 for thesis-specific options"
3. **Bilingual glossary** — English + German keys
4. **TikZ diagrams** for architecture, not ASCII art
5. **`minted` code blocks** with language highlighting
6. **`\sym{}` / `\abb{}` for all symbols and abbreviations** (glossary-driven)
7. **`\ctanpackage{}` for all referenced packages**
8. **`\adaptedfrom{}` for any content adapted from external sources**
9. **`\index{}` entries for the back-of-book index**
10. **Lean theorem references** where applicable (e.g., page geometry → `PageGeometry.lean`)

## File Organization

```
examples/manual/
  main.tex                    # Document entry point
  config/
    document-settings.sty     # Manual-specific metadata
    paths.sty                 # Path macros
  content/
    00_frontmatter.tex        # Aggregator
    01_preface.tex
    02_notation.tex
    10_installation.tex
    11_quickstart.tex
    ... (one .tex per chapter)
    B0_appendix_commands.tex
    B1_appendix_options.tex
    ...
    backmatter.tex            # Bibliography + index
  assets/
    images/
      bitmaps/                # PNG/JPG images
      svg/                    # SVG diagrams
  bibliography.bib            # Manual's own .bib
```
