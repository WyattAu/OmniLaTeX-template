# OmniLaTeX API Reference

Auto-generated reference for all public commands defined in OmniLaTeX `.sty` files.
Source: v2.4.1 (2026/06/06)

---

## Title Page Commands

These commands configure the document title page metadata. Use them in your
preamble or in `config/omnilatex-document-settings.sty`.

### `\title{<title>}`

Sets the document title displayed on the title page and in PDF metadata.

- **Parameters:** `#1` — title text (may contain LaTeX formatting)
- **Source:** `config/omnilatex-document-settings.sty`
- **Example:**
  ```latex
  \title{My Master Thesis Title}
  ```

### `\author{<name>}`

Sets the document author displayed on the title page.

- **Parameters:** `#1` — author name(s), separated by commas for multiple authors
- **Source:** `config/omnilatex-document-settings.sty`
- **Example:**
  ```latex
  \author{Jane Doe, John Smith}
  ```

### `\date{<date>}`

Sets the date displayed on the title page. Accepts arbitrary LaTeX content.

- **Parameters:** `#1` — date expression (e.g., `\today`, `\DTMdate{2026-01-15}`)
- **Source:** `config/omnilatex-document-settings.sty`
- **Example:**
  ```latex
  \date{\DTMtoday{}}
  ```

### `\subtitle{<text>}`

Sets the subtitle or abstract shown on the article title page.

- **Parameters:** `#1` — subtitle or abstract text
- **Source:** `config/document-types/omnilatex-doctype-article.sty`
- **Example:**
  ```latex
  \subtitle{A comprehensive study of template architectures}
  ```

### `\affiliation{<text>}`

Sets the author affiliation displayed on the article title page.

- **Parameters:** `#1` — affiliation text (may include LaTeX formatting)
- **Source:** `config/document-types/omnilatex-doctype-article.sty`
- **Example:**
  ```latex
  \affiliation{Department of Computer Science, University of Example}
  ```

### `\keywords{<keywords>}`

Sets keywords for the article title page metadata block.

- **Parameters:** `#1` — comma-separated keyword list
- **Source:** `config/document-types/omnilatex-doctype-article.sty`
- **Example:**
  ```latex
  \keywords{latex, template, academic writing}
  ```

### `\doi{<doi>}`

Sets the DOI identifier for the article.

- **Parameters:** `#1` — DOI string (e.g., `10.1234/example.5678`)
- **Source:** `config/document-types/omnilatex-doctype-article.sty`
- **Example:**
  ```latex
  \doi{10.1234/example.5678}
  ```

### `\contact{<email>}`

Sets the contact email displayed on the article title page.

- **Parameters:** `#1` — contact email or author info
- **Source:** `config/document-types/omnilatex-doctype-article.sty`
- **Example:**
  ```latex
  \contact{jane.doe@university.edu}
  ```

---

## Thesis-Specific Commands

These commands configure the thesis title page. They are defined in the
thesis document type profile and are only relevant for thesis documents.

### `\thesisinstitution{<name>}`

Sets the institution name (e.g., university) for the thesis title page.

- **Parameters:** `#1` — institution name
- **Default:** `University`
- **Source:** `config/document-types/omnilatex-doctype-thesis.sty`
- **Example:**
  ```latex
  \thesisinstitution{Hamburg University of Technology}
  ```

### `\thesisdepartment{<name>}`

Sets the department name for the thesis title page.

- **Parameters:** `#1` — department name
- **Default:** `Department`
- **Source:** `config/document-types/omnilatex-doctype-thesis.sty`
- **Example:**
  ```latex
  \thesisdepartment{Institute of Technical Thermodynamics}
  ```

### `\thesisdegree{<degree>}`

Sets the degree being pursued (e.g., "Master of Science").

- **Parameters:** `#1` — degree name
- **Default:** `Master of Science`
- **Source:** `config/document-types/omnilatex-doctype-thesis.sty`
- **Example:**
  ```latex
  \thesisdegree{Bachelor of Science}
  ```

### `\thesisadvisor{<name>}`

Sets the thesis advisor name displayed on the title page.

- **Parameters:** `#1` — advisor name
- **Default:** `Advisor Name`
- **Source:** `config/document-types/omnilatex-doctype-thesis.sty`
- **Example:**
  ```latex
  \thesisadvisor{Prof. Dr.-Ing. Jane Doe}
  ```

### `\thesiscommittee{<members>}`

Sets the committee members listed on the thesis title page.

