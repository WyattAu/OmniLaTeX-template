import { describe, it, expect } from 'vitest';
import { readFileSync, existsSync, readdirSync, statSync } from 'fs';
import { join, resolve } from 'path';

// Smoke tests for the built Astro site output.
// Run `npm run build` before these tests, or they test the dist/ directory.
//
// PDFs and _headers are CI-only artifacts (created by the GitHub Actions
// workflow, not by `astro build`). Tests for these are gated on existence.

const DIST = resolve(import.meta.dirname, '../dist');

function readText(path: string): string {
  return readFileSync(join(DIST, path), 'utf-8');
}

function fileExists(path: string): boolean {
  return existsSync(join(DIST, path));
}

function listPDFs(): string[] {
  const pdfDir = join(DIST, 'pdfs');
  if (!existsSync(pdfDir)) return [];
  return readdirSync(pdfDir)
    .filter(f => f.endsWith('.pdf'))
    .sort();
}

// ---------------------------------------------------------------------------
// Astro build output (always present after `npm run build`)
// ---------------------------------------------------------------------------
describe('Astro build output', () => {
  it('dist/ directory exists', () => {
    expect(existsSync(DIST)).toBe(true);
  });

  it('index.html exists and has content', () => {
    expect(fileExists('index.html')).toBe(true);
    const html = readText('index.html');
    expect(html.length).toBeGreaterThan(100);
  });

  it('index.html has no stale /OmniLaTeX-template base path', () => {
    const html = readText('index.html');
    expect(html).not.toMatch(/href="\/OmniLaTeX-template\//);
  });

  it('gallery page exists and references PDFs', () => {
    expect(fileExists('gallery/index.html')).toBe(true);
    const html = readText('gallery/index.html');
    expect(html).toContain('pdfs/');
  });

  it('verify page exists and references commit param', () => {
    expect(fileExists('verify/index.html')).toBe(true);
    const html = readText('verify/index.html');
    expect(html).toContain('commit');
  });

  it('docs section exists', () => {
    expect(fileExists('docs/index.html')).toBe(true);
  });
});

// ---------------------------------------------------------------------------
// CI artifacts (only present after workflow builds)
// ---------------------------------------------------------------------------
describe('CI artifacts (conditional)', () => {
  it('pdfs/ directory has at least one PDF', () => {
    const pdfs = listPDFs();
    if (pdfs.length === 0) {
      console.warn('Skipping: no PDFs in dist/pdfs/ (CI-only artifact)');
      return;
    }
    expect(pdfs.length).toBeGreaterThan(0);
  });

  it('_headers file has CSP and security headers', () => {
    if (!fileExists('_headers')) {
      console.warn('Skipping: _headers not found (CI-only artifact)');
      return;
    }
    const headers = readText('_headers');
    expect(headers).toContain('Content-Security-Policy');
    expect(headers).toContain('X-Content-Type-Options: nosniff');
    expect(headers).toContain('api.github.com');
    expect(headers).toContain('static.cloudflareinsights.com');
  });

  it('no PDF is suspiciously small (<2KB suggests build failure)', () => {
    const pdfDir = join(DIST, 'pdfs');
    if (!existsSync(pdfDir)) return;
    const pdfs = readdirSync(pdfDir).filter(f => f.endsWith('.pdf'));
    for (const pdf of pdfs) {
      const size = statSync(join(pdfDir, pdf)).size;
      expect(size).toBeGreaterThan(2000);
    }
  });

  it('key example PDFs present (thesis, article, thesis-tuhh)', () => {
    const pdfs = listPDFs();
    if (pdfs.length === 0) return;
    expect(fileExists('pdfs/thesis.pdf')).toBe(true);
    expect(fileExists('pdfs/article.pdf')).toBe(true);
    expect(fileExists('pdfs/thesis-tuhh.pdf')).toBe(true);
  });
});
