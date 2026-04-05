# Editor Integration

Configuration snippets for popular LaTeX editors.

## VS Code

### Prerequisites

- [LaTeX Workshop](https://github.com/James-Yu/LaTeX-Workshop) extension
- OmniLaTeX built via Docker or Nix

### Setup

1. Open the OmniLaTeX-template repository in VS Code
2. Use the included Dev Container (recommended) or local setup
3. LaTeX Workshop auto-detects `.latexmkrc` and uses `latexmk -lualatex`

### Key Settings

The project includes `.vscode/settings.json` with OmniLaTeX-specific configuration:

```jsonc
{
  "latex-workshop.latex.tools": [
    {
      "name": "latexmk",
      "command": "latexmk",
      "args": [
        "-synctex=1",
        "-interaction=nonstopmode",
        "-file-line-error",
        "-lualatex",
        "-outdir=%OUTDIR%",
        "%DOC%"
      ]
    }
  ],
  "latex-workshop.latex.recipes": [
    {
      "name": "latexmk (LuaLaTeX)",
      "tools": ["latexmk"]
    }
  ]
}
```

### Build Tasks

Use `Ctrl+Shift+B` (or `Cmd+Shift+B` on macOS) to build. The included
`.vscode/tasks.json` provides:

- **Build**: Compile current document
- **Clean**: Remove auxiliary files
- **Test**: Run test suite
- **Doctor**: Environment health check

### PDF Preview

LaTeX Workshop provides a built-in PDF viewer with synctex support.
Click on the PDF to jump to the source, and vice versa.

## Vim / Neovim

### VimTeX

Install [VimTeX](https://github.com/lervag/vimtex):

```vim
" In ~/.vimrc or ~/.config/nvim/init.vim
Plug 'lervag/vimtex'

let g:vimtex_compiler_method = 'latexmk'
let g:vimtex_compiler_latexmk = {
    \ 'options' : [
    \   '-lualatex',
    \   '-verbose',
    \   '-file-line-error',
    \   '-synctex=1',
    \   '-interaction=nonstopmode',
    \],
    \}
```

### Build Commands

```vim
" Build current file
\ll          " Start continuous compilation
\lk          " Stop continuous compilation
\lv          " View compiled PDF
\le          " View errors
\lo          " Open table of contents
\lT          " Open table of contents in new tab
```

### LSP: texlab

Install [texlab](https://github.com/latex-lsp/texlab) for completion and diagnostics:

```vim
" With coc.nvim
:CocInstall coc-texlab

" With nvim-lspconfig
lua << EOF
require('lspconfig').texlab.setup({
  settings = {
    texlab = {
      build = {
        executable = 'latexmk',
        args = { '-lualatex', '-interaction=nonstopmode', '-synctex=1', '%f' },
        onSave = true,
        forwardSearchAfter = true,
      },
      forwardSearch = {
        executable = 'zathura',  " or 'skim' on macOS
        args = { '--synctex-forward', '%l', '%p' },
      },
    },
  },
})
EOF
```

## Emacs

### AUCTeX

AUCTeX is included in most Emacs distributions. Add to `~/.emacs.d/init.el`:

```elisp
;; AUCTeX configuration
(setq TeX-engine 'luatex)
(setq TeX-command-extra-options "-shell-escape")
(setq TeX-save-query nil)
(setq TeX-show-compilation t)

;; Use latexmk for compilation
(setq TeX-command "latexmk")
(setq TeX-command-default "latexmk")

;; PDF viewer with synctex
(setq TeX-view-program-selection '((output-pdf "PDF Tools")))
(setq TeX-source-correlate-start-server t)
```

### Build Commands

| Key | Command |
|-----|---------|
| `C-c C-c` | Compile (prompts for latexmk) |
| `C-c C-v` | View PDF |
| `C-c C-a` | Insert citation |
| `C-c C-m` | Insert math macro |
| `C-c C-e` | Insert environment |
| `C-c C-s` | Insert section |
| `C-c .` | Insert item |

### LSP: lsp-mode

```elisp
(use-package lsp-mode
  :hook (LaTeX-mode . lsp)
  :config
  (setq lsp-tex-server 'texlab))

(use-package lsp-ui
  :commands lsp-ui-mode)
```

## Common Settings

### OmniLaTeX-Specific Completion

All OmniLaTeX commands use the `omnilatex@` prefix (internal) or are
documented in `docs/api_reference.md`. Key user-facing commands:

| Command | Description |
|---------|-------------|
| `\documenttype{...}` | Set document type label |
| `\documentfontsize{...}` | Set font size |
| `\documentlayout{...}` | Set KOMA-Script layout |
| `\documentcolormode{...}` | Set color mode |
| `\documentlinespacing{...}` | Set line spacing |
| `\parens{...}` | Parentheses delimiters |
| `\brackets{...}` | Bracket delimiters |
| `\floor{...}` | Floor function |
| `\ceil{...}` | Ceiling function |
| `\bigO{...}` | Big-O notation |

### Synctex

All editors support synctex for source-PDF synchronization. OmniLaTeX
enables synctex by default via `.latexmkrc` (`-synctex=1`).

### Build with `build.py` (alternative to latexmk)

If you prefer `build.py` over direct `latexmk`:

```bash
# Build a specific example
python build.py build-example thesis

# Build with timing info
python build.py build-example thesis --timings

# Watch for changes
python build.py watch
```