- **Parameters:** `#1` — comma-separated list of committee member names
- **Default:** `Committee Member A, Committee Member B`
- **Source:** `config/document-types/omnilatex-doctype-thesis.sty`
- **Example:**
  ```latex
  \thesiscommittee{Prof. Dr.-Ing. A. Smith, Prof. Dr. B. Jones}
  ```

### `\defensedate{<date>}`

Sets the defense date displayed on the thesis title page.

- **Parameters:** `#1` — date string or expression
- **Default:** `\today`
- **Source:** `config/document-types/omnilatex-doctype-thesis.sty`
- **Example:**
  ```latex
  \defensedate{\DTMdate{2026-03-15}}
  ```

### `\thesislocation{<location>}`

Sets the thesis location (city, country) displayed on the title page.

- **Parameters:** `#1` — location string
- **Default:** `City, Country`
- **Source:** `config/document-types/omnilatex-doctype-thesis.sty`
- **Example:**
  ```latex
  \thesislocation{Hamburg, Germany}
  ```

---

## Document Examiner and Supervisor Commands

These commands configure examiner and supervisor metadata for the title page.
Defined in the core document module.

### `\firstexaminer{<name>}`

Sets the name of the first examiner.

- **Parameters:** `#1` — examiner name
- **Default:** `Prof. Dr. Jane Doe`
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \firstexaminer{Prof. Dr.-Ing. Arne Speerforck}
  ```

### `\secondexaminer{<name>}`

Sets the name of the second examiner.

- **Parameters:** `#1` — examiner name
- **Default:** `Prof. Dr. Foo Bar`
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \secondexaminer{Prof. Dr.-Ing. Foo Bar}
  ```

### `\supervisor{<name>}`

Sets the supervisor name.

- **Parameters:** `#1` — supervisor name
- **Default:** `John Doe, M.Sc.`
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \supervisor{John Doe, M.Sc.}
  ```

### `\idnumber{<number>}`

Sets the student ID or enrolment number.

- **Parameters:** `#1` — ID number
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \idnumber{12345678}
  ```

---

## Document Type and Layout Commands

Commands for controlling document type, font size, layout, spacing, and
general formatting. Defined in the document module and document settings.

### `\documenttype{<type>}`

Sets the document type label (e.g., "Bachelor Thesis", "Research Article").

- **Parameters:** `#1` — document type string
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \documenttype{Master Thesis}
  ```

### `\documentfontsize{<size>}`

Sets the base document font size. Accepts standard LaTeX sizes.

- **Parameters:** `#1` — font size (e.g., `10pt`, `11pt`, `12pt`)
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \documentfontsize{12pt}
  ```

### `\documentlayout{<options>}`

Passes KOMA-Script typearea options for page layout control.

- **Parameters:** `#1` — KOMA option string (e.g., `DIV=12`)
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \documentlayout{DIV=12,headinclude=true}
  ```

### `\setCustomMargins{<left>}{<right>}{<top>}{<bottom>}`

Overrides KOMA typearea margins with explicit values. Call after
`\begin{document}` for reliable results.

- **Parameters:** `#1` left, `#2` right, `#3` top, `#4` bottom (dimension strings)
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \setCustomMargins{25mm}{25mm}{30mm}{25mm}
  ```

### `\documentlinespacing{<mode>}`

Sets the document line spacing mode.

- **Parameters:** `#1` — `single`, `onehalf`, `double`, or a numeric factor
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \documentlinespacing{onehalf}
  ```

### `\documentparspacing{<mode>}`

Sets the paragraph spacing mode.

- **Parameters:** `#1` — `none`, `half`, `full`, or a dimension
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \documentparspacing{half}
  ```

### `\documentitemspacing{<mode>}`

Sets the list item spacing mode.

- **Parameters:** `#1` — `none`, `compact`, `tight`, `normal`, or a dimension
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \documentitemspacing{compact}
  ```

### `\documentfontmode{<mode>}`

Sets the default text font family for the document.

- **Parameters:** `#1` — `serif`, `sans`, or `mono`
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \documentfontmode{sans}
  ```

### `\documentcolormode{<mode>}`

Sets the document color/link mode.

- **Parameters:** `#1` — `color`, `dark`, `light`, or `bw`
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \documentcolormode{color}
  ```

### `\documentlinkstyle{<style>}`

Sets the hyperlink appearance style.

- **Parameters:** `#1` — `color`, `plain`, or `black`
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \documentlinkstyle{color}
  ```

### `\documentcodestyle{<style>}`

Sets the code listing highlight style (requires minted).

- **Parameters:** `#1` — `color`, `bw`, or a Pygments style name
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \documentcodestyle{color}
  ```

---

## Font Override Commands

Commands for overriding the default font families. Use in the preamble
after `\documentclass` but before `\begin{document}`.

### `\setMainFont{<font-name>}`

Overrides the default main serif font.

- **Parameters:** `#1` — installed font name
- **Default:** Libertinus Serif
- **Source:** `lib/typography/omnilatex-fonts.sty`
- **Example:**
  ```latex
  \setMainFont{TeX Gyre Termes}
  ```

