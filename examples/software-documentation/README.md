# Software Documentation Template

Complete software documentation with architecture diagrams, installation guides, configuration reference, API docs, CLI reference, code examples, and troubleshooting.

## Key Features

- Architecture, component, and deployment diagrams (TikZ)
- Data flow diagram with dead-letter queue
- Platform-specific installation table
- YAML configuration file with `minted`
- Environment variables and feature flags tables
- REST API endpoint documentation with request/response examples
- Error codes table
- CLI command reference
- Multi-language code examples (Python, Rust, Shell)
- Changelog with version history

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
software-documentation/
├── main.tex          # Complete documentation in one file
└── README.md
```

## Customization Tips

- Add new API endpoints by extending `tab:rest-api`
- Document new CLI commands in `tab:cli`
- Add changelog entries with `\subsection*{vX.Y.Z --- YYYY-MM-DD}`
- Use `\begin{minted}[caption={...}, label={lst:...}]{lang}` for captioned code
- Adjust TikZ node colours by changing `fill=<color>!15` values
