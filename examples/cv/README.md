# CV / Resume Template

A professional curriculum vitae with skill bars, timeline entries, multi-column layout, and TikZ visualisations for language proficiency.

## Key Features

- Custom `\cvitem`, `\cvskillbar`, and `\cvtimelineentry` commands
- Skill proficiency bars drawn with TikZ
- Multi-column skill categories using `tabularx`
- Language proficiency indicators with proportional bars
- Icon-decorated section headers via `\faIcon`
- Structured entries for experience, education, projects, publications, and awards
- Custom colour scheme for accent, skills, links, and sections

## Build

```bash
latexmk -lualatex main.tex
```

## File Structure

```
cv/
├── main.tex          # Complete CV in one file
└── README.md
```

## Customization Tips

- Redefine `\cvskillbar{<percentage>}{<label>}` to adjust bar widths
- Modify the colour palette by changing `cvaccent`, `cvskill`, `cvlink` definitions
- Use `\cvtimelineentry{date}{title}{description}` for experience timelines
- Add new sections by following the `\section{\texorpdfstring{...}{}}` pattern
- Adjust `\cvbulletspacing` to control spacing between bullet items