### `\setSansFont{<font-name>}`

Overrides the default sans-serif font.

- **Parameters:** `#1` — installed font name
- **Default:** Atkinson Hyperlegible Next (fallback: Libertinus Sans)
- **Source:** `lib/typography/omnilatex-fonts.sty`
- **Example:**
  ```latex
  \setSansFont{Fira Sans}
  ```

### `\setMonoFont[<options>]{<font-name>}`

Overrides the default monospace font. Optional argument passes fontspec options.

- **Parameters:** `#1` [optional] fontspec options, `#2` — font name
- **Default:** Monaspace Neon (fallback: Latin Modern Mono)
- **Source:** `lib/typography/omnilatex-fonts.sty`
- **Example:**
  ```latex
  \setMonoFont[Scale=MatchLowercase]{Fira Code}
  ```

### `\setMathFont{<font-name>}`

Overrides the default math font.

- **Parameters:** `#1` — installed OpenType math font name
- **Default:** Libertinus Math
- **Source:** `lib/typography/omnilatex-fonts.sty`
- **Example:**
  ```latex
  \setMathFont{TeX Gyre Termes Math}
  ```

---

## Color Theme Commands

Commands for controlling the document color theme. Defined in the
themes module.

### `\usetheme{<theme-name>}`

Applies a complete color theme to the document.

- **Parameters:** `#1` — theme name: `default`, `midnight`, `forest`, `rose`, `sepia`, `monochrome`
- **Source:** `lib/utils/omnilatex-themes.sty`
- **Example:**
  ```latex
  \usetheme{midnight}
  ```

### `\darkmode`

Switches the document to dark mode using the current theme's dark variant.

- **Parameters:** none
- **Source:** `lib/utils/omnilatex-themes.sty`
- **Example:**
  ```latex
  \darkmode
  ```

### `\lightmode`

