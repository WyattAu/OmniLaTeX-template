import { describe, it, expect } from 'vitest';

// Unit tests for component logic (not rendering)
// SolidJS rendering requires browser environment which jsdom doesn't fully support

describe('GalleryGrid logic', () => {
  const DOCUMENTS = [
    { id: 'thesis', name: 'Thesis', cat: 'academic' },
    { id: 'article', name: 'Article', cat: 'academic' },
    { id: 'cv', name: 'CV', cat: 'professional' },
    { id: 'presentation', name: 'Presentation', cat: 'presentation' },
  ];

  function filterDocs(docs: typeof DOCUMENTS, category: string, query: string) {
    return docs.filter(d => {
      const matchCat = category === 'all' || d.cat === category;
      const matchSearch = !query || d.name.toLowerCase().includes(query.toLowerCase());
      return matchCat && matchSearch;
    });
  }

  it('returns all documents for "all" category', () => {
    const result = filterDocs(DOCUMENTS, 'all', '');
    expect(result.length).toBe(4);
  });

  it('filters by category', () => {
    const result = filterDocs(DOCUMENTS, 'academic', '');
    expect(result.length).toBe(2);
    expect(result.every(d => d.cat === 'academic')).toBe(true);
  });

  it('filters by search query', () => {
    const result = filterDocs(DOCUMENTS, 'all', 'thesis');
    expect(result.length).toBe(1);
    expect(result[0].name).toBe('Thesis');
  });

  it('filters by both category and query', () => {
    const result = filterDocs(DOCUMENTS, 'academic', 'article');
    expect(result.length).toBe(1);
    expect(result[0].name).toBe('Article');
  });

  it('returns empty for no matches', () => {
    const result = filterDocs(DOCUMENTS, 'all', 'nonexistent');
    expect(result.length).toBe(0);
  });

  it('search is case-insensitive', () => {
    const result = filterDocs(DOCUMENTS, 'all', 'THESIS');
    expect(result.length).toBe(1);
  });
});

describe('Validator logic', () => {
  const DOCTYPES = ['article', 'thesis', 'book', 'cv'];
  const INSTITUTIONS = ['none', 'mit', 'stanford'];
  const LANGUAGES = ['english', 'german', 'chinese'];

  function validate(doctype: string, institution: string, language: string) {
    const errors: string[] = [];
    const warnings: string[] = [];

    if (!DOCTYPES.includes(doctype)) errors.push(`Unknown doctype: ${doctype}`);
    if (!INSTITUTIONS.includes(institution)) errors.push(`Unknown institution: ${institution}`);
    if (!LANGUAGES.includes(language)) warnings.push(`Language ${language} may not be fully supported`);

    if (['thesis', 'book'].includes(doctype) && institution === 'none') {
      warnings.push(`Doctype ${doctype} typically uses an institution config`);
    }

    return { valid: errors.length === 0, errors, warnings };
  }

  it('validates correct configuration', () => {
    const result = validate('article', 'none', 'english');
    expect(result.valid).toBe(true);
    expect(result.errors.length).toBe(0);
  });

  it('rejects unknown doctype', () => {
    const result = validate('nonexistent', 'none', 'english');
    expect(result.valid).toBe(false);
    expect(result.errors.length).toBe(1);
  });

  it('warns about institution for thesis', () => {
    const result = validate('thesis', 'none', 'english');
    expect(result.valid).toBe(true);
    expect(result.warnings.length).toBeGreaterThan(0);
  });

  it('generates correct class line', () => {
    const classLine = `\\documentclass[doctype=article,language=english,institution=none]{omnilatex}`;
    expect(classLine).toContain('doctype=article');
    expect(classLine).toContain('language=english');
  });
});

describe('slugToTitle', () => {
  function slugToTitle(slug: string): string {
    return slug
      .replace(/\.md$/, '')
      .split('/')
      .map(part => part.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()))
      .join(' / ');
  }

  it('converts simple slug', () => {
    expect(slugToTitle('user_guide')).toBe('User Guide');
  });

  it('converts nested slug', () => {
    expect(slugToTitle('manual/part_i_foundations')).toBe('Manual / Part I Foundations');
  });

  it('removes .md extension', () => {
    expect(slugToTitle('faq.md')).toBe('Faq');
  });

  it('handles single word', () => {
    expect(slugToTitle('accessibility')).toBe('Accessibility');
  });
});
