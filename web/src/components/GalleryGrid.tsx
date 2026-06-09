import { createSignal, For, Show, onMount } from 'solid-js';
import { Tabs } from '@kobalte/core/tabs';
import { autoAnimate } from '@formkit/auto-animate';

function getBaseURL(): string {
  // @ts-expect-error -- Astro Vite import.meta.env
  const base = import.meta.env.BASE_URL;
  return base.endsWith('/') ? base : base + '/';
}

interface Document {
  id: string;
  name: string;
  desc: string;
  cat: string;
  file: string;
}

const DOCUMENTS: Document[] = [
  // Academic
  { id: 'thesis', name: 'Thesis', desc: 'Academic thesis with chapters (TUHH)', cat: 'academic', file: 'thesis.pdf' },
  { id: 'thesis-spacing', name: 'Thesis (Spacing)', desc: 'Thesis with custom spacing', cat: 'academic', file: 'thesis-spacing.pdf' },
  { id: 'thesis-tuhh', name: 'Thesis (TUHH)', desc: 'TU Hamburg thesis template', cat: 'academic', file: 'thesis-tuhh.pdf' },
  { id: 'dissertation', name: 'Dissertation', desc: 'Doctoral dissertation', cat: 'academic', file: 'dissertation.pdf' },
  { id: 'article', name: 'Article', desc: 'Journal article format', cat: 'academic', file: 'article.pdf' },
  { id: 'article-color', name: 'Article (Color)', desc: 'Article with color themes', cat: 'academic', file: 'article-color.pdf' },
  { id: 'journal', name: 'Journal', desc: 'Journal paper layout', cat: 'academic', file: 'journal.pdf' },
  { id: 'inline-paper', name: 'Inline Paper', desc: 'Paper without title page', cat: 'academic', file: 'inline-paper.pdf' },
  { id: 'book', name: 'Book', desc: 'Full book with parts', cat: 'academic', file: 'book.pdf' },
  { id: 'research-proposal', name: 'Research Proposal', desc: 'Grant proposal', cat: 'academic', file: 'research-proposal.pdf' },
  { id: 'exam', name: 'Exam', desc: 'Examination paper', cat: 'academic', file: 'exam.pdf' },
  { id: 'homework', name: 'Homework', desc: 'Problem set', cat: 'academic', file: 'homework.pdf' },
  { id: 'handout', name: 'Handout', desc: 'Class handout', cat: 'academic', file: 'handout.pdf' },
  { id: 'lecture-notes', name: 'Lecture Notes', desc: 'Course notes', cat: 'academic', file: 'lecture-notes.pdf' },
  { id: 'syllabus', name: 'Syllabus', desc: 'Course syllabus', cat: 'academic', file: 'syllabus.pdf' },
  { id: 'citation-styles', name: 'Citation Styles', desc: 'Bibliography citation examples', cat: 'academic', file: 'citation-styles.pdf' },
  // Professional
  { id: 'cv', name: 'CV', desc: 'Curriculum vitae', cat: 'professional', file: 'cv.pdf' },
  { id: 'cv-twopage', name: 'CV (Two Page)', desc: 'Extended two-page CV', cat: 'professional', file: 'cv-twopage.pdf' },
  { id: 'cover-letter', name: 'Cover Letter', desc: 'Professional cover letter', cat: 'professional', file: 'cover-letter.pdf' },
  { id: 'cover-letter-formal', name: 'Cover Letter (Formal)', desc: 'Formal cover letter variant', cat: 'professional', file: 'cover-letter-formal.pdf' },
  { id: 'letter', name: 'Letter', desc: 'Formal correspondence', cat: 'professional', file: 'letter.pdf' },
  { id: 'invoice', name: 'Invoice', desc: 'Business invoice', cat: 'professional', file: 'invoice.pdf' },
  { id: 'memo', name: 'Memo', desc: 'Memorandum', cat: 'professional', file: 'memo.pdf' },
  { id: 'white-paper', name: 'White Paper', desc: 'Technical white paper', cat: 'professional', file: 'white-paper.pdf' },
  // Presentation
  { id: 'presentation', name: 'Presentation', desc: 'Beamer slides', cat: 'presentation', file: 'presentation.pdf' },
  { id: 'poster', name: 'Poster', desc: 'Conference poster', cat: 'presentation', file: 'poster.pdf' },
  { id: 'beamer-academic', name: 'Beamer (Academic)', desc: 'Academic presentation theme', cat: 'presentation', file: 'beamer-academic.pdf' },
  { id: 'beamer-corporate', name: 'Beamer (Corporate)', desc: 'Corporate presentation theme', cat: 'presentation', file: 'beamer-corporate.pdf' },
  { id: 'beamer-minimal', name: 'Beamer (Minimal)', desc: 'Minimal presentation theme', cat: 'presentation', file: 'beamer-minimal.pdf' },
  { id: 'beamer-defense', name: 'Beamer (Defense)', desc: 'Thesis defense slides', cat: 'presentation', file: 'beamer-defense.pdf' },
  { id: 'beamer-native', name: 'Beamer (Native)', desc: 'Native beamer theme', cat: 'presentation', file: 'beamer-native.pdf' },
  // Technical
  { id: 'manual', name: 'Manual', desc: 'Technical manual', cat: 'technical', file: 'manual.pdf' },
  { id: 'technical-report', name: 'Technical Report', desc: 'Engineering report', cat: 'technical', file: 'technical-report.pdf' },
  { id: 'standard', name: 'Standard', desc: 'Standards document', cat: 'technical', file: 'standard.pdf' },
  { id: 'patent', name: 'Patent', desc: 'Patent application', cat: 'technical', file: 'patent.pdf' },
  { id: 'dictionary', name: 'Dictionary', desc: 'Reference dictionary', cat: 'technical', file: 'dictionary.pdf' },
  // Language
  { id: 'cjk-chinese', name: 'CJK (Chinese)', desc: 'Chinese language document', cat: 'language', file: 'cjk-chinese.pdf' },
  { id: 'cjk-japanese', name: 'CJK (Japanese)', desc: 'Japanese language document', cat: 'language', file: 'cjk-japanese.pdf' },
  { id: 'cjk-korean', name: 'CJK (Korean)', desc: 'Korean language document', cat: 'language', file: 'cjk-korean.pdf' },
  { id: 'rtl-arabic', name: 'RTL (Arabic)', desc: 'Arabic right-to-left document', cat: 'language', file: 'rtl-arabic.pdf' },
  { id: 'rtl-hebrew', name: 'RTL (Hebrew)', desc: 'Hebrew right-to-left document', cat: 'language', file: 'rtl-hebrew.pdf' },
  { id: 'multi-language', name: 'Multi-Language', desc: 'Multiple languages in one document', cat: 'language', file: 'multi-language.pdf' },
  // Features
  { id: 'color-themes', name: 'Color Themes', desc: 'Color theme showcase', cat: 'features', file: 'color-themes.pdf' },
  { id: 'lua-showcase', name: 'Lua Showcase', desc: 'LuaLaTeX features demo', cat: 'features', file: 'lua-showcase.pdf' },
  { id: 'music', name: 'Music', desc: 'Musical notation (MusiXTeX)', cat: 'features', file: 'music.pdf' },
  { id: 'accessibility-test', name: 'Accessibility Test', desc: 'PDF accessibility features', cat: 'features', file: 'accessibility-test.pdf' },
  { id: 'plugin-demo', name: 'Plugin Demo', desc: 'Plugin system demonstration', cat: 'features', file: 'plugin-demo.pdf' },
  { id: 'recipe', name: 'Recipe', desc: 'Recipe card', cat: 'features', file: 'recipe.pdf' },
  // Starter
  { id: 'minimal-starter', name: 'Minimal Starter', desc: 'Bare minimum template', cat: 'starter', file: 'minimal-starter.pdf' },
  { id: 'minimal-custom', name: 'Minimal Custom', desc: 'Customized minimal template', cat: 'starter', file: 'minimal-custom.pdf' },
];

