# OmniLaTeX WASM Feasibility Report

**Date:** 2026-06-07
**Status:** FEASIBLE (hybrid approach) / HARD (pure WASM LuaTeX)
**Author:** Nexus Architecture Engine

---

## Executive Summary

Pure in-browser LuaTeX compilation via WebAssembly is technically possible but
requires 6-12 months of dedicated C/WASM engineering. The primary blockers are
(1) compiling LuaTeX's 500K-line C codebase to WASM, (2) fontconfig/fontspec
integration in a virtual filesystem, and (3) the 150-300 MB package payload for
OmniLaTeX's full feature set.

A **hybrid architecture** (WASM editor + server-side compilation via WebSocket)
delivers 90% of the user experience benefit at 10% of the implementation cost.
This is the recommended path.

---

## 1. Current State of TeX-on-WASM

### 1.1 Existing Projects

| Project | Engine | Status | WASM Binary | Notes |
|---------|--------|--------|-------------|-------|
| SwiftLaTeX | pdfTeX | Dead (repo deleted) | ~8-12 MB | Proved single-pass pdfTeX works in browser |
| texlive.js | pdfTeX | Abandoned (~2020) | ~15-25 MB | Emscripten asm.js, not true WASM |
| tectonic | XeTeX | Active | Rust->WASM viable | Uses XeTeX, not LuaTeX. Rust has mature WASM story |
| Overleaf | Server-side | Active, production | N/A | Full TeX Live on server, WebSocket to browser |
| Fengari | Lua (JS) | Active | ~200 KB JS | Pure JS Lua 5.3. Could replace embedded Lua VM |

### 1.2 Key Finding

No existing project compiles LuaTeX to WASM. The closest is tectonic (Rust
wrapper around XeTeX), but OmniLaTeX requires LuaTeX (`\RequireLuaTeX{}`).

---

## 2. OmniLaTeX WASM Requirements

### 2.1 Engine Dependencies

| Component | Required | WASM Status | Size |
|-----------|----------|-------------|------|
| LuaTeX C engine | Yes | No WASM port exists | ~2-5 MB compiled |
| PUC Lua 5.4 | Yes | WASM port exists (~300 KB) | Embedded in LuaTeX |
| fontconfig | Yes (via fontspec) | No WASM port | Must patch |
| harfbuzz | Yes (LuaTeX embeds) | Has WASM port (Chrome) | ~1 MB |
| libpng/zlib | Yes | WASM ports exist | ~200 KB |
| MetaFont | Indirectly | Can pre-generate fonts | N/A |

### 2.2 External Tools

| Tool | Required | WASM Feasible | Alternative |
|------|----------|---------------|-------------|
| biber | Bibliography | No (Perl + deps) | Pre-generate .bbl |
| bib2gls | Glossaries | No (Java) | Pre-generate .glstex |
| pygmentize | Code listings | Possible (Pyodide, ~15 MB) | Use listings package |
| inkscape | SVG conversion | No | Pre-convert SVG to PDF |
| latexmk | Build orchestrator | Rewrite in JS | Custom JS build loop |

### 2.3 Font Requirements

| Font | Size | Required | WASM Strategy |
|------|------|----------|---------------|
| Libertinus Serif | ~800 KB | Yes (main font) | Bundle in VFS |
| Libertinus Math | ~1.2 MB | Yes (math font) | Bundle in VFS |
| Libertinus Sans | ~600 KB | Yes (sans fallback) | Bundle in VFS |
| Latin Modern | ~2 MB | Yes (fallback) | Bundle in VFS |
| Monaspace Neon | ~1 MB | No (fallback exists) | Skip |
| Atkinson Hyperlegible | ~800 KB | No (fallback exists) | Skip |
| Noto CJK | ~100 MB | No (CJK only) | Lazy-load per language |
| fontawesome5 | ~1 MB | No (icons) | Skip or inline SVG |

**Minimum font bundle: ~5 MB** (Libertinus + Latin Modern)

### 2.4 Package Requirements

| Category | Packages | Size | Loading |
|----------|----------|------|---------|
| Core LaTeX | latex kernel, amsmath, hyperref, graphics | ~20 MB | Eager |
| KOMA-Script | scrbook, scrreprt, scrartcl, scrlayer-scrpage | ~5 MB | Eager |
| OmniLaTeX .sty | 31 modules in lib/ | ~500 KB | Eager |
| polyglossia | 25+ language patterns | ~2 MB | Eager |
| biblatex | Bibliography system | ~5 MB | Eager |
| tikz/pgfplots | Graphics | ~15 MB | Eager |
| fontspec | Font loading | ~500 KB | Eager |
| minted | Code listings | ~200 KB | Skip (needs pygmentize) |
| **Minimum viable** | | **~50 MB** | |
| **Full OmniLaTeX** | | **~150-300 MB** | |

---

## 3. Architecture Options

### 3.1 Option A: Pure WASM LuaTeX (6-12 months)

