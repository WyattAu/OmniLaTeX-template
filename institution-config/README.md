# Institution Configuration Directory

This directory contains institution-specific configurations for the academic LaTeX template.

## Structure

Each institution configuration file provides:
- **Branding**: Logos, colors, institution names
- **Title Page Styles**: Custom title page layouts
- **Translations**: Institution-specific text and labels
- **Default Values**: Examiners, publishers, links

## Available Configurations

### TUHH (Hamburg University of Technology - Institute of Engineering Thermodynamics)
- **File**: `tuhh-config.sty`
- **Title Styles**: `TUHH` (with institutional logos)
- **Logos**: TUHH university and ITT institute logos
- **Languages**: English and German

## Creating a New Institution Configuration

To create a configuration for your institution:

1. Copy `tuhh-config.sty` as a template
2. Rename to `yourinstitution-config.sty`
3. Update the following sections:
   - Logo definitions (`\DeclareTranslation{LogoXXX}`)
   - Institution links and names
   - Title page styles
   - Default examiner/supervisor names
   - Any custom TikZ graphics or branding elements

4. Use in your document:
   ```latex
   \documentclass[institution=yourinstitution]{academic}
   ```

## Integration with academic.cls

The `academic.cls` class automatically loads the configuration based on the `institution` option:
- `institution=tuhh` → loads `tuhh-config.sty`
- `institution=none` → no institutional branding (generic template)

If no `institution` option is provided, the class defaults to generic styling without institutional branding.
