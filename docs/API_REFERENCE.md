---
title: API Reference
---
# OmniLaTeX API Reference

> Auto-generated from `specs/module_contracts/*.toml`
> Run `python scripts/generate_api_docs.py` to regenerate.

**Modules:** 31

## Module Index

| Module | File | Version | Exports |
|--------|------|---------|---------|
| [omnilatex-accessibility](#omnilatexaccessibility) | `lib/layout/omnilatex-accessibility.sty` | 2026-05-13 v1.25.0 | 7 |
| [omnilatex-base](#omnilatexbase) | `lib/core/omnilatex-base.sty` | 2024-10-11 v6.0.0 | 5 |
| [omnilatex-beamer](#omnilatexbeamer) | `lib/graphics/omnilatex-beamer.sty` | 2026-05-13 v1.25.0 | 4 |
| [omnilatex-biblio](#omnilatexbiblio) | `lib/references/omnilatex-biblio.sty` | 2024-10-11 v6.0.0 | 4 |
| [omnilatex-boxes](#omnilatexboxes) | `lib/layout/omnilatex-boxes.sty` | 2024-10-11 v6.0.0 | 2 |
| [omnilatex-citations](#omnilatexcitations) | `lib/references/omnilatex-citations.sty` | 2026-05-13 v1.25.0 | 10 |
| [omnilatex-cjk](#omnilatexcjk) | `lib/language/omnilatex-cjk.sty` | 2026-05-13 v1.25.0 | 12 |
| [omnilatex-colors](#omnilatexcolors) | `lib/utils/omnilatex-colors.sty` | 2024-10-11 v6.0.0 | 41 |
| [omnilatex-document](#omnilatexdocument) | `lib/layout/omnilatex-document.sty` | 2024-10-11 v6.0.0 | 19 |
| [omnilatex-floats](#omnilatexfloats) | `lib/layout/omnilatex-floats.sty` | 2024-10-11 v6.0.0 | 7 |
| [omnilatex-fonts](#omnilatexfonts) | `lib/typography/omnilatex-fonts.sty` | 2024-10-11 v6.0.0 | 1 |
| [omnilatex-glossary](#omnilatexglossary) | `lib/references/omnilatex-glossary.sty` | 2024-10-11 v6.0.0 | 21 |
| [omnilatex-graphics](#omnilatexgraphics) | `lib/graphics/omnilatex-graphics.sty` | 2024-10-11 v6.0.0 | 4 |
| [omnilatex-hyperref](#omnilatexhyperref) | `lib/references/omnilatex-hyperref.sty` | 2024-10-11 v6.0.0 | 11 |
| [omnilatex-i18n](#omnilatexi18n) | `lib/language/omnilatex-i18n.sty` | 2024-10-11 v6.0.0 | 19 |
| [omnilatex-koma](#omnilatexkoma) | `lib/layout/omnilatex-koma.sty` | 2024-10-11 v6.0.0 | 3 |
| [omnilatex-listings](#omnilatexlistings) | `lib/code/omnilatex-listings.sty` | 2024-10-11 v6.0.0 | 6 |
| [omnilatex-lists](#omnilatexlists) | `lib/typography/omnilatex-lists.sty` | 2024-10-11 v6.0.0 | 4 |
| [omnilatex-math](#omnilatexmath) | `lib/typography/omnilatex-math.sty` | 2024-10-11 v6.0.0 | 42 |
| [omnilatex-page](#omnilatexpage) | `lib/layout/omnilatex-page.sty` | 2024-10-11 v6.0.0 | 4 |
| [omnilatex-plugin](#omnilatexplugin) | `lib/utils/omnilatex-plugin.sty` | 2.0.0 | 5 |
| [omnilatex-presentation](#omnilatexpresentation) | `lib/layout/omnilatex-presentation.sty` | 2026-05-13 v1.25.0 | 16 |
| [omnilatex-review](#omnilatexreview) | `lib/utils/omnilatex-review.sty` | 2026/05/18 v2.0.0 | 5 |
| [omnilatex-rtl](#omnilatexrtl) | `lib/language/omnilatex-rtl.sty` | 2026-05-13 v1.25.0 | 8 |
| [omnilatex-tables](#omnilatextables) | `lib/tables/omnilatex-tables.sty` | 2024-10-11 v6.0.0 | 2 |
| [omnilatex-themes](#omnilatexthemes) | `lib/utils/omnilatex-themes.sty` | 2026-05-13 v1.25.0 | 6 |
| [omnilatex-tikz-core](#omnilatextikzcore) | `lib/graphics/omnilatex-tikz-core.sty` | 2024-10-11 v6.0.0 | 7 |
| [omnilatex-tikz-engineering](#omnilatextikzengineering) | `lib/graphics/omnilatex-tikz-engineering.sty` | 2024-10-11 v6.0.0 | 35 |
| [omnilatex-todo](#omnilatextodo) | `lib/utils/omnilatex-todo.sty` | 2.0.0 | 4 |
| [omnilatex-typesetting](#omnilatextypesetting) | `lib/typography/omnilatex-typesetting.sty` | 2024-10-11 v6.0.0 | 1 |
| [omnilatex-utils](#omnilatexutils) | `lib/utils/omnilatex-utils.sty` | 2024-10-11 v6.0.0 | 1 |

## Detailed Reference

### omnilatex-accessibility

**File:** `lib/layout/omnilatex-accessibility.sty`
**Version:** 2026-05-13 v1.25.0
**Description:** PDF/UA-1 accessibility support: tagged PDF via tagpdf, alt text for figures and TikZ, accessible links, table markup, heading hierarchy validation, color contrast checks, reading order hints, and language tagging
**Line count:** 106

**Dependencies:**

- Required: `tagpdf`, `pdfcomment`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\alttext` | command | `{description}` | Set alt text for the next figure environment; attached via env/figure/begin hook |
| `\tikzalttext` | command | `{description}` | Set alt text for the next tikzpicture environment; attached via env/tikzpicture/begin hook |
| `\accessiblelink` | command | `{display text}{url}{screen reader description}` | Accessible hyperlink with pdftooltip for screen reader description |
| `\validatstructure` | command | `` | Logs informational heading hierarchy validation check at compile time |
| `\checkcontrast` | command | `{foreground}{background}` | Informative color contrast check; logs reminder to verify WCAG AA 4.5:1 manually |
| `\readingorder` | command | `{order specification}` | Set PDF logical reading order via tagpdf structure/text-order |
| `\langtag` | command | `{ISO 639-1 code}{text}` | Wrap text with language attribute for WCAG 2.1 AA 3.1.2 compliance |

---

### omnilatex-base

**File:** `lib/core/omnilatex-base.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Core functionality and base setup: build mode detection, conditionals, date/time, spacing
**Line count:** 75

**Dependencies:**

- Required: `import`, `nth`, `etoolbox`, `xstring`, `datetime2`, `setspaceenhanced`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\omnilatex@buildmode` | command | `` | Internal macro holding the current build mode string (dev/prod/ultra), set via BUILD_MODE env var or Lua |
| `ifOmniDev` | command | `` | Boolean conditional: true when build mode is 'dev' (default) |
| `ifOmniProd` | command | `` | Boolean conditional: true when build mode is 'prod' |
| `ifOmniUltra` | command | `` | Boolean conditional: true when build mode is 'ultra' |
| `\OmniBuildMode` | command | `` | Public accessor that expands to the current build mode string |

---

### omnilatex-beamer

**File:** `lib/graphics/omnilatex-beamer.sty`
**Version:** 2026-05-13 v1.25.0
**Description:** Beamer integration: applies OmniLaTeX color and font system to Beamer presentations, including element colors, fonts, navigation removal, and frame numbering
**Line count:** 46

**Dependencies:**

- Required: `omnilatex-colors`, `omnilatex-fonts`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `OmniPrimaryColor (beamer)` | color_application | `` | Applied to Beamer structure, frametitle, title, block title, and items via \setbeamercolor |
| `OmniAccentColor (beamer)` | color_application | `` | Applied to Beamer subtitle, author, date, institute, subitem, and footline via \setbeamercolor |
| `navigation symbols` | template | `` | Removed via \setbeamertemplate{navigation symbols}{} for cleaner slides |
| `footline` | template | `` | Frame number footer: N/M right-aligned, via custom \setbeamertemplate{footline} |

---

### omnilatex-biblio

**File:** `lib/references/omnilatex-biblio.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Bibliography management with biblatex: ext-authoryear style, citation formatting, and uncited works category
**Line count:** 119

**Dependencies:**

- Required: `biblatex`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `bibnonum` | environment | `` | Custom bibliography environment without numbering, based on biblatex list infrastructure |
| `cited` | bibliography_category | `` | Bibliography category tracking which entries were actually cited vs. only in bib file |
| `notcited` | bibliography_heading | `` | Bibliography heading for uncited works with translated 'Further Reading' section title |
| `subbibliography` | bibliography_heading | `` | Bibliography heading for per-chapter bibliographies using cref to the refsegment |

---

### omnilatex-boxes

**File:** `lib/layout/omnilatex-boxes.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Color boxes and tcolorbox environments: example boxes with auto-counter and Git verification box
**Line count:** 84

**Dependencies:**

- Required: `tcolorbox`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `example` | environment | `[label]{title}` | Numbered tcolorbox example environment with auto-counter, breakable, gray styling, listed in loe |
| `\GitVerificationBox` | command | `` | Inline tcbox with a hyperlink to verify the current git commit |

---

### omnilatex-citations

**File:** `lib/references/omnilatex-citations.sty`
**Version:** 2026-05-13 v1.25.0
**Description:** Citation style library with pre-configured biblatex options for 9 academic publishers: ieee, acm, apa, chicago, nature, science, harvard, vancouver, mla
**Line count:** 176

**Dependencies:**

- Required: `kvoptions`
- Optional: `biblatex-ieee`, `biblatex-apa`, `biblatex-chicago`, `biblatex-nature`, `biblatex-science`, `biblatex-harvard`, `biblatex-vancouver`, `biblatex-mla`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\citationstyle` | command | `{name}` | Apply a citation style by name; loads dedicated biblatex package if available, otherwise uses built-in options |
| `\citestyle@ieee` | command | `` | IEEE style: numeric [1] brackets, citation order, 3 max cite names, giveninits |
| `\citestyle@acm` | command | `` | ACM style: numeric [1], alphabetical by author (nyt), up to 9 bib names |
| `\citestyle@apa` | command | `` | APA 7th edition: author-year, (Author, Year), natbib=true, 2 max cite names |
| `\citestyle@chicago` | command | `` | Chicago author-date: (Author Year), alphabetical, ibidtracker constrict |
| `\citestyle@nature` | command | `` | Nature style: numeric, superscript, citation order, 6 max cite names |
| `\citestyle@science` | command | `` | Science style: numeric [1], citation order, 10 max names, doi/url/eprint/isbn disabled |
| `\citestyle@harvard` | command | `` | Harvard style: author-year, dashed=false, punctfield=false, 2 max cite names |
| `\citestyle@vancouver` | command | `` | Vancouver style: numeric [1], citation order, 6 max names, uniquenames=false |
| `\citestyle@mla` | command | `` | MLA 9th edition: author-page, alphabetical, 3 max names |

---

### omnilatex-cjk

**File:** `lib/language/omnilatex-cjk.sty`
**Version:** 2026-05-13 v1.25.0
**Description:** CJK typography support: luatexja integration, Noto CJK font fallback chain, per-script presets (SC/TC/JP/KR), CJK-Latin inter-character spacing, ruby annotations (furigana/pinyin), and vertical writing mode
**Line count:** 192

**Dependencies:**

- Required: `luatexja`, `luatexja-fontspec`, `luatexja-ruby`, `xstring`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\setCJKMainFont` | command | `{font name}` | Set CJK main (serif) font; auto-applies via omnilatex@apply@cjkfonts |
| `\setCJKSansFont` | command | `{font name}` | Set CJK sans-serif font; auto-applies via omnilatex@apply@cjkfonts |
| `\setCJKMonoFont` | command | `{font name}` | Set CJK monospace font; auto-applies via omnilatex@apply@cjkfonts |
| `\setCJKScript` | command | `{sc|tc|jp|kr}` | Apply per-script font preset: SC (Simplified Chinese), TC (Traditional Chinese), JP (Japanese), KR (Korean) |
| `\setCJKLatinSpacing` | command | `{length}` | Adjust CJK-Latin inter-character spacing (xkanjiskip), default 0.25em |
| `\ruby` | command | `{base text}{ruby text}` | Ruby annotation (phonetic guide above base text), wraps luatexja-ruby \ltjruby |
| `\rubytwo` | command | `{base text}{ruby text}` | Two-character-per-group ruby annotation, wraps luatexja-ruby \ltjrubytwo |
| `\furigana` | command | `{base text}{ruby text}` | Japanese furigana alias for \ruby |
| `\pinyin` | command | `{base text}{ruby text}` | Chinese pinyin alias for \ruby |
| `\setRubyScale` | command | `{scale factor}` | Set ruby font size relative to base font, default 0.5 |
| `vertical` | environment | `` | Vertical writing mode: right-to-left columns, top-to-bottom lines (traditional CJK layout) |
| `\verticaltext` | command | `{text}` | Inline vertical text for short passages |

---

### omnilatex-colors

**File:** `lib/utils/omnilatex-colors.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Color definitions and named color schemes for diagrams, plots, code, and links
**Line count:** 80

**Dependencies:**

- Required: `xcolor`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `g1` | color | `` | Gradient shade: black!70 |
| `g2` | color | `` | Gradient shade: black!55 |
| `g3` | color | `` | Gradient shade: black!40 |
| `g4` | color | `` | Gradient shade: black!20 |
| `g5` | color | `` | Gradient shade: black!10 |
| `g6` | color | `` | Gradient shade: black!05 |
| `Glass` | color | `` | Very light blue for diagrams (RGB 170,238,255) |
| `Air` | color | `` | Light blue for diagrams (RGB 213,246,255) |
| `LightFluid` | color | `` | Light fluid blue (RGB 148,224,255) |
| `MediumFluid` | color | `` | Medium fluid blue (RGB 135,178,232) |
| `DarkFluid` | color | `` | Dark fluid blue (RGB 119,151,197) |
| `HotFluid` | color | `` | Hot fluid red (RGB 255,128,128) |
| `darklink` | color | `` | Dark blue link color (RGB 48,62,116) |
| `rdylbu1` | color | `` | ColorBrewer RdYlBu red (RGB 215,48,39) |
| `rdylbu2` | color | `` | ColorBrewer RdYlBu orange (RGB 252,141,89) |
| `rdylbu3` | color | `` | ColorBrewer RdYlBu light yellow (RGB 254,224,144) |
| `rdylbu4` | color | `` | ColorBrewer RdYlBu light blue (RGB 224,243,248) |
| `rdylbu5` | color | `` | ColorBrewer RdYlBu medium blue (RGB 145,191,219) |
| `rdylbu6` | color | `` | ColorBrewer RdYlBu dark blue (RGB 69,117,180) |
| `Set2A` | color | `` | ColorBrewer Set2 qualitative A (RGB 102,194,165) |
| `Set2B` | color | `` | ColorBrewer Set2 qualitative B (RGB 252,141,98) |
| `Set2C` | color | `` | ColorBrewer Set2 qualitative C (RGB 141,160,203) |
| `Set2D` | color | `` | ColorBrewer Set2 qualitative D (RGB 231,138,195) |
| `Set2E` | color | `` | ColorBrewer Set2 qualitative E (RGB 166,216,84) |
| `Set2F` | color | `` | ColorBrewer Set2 qualitative F (RGB 255,217,47) |
| `Set2G` | color | `` | ColorBrewer Set2 qualitative G (RGB 229,196,148) |
| `Set2H` | color | `` | ColorBrewer Set2 qualitative H (RGB 179,179,179) |
| `mBlue` | color | `` | Matlab blue for plots (HTML 0072BD) |
| `mOrange` | color | `` | Matlab orange for plots (HTML D95319) |
| `mYellow` | color | `` | Matlab yellow for plots (HTML EDB120) |
| `mPurple` | color | `` | Matlab purple for plots (HTML 7E2F8E) |
| `mGreen` | color | `` | Matlab green for plots (HTML 77AC30) |
| `mSky` | color | `` | Matlab sky blue for plots (HTML 4DBEEE) |
| `mRed` | color | `` | Matlab red for plots (HTML A2142F) |
| `cRed` | color | `` | Code annotation red (RGB 209,0,86) |
| `cBlue` | color | `` | Code annotation blue (RGB 0,130,185) |
| `cGreen` | color | `` | Code annotation green (RGB 0,128,63) |
| `cOrange` | color | `` | Code annotation orange (RGB 244,131,66) |
| `DarkLinkGreen` | color | `` | Demonstration link green (RGB 65,107,60) |
| `kit-blue50` | color | `` | KIT corporate blue 50% (RGB 0,84,159) |
| `kit-blue40` | color | `` | KIT corporate blue 40% (RGB 64,127,183) |

---

### omnilatex-document

**File:** `lib/layout/omnilatex-document.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Document metadata commands: document type, font size, layout controls, metadata fields, and utility commands
**Line count:** 288

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\documenttype` | command | `{type}` | Set the document type string (e.g., Bachelor Thesis, Master Thesis) |
| `\documentfontsize` | command | `{size}` | Set document font size via KOMAoptions and recalculate typearea |
| `\documentlayout` | command | `{layout}` | Set document layout KOMAoptions and recalculate typearea |
| `\documentcolormode` | command | `{mode}` | Set document color mode (dark/light/color) applied at begin-document |
| `\documentlinespacing` | command | `{spacing}` | Set line spacing (single/onehalf/double or numeric) applied at begin-document |
| `\documentparspacing` | command | `{spacing}` | Set paragraph spacing (none/half/full or dimension) applied at begin-document |
| `\documentitemspacing` | command | `{spacing}` | Set list item spacing (none/compact/normal or dimension) applied at begin-document |
| `\documentfontmode` | command | `{mode}` | Set document font mode (serif/sans/mono) applied at begin-document |
| `\documentlinkstyle` | command | `{style}` | Set document link style (color/plain) applied at begin-document |
| `\documentcodestyle` | command | `{style}` | Set document code listing style (color/bw or minted style name) applied at begin-document |
| `\idnumber` | command | `{id}` | Set student ID number |
| `\firstexaminer` | command | `{name}` | Set first examiner name |
| `\secondexaminer` | command | `{name}` | Set second examiner name |
| `\supervisor` | command | `{name}` | Set supervisor name |
| `\signaturefield` | command | `[name]` | Typeset a signature field with lines for name and place/date, defaults to \@author |
| `\iecfeg` | command | `{text}` | Wraps text in italics for abbreviations like i.e., e.g., c.f. |
| `\adaptedfrom` | command | `` | Prints 'Adapted from' or 'Adaptiert von' based on current language |
| `\ctanpackage` | command | `[url]{package_name}` | Wraps package name as a hyperlink to CTAN (or custom URL) |
| `\sampletext` | command | `` | Prints the pangram 'The quick brown Fox jumps over the lazy Dog 13 times!' |

---

### omnilatex-floats

**File:** `lib/layout/omnilatex-floats.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Float configuration: captions, subfloats, and high-level float wrapper commands with key-value options
**Line count:** 293

**Dependencies:**

- Required: `flafter`, `caption`, `xparse`, `array`, `subcaption`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\omnlFigure` | command | `[options]{content}` | High-level figure wrapper with key-value options: placement, caption, short-caption, label, footnote, caption-width, align, caption-position |
| `\omnlTable` | command | `[options]{content}` | High-level table wrapper with key-value options; defaults to top caption placement |
| `\omnlFloatCaption` | command | `` | Manually typeset the float caption when caption-position=manual |
| `\omnlFloatNote` | command | `{text}` | Adds an unnumbered caption note below the float |
| `\omnlFloatFootmark` | command | `[number]` | Places a footnote mark inside a float; auto-increments if no number given |
| `\omnlFloatFoottext` | command | `[number]{text}` | Places footnote text corresponding to omnlFloatFootmark |
| `omnlFloatRow` | environment | `[columns]` | Minipage-based row layout for side-by-side floats, default 2 columns |

---

### omnilatex-fonts

**File:** `lib/typography/omnilatex-fonts.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Font configuration and loading for LuaLaTeX: main, mono, sans, math, unit, and icon fonts
**Line count:** 114

**Dependencies:**

- Required: `fontspec`, `fix-cm`, `amsmath`, `lualatex-math`, `amssymb`, `unicode-math`, `fontawesome5`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\unitnumberfont` | command | `` | Font family for typesetting units with siunitx, using Libertinus Serif with upright numbers |

---

### omnilatex-glossary

**File:** `lib/references/omnilatex-glossary.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Glossary management: symbols, abbreviations, subscripts, constants, index, custom fields, and glossary printing styles
**Line count:** 515

**Dependencies:**

- Required: `glossaries-extra`, `longtable`, `glossary-longextra`, `glossary-bookindex`, `glossary-mcols`
- Optional: `tabularray`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\sym` | command | `{label}` | Alias for \gls{sym.label} to access symbol glossary entries |
| `\sub` | command | `{label}` | Alias for \gls{sub.label} to access subscript glossary entries |
| `\name` | command | `{label}` | Alias for \gls{name.label} to access name glossary entries |
| `\cons` | command | `{label}` | Alias for \gls{cons.label} to access constant glossary entries |
| `\idx` | command | `{label}` | Alias for \gls{idx.label} to access index glossary entries |
| `\abb` | command | `{label}` | Alias for \gls{abb.label} to access abbreviation glossary entries |
| `\symspec` | command | `[options]{label}` | Shortcut for \glsspecific{sym.label} to access the 'specific' field of a symbol entry |
| `\symprefix` | command | `` | Prefix string 'sym.' for symbol glossary labels |
| `\subprefix` | command | `` | Prefix string 'sub.' for subscript glossary labels |
| `\nameprefix` | command | `` | Prefix string 'name.' for name glossary labels |
| `\constantsprefix` | command | `` | Prefix string 'cons.' for constant glossary labels |
| `\indexprefix` | command | `` | Prefix string 'idx.' for index glossary labels |
| `\abbreviationprefix` | command | `` | Prefix string 'abb.' for abbreviation glossary labels |
| `\glshdrfont` | command | `{text}` | Font command for glossary table headers (bold) |
| `\specificsymbolmark` | command | `` | Mark appended after description for specific symbols (asterisk) |
| `\alternativesymbolmark` | command | `` | Separator mark between symbol and its alternative version (slash) |
| `symbunitlong` | glossary_style | `` | Custom glossary style for symbols with symbol, description, and unit columns |
| `numberlong` | glossary_style | `` | Custom glossary style for constants with symbol, description, value, and unit columns |
| `custom-base` | glossary_style | `` | Base glossary style extending long-name-desc-loc with removed header |
| `subscripts` | glossary_type | `` | Custom glossary type for subscript entries |
| `notprinted` | glossary_type | `` | Glossary type for entries that should not appear in printed output |

---

### omnilatex-graphics

**File:** `lib/graphics/omnilatex-graphics.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Image handling, SVG support, graphics paths, contour text, and TikZ+SVG debug helpers
**Line count:** 126

**Dependencies:**

- Required: `graphicx`, `xparse`, `svg`, `scalerel`, `contour`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\ctrw` | command | `{text}` | Black text with white contour outline for legibility on noisy backgrounds |
| `\ctrb` | command | `{text}` | White text with black contour outline for legibility on noisy backgrounds |
| `\debugtikzsvg` | command | `` | Debug overlay for TikZ+SVG alignment: draws grid and position labels over an image node |
| `\mtlbsmlkicon` | command | `{icon_name}` | Include and scale a MATLAB/Simulink icon from assets/logos/matlab_simulink/ to height of capital X |

---

### omnilatex-hyperref

**File:** `lib/references/omnilatex-hyperref.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Hyperlinks, PDF metadata, bookmarks, cross-references with cleveref, and git metadata integration
**Line count:** 165

**Dependencies:**

- Required: `hyperref`, `ocgx2`, `bookmark`, `cleveref`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\GitRefName` | command | `` | Current git reference name (branch/tag), provided by git-metadata.lua or fallback 'n.a.' |
| `\GitShortSHA` | command | `` | Short git commit SHA, provided by git-metadata.lua or fallback 'n.a.' |
| `\GitLongSHA` | command | `` | Full git commit SHA, provided by git-metadata.lua or fallback 'n.a.' |
| `\GitRepositorySlug` | command | `` | Git repository slug, provided by git-metadata.lua or fallback 'n.a.' |
| `\GitProjectName` | command | `` | Git project name, provided by git-metadata.lua or fallback 'n.a.' |
| `\GitHostPagesURL` | command | `` | Git hosting pages URL, provided by git-metadata.lua or fallback 'n.a.' |
| `\GitHostAPIProvider` | command | `` | Git hosting API provider name, provided by git-metadata.lua or fallback 'n.a.' |
| `\GitHostAPIBase` | command | `` | Git hosting API base URL, provided by git-metadata.lua or fallback 'n.a.' |
| `\BuildDate` | command | `` | Build date, defaults to \today |
| `\BuildDatePDF` | command | `` | Build date in PDF format for deterministic metadata |
| `ifboldPDFchapters` | command | `` | Boolean conditional controlling whether chapter-level PDF bookmarks are bold |

---

### omnilatex-i18n

**File:** `lib/language/omnilatex-i18n.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Internationalization: Polyglossia language setup and bilingual (English/German) translations for all UI strings
**Line count:** 219

**Dependencies:**

- Required: `polyglossia`, `translations`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `First` | translation | `` | English: \nth{1}, German: 1. |
| `Second` | translation | `` | English: \nth{2}, German: 2. |
| `Examiner` | translation | `` | English: Examiner, German: Prüfer:in |
| `Supervisor` | translation | `` | English: Supervisor, German: Betreuer:in |
| `CompiledOn` | translation | `` | English: Compiled on, German: Kompiliert am |
| `CensorNotice` | translation | `` | English: CENSORED VERSION, German: ZENSIERTE VERSION |
| `AuthorshipDeclTitle` | translation | `` | English: Declaration of Authorship, German: Erklärung zur Eigenständigkeit |
| `AuthorshipDeclText` | translation | `` | Full declaration of authorship text in both languages |
| `Reaction` | translation | `` | English: Reaction, German: Reaktion |
| `Gloss` | translation | `` | English: Glossary, German: Glossar |
| `BlankPage` | translation | `` | English: Rest of this page intentionally left blank, German: Rest der Seite absichtlich freigelassen |
| `Listing` | translation | `` | English: Code Listing, German: Code |
| `Example` | translation | `` | English: Example, German: Beispiel |
| `Contfoot` | translation | `` | English: Continued on next page, German: Fortgeführt auf der nächsten Seite |
| `Conthead` | translation | `` | English: (Continued), German: (Fortgesetzt) |
| `FurtherReadingTitle` | translation | `` | English: Further Reading, German: Weitere Literatur |
| `Constant` | translation | `` | English: const, German: konst |
| `Unit` | translation | `` | English: Unit, German: Einh. |
| `AdaptedFrom` | translation | `` | English: Adapted from, German: Adaptiert von |

---

### omnilatex-koma

**File:** `lib/layout/omnilatex-koma.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** KOMA-Script customization: chapter formatting, title page styles (thesis/book/TUHH), and TOC configuration
**Line count:** 276

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\maketitle` | command | `` | Renewed maketitle that renders a custom title page based on omnilatex@titlestyle (thesis/book/TUHH) |
| `documenttype` | komafont | `` | KOMA font for the document type label on the title page |
| `example` | toc_type | `` | New TOC type 'example' with listname from translations, creating \listofexamples |

---

### omnilatex-listings

**File:** `lib/code/omnilatex-listings.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Source code highlighting with minted: configuration, listing environments, and code annotation commands
**Line count:** 86

**Dependencies:**

- Required: `minted`, `accsupp`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `longlisting` | environment | `` | Environment for long code listings using captionsetup with type=listing |
| `\emptyaccsupp` | command | `{content}` | Wraps content with empty ActualText for PDF accessibility (invisible to screen readers) |
| `\phstring` | command | `{text}` | Highlights text as a string placeholder in red (cRed) |
| `\phnum` | command | `{text}` | Highlights text as a numeric placeholder in blue (cBlue) |
| `\phother` | command | `{text}` | Highlights text as other placeholder in green (cGreen) |
| `\phnote` | command | `{text}` | Highlights text as annotation note in bold orange (cOrange) |

---

### omnilatex-lists

**File:** `lib/typography/omnilatex-lists.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** List configuration and custom list environments for standard and compact (table) usage
**Line count:** 70

**Dependencies:**

- Required: `enumitem`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `tabitemize` | environment | `` | Compact single-level itemize list for table cells with no vertical spacing |
| `tabenum` | environment | `` | Compact single-level enumerate list for table cells with no vertical spacing |
| `descriptcount` | counter | `` | Counter for enumerated description list items |
| `enumdescript` | environment | `` | Enumerated description list with auto-numbered bold labels (a., b., ...) |

---

### omnilatex-math

**File:** `lib/typography/omnilatex-math.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Mathematical typesetting: delimiters, chemistry, units, operators, derivatives, statistical/physical notation
**Line count:** 416

**Dependencies:**

- Required: `mathtools`, `empheq`, `chemmacros`, `siunitx`, `suffix`, `xfrac`, `nicefrac`, `eurosym`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\parens` | command | `{content}` | Auto-scaling paired delimiter for parentheses; starred variant scales with \left/\right |
| `\brackets` | command | `{content}` | Auto-scaling paired delimiter for square brackets; starred variant scales |
| `\braces` | command | `{content}` | Auto-scaling paired delimiter for curly braces; starred variant scales |
| `reactionsgather` | environment | `` | Chemistry reaction environment like AMSmath gather, with R-tag and equation numbering |
| `reactionsgather*` | environment | `` | Unnumbered chemistry reaction gather environment |
| `\eqend` | command | `` | Inserts comma-period with thin space to end a display equation |
| `\eqcomma` | command | `` | Inserts comma with thin space for mid-equation punctuation |
| `\grad` | command | `` | Upright 'grad' math operator via DeclareMathOperator |
| `\const` | command | `` | Upright 'const.' notation for constant expressions, language-aware |
| `\qq` | command | `{text}` | Quick quad: inserts \quad\text{#1}\quad for text between equation parts |
| `\chemamount` | command | `{quantity}{unit}{substance}` | Unified markup for '1.2 ppm CO2' constructs with correct spacing |
| `\circlednum` | command | `{number}` | Renders a number inside a circle using TikZ circlednum style |
| `\symbolplaceholder` | command | `` | Prints a raised dottedsquare as a placeholder for symbols |
| `\meanfmt` | command | `{variable}` | Mean value formatting: horizontal overbar with adjusted kerning |
| `\mean` | command | `{variable}` | Mean value with overbar, linked to glossary entry sym.mean |
| `\logmeanfmt` | command | `{variable}` | Logarithmic mean formatting: tilde over variable |
| `\logmean` | command | `{variable}` | Logarithmic mean with tilde, linked to glossary entry sym.logmean |
| `\absfmt` | command | `{content}` | Absolute value paired delimiter using \lvert/\rvert |
| `\abs` | command | `{content}` | Absolute value with auto-scaling, linked to glossary entry sym.abs |
| `\flowfmt` | command | `{variable}` | Dotted symbol formatting for flow quantities |
| `\flow` | command | `{variable}` | Flow notation with dot, linked to glossary entry sym.flow |
| `\differencefmt` | command | `{variable}` | Delta/difference formatting |
| `\difference` | command | `{variable}` | Delta notation, linked to glossary entry sym.difference |
| `\nablaoperatorfmt` | command | `{variable}` | Nabla operator formatting |
| `\nablaoperator` | command | `[degree]{variable}` | Nabla wrapper with optional degree, linked to glossary entry sym.nabla |
| `\heatexentryfmt` | command | `{variable}` | Heat exchanger entry formatting (prime suffix) |
| `\heatexentry` | command | `{variable}` | Heat exchanger entry notation, linked to glossary entry sym.heatexentry |
| `\heatexexitfmt` | command | `{variable}` | Heat exchanger exit formatting (double-prime suffix) |
| `\heatexexit` | command | `{variable}` | Heat exchanger exit notation, linked to glossary entry sym.heatexexit |
| `\vectfmt` | command | `{variable}` | Vector formatting using bold symbol |
| `\vect` | command | `{variable}` | Vector notation with bold symbol, linked to glossary entry sym.vector |
| `\derivativefmt` | command | `{variable}` | Upright d derivative formatting |
| `\partialderivativefmt` | command | `{variable}` | Partial derivative formatting |
| `\deriv` | command | `[degree]{variable}` | Derivative notation, linked to glossary entry sym.derivative |
| `\deriv*` | command | `[degree]{variable}` | Partial derivative notation (starred variant), linked to sym.partial_derivative |
| `\fracderiv` | command | `[degree]{numerator}{denominator}` | Derivative fraction notation |
| `\fracderiv*` | command | `[degree]{numerator}{denominator}` | Partial derivative fraction notation (starred variant) |
| `\timederiv` | command | `[degree]{variable}` | Time derivative fraction, denominator is time symbol |
| `\timederiv*` | command | `[degree]{variable}` | Partial time derivative fraction |
| `\posderiv` | command | `[degree]{variable}` | Positional derivative fraction, denominator is first Cartesian coordinate |
| `\posderiv*` | command | `[degree]{variable}` | Partial positional derivative fraction |
| `\temperaturepair` | command | `{temp1}{temp2}` | Prints temperature range like 45/55 degC using siunitx |

---

### omnilatex-page

**File:** `lib/layout/omnilatex-page.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Page layout: headers, footers, page styles using SCRLayer, and deliberately blank page handling
**Line count:** 96

**Dependencies:**

- Required: `scrlayer-scrpage`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\headerrulelength` | length | `` | Length controlling the height of the vertical header rule |
| `\headerrule` | command | `` | Draws a vertical rule in the header with height set by \headerrulelength |
| `\blankpage` | command | `` | Typesets a centered message on deliberately blank pages using translated BlankPage text |
| `blank` | pagestyle | `` | Page style for deliberately blank pages, registered as cleardoublepage style |

---

### omnilatex-plugin

**File:** `lib/utils/omnilatex-plugin.sty`
**Version:** 2.0.0
**Description:** Plugin loading system for third-party OmniLaTeX extensions
**Line count:** 80

**Dependencies:**

- Required: `kvoptions`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `useplugin` | command | `{name}` | Load plugin omnilatex-plugin-<name>.sty |
| `useplugin` | command | `[options]{name}` | Load plugin with options |
| `pluginpath` | command | `{name}` | Expand to expected plugin file path |
| `listplugins` | command | `` | List all loaded plugins (to log) |
| `ifpluginloaded` | command | `{name}{true}{false}` | Conditional: execute true branch if plugin is loaded |

---

### omnilatex-presentation

**File:** `lib/layout/omnilatex-presentation.sty`
**Version:** 2026-05-13 v1.25.0
**Description:** Presentation layout module: slide frames with TikZ headers/footers, progress bar, block environments (presentationblock, alertblock, exampleblock, noteblock, definitionblock), section dividers, and two-column layout
**Line count:** 304

**Dependencies:**

- Required: `tcolorbox`, `calc`, `ifthen`
- Optional: `tikz`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `presentationframe` | environment | `[optional title]` | Slide frame with header, footer, and progress bar; auto-increments frame counter |
| `slideframe` | environment | `[optional title]` | Backward-compatible alias for presentationframe |
| `\maketitle` | command | `` | Renders presentation title page with TikZ banner, title, author, institute, date |
| `presentationblock` | environment | `[tcolorbox options]{title}` | Primary content block with left border accent and universityprimary color |
| `alertblock` | environment | `[tcolorbox options]{title}` | Alert/warning block with red left border accent |
| `exampleblock` | environment | `[tcolorbox options]{title}` | Example block with green left border accent |
| `noteblock` | environment | `[tcolorbox options]{title}` | Note block with blue left border accent |
| `definitionblock` | environment | `[tcolorbox options]{title}` | Definition block with orange left border accent |
| `\presentationSection` | command | `{section title}` | Full-page section divider with TikZ background and large centered title |
| `presentationcolumns` | environment | `[column width fraction]` | Two-column slide layout wrapper, defaults to 0.48\textwidth per column |
| `\presentationcolumn` | command | `[width fraction]` | Begin a column within presentationcolumns |
| `\slidetitle` | command | `{title text}` | Centered slide title with universityprimary color and horizontal rule |
| `\presentationnavsymbolson` | command | `` | Enable Beamer navigation symbols |
| `\presentationnavsymbolsoff` | command | `` | Disable Beamer navigation symbols (default) |
| `\presentationprogresson` | command | `` | Enable bottom progress bar (default) |
| `\presentationprogressoff` | command | `` | Disable bottom progress bar |

---

### omnilatex-review

**File:** `lib/utils/omnilatex-review.sty`
**Version:** 2026/05/18 v2.0.0
**Description:** Margin note review functionality: numbered review items, review footnotes, review blocks, and review list for collaborative editing
**Line count:** N/A

**Dependencies:**

- Required: `omnilatex-utils`, `xcolor`, `marginnote`, `etoolbox`, `tcolorbox`

**Options:**

| Option | Description |
|--------|-------------|
| `margin` | Review notes appear in margins (default) |
| `inline` | Review notes appear inline in the text |
| `disable` | Suppress all review output entirely |
| `color=<color>` | Set review highlight color (default: orange!30) |

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `review` | counter | `` | Counter for numbering review items sequentially across the document |
| `\review` | command | `[label]{comment}` | Adds a colored margin note with reviewer comment; optional label prefixes the numbered item |
| `\reviewfootnote` | command | `{comment}` | Adds review comment as a footnote with highlighted background |
| `\reviewlist` | command | `` | Lists all review items accumulated in the document at the current position |
| `reviewblock` | environment | `{title}` | Inline review block with highlighted background and titled header |

---

### omnilatex-rtl

**File:** `lib/language/omnilatex-rtl.sty`
**Version:** 2026-05-13 v1.25.0
**Description:** RTL language support for Arabic, Persian, and Hebrew: bidi paragraph direction, mirrored page layout, script-specific font configuration with fallback, Arabic-Indic numerals, LTR math mode, and inline direction overrides
**Line count:** 271

**Dependencies:**

- Required: `xstring`
- Optional: `bidi`, `fontspec`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\setArabicFont` | command | `{font name}` | Set Arabic script font family with Script=Arabic and FakeBold=2 |
| `\setArabicBoldFont` | command | `{font name}` | Set Arabic bold font variant |
| `\setHebrewFont` | command | `{font name}` | Set Hebrew script font family with Script=Hebrew and FakeBold=2 |
| `\setHebrewBoldFont` | command | `{font name}` | Set Hebrew bold font variant |
| `\arabicindictrue` | command | `` | Enable Arabic-Indic numerals (٠١٢٣٤٥٦٧٨٩) for Arabic documents |
| `\arabicindicfalse` | command | `` | Disable Arabic-Indic numerals, use Western Arabic digits (0123456789) instead |
| `\LTRinline` | command | `{text}` | Inline left-to-right text override inside an RTL document, wraps bidi \textLR |
| `\RTLinline` | command | `{text}` | Inline right-to-left text override inside an LTR document, wraps bidi \textRL |

---

### omnilatex-tables

**File:** `lib/tables/omnilatex-tables.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Table formatting: booktabs, tabularray, custom column types, and helper commands for rotated multi-row cells
**Line count:** 64

**Dependencies:**

- Required: `array`, `multirow`, `booktabs`, `tabularray`, `fvextra`
- Optional: `longtblr`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `M` | column_type | `{width}` | Centered paragraph column of specified width |
| `\multirotatecell` | command | `{rows}{text}` | Rotates text 90 degrees and wraps it in a multirow spanning the given number of rows |

---

### omnilatex-themes

**File:** `lib/utils/omnilatex-themes.sty`
**Version:** 2026-05-13 v1.25.0
**Description:** Color theme system with light/dark mode, six built-in palettes (default, midnight, forest, rose, monochrome, sepia), per-slot color overrides, and KOMA-Script compatibility shims
**Line count:** 419

**Dependencies:**

- Required: `xcolor`, `xstring`, `kvoptions`
- Optional: `tcolorbox`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\usetheme` | command | `{name}` | Apply a complete color theme; handles -dark suffix automatically (e.g. monochrome-dark) |
| `\darkmode` | command | `` | Switch to dark mode variant of the current theme |
| `\lightmode` | command | `` | Switch back to light mode variant of the current theme |
| `\setthemecolor` | command | `{slot}{color}` | Override a single theme color slot; slots: bg, fg, heading, body, accent, blockbg, blockframe, link, rule, codebg, footernote |
| `\ifthememode` | command | `{dark}{light}` | Conditional: executes dark branch if dark mode active, light branch otherwise |
| `\ifdarkmode` | if_flag | `` | TeX if-switch; true when document is in dark mode (\darkmodetrue/\darkmodefalse) |

---

### omnilatex-tikz-core

**File:** `lib/graphics/omnilatex-tikz-core.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** TikZ/PGFPlots core configuration: libraries, plot cycle lists, global plot settings, and reusable styles
**Line count:** 209

**Dependencies:**

- Required: `pgfplots`, `pgfplotstable`, `forest`, `tikz-3dplot`, `circuitikz`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `regularplot` | style | `` | PGFPlots style for a broadly usable regular plot with grids, thick lines, outside ticks |
| `plainplot` | style | `` | PGFPlots style for a clean plot without numerical labels or ticks |
| `tuftelike` | style | `` | PGFPlots style inspired by Tufte: minimal ticks, shifted axis lines |
| `arrowplot` | style | `{arrow_spec}` | PGFPlots style that decorates a path with repeated arrows along its length |
| `log x ticks with fixed point` | style | `` | PGFPlots style for logarithmic x-axis with fixed-point labels instead of scientific notation |
| `log y ticks with fixed point` | style | `` | PGFPlots style for logarithmic y-axis with fixed-point labels instead of scientific notation |
| `\parsenode` | command | `[options]text\pgf@nil` | Internal helper for add node at x style: parses label options and text |

---

### omnilatex-tikz-engineering

**File:** `lib/graphics/omnilatex-tikz-engineering.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Engineering shapes, technical diagrams, custom PGF node shapes, and TikZ styles for thermodynamic/mechanical drawings
**Line count:** 1049

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `startstop` | style | `` | Flow chart style: rounded rectangle, red fill, for start/stop nodes |
| `io` | style | `` | Flow chart style: ellipse, blue fill, for input/output nodes |
| `process` | style | `` | Flow chart style: rectangle, orange fill, for process nodes |
| `decision` | style | `` | Flow chart style: signal shape, green fill, for decision nodes |
| `arrow` | style | `` | Flow chart style: thick arrow with stealth tip |
| `symmetrycross` | style | `[size]` | Rotated cross-out to mark symmetry center in technical drawings |
| `pipecrosssection` | style | `[size]` | Circle simulating a pipe cross-section with thick border and MediumFluid fill |
| `arrowlabel` | style | `[position]` | Label style for positioning text along arrows with white background |
| `wall` | style | `[fill_color]` | Wall style for cross-sections: thick, drawn, with rounded corners |
| `fluid` | style | `[fill_color]` | Fluid fill style, default MediumFluid |
| `flowarrow` | style | `{inverse_frequency}{amplitude}` | Squiggly dashed arrow style for flow visualization using snake decoration |
| `annotationarrow` | style | `` | Arrow style with thick dot at end, for annotation pointing |
| `origindot` | style | `[fill_color]` | Small filled circle for coordinate origins |
| `add node at x` | style | `{x_position}{label_text}` | Place a labeled node at a given x-position on a plot, computing y automatically |
| `shorten <>` | style | `{length}` | Shorten both ends of a path simultaneously |
| `circlednum` | style | `` | Circle shape with draw, white fill, used for circled numbers |
| `radiator` | pic | `` | Detailed 3D radiator pic with front/top/right surfaces and named coordinates |
| `TUHHuman` | pic | `` | Stylized human figure pic with TUHH chest emblem |
| `boilercylinder` | style | `` | Cylinder shape styled as a boiler with shading |
| `boiler` | pic | `` | Boiler pic using boilercylinder style with contoured text |
| `equalizing tank` | style | `[size]` | Circle split node styled as an equalizing tank |
| `pipe` | style | `[width]` | Double-line pipe style with MediumFluid fill and triangle arrow caps |
| `valve` | style | `[size]` | Valve node style using custom valve shape, white fill, rotated 90deg |
| `control valve` | style | `[size]` | Control valve style with semicircle control wheel extension |
| `threeway valve` | style | `[size]` | Three-way valve style with asymmetrical port layout |
| `fourway valve` | style | `[size]` | Four-way valve style with symmetrical cross-pattern |
| `threeway control valve` | style | `` | Three-way control valve combining threeway valve and control valve features |
| `radiator` | style | `[size]` | Radiator node style with 3D front/top/right surfaces and vertical slats |
| `vented radiator` | style | `` | Radiator with ventilation outlet on top-left corner |
| `pump` | style | `[size]` | Pump node style: circle with internal triangle |
| `compressor` | style | `[size]` | Compressor node style: circle with internal zigzag pattern |
| `heat exchanger` | style | `[size]` | Heat exchanger node with triangle heat symbol and in/out anchors |
| `simple heat exchanger` | style | `[size]` | Simple heat exchanger: rectangle with diagonal cross |
| `sensor` | style | `[size]` | Sensor node: vertical stroke with three decreasing horizontal lines |
| `level indicator` | style | `[size]` | Level indicator: inverted triangle with three decreasing horizontal lines |

---

### omnilatex-todo

**File:** `lib/utils/omnilatex-todo.sty`
**Version:** 2.0.0
**Description:** TODO item tracker with priority grouping and inline margin notes
**Line count:** 30

**Dependencies:**

- Required: `xcolor`

**Options:**

| Option | Description |
|--------|-------------|
| `todonotes` | Boolean: enable todo tracking and inline notes |

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `todo` | command | `{text}` | Add a TODO item (tracked by Lua, displayed as margin note) |
| `todo` | command | `[priority]{text}` | Add a TODO item with priority (high/medium/low) |
| `todolist` | command | `` | Print grouped summary of all TODO items by priority |
| `todocount` | command | `` | Expand to total number of TODO items found |

---

### omnilatex-typesetting

**File:** `lib/typography/omnilatex-typesetting.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** Typography helpers: hyphenation, microtype, line spacing, quotation support, and ragged-right text
**Line count:** 74

**Dependencies:**

- Required: `extdash`, `microtype`, `ragged2e`, `blindtext`, `pdflscape`, `url`, `setspaceenhanced`, `csquotes`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\mkbegdispquote` | command | `` | Renewed to add italic shape at the beginning of display quote environments |

---

### omnilatex-utils

**File:** `lib/utils/omnilatex-utils.sty`
**Version:** 2024-10-11 v6.0.0
**Description:** System utilities, TODO notes, git metadata, keyboard macros, censoring, and miscellaneous packages
**Line count:** 109

**Dependencies:**

- Required: `hologo`, `menukeys`, `censor`, `cancel`
- Optional: `todonotes`

**Exports:**

| Name | Type | Signature | Description |
|------|------|-----------|-------------|
| `\fakeverb` | command | `{content}` | Typesets argument in ttfont with detokenize, useful for showing verbatim-like text |

---
