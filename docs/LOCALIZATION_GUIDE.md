---
title: LOCALIZATION GUIDE
---
# OmniLaTeX Localization Guide

## Overview

OmniLaTeX internationalization is built on two layers:

1. **Polyglossia** -- handles standard language rules (hyphenation, date formatting, caption names) via the `polyglossia` package. Configured in `lib/language/omnilatex-i18n.sty`.
2. **Custom translation keys** -- OmniLaTeX-specific UI strings (47 keys per language) registered via the `translations` package with `\DeclareTranslation{<language>}{<key>}{<value>}`.

The main document language is set at `\documentclass` time (e.g., `language=german`) and propagated via `\omnilatex@language`. All supported languages are registered as "other" languages in `\setotherlanguages{...}` (line 36 of `omnilatex-i18n.sty`), enabling inline language switching with `\begin{<language>}...\end{<language>}`.

**Currently supported languages:** english, german, ngerman, french, spanish, italian, portuguese, russian, dutch, polish, czech, greek, turkish, simplifiedchinese, traditionalchinese, japanese, korean, arabic, hebrew, vietnamese, hindi, swedish, finnish, danish, norsk.

**Source file:** `lib/language/omnilatex-i18n.sty`

---

## Translation Key System

Each language defines up to 47 translation keys using `\DeclareTranslation`. Keys are retrieved at compile time with `\GetTranslation{<key>}`. The `translations` package falls back to the default language if a key is missing.

Keys are organized by functional area:

| Area | Keys |
|---|---|
| Title page | `First`, `Second`, `Examiner`, `FirstExaminer`, `SecondExaminer`, `Supervisor` |
| Task page | `PlaceDate`, `Topic`, `Task`, `For` |
| Authorship declaration | `AuthorshipDeclTitle`, `AuthorshipDeclText`, `author`, `authorArticle` |
| Colophon | `CompiledOn`, `LatexClass`, `Generator` |
| Glossary | `Gloss`, `Greek`, `Roman`, `Other`, `Terms`, `Names`, `Acronyms`, `Subscripts`, `Superscripts`, `SubSuperTitle` |
| Content lists | `IllustrativeElements`, `ListOfIllustrations`, `Listing`, `Listings`, `ListOfListings`, `ListOfExamples`, `Example`, `Examples` |
| Tables | `Contfoot`, `Conthead` |
| Bibliography | `FurtherReadingTitle`, `FurtherReadingText` |
| Math/science | `Constant`, `Unit`, `PhysicalQuantity` |
| Attribution | `AdaptedFrom`, `CensorNotice` |
| Cross-references | `Reaction`, `Reactions` |
| Layout | `BlankPage` |

---

## Adding a New Language

### Step 1: Register with polyglossia

Add the language identifier to `\setotherlanguages` in `lib/language/omnilatex-i18n.sty` (line 36):

```latex
\setotherlanguages{german,ngerman,english,...,yourlanguage}
```

