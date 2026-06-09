# Exam Paper

A computer science exam with numbered questions, sub-parts, and designated answer spaces.

## Usage

    latexmk -lualatex main.tex

Or using the build system:

    python build.py build-example exam

## Class Options

| Option | Value | Description |
|--------|-------|-------------|
| doctype | exam | Exam paper doctype |
| language | english | English language support |
| institution | none | No institutional branding |

## Features Demonstrated

- `question` environment with point values
- `answer` environment with configurable height
- Enumerated sub-questions with custom labels (`(\alph*)`)
- Display mathematics (Big-O notation, summations, recurrences)
- Part marks with `\textit{[n marks]}`

## Notes

Uses the OmniLaTeX exam doctype which provides `question` and `answer` environments. Point values appear in brackets after each question. Answer spaces are sized to fit the expected response length.
