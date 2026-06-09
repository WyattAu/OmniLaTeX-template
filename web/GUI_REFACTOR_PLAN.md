# OmniLaTeX GUI Refactor: SolidJS Integration Analysis

**Date:** 2026-06-08
**Status:** PROPOSED
**Current Stack:** Astro 5.7 + SolidJS 1.9 + MDX + Sitemap

---

## 1. Current Architecture

### What Exists

```
web/
  src/
    components/
      GalleryGrid.tsx     # 50 document cards, category filtering, search
      Validator.tsx        # doctype/institution/language validation form
    pages/
      index.astro          # Landing page with hero + gallery
      gallery.astro        # Gallery page
      verify.astro         # Validation page
      docs/
        index.astro        # Docs index with grouped links
        [...slug].astro    # Dynamic doc renderer
    layouts/
      BaseLayout.astro     # Nav, footer, meta tags, CSP
    styles/
      global.css           # Design tokens + base styles
    content.config.ts      # Content collections for docs/
```

### Current Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| astro | 5.7 | Static site generator |
| @astrojs/solid-js | 5.0 | SolidJS integration for islands |
| @astrojs/mdx | 4.2 | MDX support for docs |
| @astrojs/sitemap | 3.7 | Sitemap generation |
| solid-js | 1.9 | Reactive UI components |

### Current Pain Points

1. **No client-side routing** -- every page navigation is a full page load
2. **No search** -- docs have no search functionality
3. **No virtualization** -- gallery renders all 50 cards at once
4. **No animations** -- static transitions only
5. **No i18n** -- English only
6. **No testing** -- zero frontend tests
7. **No linting** -- no ESLint for SolidJS patterns
8. **No code editor** -- validator uses native `<select>` elements
9. **No toast notifications** -- copy-to-clipboard has no feedback
10. **No form validation library** -- manual validation logic

---

## 2. Integration Analysis

### 2.1 Routing & SEO

| Integration | Useful? | Rationale |
|-------------|---------|-----------|
| `@solidjs/router` | **NO** | Astro handles routing. SolidJS components are islands, not a SPA. Adding a client-side router would conflict with Astro's static generation. |
| `@solidjs/meta` | **NO** | Astro handles `<head>` via `BaseLayout.astro`. No need for SolidJS meta management. |
| `@tanstack/solid-router` | **NO** | Same as above -- overkill for island architecture. |

**Decision:** Skip all routing libraries. Astro's file-based routing is correct for this architecture.

### 2.2 Component Libraries

| Integration | Useful? | Rationale |
|-------------|---------|-----------|
| **Kobalte** | **YES** | Accessible, unstyled components. Would replace hand-built gallery tabs, form selects, and buttons with proper ARIA-compliant primitives. Directly addresses the accessibility audit findings. |
| **Zag JS** | **MAYBE** | State machines for complex UI. Overkill for current components but useful if we add a code editor or complex form wizard. |
| **Ark UI** | **NO** | Built on Zag JS -- same overkill assessment. |
| **Suid** | **NO** | Material Design doesn't match the Spatial Materialism/Brutalism design language. |
| **Flowbite SolidJS** | **NO** | Tailwind-based. We use vanilla CSS with design tokens. |

**Decision:** Adopt **Kobalte** for accessible primitives (tabs, select, dialog, toast).

### 2.3 UI Components

| Integration | Useful? | Rationale |
|-------------|---------|-----------|
| **@tanstack/solid-table** | **NO** | No data tables in the current site. The gallery is a grid, not a table. |
| **@tanstack/solid-virtual** | **YES** | The gallery has 50 cards. Virtualization would improve initial render performance and enable lazy loading of PDF previews. |
| **solid-sonner** | **YES** | Toast notifications for copy-to-clipboard, validation results, and error messages. Clean, accessible, minimal. |
| **solid-icons** | **MAYBE** | Currently using inline SVGs. Would reduce code but adds a dependency. Low priority. |
| **@formkit/auto-animate** | **YES** | Zero-config animations for gallery card filtering, doc list changes, and validation result transitions. |
| **@thisbeyond/solid-dnd** | **NO** | No drag-and-drop use case. |

**Decision:** Adopt **@tanstack/solid-virtual**, **solid-sonner**, **@formkit/auto-animate**.

### 2.4 Forms & Editors

| Integration | Useful? | Rationale |
|-------------|---------|-----------|
| **Felte** | **MAYBE** | The validator is simple (3 selects). Felte would be useful if we add a plugin manifest editor or a more complex form. Low priority now. |
| **TipTap Solid** | **MAYBE** | Useful for a future "try it live" editor. Not needed now. |
| **Solid CodeMirror** | **MAYBE** | Useful for a future LaTeX editor. Not needed now. |

**Decision:** Skip for now. Revisit when adding a plugin editor or live preview.

### 2.5 State Management

