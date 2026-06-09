# Plugin System Demo

Demonstrates OmniLaTeX's plugin architecture for extending the class with custom formatting.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example plugin-demo

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | article | Standard article layout |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `\RegisterPlugin{}` and `\LoadPlugins` for plugin management
- Plugin API (access to `\omnilatex@language`, `\omnilatex@doctype`, `\omnilatex@institution`)
- Plugin creation guide (`.sty` file in `config/plugins/`)
- `kvoptions` integration for plugin-specific options
- Built-in LaTeX hooks (`begindocument/end`, `cmd/omnilatexusetheme/before`, `cmd/maketitle/before`)
- `verbatim` code examples

## Notes

The example plugin registration lines are commented out. Create `.sty` files in `config/plugins/` and register them with `\RegisterPlugin{filename}` (without the `.sty` extension).