```
Browser
  +-- Monaco Editor (LaTeX syntax highlighting)
  +-- Compilation Worker
  |   +-- LuaTeX WASM (PUC Lua 5.4)
  |   +-- Virtual FS (OPFS-backed)
  |   +-- Package loader (lazy from CDN)
  +-- PDF.js Viewer
  +-- Service Worker
      +-- Package cache (Cache API)
      +-- Font cache (OPFS)
      +-- Offline support
```

**Pros:** Zero server dependency, full offline, privacy
**Cons:** 6-12 months effort, 150-300 MB download, fontconfig blocker

### 3.2 Option B: Hybrid (WASM Editor + Server Compilation) [RECOMMENDED]

```
Browser                          Server
  +-- Monaco Editor              +-- Docker container
  +-- Real-time preview          |   +-- Full TeX Live
  +-- Error highlighting         |   +-- LuaTeX
  +-- PDF.js viewer              |   +-- biber, bib2gls
  +-- WebSocket client           +-- WebSocket server
                                 +-- File sync
```

**Pros:** 90% UX benefit, 2-4 weeks effort, full package support
**Cons:** Requires server, not offline-capable

### 3.3 Option C: Tectonic WASM (3-6 months)

```
Browser
  +-- Monaco Editor
  +-- Compilation Worker
  |   +-- tectonic WASM (XeTeX engine)
  |   +-- Auto-downloading package bundle
  +-- PDF.js Viewer
```

**Pros:** Rust->WASM is mature, active project, auto-downloads packages
**Cons:** Uses XeTeX not LuaTeX, requires adapting OmniLaTeX to drop Lua dependency

---

## 4. Recommended Path: Hybrid Architecture

### 4.1 Phase 1: WASM Editor (2-4 weeks)

Build a browser-based LaTeX editor with:
- Monaco editor with LaTeX language support
- Real-time syntax error highlighting
- OmniLaTeX-specific autocomplete (doctypes, institutions, options)
- WebSocket connection to compilation server
- PDF.js for preview rendering

### 4.2 Phase 2: Compilation Server (1-2 weeks)

Extend existing Docker infrastructure:
- WebSocket server wrapping the build system
- File synchronization (client <-> server)
- Real-time log streaming
- Multi-user support (session isolation)

### 4.3 Phase 3: Offline Mode (2-4 weeks)

Add progressive offline capability:
- Service Worker for caching editor assets
- IndexedDB for storing user documents
- Queue compilation requests when offline
- Sync when connection restored

### 4.4 Phase 4: Pure WASM (6-12 months, future)

If pure WASM becomes critical:
- Fork tectonic, add Lua interpreter
- Or compile LuaTeX to WASM via Emscripten
- Patch fontconfig for virtual FS
- Bundle fonts and packages

---

## 5. Proof-of-Concept: WASM Editor

### 5.1 Directory Structure

```
wasm/
  +-- editor/
  |   +-- index.html          # Main editor page
  |   +-- src/
  |   |   +-- app.ts          # Main application
  |   |   +-- editor.ts       # Monaco editor setup
  |   |   +-- compiler.ts     # WebSocket compilation client
  |   |   +-- preview.ts      # PDF.js preview
  |   |   +-- autocomplete.ts # OmniLaTeX-specific completions
  |   +-- package.json
  |   +-- tsconfig.json
  |   +-- vite.config.ts
  +-- server/
  |   +-- main.py             # WebSocket compilation server
  |   +-- requirements.txt
  +-- README.md
```

### 5.2 Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Editor | Monaco Editor | Same as VS Code, mature LaTeX support |
| Preview | PDF.js | Mozilla's PDF renderer, widely used |
| Build tool | Vite | Fast, WASM-friendly |
| WebSocket | native WebSocket API | Simple, no dependencies |
| Server | Python + websockets | Leverages existing buildlib |
| Styling | Tailwind CSS | Consistent with existing pages/ |

---

## 6. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| LuaTeX WASM compilation fails | High | Use hybrid approach as fallback |
| fontconfig never works in WASM | High | Use hybrid approach, pre-build font DB for WASM |
| Browser memory limits | Medium | Aggressive lazy loading, minimal initial tree |
| Cross-Origin Isolation breaks embedding | Medium | Proper COOP/COEP headers |
| TeX Live licensing in WASM | Low | LPPL/GPL allows distribution with source |
| WebSocket latency for compilation | Low | Server-side caching, incremental builds |

---

## 7. Decision

**Proceed with Option B (Hybrid)** as the primary path.

**Rationale:**
- Delivers 90% of the user experience (editor + live preview)
- 2-4 weeks effort vs 6-12 months for pure WASM
- Leverages existing Docker/CI infrastructure
- Can evolve to pure WASM later without rewriting the editor
- The editor component is shared between hybrid and pure WASM paths

**Next Steps:**
1. Create `wasm/` directory structure
2. Implement Monaco editor with LaTeX support
3. Build WebSocket compilation server wrapping buildlib
4. Integrate PDF.js for preview
5. Deploy as GitHub Pages app + optional self-hosted server
