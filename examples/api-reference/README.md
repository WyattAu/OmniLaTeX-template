# API Reference Template

A comprehensive REST API reference with authentication methods, rate limiting, endpoint documentation, data models, webhooks, SDK examples, and error reference.

## Key Features

- Colour-coded HTTP method commands (`\methodget`, `\methodpost`, etc.)
- Request/Response boxes with `tcolorbox` styling
- Authentication section (API key, OAuth 2.0, JWT Bearer)
- Rate limits table by plan tier
- Endpoint tables for Users, Projects, Tasks
- Data model schema tables with `tabularx`
- Webhook event types and payload examples
- SDK code examples (Python, JavaScript, Go)
- Long error reference table spanning pages
- API versioning and deprecation policy

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
api-reference/
├── main.tex          # Complete API reference in one file
└── README.md
```

## Customization Tips

- Add new endpoints by creating a new `\subsubsection{}` with req/res boxes
- Define additional HTTP method commands with `\newcommand{\methodpatch}{...}`
- Extend schema tables with new fields in `tabularx` format
- Add webhook events by appending rows to `tab:webhook-events`
- Use `\begin{reqbox}[--- \texttt{POST /v2/...}]` for consistent request formatting
