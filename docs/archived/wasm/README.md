# OmniLaTeX WASM Editor

Browser-based LaTeX editor with live compilation preview.

## Architecture

```
Browser (editor)  --WebSocket-->  Server (buildlib + LuaTeX)
     ~2 MB HTML/JS/CSS               ~4 GB Docker / local TeX Live
```

The editor component runs entirely in the browser (zero build step).
The compilation server wraps the existing `buildlib` package and TeX Live.

## Quick Start

### 1. Start the compilation server

```bash
pip install websockets
python wasm/server/main.py --port 8765
```

### 2. Open the editor

```bash
# Serve the editor (any static file server works)
python -m http.server 8080 --directory wasm/editor
# Open http://localhost:8080
```

### 3. Edit and compile

Type LaTeX in the editor. Press **Compile** or **Ctrl+Enter** to build.
The PDF appears in the preview pane.

## Requirements

- Python 3.10+
- `websockets` package (`pip install websockets`)
- TeX Live with LuaLaTeX (or Docker with the OmniLaTeX image)
- The OmniLaTeX repository (server symlinks `config/`, `lib/`, etc.)

## Docker

```bash
docker run --rm -p 8765:8765 \
  -v $(pwd):/workspace \
  -w /workspace \
  ghcr.io/wyattau/omnilatex-docker:latest \
  python wasm/server/main.py --host 0.0.0.0 --port 8765
```

## Protocol

WebSocket JSON messages:

| Direction | Type | Fields | Description |
|-----------|------|--------|-------------|
| Client -> Server | `compile` | `source`, `doctype` | Compile a document |
| Client -> Server | `ping` | | Keep-alive |
| Server -> Client | `log` | `line` | Compilation log line |
| Server -> Client | `progress` | `message` | Status update |
| Server -> Client | `success` | `pdf` (base64) | PDF generated |
| Server -> Client | `error` | `message` | Error occurred |

## Design Philosophy

The editor follows the Spatial Materialism + Amoebic UI design language:
- Dark surface hierarchy (`--bg`, `--bg-panel`, `--bg-editor`)
- Soft border radius (6px for controls)
- Accent color hierarchy (blue for primary actions)
- Responsive layout (stacks on mobile)
- No emojis in the interface
