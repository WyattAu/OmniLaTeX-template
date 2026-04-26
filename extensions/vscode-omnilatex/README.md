# OmniLaTeX VS Code Extension

VS Code extension for the OmniLaTeX document class — provides quick commands for switching document types, institutions, languages, and building documents.

## Features

- **Doctype Picker** — Quickly switch between all 16 OmniLaTeX doctype profiles (thesis, article, CV, presentation, etc.)
- **Institution Switcher** — Select from available institution configs by scanning `config/institutions/`
- **Language Picker** — Switch between 12 supported languages
- **Build Commands** — Build current example, all examples, or run diagnostics via the integrated terminal
- **Snippets** — LaTeX snippets for OmniLaTeX documents, titles, abstracts, todos, and censored text

## Commands

| Command | Description |
|---|---|
| `OmniLaTeX: Change Document Type` | Opens a QuickPick to select a doctype |
| `OmniLaTeX: Change Institution` | Opens a QuickPick to select an institution |
| `OmniLaTeX: Change Language` | Opens a QuickPick to select a language |
| `OmniLaTeX: Build Current Document` | Builds the current `.tex` file via `build.py` |
| `OmniLaTeX: Build All Examples` | Builds all example documents |
| `OmniLaTeX: Run Diagnostics` | Runs `build.py doctor` to check the setup |
| `OmniLaTeX: Create New Project` | Creates a new OmniLaTeX project via `build.py init` |

## Installation

### From source

```bash
cd extensions/vscode-omnilatex
npm install
npm run compile
```

Then press `F5` in VS Code to launch the Extension Development Host.

### As a VSIX package

```bash
npx @vscode/vsce package
code --install-extension vscode-omnilatex-0.1.0.vsix
```

## Snippets

| Prefix | Description |
|---|---|
| `omnilatex` | Full OmniLaTeX document skeleton |
| `omnilatex-title` | Title, author, date metadata |
| `omnilatex-abstract` | Abstract environment |
| `todo` | `\todo{}` note |
| `censor` | `\censor{}` redacted text |

## Requirements

- VS Code >= 1.85.0
- Python 3 with OmniLaTeX `build.py` in the workspace root
