# OmniLaTeX Public API Stability

This document defines the public API surface of OmniLaTeX and its stability guarantees.

## Stability Levels

| Level       | Semver Impact                                  |
|-------------|------------------------------------------------|
| `stable`    | Will not change without a major version bump   |
| `unstable`  | May change in minor or patch versions          |
| `internal`  | Not part of public API; may change at any time |

Internal commands are those prefixed with `\omnilatex@`, `\@`, `__omnilatex`, or `l__omnilatex`. These are never part of the public API.

---

## 1. Class Options

Defined in `omnilatex.cls` via `\DeclareStringOption` / `\DeclareBoolOption`.

| Option            | Type    | Default  | Stability |
|-------------------|---------|----------|-----------|
| `language`        | string  | `english`| stable    |
| `doctype`         | string  | `thesis` | stable    |
| `titlestyle`      | string  | `book`   | stable    |
| `institution`     | string  | `none`   | stable    |
| `censoring`       | bool    | `false`  | stable    |
| `loadGlossaries`  | bool    | `false`  | stable    |
| `todonotes`       | bool    | `false`  | stable    |
| `enablefonts`     | bool    | `false`  | stable    |
| `enablegraphics`  | bool    | `false`  | stable    |
| `enablemath`      | bool    | `true`   | stable    |
| `enabletikz`      | bool    | `true`   | stable    |
| `enableengineering`| bool   | `true`   | stable    |
| `enablecode`      | bool    | `true`   | stable    |
| `enabletables`    | bool    | `true`   | stable    |

### Void Options

| Option | Effect                          | Stability |
|--------|---------------------------------|-----------|
| `a5`   | Set A5 paper, 10pt font size    | stable    |

### Valid `doctype` Values

`book`, `thesis`, `dissertation`, `manual`, `technicalreport`, `standard`, `patent`, `article`, `inlinepaper`, `journal`, `dictionary`, `cv`, `cover-letter`, `poster`, `presentation`, `letter`, `homework`, `exam`, `research-proposal`, `recipe`, `lecture-notes`, `syllabus`, `handout`, `memo`, `white-paper`, `invoice`.

### Valid `titlestyle` Values

`book`, `thesis`, `article`, `simple`, `tuhh`.

---

## 2. User Commands

### 2.1 Document Metadata (`lib/layout/omnilatex-document.sty`)

| Command              | Signature                        | Description                          | Stability |
|----------------------|----------------------------------|--------------------------------------|-----------|
| `\documenttype`      | `{type}`                         | Set document type string             | stable    |
| `\idnumber`          | `{id}`                           | Set student ID number                | stable    |
| `\firstexamniner`    | `{name}`                         | Set first examiner                   | stable    |
| `\secondexamniner`   | `{name}`                         | Set second examiner                  | stable    |
| `\supervisor`        | `{name}`                         | Set supervisor                       | stable    |
| `\signaturefield`    | `[author]`                       | Render signature/date line           | stable    |
| `\documentfontsize`  | `{size}`                         | Set font size (applied via KOMA)     | stable    |
| `\documentlayout`    | `{options}`                      | Pass raw KOMA layout options         | stable    |
| `\documentcolormode` | `{mode}`                         | Set color mode (`dark`/`light`/`color`)| stable |
| `\documentlinespacing`| `{value}`                       | Set line spacing (`single`/`onehalf`/`double`/numeric) | stable |
| `\documentparspacing`| `{value}`                        | Set paragraph spacing (`none`/`half`/`full`/dimen) | stable |
| `\documentitemspacing`| `{value}`                       | Set item spacing (`none`/`compact`/`tight`/`normal`/dimen) | stable |
| `\documentfontmode`  | `{mode}`                         | Set font mode (`serif`/`sans`/`mono`)| stable    |
| `\documentlinkstyle` | `{style}`                        | Set link style (`color`/`plain`)     | stable    |
| `\documentcodestyle` | `{style}`                        | Set minted code style                | unstable  |
| `\setCustomMargins`  | `{left}{right}{top}{bottom}`     | Override margins with explicit dims  | stable    |
| `\iecfeg`            | `{text}`                         | Italicize abbreviations (i.e., e.g.) | stable    |
| `\adaptedfrom`       | (no args)                        | Print "Adapted from" translation     | stable    |
| `\ctanpackage`       | `[url]{name}`                    | Link to CTAN package                 | stable    |
| `\sampletext`        | (no args)                        | Insert pangram text                  | stable    |

### 2.2 Font Setters (`lib/typography/omnilatex-fonts.sty`)

