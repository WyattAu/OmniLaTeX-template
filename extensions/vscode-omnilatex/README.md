# OmniLaTeX VS Code Extension

Minimal VS Code extension for the OmniLaTeX LaTeX document class.

## Features

- **Switch Document Type**: Quick-pick from 25 document types (article, thesis, book, etc.)
- **Switch Institution**: Quick-pick from 14 institution configs
- **Document Class Snippet**: Auto-complete OmniLaTeX documentclass options
- **Build Commands**: Quick access to build.py commands

## Installation

1. Clone this repository
2. Copy `extensions/vscode-omnilatex/` to `~/.vscode/extensions/omnilatex/`
3. Reload VS Code window

## Usage

- Open a LaTeX file
- `Ctrl+Shift+P` → "OmniLaTeX: Switch Document Type"
- `Ctrl+Shift+P` → "OmniLaTeX: Switch Institution"

## Development

```bash
cd extensions/vscode-omnilatex
npm install
code --extensionDevelopmentPath . --extensionDevelopmentHost .
```

## License

Apache 2.0
