# Quarterly Report Template

A corporate quarterly report with KPI dashboards, financial statements, department reviews, risk heatmaps, and strategic initiative tracking.

## Key Features

- KPI dashboard table with colour-coded status indicators
- Revenue trend bar charts with trend lines
- Stacked expense comparison charts
- Customer growth trajectory plots
- Risk heatmap matrix (TikZ)
- Department status tables (Engineering, Sales, Marketing)
- Strategic initiative tracker with progress percentages
- Condensed balance sheet and cash flow statement
- Q3 guidance scenario table

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
quarterly-report/
├── main.tex          # Complete report in one file
└── README.md
```

## Customization Tips

- Update KPI values in the executive summary table
- Modify the risk heatmap by adjusting TikZ matrix cell positions
- Add new departments by creating additional `\subsection{}` blocks
- Use `\cellcolor{green!20}` for positive and `\cellcolor{red!20}` for negative indicators
- Adjust bar chart `symbolic x coords` to match your quarter labels