| Command          | Signature          | Description                    | Stability |
|------------------|--------------------|--------------------------------|-----------|
| `\setMainFont`   | `{fontname}`       | Set main (serif) font          | stable    |
| `\setSansFont`   | `{fontname}`       | Set sans-serif font            | stable    |
| `\setMonoFont`   | `[options]{name}`  | Set monospace font             | stable    |
| `\setMathFont`   | `{fontname}`       | Set math font                  | stable    |

### 2.3 Math Commands (`lib/typography/omnilatex-math.sty`)

#### Delimiters

| Command      | Description                     | Stability |
|--------------|---------------------------------|-----------|
| `\parens`    | Parentheses delimiter           | stable    |
| `\brackets`  | Square brackets delimiter       | stable    |
| `\braces`    | Curly braces delimiter          | stable    |
| `\absfmt`    | Absolute value formatting       | stable    |
| `\abs`       | Absolute value (with glossary)  | stable    |

#### Equation Punctuation

| Command      | Description                     | Stability |
|--------------|---------------------------------|-----------|
| `\eqend`     | Period after display equation   | stable    |
| `\eqcomma`   | Comma after display equation    | stable    |

#### Operators and Constants

| Command      | Description                     | Stability |
|--------------|---------------------------------|-----------|
| `\grad`      | Gradient operator (upright)     | stable    |
| `\const`     | "Const." label                  | stable    |
| `\qq`        | Text between equation parts     | stable    |

#### Statistical Notation

| Command          | Description                     | Stability |
|------------------|---------------------------------|-----------|
| `\meanfmt`       | Mean value overbar format       | stable    |
| `\mean`          | Mean value (with glossary)      | stable    |
| `\logmeanfmt`    | Logarithmic mean tilde format   | stable    |
| `\logmean`       | Logarithmic mean (with glossary)| stable    |

#### Physical Notation

| Command              | Description                     | Stability |
|----------------------|---------------------------------|-----------|
| `\flowfmt`           | Dotted flow symbol format       | stable    |
| `\flow`              | Flow (with glossary)            | stable    |
| `\differencefmt`     | Delta symbol format             | stable    |
| `\difference`        | Difference (with glossary)      | stable    |
| `\nablaoperatorfmt`  | Nabla operator format           | stable    |
| `\nablaoperator`     | Nabla operator (with glossary)  | stable    |
| `\heatexentryfmt`    | Heat exchanger entry prime      | stable    |
| `\heatexentry`       | Heat exchanger entry (glossary) | stable    |
| `\heatexexitfmt`     | Heat exchanger exit double-prime| stable    |
| `\heatexexit`        | Heat exchanger exit (glossary)  | stable    |
| `\vectfmt`           | Bold vector format              | stable    |
| `\vect`              | Vector (with glossary)          | stable    |

#### Derivatives

| Command      | Signature             | Description                          | Stability |
|--------------|-----------------------|--------------------------------------|-----------|
| `\deriv`     | `[degree]{symbol}`    | Ordinary derivative                  | stable    |
| `\deriv*`    | `[degree]{symbol}`    | Partial derivative                    | stable    |
| `\fracderiv` | `[degree]{num}{den}`  | Derivative fraction                   | stable    |
| `\fracderiv*`| `[degree]{num}{den}`  | Partial derivative fraction           | stable    |
| `\timederiv` | `[degree]{symbol}`    | Time derivative                       | stable    |
| `\timederiv*`| `[degree]{symbol}`    | Partial time derivative               | stable    |
| `\posderiv`  | `[degree]{symbol}`    | Positional derivative                 | stable    |
| `\posderiv*` | `[degree]{symbol}`    | Partial positional derivative          | stable    |

#### Chemistry and Units

| Command          | Description                     | Stability |
|------------------|---------------------------------|-----------|
| `\ch`            | Chemical formula (chemmacros)   | stable    |
| `\chcpd`         | Chemical compound               | stable    |
| `\chemamount`    | Amount with unit and compound   | stable    |
| `\temperaturepair`| Temperature range              | stable    |
| `\circlednum`    | Circled number                  | stable    |
| `\symbolplaceholder`| Dotted square placeholder     | stable    |

#### Custom SI Units

| Unit macro              | Value              | Stability |
|-------------------------|--------------------|-----------|
| `\volpercent`           | Vol.-%             | stable    |
| `\watthour`             | Wh                 | stable    |
| `\annum`                | a                  | stable    |
| `\atmosphere`           | atm                | stable    |
| `\partspermillion`      | ppm                | stable    |
| `\bar`                  | bar                | stable    |
| `\relhumidity`          | % RH / % r.F.      | stable    |

