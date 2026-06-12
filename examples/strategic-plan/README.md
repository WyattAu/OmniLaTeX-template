# Strategic Plan Template

A multi-year strategic plan with vision/mission statements, strategic pillars, SWOT analysis, competitive landscape, roadmap, risk matrix, and KPI dashboard.

## Key Features

- Vision and Mission boxes with `tcolorbox` styling
- Revenue growth projections with bar charts
- Product leadership progress (horizontal bar chart)
- SWOT analysis matrix with colour-coded quadrants
- Competitive capability comparison table
- Implementation roadmap with phased timeline (TikZ)
- Risk matrix with likelihood vs. impact plotting
- Multi-year budget and headcount tables
- Governance structure org chart
- KPI dashboard across financial, customer, product, and people dimensions

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
strategic-plan/
├── main.tex          # Complete plan in one file
└── README.md
```

## Customization Tips

- Modify strategic pillars by adding new `\subsection{Pillar N: ...}` blocks
- Adjust the roadmap timeline by changing `\foreach` coordinates
- Update risk positions in the TikZ risk matrix scatter plot
- Use `\addplot` coordinates to extend projection charts to new years
- Customise `tcolorbox` with `colback` and `colframe` for branded boxes
