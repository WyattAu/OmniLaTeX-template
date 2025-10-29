# OmniLaTeX

A modular LaTeX template system for academic and professional documents. This fork from the TUHH thesis template provides boilerplates for multiple document types.

## Features

- Support for books, theses, dissertations, articles, journals, CVs, manuals, technical reports, patents, and standards
- LuaLaTeX engine with Lua scripting
- Content support for code listings, mathematics, tables, figures, bibliographies, glossaries, TikZ graphics, and multi-language documents
- CI/CD integration for GitHub Actions, GitLab CI, Forgejo, and Gitea
- PDF verification with commit SHA embedding
- Docker container for consistent builds
- Ready-to-use templates in the examples directory

## Installation

### Prerequisites

- LuaLaTeX
- Python 3.8+ for build script
- Git for version control and verification

### Quick Start

1. Clone the repository:
    ```bash
    git clone https://github.com/WyattAu/OmniLaTeX-template.git
    cd OmniLaTeX-template
    ```
2. Reopen in container if you are in VSCode or run:
   ```bash
      docker run -it --rm -v $(pwd):/workspace ghcr.io/wyattau/omnilatex-docker:latest
   ```

3. Build a document:
    ```bash
    python build.py build-root
    ```
    Please do use the `build.py` to compile as custom scripts are required for all functionalities to work.

### Development Environment

Use the provided Docker container for consistent builds:

```bash
docker run -it --rm -v $(pwd):/workspace ghcr.io/wyattau/omnilatex-docker:latest
```

#### VSCode Integration

The project includes VSCode configuration for streamlined development:

- **Dev Container**: `.devcontainer/devcontainer.json` provides a containerized environment with LaTeX Workshop extension
- **Tasks**: `.vscode/tasks.json` includes build, clean, test, and quality assurance tasks
- **Extensions**: Recommended extensions for Python, LaTeX, and code quality

## Usage

### Basic Compilation

Compile any `.tex` file containing `\documentclass{omnilatex}`:

```bash
latexmk -lualatex main.tex
```

### Build Script

The `build.py` script provides commands for building and managing documents:

```bash
# Build the root document
python build.py build-root

# Build all examples
python build.py build-examples

# Build specific example
python build.py build-example thesis

# Clean auxiliary files
python build.py clean

# Run preflight checks
python build.py preflight
```

### Document Types

Configure the document type in your `.tex` file:

```latex
\documentclass[doctype=thesis,institution=tuhh]{omnilatex}
```

Available types: `book`, `thesis`, `dissertation`, `article`, `inlinepaper`, `journal`, `manual`, `technicalreport`, `standard`, `patent`, `cv`, `dictionary`

### Configuration

Customize documents through configuration files:

- `config/document-settings.sty`: Global settings
- `config/document-types/*.sty`: Document type settings
- `config/institutions/*.sty`: Institution branding

## Examples

The `examples/` directory contains templates:

- `minimal-starter/`: Basic setup with all assets
- `thesis-tuhh/`: TUHH-specific thesis template
- `article-color/`: Colored article template
- `cv-bw/`: Black and white CV template

Build an example:
```bash
python build.py build-example minimal-starter
```

## CI/CD Integration

Built-in support for GitHub Actions, GitLab CI, Forgejo, and Gitea.

### Environment Variables

- `CI_COMMIT_REF_NAME` / `GITHUB_REF_NAME` / `GITHUB_HEAD_REF`: Branch name
- `CI_COMMIT_SHA` / `GITHUB_SHA`: Commit hash
- `CI_PROJECT_PATH` / `GITHUB_REPOSITORY` / `FORGEJO_REPOSITORY` / `GITEA_REPOSITORY`: Repository slug
- `CI_PROJECT_TITLE` / `CI_PROJECT_NAME` (optional): Project title

### Pages Deployment

For PDF verification, set the public base URL:

- GitHub Pages: Automatic
- Cloudflare Pages / Other: Set `OMNILATEX_VERIFICATION_BASE_URL`, `CF_PAGES_URL`, `PAGES_URL`, `DEPLOYMENT_URL`, or `PAGES_BASE_URL`

## PDF Verification

Commit SHA verification system embeds links in PDFs to verify authenticity. Access verification at `pages/verify.html`.

## Project Structure

```
├── omnilatex.cls              # Main document class
├── build.py                   # Build automation script
├── .latexmkrc                 # LaTeX compilation settings
├── config/                    # Configuration files
│   ├── document-settings.sty
│   ├── document-types/
│   └── institutions/
├── lib/                       # Core modules
│   ├── core/
│   ├── layout/
│   ├── typography/
│   └── ...
├── content/                   # Sample content
├── examples/                  # Example documents
├── assets/                    # Images, data, code samples
├── bib/                       # Bibliography and glossaries
├── pages/                     # Web assets (verification page)
└── tests/                     # Test suite
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Test with `python build.py test`
5. Submit a pull request

## License

Licensed under Apache License 2.0 - see LICENSE file.

## Acknowledgments

- Fork from [TUHH LaTeX Template](https://collaborating.tuhh.de/m21/public/theses/itt-latex-template)
- Modern LaTeX practices and community contributions