Switches the document to light mode (restores the current theme's light variant).

- **Parameters:** none
- **Source:** `lib/utils/omnilatex-themes.sty`
- **Example:**
  ```latex
  \lightmode
  ```

### `\setthemecolor{<slot>}{<color>}`

Overrides a single color slot in the current theme.

- **Parameters:** `#1` — slot name (`bg`, `fg`, `heading`, `body`, `accent`, `blockbg`,
  `blockframe`, `link`, `rule`, `codebg`, `footernote`), `#2` — xcolor expression
- **Source:** `lib/utils/omnilatex-themes.sty`
- **Example:**
  ```latex
  \setthemecolor{accent}{blue!60!black}
  ```

---

## Bibliography Commands

Commands for managing bibliography resources and citation styles.
Bibliography management is powered by biblatex (biber backend).

### `\addbibresource{<file>}`

Adds a `.bib` file as a bibliography resource. Standard biblatex command.

- **Parameters:** `#1` — path to `.bib` file
- **Source:** biblatex (loaded by `lib/references/omnilatex-biblio.sty`)
- **Example:**
  ```latex
  \addbibresource{references.bib}
  \addbibresource{secondary.bib}
  ```

### `\printbibliography[<options>]`

Prints the bibliography at the current location. Standard biblatex command.

- **Parameters:** `[optional]` — biblatex options (e.g., `heading=bibintoc`, `title={References}`)
- **Source:** biblatex (loaded by `lib/references/omnilatex-biblio.sty`)
- **Example:**
  ```latex
  \printbibliography[heading=bibintoc,title={References}]
  ```

### `\citationstyle{<style>}`

Switches the citation and bibliography formatting style. Must be called
before `\begin{document}`.

- **Parameters:** `#1` — style name: `ieee`, `acm`, `apa`, `chicago`, `nature`, `science`,
  `harvard`, `vancouver`, `mla`, `turabian`, `abnt`, `mhra`, `cse`, `asa`, `bluebook`
- **Default:** `ieee` (set by document type profiles)
- **Source:** `lib/references/omnilatex-citations.sty`
- **Example:**
  ```latex
  \citationstyle{apa}
  ```

---

## Glossary and Symbol Commands

Commands for managing glossaries, symbols, abbreviations, and the index.
Powered by glossaries-extra and bib2gls.

### `\makeglossaries`

Initializes glossary processing. Standard glossaries command. Required
before using glossary entry commands.

- **Parameters:** none
- **Source:** glossaries (loaded by `lib/references/omnilatex-glossary.sty`)
- **Example:**
  ```latex
  \makeglossaries
  ```

### `\sym{<entry-name>}`

Inserts a symbol glossary entry inline. Aliases `\gls{sym.<entry>}`.

- **Parameters:** `#1` — symbol entry name (without prefix)
- **Source:** `lib/references/omnilatex-glossary.sty`
- **Example:**
  ```latex
  The velocity is denoted \sym{velocity}.
  ```

### `\abb{<entry-name>}`

Inserts an abbreviation glossary entry inline. Aliases `\gls{abb.<entry>}`.

- **Parameters:** `#1` — abbreviation entry name (without prefix)
- **Source:** `lib/references/omnilatex-glossary.sty`
- **Example:**
  ```latex
  The \abb{cpu} processes instructions.
  ```

### `\cons{<entry-name>}`

Inserts a physical constant entry inline. Aliases `\gls{cons.<entry>}`.

- **Parameters:** `#1` — constant entry name (without prefix)
- **Source:** `lib/references/omnilatex-glossary.sty`
- **Example:**
  ```latex
  The speed of light is \cons{c}.
  ```

### `\idx{<entry-name>}`

Inserts an index term inline. Aliases `\gls{idx.<entry>}`.

- **Parameters:** `#1` — index entry name (without prefix)
- **Source:** `lib/references/omnilatex-glossary.sty`
- **Example:**
  ```latex
  See \idx{relativity} for details.
  ```

### `\sub{<entry-name>}`

Inserts a subscript entry inline. Aliases `\gls{sub.<entry>}`.

- **Parameters:** `#1` — subscript entry name (without prefix)
- **Source:** `lib/references/omnilatex-glossary.sty`
- **Example:**
  ```latex
  $v_{\sub{max}}$
  ```

### `\name{<entry-name>}`

Inserts a person name from the glossary index. Aliases `\gls{name.<entry>}`.

- **Parameters:** `#1` — name entry (without prefix)
- **Source:** `lib/references/omnilatex-glossary.sty`
- **Example:**
  ```latex
  \name{einstein} proposed the theory.
  ```

### `\printunsrtglossary[<options>]`

Prints a glossary in definition order (unsorted). Used for symbols, subscripts, etc.

- **Parameters:** `[optional]` — `type=<glossary type>`, `title=<title>`
- **Source:** glossaries-extra (loaded by `lib/references/omnilatex-glossary.sty`)
- **Example:**
  ```latex
  \printunsrtglossary[type=symbols,title={List of Symbols}]
  ```

---

## Utility Commands

General-purpose utility commands provided by OmniLaTeX.

### `\iecfeg{<text>}`

Wraps Latin abbreviations (i.e., e.g., c.f., etc.) in italics for
consistent typographic treatment.

- **Parameters:** `#1` — abbreviation text
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  The result \iecfeg{i.e.}, convergence, was achieved.
  ```

### `\adaptedfrom`

Produces the localized "Adapted from" label for indicating sourced figures.

- **Parameters:** none
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \caption{Diagram. \adaptedfrom{Smith (2020).}}
  ```

### `\ctanpackage[<url>]{<name>}`

Creates a linked, bold monospace reference to a CTAN package. If no URL
is given, links to `https://ctan.org/pkg/<name>`.

- **Parameters:** `#1` [optional] custom URL, `#2` — package name
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  Uses the \ctanpackage{siunitx} package for units.
  ```

### `\signaturefield[<name>]`

Renders a signature line with place/date fields. Defaults to `\@author`.

- **Parameters:** `[optional]` — name to print under the signature line
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \signaturefield
  ```

### `\sampletext`

Outputs a pangram containing all 26 Latin letters for font testing.

- **Parameters:** none
- **Source:** `lib/layout/omnilatex-document.sty`
- **Example:**
  ```latex
  \sampletext
  ```

---

*This document was auto-generated from source `.sty` files. For the most
up-to-date information, consult the source files directly.*
