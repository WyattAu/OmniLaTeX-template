# Presentation (Non-Beamer)

A non-beamer presentation using OmniLaTeX's custom presentation doctype with page-based slides.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example presentation

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | presentation | Non-beamer presentation doctype |
| language | English | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `presentationframe` environment for slide pages
- `\slidetitle` for slide headings
- `\presentationSection` for section divider slides
- Block variants: `presentationblock`, `definitionblock`, `exampleblock`, `alertblock`, `noteblock`
- `multicols` layout within slides
- Custom institute definition

## Notes

This is OmniLaTeX's own presentation system (not Beamer). It produces a regular PDF where each `presentationframe` is a separate page. Suitable for simpler presentations that don't need Beamer's overlay features.
