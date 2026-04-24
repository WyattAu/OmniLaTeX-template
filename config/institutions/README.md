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

### TUM (Technische Universität München)
- **File**: `tum.sty`
- **Colors**: TUM Blue, TUM Dark Blue, TUM Light Blue
- **Languages**: English and German

### ETH Zürich
- **File**: `eth.sty`
- **Colors**: ETH Blue, ETH Dark, ETH Teal
- **Languages**: English and German

### MIT (Massachusetts Institute of Technology)
- **File**: `mit.sty`
- **Colors**: MIT Crimson, Cool Gray, Black
- **Languages**: English

### Stanford University
- **File**: `stanford.sty`
- **Colors**: Stanford Cardinal, Stanford Sandstone, Stanford Green
- **Languages**: English

### University of Cambridge
- **File**: `cambridge.sty`
- **Colors**: Cambridge Green, Cambridge Blue, Cambridge Dark Gray
- **Languages**: English

### TU Delft (Delft University of Technology)
- **File**: `tudelft.sty`
- **Colors**: TU Delft Cyan, White, TU Delft Dark Blue
- **Languages**: English and Dutch

### Generic (Template)
- **File**: `generic.sty`
- **Description**: Minimal template for creating new institution configs
- **Languages**: All (user-defined)

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
