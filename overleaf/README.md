# OmniLaTeX

A modular, engineering-grade LaTeX document class for academic and professional documents. Built on LuaLaTeX + KOMA-Script with 55 doctype aliases, 16 document profiles, 21 modules, and pluggable institution configs.

## Quick Start

1. Set the compiler to **LuaLaTeX**: click the **Menu** button (top-left), then set **Compiler** to **LuaLaTeX**
2. Click **Recompile**
3. Edit `main.tex` to customize your document

That's it. Everything else is handled by OmniLaTeX.

## What is OmniLaTeX?

OmniLaTeX is a single `\documentclass` that adapts to whatever you're writing — thesis, article, CV, patent, report, or book. Instead of hunting for a different template for each document type, you switch by changing one option:

```latex
\documentclass[doctype=thesis]{omnilatex}
```

**Why OmniLaTeX over other templates?**

| | OmniLaTeX | Typical template |
|---|---|---|
| Document types | 55 aliases, 16 profiles | 1–3 |
| Base classes | 3 KOMA-Script classes | 1 |
| Test coverage | 239 test cases | 0 |
| Font fallbacks | Graceful degradation | Crash or silent substitution |
| Institution configs | Pluggable | Hardcoded |

## Document Types

All 16 profiles are available via `doctype=`:

| Profile | Base Class | Description |
|---|---|---|
| `thesis` | scrbook | Academic thesis or dissertation |
| `dissertation` | scrbook | Doctoral dissertation |
| `book` | scrbook | Book or monograph |
| `dictionary` | scrbook | Dictionary or lexicon |
| `technicalreport` | scrreprt | Technical or research report |
| `report` | scrreprt | General report |
| `standard` | scrreprt | Standards document |
| `patent` | scrreprt | Patent application |
| `manual` | scrreprt | Manual, guide, or handbook |
| `article` | scrartcl | Academic article or paper |
| `journal` | scrartcl | Journal article |
| `inlinepaper` | scrartcl | Inline research paper |
| `cv` | scrartcl | Curriculum vitae / resume |
| `cover-letter` | scrartcl | Cover letter |
| `letter` | scrartcl | Formal letter |
| `poster` | scrartcl | Conference poster |
| `presentation` | scrartcl | Presentation slides |

Each profile has aliases (e.g., `paper`, `papers`, `article`, `articles` all resolve to the `article` profile).

## Customization

### Change Document Type

Edit the `\documentclass` line in `main.tex`:

```latex
\documentclass[doctype=thesis,language=english]{omnilatex}
```

### Change Language

Set the `language` option. Supported: `english`, `german`, `french`, `spanish`, `portuguese`, `italian`, `dutch`, `russian`, `chinese`, `japanese`, `korean`, `arabic`.

```latex
\documentclass[doctype=article,language=german]{omnilatex}
```

### Set Institution

Add the `institution` option to apply institutional branding and formatting:

```latex
\documentclass[doctype=thesis,institution=tuhh,language=english]{omnilatex}
```

Available institutions: `tuhh`, `tum`, `eth`, `mit`, `stanford`, `cambridge`, `tudelft`, `generic`.

### Disable Modules You Don't Need

Speed up compilation by disabling unused features:

```latex
\documentclass[
  doctype=article,
  enablecode=false,       % No code listings
  enabletikz=false,       % No TikZ graphics
  enableengineering=false,% No engineering diagrams
  enablemath=false,       % No math support
]{omnilatex}
```

## Features

- **Math** — unicode-math with Libertinus Math font
- **Code listings** — syntax highlighting via minted
- **Engineering diagrams** — 1,000+ lines of TikZ: thermodynamics, P&ID, flowcharts
- **Bibliography** — biblatex with Biber backend
- **Glossaries** — bib2gls for acronyms and terms
- **Tables** — booktabs + tabularx
- **CJK support** — Chinese, Japanese, Korean with automatic font detection

## Full Documentation

- **GitHub**: https://github.com/WyattAu/OmniLaTeX-template
- **Examples**: 24 example templates at [examples/](https://github.com/WyattAu/OmniLaTeX-template/tree/main/examples)
- **License**: Apache-2.0
