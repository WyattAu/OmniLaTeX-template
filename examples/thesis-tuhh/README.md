# TUHH Thesis Example

A comprehensive thesis template with full TUHH (Hamburg University of Technology) branding and ITT (Institute of Engineering Thermodynamics) styling.

## Description

This example demonstrates a complete thesis setup for TUHH students, featuring:
- **Institutional Branding**: TUHH and ITT logos, colors, and styling
- **Custom Title Page**: TUHH-specific title page layout with examiners and supervisor
- **Complete Structure**: Front matter, main matter, and back matter organization
- **All OmniLaTeX Features**: Comprehensive showcase of capabilities including:
  - Bibliography management with BibLaTeX
  - Glossaries, acronyms, and symbols
  - Code listings with syntax highlighting
  - Figures, tables, and floats
  - TikZ graphics and diagrams
  - Mathematical typesetting
  - Cross-referencing and indexing

## Building

### From Root Directory
```bash
# Using Python build script
python build.py build-example thesis-tuhh

# Output will be in: build/examples/thesis-tuhh.pdf
```

### From Example Directory
```bash
cd examples/thesis-tuhh
latexmk main.tex
```

### Using VSCode
Use the task "Build: TUHH Thesis Example" from the Command Palette (Ctrl+Shift+P > Tasks: Run Task)

## Structure

```
thesis-tuhh/
├── main.tex                          # Main document file
├── .latexmkrc                        # Build configuration
├── config/
│   └── document-settings.sty         # Title, author, metadata settings
├── content/
│   ├── frontmatter.tex               # Front matter (abstract, TOC, etc.)
│   ├── mainmatter.tex                # Main content chapters
│   ├── backmatter.tex                # Appendices, bibliography
│   ├── frontmatter/
│   │   ├── abstract.tex
│   │   ├── authorship_declaration.tex
│   │   ├── colophon.tex
│   │   └── dedication.tex
│   ├── mainmatter/
│   │   ├── base-features.tex         # Basic LaTeX features
│   │   ├── code-listings.tex         # Code examples
│   │   ├── floats.tex                # Figures and tables
│   │   ├── graphics.tex              # TikZ and graphics
│   │   ├── introduction.tex
│   │   └── math.tex                  # Mathematical notation
│   └── backmatter/
│       ├── 01_appendix.tex
│       └── 02_appendix.tex
└── README.md                         # This file
```

## Customization

### Personal Information
Edit `config/document-settings.sty` to customize:
- **Document type**: Master Thesis, PhD Thesis, Bachelor Thesis, etc.
- **Title**: Your thesis title
- **Author**: Your name
- **Date**: Submission date
- **Examiners**: First and second examiner names
- **Supervisor**: Your supervisor's name
- **Student ID**: Your matriculation number

### Content
- **Front Matter**: Edit files in `content/frontmatter/`
  - `abstract.tex`: Your abstract
  - `authorship_declaration.tex`: Declaration of authorship
  - `dedication.tex`: Optional dedication
  
- **Main Matter**: Edit files in `content/mainmatter/`
  - Replace example chapters with your own content
  - Add new chapter files as needed
  - Update `content/mainmatter.tex` to include your chapters

- **Back Matter**: Edit files in `content/backmatter/`
  - Add appendices as needed
  - Bibliography is automatically generated from `bib/bibliography.bib`

### Document Class Options
In `main.tex`, you can modify the `\documentclass` options:

```latex
\documentclass[
    language=english,        % or german
    institution=tuhh,        % TUHH-specific features
    twoside,                 % or oneside for screen viewing
    titlestyle=TUHH,         % TUHH-specific title page
    BCOR=5mm,                % Binding correction for printing
    censoring=true,          % Enable \censor{} commands
    loadGlossaries,          % Enable glossaries
    todonotes,               % Enable \todo{} commands
]{../../omnilatex}
```

### Bibliography
- Add references to `../../bib/bibliography.bib` (shared bibliography)
- Or create a local `bib/bibliography.bib` and update the path in `main.tex`

### Glossaries and Acronyms
- Located in `../../bib/glossaries/`
- Add terms to `abbreviations.bib`, `symbols/*.bib`, etc.
- Automatically compiled with bib2gls