| Integration | Useful? | Rationale |
|-------------|---------|-----------|
| **@solid-primitives/state** | **YES** | The gallery and validator use local signals. If we add cross-component state (e.g., shared search, theme toggle), primitives are the correct lightweight choice. |
| **@tanstack/solid-query** | **NO** | No server-state fetching. The site is static. |
| **@nanostores/solid** | **NO** | Overkill for current scale. |

**Decision:** Adopt **@solid-primitives** for utility hooks (media queries, keyboard, storage). Skip state management libraries.

### 2.6 Internationalization

| Integration | Useful? | Rationale |
|-------------|---------|-----------|
| **@solid-primitives/i18n** | **YES** | OmniLaTeX supports 25+ languages. The site should at minimum support EN/DE/ZH for the gallery and validator. The docs are English-only but the UI chrome should be translatable. |

**Decision:** Adopt **@solid-primitives/i18n** for UI chrome translations.

### 2.7 Testing & DX

| Integration | Useful? | Rationale |
|-------------|---------|-----------|
| **@testing-library/solid** | **YES** | Zero frontend tests currently. This is a gap. |
| **eslint-plugin-solid** | **YES** | No linting for SolidJS patterns. Would catch common mistakes (early destructuring, missing cleanup). |
| **LocatorJS** | **NO** | Development-only tool. Not worth adding as a dependency. |

**Decision:** Adopt **@testing-library/solid** and **eslint-plugin-solid**.

---

## 3. Recommended Stack

### Tier 1: Adopt Now (High Impact, Low Risk)

| Package | Purpose | Impact |
|---------|---------|--------|
| `@kobalte/core` | Accessible primitives (tabs, select, dialog) | Fixes accessibility audit findings |
| `@tanstack/solid-virtual` | Virtualized gallery grid | Performance for 50+ cards |
| `solid-sonner` | Toast notifications | UX feedback for copy/error actions |
| `@formkit/auto-animate` | Zero-config animations | Visual polish for filtering/transitions |
| `@solid-primitives/media` | Media query primitives | Responsive design helpers |
| `@solid-primitives/keyboard` | Keyboard handler primitives | Keyboard navigation for gallery |
| `eslint-plugin-solid` | SolidJS linting | Code quality |
| `@testing-library/solid` | Component testing | Test coverage |

### Tier 2: Adopt Soon (Medium Impact, Medium Risk)

| Package | Purpose | Impact |
|---------|---------|--------|
| `@solid-primitives/i18n` | UI chrome translations | Multi-language support |
| `@solid-primitives/storage` | Persistent state | Remember user preferences (theme, language) |
| `virtua` | Alternative virtual scroll | If tanstack/virtual is too complex |

### Tier 3: Future (When Needed)

| Package | Purpose | When |
|---------|---------|------|
| `solid-codemirror` | LaTeX editor | When building "try it live" feature |
| `@tanstack/solid-query` | Server state | When adding API-backed features |
| `felte` | Form management | When adding plugin manifest editor |
| `@thisbeyond/solid-dnd` | Drag and drop | When adding card reordering |

### Tier 4: Skip (Not Applicable)

| Package | Reason |
|---------|--------|
| `@solidjs/router` | Astro handles routing |
| `@solidjs/meta` | Astro handles `<head>` |
| `@tanstack/solid-table` | No data tables |
| `suid` | Wrong design language |
| `flowbite-solidjs` | Wrong CSS approach |
| `solid-bootstrap` | Wrong design language |
| `@nanostores/solid` | Overkill |
| `@tanstack/solid-query` | No server state |

---

## 4. Migration Roadmap

### Phase 1: Foundation (Week 1)

**Goal:** Install dependencies, set up linting and testing infrastructure.

| Task | Package | Effort |
|------|---------|--------|
| Install `eslint-plugin-solid` | DX | 30 min |
| Configure ESLint for SolidJS patterns | DX | 1 hour |
| Install `@testing-library/solid` + `vitest` | Testing | 1 hour |
| Write first test for `Validator.tsx` | Testing | 2 hours |
| Write first test for `GalleryGrid.tsx` | Testing | 2 hours |

**Deliverable:** Linting passes, 2 component test files exist.

### Phase 2: Accessibility (Week 2)

**Goal:** Replace hand-built components with Kobalte primitives.

| Task | Package | Effort |
|------|---------|--------|
| Install `@kobalte/core` | Accessibility | 15 min |
| Replace gallery tabs with `<Kobalte.Tabs>` | Accessibility | 2 hours |
| Replace validator selects with `<Kobalte.Select>` | Accessibility | 2 hours |
| Add `<Kobalte.Toast>` for copy feedback | Accessibility | 1 hour |
| Verify all accessibility tests pass | Testing | 1 hour |

**Deliverable:** All interactive components use Kobalte primitives. Accessibility audit passes.

### Phase 3: Performance (Week 3)