### 2.4 Float Commands (`lib/layout/omnilatex-floats.sty`)

| Command            | Signature                              | Description                       | Stability |
|--------------------|----------------------------------------|-----------------------------------|-----------|
| `\omnlFigure`      | `[options]{content}`                   | Figure float with keyval options  | stable    |
| `\omnlTable`       | `[options]{content}`                   | Table float with keyval options   | stable    |
| `\omnlFloatCaption`| (no args)                              | Typeset caption at current position| stable   |
| `\omnlFloatNote`   | `{text}`                               | Footnote text below float         | stable    |
| `\omnlFloatFootmark`| `[num]`                               | Footnote mark in float            | stable    |
| `\omnlFloatFoottext`| `[num]{text}`                         | Footnote text for float           | stable    |

#### Float Keyval Options

Available in `\omnlFigure` and `\omnlTable`:

| Key                | Values                         | Default   | Stability |
|--------------------|--------------------------------|-----------|-----------|
| `placement`        | float placement specifiers     | `tbp`     | stable    |
| `caption`          | text                           | (none)    | stable    |
| `short-caption`    | text                           | (none)    | stable    |
| `label`            | label name                     | (none)    | stable    |
| `footnote`         | text                           | (none)    | stable    |
| `caption-width`    | dimension                      | (auto)    | stable    |
| `align`            | `center`/`left`/`right`        | `center`  | stable    |
| `caption-position` | `top`/`bottom`/`manual`        | `bottom` for figure, `top` for table | stable |

### 2.5 Box Commands (`lib/layout/omnilatex-boxes.sty`)

| Command               | Description                           | Stability |
|-----------------------|---------------------------------------|-----------|
| `\GitVerificationBox` | Render git verification link box      | unstable  |

### 2.6 Utility Commands (`lib/utils/omnilatex-utils.sty`)

| Command      | Signature | Description              | Stability |
|--------------|-----------|--------------------------|-----------|
| `\fakeverb`  | `{text}`  | Detokenized verbatim text| stable    |

### 2.7 Typesetting Commands (`lib/typography/omnilatex-typesetting.sty`)

No user-facing commands are defined. This module configures packages (`extdash`, `microtype`, `ragged2e`, `csquotes`). The `\enquote` command is provided by the `csquotes` package, not by OmniLaTeX directly.

---

## 3. Environments

### 3.1 Float Environments (`lib/layout/omnilatex-floats.sty`)

| Environment      | Signature  | Description                        | Stability |
|------------------|------------|------------------------------------|-----------|
| `omnlFloatRow`   | `[cols]`   | Minipage tabular row for subfloats | stable    |

Default `[cols]` is `2`.

### 3.2 Box Environments (`lib/layout/omnilatex-boxes.sty`)

| Environment | Arguments        | Description                        | Stability |
|-------------|------------------|------------------------------------|-----------|
| `example`   | `[label]{title}` | Numbered, breakable tcolorbox      | stable    |

### 3.3 Chemistry Environments (`lib/typography/omnilatex-math.sty`)

| Environment           | Description                        | Stability |
|-----------------------|------------------------------------|-----------|
| `reactionsgather`     | Numbered reaction gather env       | stable    |
| `reactionsgather*`    | Unnumbered reaction gather env     | stable    |

### 3.4 Bibliography Environments (`lib/references/omnilatex-biblio.sty`)

| Environment  | Description                        | Stability |
|--------------|------------------------------------|-----------|
| `bibnonum`   | Bibliography without entry numbers | stable    |

---

## 4. Deprecation Policy

### Process

1. **Warning phase**: Deprecated commands emit a `\PackageWarning` on use. The command continues to function as before.
2. **Grace period**: Deprecated features remain functional for at least **two minor releases** (e.g., deprecated in v1.x, removable in v1.(x+2)).
3. **Removal**: After the grace period, the command is removed or renamed. Removal occurs only at a **major version boundary** when feasible.
4. **Documentation**: Every deprecation is recorded in the CHANGELOG with the target removal version.

### Guidelines

- A `\newcommand` that is removed will first be aliased to its replacement via `\renewcommand` with a deprecation warning.
- No `internal` command will ever go through deprecation; it may be removed or renamed at any time.
- The `unstable` marker indicates a command that is still being designed. Unstable commands may change signature or behavior in any release without a deprecation warning, but changes will be noted in the CHANGELOG.

### User Action

When a deprecation warning appears, migrate to the recommended replacement before the stated removal version. Suppressing the warning is possible but not recommended.
