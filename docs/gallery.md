# Template Gallery

Visual showcase of all 24 OmniLaTeX example templates.

## Quick Start

Build any example with:
```bash
python build.py build-example <name>
```

## Templates

### Academic Documents

| Example | Doctype | Description | PDF |
|---------|---------|-------------|-----|
| `thesis` | thesis | Generic academic thesis | [thesis.pdf](build/examples/thesis.pdf) |
| `thesis-tuhh` | thesis | TUHH thesis with institutional branding | [thesis-tuhh.pdf](build/examples/thesis-tuhh.pdf) |
| `thesis-spacing` | thesis | Thesis with custom line spacing | [thesis-spacing.pdf](build/examples/thesis-spacing.pdf) |
| `dissertation` | dissertation | Dissertation document | [dissertation.pdf](build/examples/dissertation.pdf) |
| `inline-paper` | inlinepaper | Inline research paper | [inline-paper.pdf](build/examples/inline-paper.pdf) |
| `journal` | journal | Journal / magazine article | [journal.pdf](build/examples/journal.pdf) |
| `technical-report` | technicalreport | Technical report format | [technical-report.pdf](build/examples/technical-report.pdf) |

### Short Documents

| Example | Doctype | Description | PDF |
|---------|---------|-------------|-----|
| `article` | article | Standard article format | [article.pdf](build/examples/article.pdf) |
| `article-color` | article | Article with color configuration | [article-color.pdf](build/examples/article-color.pdf) |
| `cover-letter` | cover-letter | Cover letter template | [cover-letter.pdf](build/examples/cover-letter.pdf) |
| `cover-letter-formal` | cover-letter | Formal cover letter variant | [cover-letter-formal.pdf](build/examples/cover-letter-formal.pdf) |
| `cv` | cv | Curriculum vitae template | [cv.pdf](build/examples/cv.pdf) |
| `cv-twopage` | cv | Two-page CV variant | [cv-twopage.pdf](build/examples/cv-twopage.pdf) |
| `poster` | poster | Conference poster (A1 landscape) | [poster.pdf](build/examples/poster.pdf) |
| `presentation` | presentation | Presentation slides (KOMA-based) | [presentation.pdf](build/examples/presentation.pdf) |
| `letter` | letter | Formal letter | [letter.pdf](build/examples/letter.pdf) |

### Books & Reference

| Example | Doctype | Description | PDF |
|---------|---------|-------------|-----|
| `book` | book | Book-length document | [book.pdf](build/examples/book.pdf) |
| `manual` | manual | Manual / handbook document | [manual.pdf](build/examples/manual.pdf) |
| `dictionary` | dictionary | Dictionary / lexicon | [dictionary.pdf](build/examples/dictionary.pdf) |
| `standard` | standard | Standards document | [standard.pdf](build/examples/standard.pdf) |

### Starter Templates

| Example | Doctype | Description | PDF |
|---------|---------|-------------|-----|
| `minimal-starter` | thesis | Minimal starter demonstrating all major features | [minimal-starter.pdf](build/examples/minimal-starter.pdf) |
| `minimal-custom` | thesis | Minimal template showing customization options | [minimal-custom.pdf](build/examples/minimal-custom.pdf) |
| `multi-language` | article | Multilingual document (English/German) | [multi-language.pdf](build/examples/multi-language.pdf) |

### Accessibility

| Example | Doctype | Description | PDF |
|---------|---------|-------------|-----|
| `accessibility-test` | article | Tagged PDF (PDF/UA-1) via tagpdf | [accessibility-test.pdf](build/examples/accessibility-test.pdf) |

## Build All Examples

```bash
python build.py --mode prod --force build-examples
```

Output PDFs are placed in `build/examples/`.

## Customization

Change the doctype, language, and institution in your `.tex` file:

```latex
\documentclass[
  doctype=thesis,
  language=french,
  institution=tuhh,
]{omnilatex}
```

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guides on adding custom institutions,
languages, and doctypes.