## TUHH-Specific Features

### Title Page Style
The TUHH title page includes:
- Vertical line design element
- TUHH and ITT logos with hyperlinks
- Document type badge with icon
- Author, date, and title
- Examiners and supervisor table
- Publisher information

### Institution Configuration
The TUHH configuration (`config/institutions/tuhh/tuhh.sty`) provides:
- **Logos**: Automatically language-aware (German/English)
- **Links**: Official TUHH and ITT websites
- **Branding**: TUHH colors and styling
- **Custom Graphics**: TikZ pics (e.g., `TUHHuman`)

### Changing to Generic Style
To remove TUHH branding, change in `main.tex`:
```latex
institution=none,           % Remove TUHH branding
titlestyle=book,            % Use generic title page
```

## Common Tasks

### Adding a New Chapter
1. Create `content/mainmatter/your-chapter.tex`
2. Add to `content/mainmatter.tex`:
   ```latex
   \import{mainmatter/}{your-chapter}
   ```

### Adding Figures
```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{../../assets/yourimage.pdf}
    \caption{Your caption}
    \label{fig:yourlabel}
\end{figure}
```

### Adding Citations
```latex
Text with citation \cite{key}.
Multiple citations \cite{key1,key2}.
```

### Adding Acronyms
In `../../bib/glossaries/abbreviations.bib`:
```bibtex
@abbreviation{tuhh,
    short = {TUHH},
    long  = {Hamburg University of Technology},
}
```

Use in text: `\gls{tuhh}` (first use shows full, subsequent uses show short)

### Code Listings
```latex
\begin{listing}[htbp]
\begin{minted}{python}
def hello_world():
    print("Hello, World!")
\end{minted}
\caption{Hello World in Python}
\label{lst:hello}
\end{listing}
```

## Requirements

### Software
- **LaTeX Distribution**: TeXLive 2020+ or MiKTeX
- **LuaLaTeX**: Required (set by default in .latexmkrc)
- **latexmk**: Build automation tool
- **bib2gls**: For glossaries (included in TeXLive)
- **biber**: For bibliography (included in TeXLive)

### Docker (Recommended)
Use the OmniLaTeX Docker image for a complete, pre-configured environment:
```bash
docker run --rm -v $(pwd):/tex -w /tex/examples/thesis-tuhh \
    ghcr.io/wyattau/omnilatex-docker:latest \
    latexmk main.tex
```

## Tips

### Compilation Time
First compilation takes 5-15 minutes due to:
- Font loading and caching
- TikZ externalization
- Bibliography processing
- Glossary generation

Subsequent builds are much faster (1-3 minutes) as cached data is reused.

### PDF Size
The example PDF is large (~5-10 MB) because it includes:
- Many figures and diagrams
- Embedded fonts
- High-resolution images

Your actual thesis will likely be smaller if you use fewer graphics.

### Troubleshooting

**Error: File `omnilatex.cls` not found**
- Ensure you're building from the example directory with correct relative paths
- The class file should be at `../../omnilatex.cls`

**Error: Bibliography not appearing**
- Run latexmk multiple times (it handles this automatically)
- Check that bib file exists at `../../bib/bibliography.bib`

**Error: Glossaries not appearing**
- Ensure bib2gls is installed
- Check that glossary files exist in `../../bib/glossaries/`

**Warnings about undefined references**
- Normal on first run
- Should disappear after latexmk completes all passes

## Related Examples

- **[thesis-generic](../thesis-generic/)**: Generic thesis without institution branding
- **[minimal-starter](../minimal-starter/)**: Quick start boilerplate
- **[report](../report/)**: Technical report format

## Further Reading

- [OmniLaTeX Documentation](../../OMNILATEX_ARCHITECTURE.md)
- [TUHH LaTeX Wiki](https://collaborating.tuhh.de/m21/public/wiki/-/wikis/home)
- [Migration Guide](../../EXAMPLES_MIGRATION_PLAN.md)

## License

This template follows the same license as the main OmniLaTeX project.

---

**Need help?** Check the main examples [README](../README.md) or review the comprehensive features in the generated PDF.
