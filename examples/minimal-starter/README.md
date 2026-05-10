# Minimal Starter Template

Quick-start boilerplate demonstrating all OmniLaTeX capabilities with minimal but idiomatic examples.

## Description

This template is designed for:

- **Learning OmniLaTeX**: See how to use each feature correctly
- **Quick Starts**: Copy and adapt for your own projects
- **Reference**: Idiomatic patterns for common tasks

Each chapter demonstrates one category of features with commented, copy-paste-ready examples.

## Features Demonstrated

- [x] Text formatting and Unicode support
- [x] Citations and bibliography
- [x] Cross-references (sections, figures, tables, equations)
- [x] Lists (itemize, enumerate, description)
- [x] Mathematics (inline and display)
- [x] Figures with TikZ
- [x] Tables with booktabs
- [x] Code listings with syntax highlighting
- [x] Glossaries and acronyms
- [x] Hyperlinks and URLs
- [x] Footnotes
- [x] Colors
- [x] Appendices

## Building

```bash
# From root
python build.py build-example minimal-starter

# From example directory
cd examples/minimal-starter
latexmk main.tex
```

## File Structure

```
minimal-starter/
├── main.tex                      # All content in one file
├── .latexmkrc                    # Build configuration
├── config/
│   └── document-settings.sty     # Title, author, metadata
└── README.md                     # This file
```

## Customization

### Quick Start

1. **Copy this template** to your project:

   ```bash
   cp -r examples/minimal-starter my-project
   ```

2. **Edit** `config/document-settings.sty`:
   - Change title, author, date
   - Update metadata

3. **Edit** `main.tex`:
   - Replace example content with your own
   - Keep the structure and patterns
   - Remove features you don't need

4. **Build**:

   ```bash
   cd my-project
   latexmk main.tex
   ```

### Expanding the Template

This minimal template uses a single-file structure. For larger projects:

1. **Split content** into separate files:

   ```
   content/
   ├── chapter1.tex
   ├── chapter2.tex
   └── chapter3.tex
   ```

2. **Include files** in main.tex:

   ```latex
   \import{content/}{chapter1}
   \import{content/}{chapter2}
   \import{content/}{chapter3}
   ```

3. **See** `thesis-tuhh` or `thesis-generic` for multi-file examples

### Adding Your Own Content

#### New Chapter

```latex
\chapter{Your Chapter Title}

Your content here...
```

#### New Section

```latex
\section{Your Section}

Content...

\subsection{Subsection}

More content...
```

#### Figure

```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{image.pdf}
    \caption{Your caption}
    \label{fig:yourlabel}
\end{figure}
```

#### Table

```latex
\begin{table}[htbp]
    \centering
    \caption{Your table}
    \label{tab:yourlabel}
    \begin{tabular}{lcc}
        \toprule
        Column 1 & Column 2 & Column 3 \\
        \midrule
        Data & Data & Data \\
        \bottomrule
    \end{tabular}
\end{table}
```

#### Code Listing

```latex
\begin{listing}[htbp]
\begin{minted}{python}
# Your code here
def example():
    pass
\end{minted}
\caption{Your code caption}
\label{lst:yourlabel}
\end{listing}
```

#### Citation

```latex
According to \cite{key}, ...
```

Add entry to `../../bib/bibliography.bib`:

```bibtex
@article{key,
    author = {Author Name},
    title = {Article Title},
    journal = {Journal Name},
    year = {2024},
}
```

#### Glossary Term

```latex
The \gls{term} is defined...
```

Add to `../../bib/glossaries/abbreviations.bib`:

```bibtex
@abbreviation{term,
    short = {TERM},
    long  = {Term Long Form},
}
```

## Document Class Options

In `main.tex`, you can modify options:

```latex
\documentclass[
    language=english,     % or german
    institution=none,     % or tuhh for TUHH branding
    oneside,             % or twoside for printing
    loadGlossaries,      % enable glossaries
    % todonotes,         % enable TODO notes
    % censoring=true,    % enable \censor{} commands
]{../../omnilatex}
```

## Common Patterns

### Multiple Authors

```latex
\author{%
    First Author\and
    Second Author\and
    Third Author%
}
```

### Custom Date

```latex
\date{January 15, 2024}
% or
\date{\DTMdate{2024-01-15}}
```

### Suppress Page Numbers

```latex
\pagestyle{empty}  % No headers/footers
```

### Change Paper Size

```latex
\documentclass[
    a5,  % A5 paper (default is A4)
    ...
]{../../omnilatex}
```

### Two-Column Layout

```latex
\documentclass[
    twocolumn,  % Two-column layout
    ...
]{../../omnilatex}
```

## Tips

### Starting Fresh

1. Use this template to learn the syntax
2. Check the generated PDF for examples
3. Copy patterns you need to your document
4. Remove features you don't use

### Getting Help

- **Check the example**: Read the LaTeX source in `main.tex`
- **View the PDF**: See the rendered output
- **Compare**: Look at other examples (thesis-tuhh, etc.)
- **Documentation**: Read the [examples README](../README.md)

### Common Mistakes

- **Wrong**: `\cite{key}` but key not in .bib file
- **Right**: Add entry to bibliography.bib first

- **Wrong**: `\ref{fig:label}` but label doesn't exist
- **Right**: Add `\label{fig:label}` after `\caption{}`

- **Wrong**: `\gls{term}` but term not defined
- **Right**: Add term to glossaries/*.bib first

### Best Practices

1. **Labels**: Use prefixes (`fig:`, `tab:`, `eq:`, `sec:`)
2. **Citations**: Cite early and often
3. **Comments**: Add % comments to explain your LaTeX
4. **Structure**: Keep content organized
5. **Compile**: Build frequently to catch errors early

## Troubleshooting

### Bibliography Not Showing

- Ensure you have `\cite{}` commands
- Check `\addbibresource{}` path
- Run latexmk (it handles multiple passes)

### Glossaries Not Appearing

- Add terms to `../../bib/glossaries/*.bib`
- Use `\gls{}` commands in text
- Enable `loadGlossaries` in documentclass
- Ensure bib2gls is installed

### Code Highlighting Not Working

- Minted requires Python and Pygments
- Install: `pip install Pygments`
- Or use `listings` package instead

### TikZ Errors

- Check syntax carefully
- Start simple, add complexity gradually
- See TikZ manual: `texdoc tikz`

## Next Steps

Once you're comfortable with this template:

1. **Explore other examples**:
   - `thesis-tuhh`: Full-featured thesis
   - `report`: Technical reports
   - `article`: Academic papers

2. **Read documentation**:
   - [OmniLaTeX Architecture](../../OMNILATEX_ARCHITECTURE.md)
   - [Examples README](../README.md)
   - Package documentation: `texdoc <package-name>`

3. **Customize further**:
   - Add custom commands
   - Load additional packages
   - Create your own style

## Related Examples

- **[thesis-tuhh](../thesis-tuhh/)**: Comprehensive thesis with TUHH branding
- **[thesis-generic](../thesis-generic/)**: Generic thesis template
- **[examples README](../README.md)**: Overview of all examples

## Requirements

- LaTeX distribution (TeXLive 2020+ or MiKTeX)
- LuaLaTeX (automatically used by .latexmkrc)
- Python 3+ with Pygments (for minted code highlighting)
- bib2gls (for glossaries)

### Docker Alternative

```bash
docker run --rm -v $(pwd):/tex -w /tex/examples/minimal-starter \
    ghcr.io/wyattau/omnilatex-docker:latest \
    latexmk main.tex
```

---

**Start building your document!**

This template gives you everything you need to get started with OmniLaTeX.