const CATEGORIES = ['all', 'academic', 'professional', 'presentation', 'technical', 'language', 'features', 'starter'] as const;

export default function GalleryGrid() {
  const [activeCategory, setActiveCategory] = createSignal<string>('all');
  const [searchQuery, setSearchQuery] = createSignal('');
  let gridRef: HTMLDivElement | undefined;

  onMount(() => {
    if (gridRef) autoAnimate(gridRef);
  });

  const filteredDocs = () => {
    const cat = activeCategory();
    const q = searchQuery().toLowerCase();
    return DOCUMENTS.filter(d => {
      const matchCat = cat === 'all' || d.cat === cat;
      const matchSearch = !q || d.name.toLowerCase().includes(q) || d.desc.toLowerCase().includes(q);
      return matchCat && matchSearch;
    });
  };

  const base = getBaseURL();

  return (
    <div>
      <div class="controls">
        <Tabs value={activeCategory()} onChange={setActiveCategory} aria-label="Document categories">
          <Tabs.List class="category-tabs">
            <For each={CATEGORIES}>
              {(cat) => (
                <Tabs.Trigger value={cat} class="tab">
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </Tabs.Trigger>
              )}
            </For>
          </Tabs.List>
        </Tabs>
        <input
          type="text"
          placeholder="Search documents..."
          value={searchQuery()}
          onInput={(e) => setSearchQuery(e.currentTarget.value)}
          class="search-input"
          aria-label="Search documents"
        />
      </div>

      <div ref={gridRef} class="grid" role="tabpanel" aria-label="Document gallery">
        <For each={filteredDocs()}>
          {(doc) => (
            <a
              href={`${base}pdfs/${doc.file}`}
              target="_blank"
              rel="noopener noreferrer"
              class="card"
              aria-label={`${doc.name}: ${doc.desc}`}
            >
              <div class="card-icon">
                <svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                </svg>
              </div>
              <div class="card-name">{doc.name}</div>
              <div class="card-desc">{doc.desc}</div>
              <span class="card-cat">{doc.cat}</span>
            </a>
          )}
        </For>
      </div>

      <Show when={filteredDocs().length === 0}>
        <div class="empty-state">
          <p>No documents match your search.</p>
        </div>
      </Show>
    </div>
  );
}
