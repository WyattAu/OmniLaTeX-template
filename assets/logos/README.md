# Institution Logos

Logos in this directory are used by OmniLaTeX institution configurations.

## Usage Rights

| Institution | Logo | License | Source |
|-------------|------|---------|--------|
| MIT | `mit/logo.svg` | Public Domain | Wikimedia Commons |
| TUHH | `tuhh/*.svg` | Institutional (approved for template use) | TUHH Corporate Design |

All other institution logos are **not included** in this repository due to trademark
restrictions. Users must obtain logos from their institution's brand portal.

## Adding Your Institution's Logo

1. Obtain the logo in SVG or PDF format from your institution's press kit
2. Save it to `assets/logos/<institution>/logo.{svg,pdf,png}`
3. Update your institution's `.sty` file to reference the logo:

```latex
\DeclareTranslation{english}{LogoInstitution}{%
    \includegraphics[height=1.5cm]{assets/logos/<institution>/logo}%
}
```

## Logo Specifications

- Format: SVG (preferred) or PDF
- Height: 1.5–3 cm at 100% scale
- Color: Use institutional colors (defined in institution `.sty`)
- Background: Transparent preferred

## Contributing Logos

If you have permission to redistribute your institution's logo, please open a pull
request. Include:

- The logo file(s) in SVG format
- Written permission from the institution's communications office, OR
- A link to the institution's public brand portal with download terms
