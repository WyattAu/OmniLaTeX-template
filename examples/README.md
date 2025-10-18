# OmniLaTeX Examples

Welcome to the OmniLaTeX examples collection! This directory contains complete, ready-to-use template documents demonstrating OmniLaTeX capabilities for various document types.

## Overview

Each example is a self-contained project that showcases how to use OmniLaTeX for a specific purpose. All examples use the same core `omnilatex.cls` class but with different configurations and content structures.

## Available Examples

### 📚 thesis-tuhh
**Full-featured thesis with TUHH (Hamburg University of Technology) branding**

A comprehensive thesis template showcasing all OmniLaTeX features with institution-specific styling, logos, and title pages.

- **Best for**: TUHH students, comprehensive feature demonstration
- **Document type**: Master/PhD/Bachelor thesis
- **Pages**: ~50+ (comprehensive showcase)
- **Features**: All features enabled, TUHH branding, ITT styling
- **Status**: ✅ Complete

[View README](thesis-tuhh/README.md) | [View Structure](thesis-tuhh/)

---

### 📖 thesis-generic *(Coming Soon)*
**Clean thesis template without institution branding**

A generic thesis template suitable for any university or institution.

- **Best for**: Students at any institution, generic academic work
- **Document type**: Master/PhD/Bachelor thesis
- **Features**: All core features, generic title page
- **Status**: ⏳ Planned

---

### 📄 report *(Coming Soon)*
**Technical and scientific reports**

Optimized for technical reports, lab reports, and project documentation.

- **Best for**: Course reports, technical documentation
- **Document type**: Report
- **Features**: Sections (not chapters), compact layout
- **Status**: ⏳ Planned

---

### 📰 article *(Coming Soon)*
**Journal and conference articles**

Academic paper template with optional two-column layout.

- **Best for**: Journal submissions, conference papers
- **Document type**: Article
- **Features**: Compact, citation-heavy, minimal front matter
- **Status**: ⏳ Planned

---

### 📕 book *(Coming Soon)*
**Books, manuals, and extensive documentation**

Professional book layout with chapters, parts, and comprehensive structure.

- **Best for**: Books, manuals, long-form documentation
- **Document type**: Book
- **Features**: Part divisions, professional typography
- **Status**: ⏳ Planned

---

### 📋 cv *(Coming Soon)*
**Curriculum Vitae / Resume**

Professional CV/resume template.

- **Best for**: Job applications, academic CVs
- **Document type**: CV
- **Features**: Compact layout, contact information, experience sections
- **Status**: ⏳ Planned

---

### ⚡ minimal-starter *(Coming Soon)*
**Minimal boilerplate with all features demonstrated**

Quick-start template showing idiomatic usage of all major features in minimal pages.

- **Best for**: Learning OmniLaTeX, starting new projects
- **Document type**: Any
- **Pages**: 5-10 (one page per feature)
- **Features**: All features demonstrated minimally with extensive comments
- **Status**: ⏳ Planned

---

## Using Examples

### Building Examples

#### Option 1: Python Build Script (Recommended)
```bash
# From repository root

# List all available examples
python build.py list-examples

# Build a specific example
python build.py build-example thesis-tuhh

# Build all examples
python build.py build-examples

# Clean example artifacts
python build.py clean-example thesis-tuhh
python build.py clean-examples
```

Built PDFs are placed in `build/examples/`.

#### Option 2: Direct LaTeX Compilation
```bash
# Navigate to example directory
cd examples/thesis-tuhh

# Build with latexmk
latexmk main.tex

# PDF will be generated in the example directory
```

#### Option 3: VSCode Tasks
If using Visual Studio Code:
1. Copy `config/vscode-tasks.json` to `.vscode/tasks.json`
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Select "Tasks: Run Task"
4. Choose an example build task

### Starting Your Own Project

1. **Choose the most appropriate example** for your document type
2. **Copy the example directory** to your project location:
   ```bash
   cp -r examples/thesis-tuhh ~/my-thesis
   ```
3. **Navigate to your copy**:
   ```bash
   cd ~/my-thesis
   ```
4. **Customize** `config/document-settings.sty` with your information
5. **Edit content** in the `content/` directory
6. **Build**:
   ```bash
   latexmk main.tex
   ```

### Docker Usage

Use the OmniLaTeX Docker image for a complete environment:

```bash
# Build an example
docker run --rm -v $(pwd):/tex -w /tex/examples/thesis-tuhh \
    ghcr.io/wyattau/omnilatex-docker:latest \
    latexmk main.tex

# Interactive shell
docker run --rm -it -v $(pwd):/tex -w /tex \
    ghcr.io/wyattau/omnilatex-docker:latest \
    bash
```

## Example Structure

All examples follow a consistent structure:

```
example-name/
├── main.tex                    # Main document file
├── .latexmkrc                  # Build configuration
├── config/
│   └── document-settings.sty   # Document-specific settings
├── content/                    # Document content
│   ├── frontmatter/            # Front matter (abstract, TOC, etc.)
│   ├── mainmatter/             # Main content
│   └── backmatter/             # Appendices, bibliography
└── README.md                   # Example-specific documentation
```

### Key Files

#### `main.tex`
The entry point for your document. Specifies:
- Document class options (language, institution, paper size, etc.)
- Preamble customizations
- Document structure (front/main/back matter)

#### `.latexmkrc`
Build configuration that:
- Sources root `.latexmkrc` for common settings
- Can add example-specific overrides
- Configures latexmk build automation

#### `config/document-settings.sty`
Document metadata including:
- Title, author, date
- Examiners and supervisors (for theses)
- PDF metadata
- Document-type-specific settings

#### `content/`
Your actual content:
- **frontmatter**: Abstract, dedication, table of contents, etc.
- **mainmatter**: Chapters or sections with your content
- **backmatter**: Appendices, bibliography, index

## Shared Resources

All examples share these root-level resources:

### Core Class
- **`omnilatex.cls`**: Main document class referenced as `../../omnilatex.cls`

### Libraries
- **`lib/`**: Modular LaTeX packages for specific functionality
  - `lib/core/`: Base functionality
  - `lib/typography/`: Fonts, math, typesetting
  - `lib/graphics/`: TikZ, figures, graphics
  - `lib/code/`: Code listings
  - `lib/tables/`: Table formatting
  - `lib/references/`: Bibliography, glossaries, hyperlinks
  - `lib/layout/`: Page layout, boxes, floats

### Configuration
- **`config/institutions/`**: Institution-specific configurations (TUHH, etc.)
- **`config/layouts/`**: Page layout configurations
- **`config/document-types/`**: Document type specific settings

### Assets
- **`assets/fonts/`**: Custom fonts
- **`assets/icons/`**: Icons and symbols
- **`assets/code/`**: Example source code files
- **`assets/data/`**: Example data files
- **`assets/logos/`**: Logos (institution-specific)

### Bibliography
- **`bib/bibliography.bib`**: Shared bibliography database
- **`bib/glossaries/`**: Shared glossary definitions, acronyms, symbols

## Customization Guide

### Changing Document Class Options

In your example's `main.tex`, modify the `\documentclass` options:

```latex
\documentclass[
    language=english,        % Language: english, german
    institution=tuhh,        % Institution: tuhh, none
    twoside,                 % Sides: twoside, oneside
    titlestyle=TUHH,         % Title: TUHH, book, thesis
    BCOR=5mm,                % Binding correction
    censoring=true,          % Enable \censor{} commands
    loadGlossaries,          % Load glossaries
    todonotes,               % Enable \todo{} notes
]{../../omnilatex}
```

### Common Options

| Option | Values | Description |
|--------|--------|-------------|
| `language` | `english`, `german` | Document language |
| `institution` | `tuhh`, `none` | Institution configuration |
| Paper sides | `twoside`, `oneside` | For printing or screen |
| `titlestyle` | `TUHH`, `book`, `thesis` | Title page style |
| `BCOR` | `5mm`, `10mm`, etc. | Binding correction |
| `a5` | flag | Use A5 paper (default A4) |
| `loadGlossaries` | flag | Enable glossaries |
| `todonotes` | flag | Enable TODO notes |
| `censoring` | `true`, `false` | Enable censoring |

### Adding Your Own Content

1. **Create new content files** in `content/mainmatter/`
2. **Include them** in `content/mainmatter.tex`:
   ```latex
   \import{mainmatter/}{your-new-file}
   ```
3. **Build** to see changes

### Using Local Bibliography

If you don't want to use the shared bibliography:

1. **Create** `bib/bibliography.bib` in your example directory
2. **Update** `main.tex`:
   ```latex
   \addbibresource{bib/bibliography.bib}
   ```

### Disabling Features

Comment out or remove options you don't need:
```latex
\documentclass[
    language=english,
    % loadGlossaries,    % Commented out to disable
    % todonotes,         % Commented out to disable
]{../../omnilatex}
```

## Troubleshooting

