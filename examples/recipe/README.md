# Recipe Cards

Chocolate chip cookies and spaghetti aglio e olio recipes demonstrating the recipe doctype.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example recipe

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | recipe | Recipe card doctype |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `ingredients` environment
- `instructions` environment
- `\recipeNote{}` for cooking tips and notes
- `\recipeMeta{key}{value}` for metadata (prep time, servings, difficulty, cuisine, calories)
- `\textdegree` for degree symbols
- Multi-recipe document with `\newpage` separator

## Notes

The `\recipeMeta` keys used are: prep, cook, servings, difficulty, cuisine, calories. Multiple recipes can be combined in one document with `\maketitle` and `\newpage` between them.
