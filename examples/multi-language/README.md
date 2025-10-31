# Multi-Language Document Example

This example demonstrates the comprehensive multilingual capabilities of OmniLaTeX, showcasing proper support for multiple European languages with correct typography, hyphenation, and character rendering.

## Languages Supported

- **English** (main language)
- **German** (Deutsch)
- **French** (Français)
- **Spanish** (Español)
- **Italian** (Italiano)
- **Portuguese** (Português)

## Features Demonstrated

### Typography & Font Coverage
- Complete character coverage for all European languages
- Proper rendering of special characters:
  - German: ä, ö, ü, ß
  - French: à, â, é, è, ê, ë, î, ï, ô, ù, û, ü, ÿ
  - Spanish: ñ, á, é, í, ó, ú
  - Italian: à, è, é, ì, í, î, ò, ó, ù, ú, û, ü
  - Portuguese: ç, á, à, â, ã, é, ê, í, ó, ô, õ, ú, û

### Language Switching
- Seamless language switching using babel
- Proper hyphenation rules for each language
- Language-specific typography conventions

### Mixed Language Content
- Demonstrates mixing multiple languages within the same document
- Proper formatting for language-specific quotation marks and conventions
- International mathematical notation with multilingual labels

### Bibliography Support
- Unicode support in bibliography entries
- Language-specific sorting and formatting
- Proper handling of international author names and titles

## File Structure

```
examples/multi-language/
├── main.tex                    # Main document demonstrating multilingual features
├── bibliography.bib            # Sample bibliography with international entries
├── config/
│   └── document-settings.sty   # Document configuration
└── README.md                   # This file
```

## Compilation

To compile this example:

```bash
cd examples/multi-language
latexmk -pdflua main.tex
```

## Requirements

- LuaLaTeX engine
- OmniLaTeX class
- Babel package with language definitions
- Libertinus Serif font family (included with OmniLaTeX)
- Biber for bibliography processing

## Key Implementation Details

### Babel Configuration
```latex
\usepackage[main=english, ngerman, french, spanish, italian, portuguese]{babel}
```

### Language Switching
```latex
\foreignlanguage{german}{Deutscher Text mit Umlauten}
\selectlanguage{french}  % Switch document language
```

### Font Coverage
The example uses Libertinus Serif, which provides excellent coverage for all European languages, ensuring consistent and beautiful typography across all supported languages.

## Educational Value

This example serves as a comprehensive reference for:
- Setting up multilingual documents
- Proper language switching techniques
- International bibliography management
- Unicode character handling in LaTeX
- Best practices for multilingual typography

## Notes

- Each language section includes authentic sample text demonstrating common use cases
- Mathematical formulas are provided with multilingual labels
- Bibliography entries include both Latin and extended character sets
- The example maintains academic formatting standards while showcasing language diversity