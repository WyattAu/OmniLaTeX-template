# Plugin Catalog

OmniLaTeX supports a plugin system for extending document functionality. Plugins
are self-contained packages with a manifest, LaTeX styles, and optional assets.

## Available Plugins

| Plugin | Version | Description | Tags |
|--------|---------|-------------|------|
| [example-plugin](https://github.com/WyattAu/OmniLaTeX-template/tree/main/plugins/example-plugin) | 1.0.0 | Example plugin demonstrating the plugin system | example, demo |
| [markdown-table](https://github.com/WyattAu/OmniLaTeX-template/tree/main/plugins/markdown-table) | 1.0.0 | Convert Markdown tables to LaTeX table environments | table, markdown |
| [watermark](https://github.com/WyattAu/OmniLaTeX-template/tree/main/plugins/watermark) | 1.0.0 | Add configurable watermarks to documents | watermark, draft |

## Using Plugins

### In main.tex

```latex
\documentclass[doctype=article,language=english]{omnilatex}
\RequirePackage{plugins/watermark/omnilatex-plugin-watermark}
\begin{document}
\watermarktext{DRAFT}
\section{Introduction}
Content here.
\end{document}
```

### Via Build System

```bash
python build.py build-example plugin-demo
```

## Creating Plugins

See the [Plugin Specification](https://github.com/WyattAu/OmniLaTeX-template/blob/main/plugins/PLUGIN_SPECIFICATION.md)
for the full specification. A minimal plugin requires:

1. A `manifest.toml` with name, version, and dependencies
2. A `.sty` file with the plugin implementation
3. Registration in `plugins/registry.toml`

### Plugin Manifest

```toml
[plugin]
name = "my-plugin"
version = "1.0.0"
description = "What this plugin does"
author = "Your Name"
license = "Apache-2.0"
omnilatex_min = "2.4.0"

[capabilities]
network = false
shell_escape = false
file_write = false
```

### Sandbox

Plugins run in a sandboxed environment. By default, plugins cannot:

- Access the network
- Execute shell commands
- Write files outside their directory

Capabilities can be requested in the manifest and must be approved by the user.

## Contributing Plugins

1. Fork the repository
2. Create your plugin in `plugins/my-plugin/`
3. Add an entry to `plugins/registry.toml`
4. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for general contribution guidelines.