**Goal:** Virtualize gallery, add animations.

| Task | Package | Effort |
|------|---------|--------|
| Install `@tanstack/solid-virtual` | Performance | 15 min |
| Virtualize gallery grid (50 cards) | Performance | 3 hours |
| Install `@formkit/auto-animate` | UX | 15 min |
| Add animations to gallery filtering | UX | 1 hour |
| Add animations to doc list | UX | 30 min |
| Install `solid-sonner` | UX | 15 min |
| Replace manual toast with Sonner | UX | 1 hour |

**Deliverable:** Gallery virtualized, smooth animations, toast notifications.

### Phase 4: i18n (Week 4)

**Goal:** Add multi-language support for UI chrome.

| Task | Package | Effort |
|------|---------|--------|
| Install `@solid-primitives/i18n` | i18n | 15 min |
| Define translation strings (EN, DE, ZH) | i18n | 2 hours |
| Add language selector to nav | i18n | 1 hour |
| Translate gallery UI | i18n | 1 hour |
| Translate validator UI | i18n | 1 hour |
| Translate docs index | i18n | 1 hour |
| Persist language preference | i18n | 30 min |

**Deliverable:** Site UI available in EN, DE, ZH. Language persisted in localStorage.

### Phase 5: Testing & Polish (Week 5)

**Goal:** Comprehensive test coverage and final polish.

| Task | Package | Effort |
|------|---------|--------|
| Write tests for all Kobalte components | Testing | 3 hours |
| Write tests for virtualized gallery | Testing | 2 hours |
| Write tests for i18n switching | Testing | 1 hour |
| Add `@solid-primitives/media` for responsive helpers | DX | 1 hour |
| Add `@solid-primitives/keyboard` for keyboard nav | A11y | 1 hour |
| Final accessibility audit | QA | 2 hours |

**Deliverable:** 80%+ component test coverage. Full accessibility compliance.

---

## 5. Dependency Summary

### Current (4 runtime deps)

```
astro, @astrojs/solid-js, @astrojs/mdx, @astrojs/sitemap, solid-js
```

### After Migration (12 runtime deps)

```
# Core (unchanged)
astro, @astrojs/solid-js, @astrojs/mdx, @astrojs/sitemap, solid-js

# Tier 1 (new)
@kobalte/core, @tanstack/solid-virtual, solid-sonner, @formkit/auto-animate

# Tier 2 (new)
@solid-primitives/i18n, @solid-primitives/media, @solid-primitives/keyboard

# Dev dependencies (new)
@testing-library/solid, vitest, eslint-plugin-solid
```

### Bundle Size Impact

| Package | Size (gzip) | Loaded |
|---------|-------------|--------|
| solid-js | 7 KB | Always |
| @kobalte/core | ~15 KB | Per-component |
| @tanstack/solid-virtual | ~5 KB | Gallery only |
| solid-sonner | ~3 KB | On toast |
| @formkit/auto-animate | ~2 KB | On mount |
| @solid-primitives/* | ~1 KB each | Per-use |
| **Total new** | **~27 KB** | Lazy-loaded |

---

## 6. Architecture After Migration

```
web/
  src/
    components/
      Gallery/
        GalleryGrid.tsx        # Kobalte Tabs + TanStack Virtual
        GalleryCard.tsx        # Individual card with auto-animate
      Validator/
        Validator.tsx          # Kobalte Select + Sonner toast
        ValidationResult.tsx   # Animated result display
      ui/
        Toast.tsx              # Sonner wrapper
        Tabs.tsx               # Kobalte Tabs wrapper
        Select.tsx             # Kobalte Select wrapper
      Nav.astro                # Static nav (Astro)
      Footer.astro             # Static footer (Astro)
    i18n/
      index.ts                 # i18n setup
      en.json                  # English strings
      de.json                  # German strings
      zh.json                  # Chinese strings
    pages/
      index.astro
      gallery.astro
      verify.astro
      docs/
        index.astro
        [...slug].astro
    layouts/
      BaseLayout.astro
    styles/
      global.css
    content.config.ts
  tests/
    GalleryGrid.test.tsx
    Validator.test.tsx
    Tabs.test.tsx
    i18n.test.tsx
```

---

## 7. Decision

**Migrate to the Tier 1 stack.** The current site works but has accessibility gaps, no tests, no animations, and no i18n. The recommended integrations directly address these gaps with minimal bundle overhead (~27 KB gzip).

**Do NOT migrate to SolidStart.** Astro is the correct framework for this project. The site is primarily static content with small interactive islands. SolidStart would add SSR complexity with no benefit.

**Do NOT add client-side routing.** Astro's file-based routing is correct. The site has 28 pages, not a complex SPA. Full page loads are fast (<100ms on GitHub Pages CDN).

**Do NOT add state management libraries.** SolidJS signals are sufficient for the current component complexity. No cross-component state sharing is needed.
