# Language Expansion Guide

## Current Status

OmniLaTeX supports 25+ languages via polyglossia. This guide explains how to add new languages.

## Supported Languages (Current)

| Language | Code | Script | Status |
|----------|------|--------|--------|
| English | english | Latin | Complete |
| German | german | Latin | Complete |
| French | french | Latin | Complete |
| Spanish | spanish | Latin | Complete |
| Italian | italian | Latin | Complete |
| Portuguese | portuguese | Latin | Complete |
| Dutch | dutch | Latin | Complete |
| Russian | russian | Cyrillic | Complete |
| Polish | polish | Latin | Complete |
| Czech | czech | Latin | Complete |
| Greek | greek | Greek | Complete |
| Turkish | turkish | Latin | Complete |
| Chinese | chinese | CJK | Complete |
| Japanese | japanese | CJK | Complete |
| Korean | korean | CJK | Complete |
| Arabic | arabic | Arabic | Complete |
| Hebrew | hebrew | Hebrew | Complete |
| Hindi | hindi | Devanagari | Complete |
| Thai | thai | Thai | Complete |
| Bengali | bengali | Bengali | Complete |
| Persian | persian | Arabic | Complete |
| Vietnamese | vietnamese | Latin | Complete |
| Swedish | swedish | Latin | Complete |
| Finnish | finnish | Latin | Complete |
| Danish | danish | Latin | Complete |

## Target Languages (40+)

### Priority 1: European Languages

| Language | Code | Script | polyglossia |
|----------|------|--------|-------------|
| Norwegian (Bokmal) | norsk | Latin | norsk |
| Norwegian (Nynorsk) | nynorsk | Latin | nynorsk |
| Icelandic | icelandic | Latin | icelandic |
| Irish | irish | Latin | irish |
| Welsh | welsh | Latin | welsh |
| Basque | basque | Latin | basque |
| Catalan | catalan | Latin | catalan |
| Galician | galician | Latin | galician |
| Romanian | romanian | Latin | romanian |
| Hungarian | hungarian | Latin | hungarian |
| Estonian | estonian | Latin | estonian |
| Latvian | latvian | Latin | latvian |
| Lithuanian | lithuanian | Latin | lithuanian |
| Slovenian | slovenian | Latin | slovenian |
| Serbian | serbian | Cyrillic | serbian |
| Croatian | croatian | Latin | croatian |
| Bulgarian | bulgarian | Cyrillic | bulgarian |

### Priority 2: Asian Languages

| Language | Code | Script | polyglossia |
|----------|------|--------|-------------|
| Thai | thai | Thai | thai |
| Bengali | bengali | Bengali | bengali |
| Tamil | tamil | Tamil | tamil |
| Telugu | telugu | Telugu | telugu |
| Hindi | hindi | Devanagari | hindi |
| Marathi | marathi | Devanagari | marathi |
| Gujarati | gujarati | Gujarati | gujarati |
| Kannada | kannada | Kannada | kannada |
| Malayalam | malayalam | Malayalam | malayalam |
| Sinhala | sinhala | Sinhala | sinhala |

### Priority 3: Other Scripts

| Language | Code | Script | polyglossia |
|----------|------|--------|-------------|
| Georgian | georgian | Georgian | georgian |
| Armenian | armenian | Armenian | armenian |
| Mongolian | mongolian | Cyrillic | mongolian |

## Adding a New Language

### Step 1: Generate Stubs

```bash
python build.py scaffold-language <language-name>
```

This creates `docs/language-guide-<language>.tex` with all translation keys.

### Step 2: Translate

Fill in all `???` placeholders with translated strings.

### Step 3: Update i18n Module

Add the language to `lib/language/omnilatex-i18n.sty`:

1. Add to `\setotherlanguages` list
2. Add `\DeclareTranslation` entries

### Step 4: Test

```latex
\documentclass[language=<language-name>]{omnilatex}
\begin{document}
\section{Test}
Hello World
\end{document}
```

### Step 5: Submit

Create a pull request with:

- Translated strings
- Test document
- Language documentation

## Translation Keys

All translation keys are defined in `lib/language/omnilatex-i18n.sty`:

| Key | English | Description |
|-----|---------|-------------|
| abstract | Abstract | Document abstract |
| bibliography | Bibliography | Bibliography title |
| contents | Contents | Table of contents |
| figure | Figure | Figure caption prefix |
| table | Table | Table caption prefix |
| listing | Listing | Code listing prefix |
| chapter | Chapter | Chapter heading |
| section | Section | Section heading |
| subsection | Subsection | Subsection heading |
| appendix | Appendix | Appendix heading |
| glossary | Glossary | Glossary title |
| index | Index | Index title |
| listfigures | List of Figures | List of figures |
| listtables | List of Tables | List of tables |
| listlistings | List of Listings | List of code listings |

## Community Contributions

We welcome language contributions! To contribute:

1. Fork the repository
2. Run `python build.py scaffold-language <language>`
3. Translate all stubs
4. Add to i18n module
5. Test compilation
6. Submit pull request

## Resource Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| polyglossia support | Yes | Yes |
| Font support | System fonts | Noto fonts |
| RTL support | Optional | Required for Arabic/Hebrew |
| CJK support | Optional | Required for CJK languages |

## Testing Matrix

Each new language must pass:

1. **Compilation test**: Document compiles without errors
2. **UTF-8 test**: All characters render correctly
3. **RTL test**: Right-to-left text works (if applicable)
4. **CJK test**: CJK characters work (if applicable)
5. **Hyphenation test**: Hyphenation patterns are correct
6. **Date format test**: Localized date formats work
7. **Number format test**: Localized number formats work
