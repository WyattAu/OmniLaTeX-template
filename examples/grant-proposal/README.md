# Grant Proposal Template

A complete grant proposal with project summary, budget justification, timeline, risk assessment, organisational chart, and biographical sketches.

## Key Features

- Project summary with Intellectual Merit and Broader Impacts
- Gantt chart for project timeline (TikZ)
- Workflow flowchart with decision nodes
- Algorithm pseudocode in TikZ box
- Multi-year budget tables with subtotals and indirect costs
- Risk assessment matrix with impact ratings
- Organisational chart with team hierarchy
- Milestone and deliverable tracking tables
- Biographical sketch sections

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
grant-proposal/
├── main.tex          # Complete proposal in one file
└── README.md
```

## Customization Tips

- Adjust Gantt chart by modifying the `\foreach` loop coordinates
- Change budget categories and amounts in `tab:budget-summary`
- Add new milestones by extending `tab:milestones`
- Modify indirect cost rate in the budget calculation
- Use `\newpage` between major sections for clean page breaks
