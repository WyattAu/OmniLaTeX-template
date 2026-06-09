# Lua Integration Showcase

Demonstrates LuaLaTeX's embedded Lua engine with practical examples including computation, string processing, and dynamic table generation.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example lua-showcase

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | article | Standard article layout |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `\luadirect{}` for inline Lua execution
- `luacode` environment for Lua function definitions
- Fibonacci computation with memoization
- Prime number generation and table rendering
- String processing (title case, number extraction)
- CSV parsing into LaTeX tables
- Custom Lua-backed LaTeX commands (`\smartdate`, `\luasum`, `\storedata`, `\retrieve`)
- `\tex.sprint()` for Lua-to-TeX output
- TikZ scatter plot generated from Lua random data
- File I/O (reading external `.sty` files)

## Notes

Requires LuaLaTeX engine (not XeLaTeX or pdfLaTeX). The file I/O section reads `lib/language/omnilatex-i18n.sty` and may not work in sandboxed CI environments. All Lua code runs at compile time.