The language name must match a polyglossia-recognized identifier. See the [polyglossia documentation](https://ctan.org/pkg/polyglossia) for the full list.

### Step 2: Add translation keys

Add a new section in `lib/language/omnilatex-i18n.sty` with all 47 keys:

```latex
% YourLanguage translations
\DeclareTranslation{yourlanguage}{First}{...}
\DeclareTranslation{yourlanguage}{Second}{...}
\DeclareTranslation{yourlanguage}{Examiner}{...}
% ... all 47 keys (see reference table below)
```

Copy the English section as a template and translate each value. Every key must be present; missing keys will fall back to the default language at compile time, producing inconsistent output.

### Step 3: Font configuration (if required)

For CJK languages, also update `lib/language/omnilatex-cjk.sty` (see CJK section below).

For RTL languages, also update `lib/language/omnilatex-rtl.sty` (see RTL section below).

For languages with special script requirements (Devanagari, Thai, etc.), add a font configuration block using fontspec's `\newfontfamily` with the appropriate `Script=` option.

### Step 4: Test compilation

```bash
# Compile with the new language as the primary language
latexmk -lualatex -e '$newlanguage = "yourlanguage"'
# Or set in main.tex: \documentclass[language=yourlanguage]{omnilatex}
latexmk -lualatex main.tex
```

Verify:

- All UI strings render in the target language
- No `translations` warnings about missing keys
- Hyphenation patterns load correctly
- Fonts display the script without substitution warnings

---

## Translation Guidelines

### Conciseness

These are UI labels and table headers, not prose. Keep translations short. Examples:

| Key | English | Good translation | Bad translation |
|---|---|---|---|
| `Unit` | Unit | Einh. | Masseinheit des physikalischen Wertes |
| `Gloss` | Glossary | Glossar | Verzeichnis der Fachbegriffe und Abkuerzungen |
| `Constant` | const | konst | Konstanter Wert |

### Formal register

OmniLaTeX targets academic documents (theses, papers, reports). Use formal language appropriate for university submission. Avoid colloquialisms.

### Pluralization

Some keys have singular/plural pairs. Translate both consistently:

- `Example` / `Examples`
- `Listing` / `Listings`
- `Reaction` / `Reactions`
- `First` / `Second`

### Consistent terminology

Maintain the same term for the same concept across all keys. If you translate `Examiner` as "Pruefer", use "Pruefer" in both `Examiner` and `FirstExaminer`/`SecondExaminer`, not a synonym.

### Key naming conventions

- **PascalCase** for multi-word keys: `AuthorshipDeclTitle`, `ListOfIllustrations`, `PhysicalQuantity`
- **Singular/plural pairs** differ only by trailing `s`: `Example`/`Examples`
- **Lowercase** for grammatical fragments: `author`, `authorArticle`
- Keys containing `Text` hold multi-sentence blocks; keys without hold short labels

### Long-form keys

`AuthorshipDeclText` and `FurtherReadingText` are multi-sentence paragraphs. Within these, you can use `\GetTranslation{authorArticle}` and `\@author{}` / `\@documenttype{}` macros. Maintain the legal/formal tone of the original.

### The `translations` package limitation

The `translations` package does not include language definition files for CJK languages (simplifiedchinese, traditionalchinese, japanese, korean). Polyglossia handles standard captions natively, but OmniLaTeX-specific keys (Gloss, BlankPage, etc.) cannot be registered via `\DeclareTranslation` for these languages. Users needing custom CJK translations must add `\DeclareTranslation` commands in their preamble.

---

## RTL Language Support

RTL support is handled by `lib/language/omnilatex-rtl.sty`, loaded automatically when the document language is `arabic`, `persian`, or `hebrew`.

### What the RTL module provides

- **Bidirectional text** via the `bidi` package
- **Mirrored page layout** -- binding edge moves to the right (inner) side
- **Script-specific fonts** with fallback chains:
  - Arabic: Amiri (fallback: Noto Naskh Arabic)
  - Hebrew: David CLM (fallback: Frank Ruehl CLM)
- **Arabic-Indic numerals** -- opt-in with `\arabicindictrue`
- **LTR math mode** -- math expressions remain left-to-right inside RTL paragraphs
- **Title page font override** -- KOMA-Script title fonts are replaced with script-specific fonts

### Font setter commands

```latex
\setArabicFont{Scheherazade}       % Change Arabic font
\setArabicBoldFont{Scheherazade Bold}
\setHebrewFont{Ezra SIL}           % Change Hebrew font
\setHebrewBoldFont{Ezra SIL Bold}
```

These must be called in the preamble, before `\begin{document}`.

### Inline direction overrides

```latex
\LTRinline{English text inside RTL paragraph}
\RTLinline{Arabic text inside LTR paragraph}
```

### Adding a new RTL language

1. Add the language to `\setotherlanguages` in `omnilatex-i18n.sty`
2. Add a new setup command in `omnilatex-rtl.sty` following the pattern of `\omnilatex@setup@arabic`
3. Add font configuration (Arabic-script languages can reuse `\omnilatex@apply@arabicfonts`)
4. Add the detection line in the auto-detection block at the bottom of `omnilatex-rtl.sty`
5. Add title page font override in the `\AtBeginDocument` block

---

## CJK Language Support

CJK support is handled by `lib/language/omnilatex-cjk.sty`, loaded automatically when the document language is `simplifiedchinese`, `traditionalchinese`, `japanese`, or `korean`.

### What the CJK module provides

- **Core engine**: `luatexja` + `luatexja-fontspec` + `luatexja-ruby`
- **Font families** per script variant (SC, TC, JP, KR) using Noto CJK fonts
- **Line breaking**: CJK line break rules via luatexja
- **Inter-character spacing**: configurable CJK-Latin gap (default 0.25em)
- **Ruby annotations**: `\ruby{base}{annotation}`, `\furigana{base}{annotation}`, `\pinyin{base}{annotation}`
- **Vertical writing**: `\begin{vertical}...\end{vertical}` environment

### Font configuration

```latex
% Per-script presets (called automatically on language detection)
\setCJKScript{sc}   % Simplified Chinese: Noto Serif/Sans CJK SC
\setCJKScript{tc}   % Traditional Chinese: Noto Serif/Sans CJK TC
\setCJKScript{jp}   % Japanese: Noto Serif/Sans CJK JP
\setCJKScript{kr}   % Korean: Noto Serif/Sans CJK KR

% Manual overrides
\setCJKMainFont{Source Han Serif SC}
\setCJKSansFont{Source Han Sans SC}
\setCJKMonoFont{Source Han Mono SC}
```

### Inter-character spacing

```latex
\setCJKLatinSpacing{0.3em}   % Adjust CJK-Latin gap (default: 0.25em)
```

### The `translations` package gap

As noted in `omnilatex-i18n.sty` (lines 56-62), the `translations` package does not define language files for CJK languages. Polyglossia provides native caption support (TOC, figure, table names), but OmniLaTeX custom keys will not work with `\DeclareTranslation{simplifiedchinese}{...}`. This is a known limitation. Workaround:

```latex
% In preamble, after language is loaded:
\addto\captionssimplifiedchinese{
  \renewcommand{\glossname}{...}
}
```

Or define a thin wrapper that maps polyglossia captions to the OmniLaTeX keys.

---

## Testing

### Compilation test

```bash
# Set the target language and compile
latexmk -lualatex -interaction=nonstopmode main.tex
```

Check the log for:

- `Package translations Warning` -- indicates missing translation keys
- `fontspec Warning` -- font substitution (expected for CJK/RTL if fonts are missing)
- `Polyglossia` errors -- unsupported language or missing hyphenation patterns

### Key coverage verification

Grep for the language identifier in `omnilatex-i18n.sty` and count keys:

```bash
grep -c '\\DeclareTranslation{yourlanguage}' lib/language/omnilatex-i18n.sty
```

The count must be 47 (or 42 if excluding the 5 CJK-incompatible keys noted above).

### Visual verification

Compile the full document and check:

1. Title page labels (Supervisor, Examiner, etc.)
2. Table of contents heading and list names
3. Glossary section headers
4. Blank page notice
5. Declaration of authorship text
6. Colophon text
7. Table continuation headers (`Contfoot`/`Conthead`)

---

## Key Reference Table

Complete list of all 47 translation keys with English defaults. Source: `lib/language/omnilatex-i18n.sty`.

### Title Page

| # | Key | English Default |
|---|---|---|
| 1 | `First` | `\nth{1}` |
| 2 | `Second` | `\nth{2}` |
| 3 | `Examiner` | Examiner |
| 4 | `FirstExaminer` | Examiner |
| 5 | `SecondExaminer` | Examiner |
| 6 | `Supervisor` | Supervisor |

### Task Page

| # | Key | English Default |
|---|---|---|
| 7 | `PlaceDate` | Place \& Date |
| 8 | `Topic` | Topic |
| 9 | `Task` | Task |
| 10 | `For` | For |

### Authorship Declaration

| # | Key | English Default |
|---|---|---|
| 11 | `AuthorshipDeclTitle` | Declaration of Authorship |
| 12 | `AuthorshipDeclText` | I, \@author{}, hereby declare to be the sole, independent author of the \@documenttype{} submitted here. No other than the cited references have been used. Any content directly or indirectly obtained from external sources has been marked up as such. This thesis has neither been submitted to a second examination authority nor been published. |
| 13 | `author` | author |
| 14 | `authorArticle` | the author |

### Colophon

| # | Key | English Default |
|---|---|---|
| 15 | `CompiledOn` | Compiled on |
| 16 | `LatexClass` | Class |
| 17 | `Generator` | Generated by |

### Censor / Disclaimer

| # | Key | English Default |
|---|---|---|
| 18 | `CensorNotice` | This passage has been redacted. |

### Glossary

| # | Key | English Default |
|---|---|---|
| 19 | `Gloss` | Glossary |
| 20 | `Greek` | Greek |
| 21 | `Roman` | Roman |
| 22 | `Other` | Other |
| 23 | `Terms` | Terms |
| 24 | `Names` | Names |
| 25 | `Acronyms` | Acronyms |
| 26 | `Subscripts` | Subscripts |
| 27 | `Superscripts` | Superscripts |
| 28 | `SubSuperTitle` | Sub- and Superscripts |

### Content Lists

| # | Key | English Default |
|---|---|---|
| 29 | `IllustrativeElements` | Illustrative Elements |
| 30 | `ListOfIllustrations` | List of Illustrations |
| 31 | `Listing` | Code Listing |
| 32 | `Listings` | Code Listings |
| 33 | `ListOfListings` | List of Code |
| 34 | `ListOfExamples` | List of Examples |
| 35 | `Example` | Example |
| 36 | `Examples` | Examples |

### Table Continuation

| # | Key | English Default |
|---|---|---|
| 37 | `Contfoot` | Continued on next page |
| 38 | `Conthead` |  (Continued) |

### Bibliography

| # | Key | English Default |
|---|---|---|
| 39 | `FurtherReadingTitle` | Further Reading |
| 40 | `FurtherReadingText` | The following references were used in this work but not cited in the text body; they are provided here as\-/is. |

### Math / Scientific Notation

| # | Key | English Default |
|---|---|---|
| 41 | `Constant` | const |
| 42 | `Unit` | Unit |
| 43 | `PhysicalQuantity` | Physical Quantity |

### Attribution

| # | Key | English Default |
|---|---|---|
| 44 | `AdaptedFrom` | Adapted from |

### Cross-References

| # | Key | English Default |
|---|---|---|
| 45 | `Reaction` | Reaction |
| 46 | `Reactions` | Reactions |

### Layout

| # | Key | English Default |
|---|---|---|
| 47 | `BlankPage` | Rest of this page intentionally left blank. |