### Build Errors

**Error: `omnilatex.cls` not found**
- Ensure relative path is correct: `../../omnilatex.cls`
- Build from the example directory or use the build script

**Error: Bibliography not appearing**
- Run latexmk (it automatically reruns as needed)
- Check bib file path in `main.tex`

**Error: Glossaries not appearing**
- Ensure `bib2gls` is installed
- Check glossary file paths
- Enable with `loadGlossaries` option

### Performance

**First compilation is slow (5-15 minutes)**
- Normal for complex documents
- Fonts, TikZ, and bibliography processing take time
- Subsequent builds are faster (1-3 minutes)

**PDF is very large**
- Example documents include many graphics
- Your actual document will likely be smaller
- Use `\includegraphics[width=...]` to optimize image size

### Platform-Specific Issues

**Windows**: Use forward slashes in paths even on Windows
**macOS**: Ensure MacTeX is up to date
**Linux**: Install full TeXLive distribution

## Requirements

### Software

#### Required
- **LaTeX Distribution**: TeXLive 2020+ or MiKTeX
- **LuaLaTeX**: Included in distributions (auto-selected)
- **latexmk**: Build automation (included in distributions)
- **biber**: Bibliography backend (included in distributions)
- **bib2gls**: Glossary processor (included in TeXLive)

#### Optional
- **Docker**: For containerized builds
- **Visual Studio Code**: With LaTeX Workshop extension
- **Git**: For version control

### Docker (Recommended)

The easiest way to get started:
```bash
# Pull the image
docker pull ghcr.io/wyattau/omnilatex-docker:latest

# Build an example
docker run --rm -v $(pwd):/tex -w /tex \
    ghcr.io/wyattau/omnilatex-docker:latest \
    python build.py build-example thesis-tuhh
```

## Contributing

### Adding New Examples

1. **Create directory**: `examples/new-example/`
2. **Add files**:
   - `main.tex` (with `\documentclass{../../omnilatex}`)
   - `.latexmkrc` (sourcing root config)
   - `config/document-settings.sty`
   - `content/` with relevant structure
   - `README.md` with description and usage
3. **Test build**: `python build.py build-example new-example`
4. **Submit PR** with your new example

### Improving Examples

- Fix typos or errors
- Add better explanations
- Improve documentation
- Optimize build times
- Add new features demonstrations

## Resources

### Documentation
- **[Main README](../README.md)**: Project overview
- **[OmniLaTeX Architecture](../OMNILATEX_ARCHITECTURE.md)**: Technical details
- **[Migration Plan](../EXAMPLES_MIGRATION_PLAN.md)**: Examples migration strategy
- **Individual Example READMEs**: Specific usage instructions

### External Resources
- **[LaTeX Project](https://www.latex-project.org/)**: Official LaTeX documentation
- **[CTAN](https://ctan.org/)**: Package documentation
- **[TeX StackExchange](https://tex.stackexchange.com/)**: Community Q&A
- **[Overleaf Guides](https://www.overleaf.com/learn)**: Tutorials and guides

### OmniLaTeX Specific
- **[GitHub Repository](https://github.com/WyattAu/OmniLaTeX-template)**: Source code
- **[Issue Tracker](https://github.com/WyattAu/OmniLaTeX-template/issues)**: Bug reports
- **[Discussions](https://github.com/WyattAu/OmniLaTeX-template/discussions)**: Community forum

## FAQ

### How do I choose which example to use?
- **Thesis (institutional)**: Use `thesis-tuhh` if you're at TUHH
- **Thesis (generic)**: Use `thesis-generic` for other institutions
- **Short document**: Use `report` or `article`
- **Book**: Use `book` for long-form content
- **Resume**: Use `cv`
- **Learning**: Use `minimal-starter`

### Can I mix features from different examples?
Yes! All examples use the same core class. Copy configuration options you like between examples.

### Do I need to keep the omnilatex.cls in a parent directory?
For standalone projects, you can copy `omnilatex.cls` and `lib/` to your project directory and update the paths in `main.tex`.

### Can I use this for commercial projects?
Check the license file in the root directory.

### How do I get help?
1. Check the example's README
2. Check this document
3. Search issues on GitHub
4. Ask on GitHub Discussions
5. Open a new issue

## License

Examples inherit the license from the main OmniLaTeX project. See [LICENSE](../LICENSE) file.

---

**Happy LaTeXing!** 🎓✨

For more information, see the [main README](../README.md) or dive into a specific [example](thesis-tuhh/).
