import { createSignal, For, Show } from 'solid-js';

interface Document {
  id: string;
  name: string;
  desc: string;
  cat: string;
  file: string;
}

const DOCUMENTS: Document[] = [
  { id: 'thesis', name: 'Thesis', desc: 'Academic thesis with chapters', cat: 'academic', file: 'thesis.pdf' },
  { id: 'article', name: 'Article', desc: 'Journal article format', cat: 'academic', file: 'article.pdf' },
  { id: 'book', name: 'Book', desc: 'Full book with parts', cat: 'academic', file: 'book.pdf' },
  { id: 'dissertation', name: 'Dissertation', desc: 'Doctoral dissertation', cat: 'academic', file: 'dissertation.pdf' },
  { id: 'cv', name: 'CV', desc: 'Curriculum vitae', cat: 'professional', file: 'cv.pdf' },
  { id: 'cover-letter', name: 'Cover Letter', desc: 'Professional cover letter', cat: 'professional', file: 'cover-letter.pdf' },
  { id: 'letter', name: 'Letter', desc: 'Formal correspondence', cat: 'professional', file: 'letter.pdf' },
  { id: 'invoice', name: 'Invoice', desc: 'Business invoice', cat: 'professional', file: 'invoice.pdf' },
  { id: 'presentation', name: 'Presentation', desc: 'Beamer slides', cat: 'presentation', file: 'presentation.pdf' },
  { id: 'poster', name: 'Poster', desc: 'Conference poster', cat: 'presentation', file: 'poster.pdf' },
  { id: 'manual', name: 'Manual', desc: 'Technical manual', cat: 'technical', file: 'manual.pdf' },
  { id: 'technical-report', name: 'Technical Report', desc: 'Engineering report', cat: 'technical', file: 'technical-report.pdf' },
  { id: 'standard', name: 'Standard', desc: 'Standards document', cat: 'technical', file: 'standard.pdf' },
  { id: 'patent', name: 'Patent', desc: 'Patent application', cat: 'technical', file: 'patent.pdf' },
  { id: 'exam', name: 'Exam', desc: 'Examination paper', cat: 'academic', file: 'exam.pdf' },
  { id: 'homework', name: 'Homework', desc: 'Problem set', cat: 'academic', file: 'homework.pdf' },
  { id: 'handout', name: 'Handout', desc: 'Class handout', cat: 'academic', file: 'handout.pdf' },
  { id: 'lecture-notes', name: 'Lecture Notes', desc: 'Course notes', cat: 'academic', file: 'lecture-notes.pdf' },
  { id: 'syllabus', name: 'Syllabus', desc: 'Course syllabus', cat: 'academic', file: 'syllabus.pdf' },
  { id: 'memo', name: 'Memo', desc: 'Memorandum', cat: 'professional', file: 'memo.pdf' },
  { id: 'white-paper', name: 'White Paper', desc: 'Technical white paper', cat: 'professional', file: 'white-paper.pdf' },
  { id: 'research-proposal', name: 'Research Proposal', desc: 'Grant proposal', cat: 'academic', file: 'research-proposal.pdf' },
  { id: 'recipe', name: 'Recipe', desc: 'Recipe card', cat: 'other', file: 'recipe.pdf' },
  { id: 'dictionary', name: 'Dictionary', desc: 'Reference dictionary', cat: 'other', file: 'dictionary.pdf' },
];

const CATEGORIES = ['all', 'academic', 'professional', 'presentation', 'technical', 'other'];

export default function GalleryGrid() {
  const [activeCategory, setActiveCategory] = createSignal('all');
  const [searchQuery, setSearchQuery] = createSignal('');

  const filteredDocs = () => {
    const cat = activeCategory();
    const q = searchQuery().toLowerCase();
    return DOCUMENTS.filter(d => {
      const matchCat = cat === 'all' || d.cat === cat;
      const matchSearch = !q || d.name.toLowerCase().includes(q) || d.desc.toLowerCase().includes(q);
      return matchCat && matchSearch;
    });
  };

  const base = import.meta.env.BASE_URL;

  return (
    <div>
      <div class="controls">
        <div class="category-tabs" role="tablist" aria-label="Document categories">
          <For each={CATEGORIES}>
            {(cat) => (
              <button
                role="tab"
                aria-selected={activeCategory() === cat}
                class={`tab ${activeCategory() === cat ? 'active' : ''}`}
                onClick={() => setActiveCategory(cat)}
              >
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </button>
            )}
          </For>
        </div>
        <input
          type="text"
          placeholder="Search documents..."
          value={searchQuery()}
          onInput={(e) => setSearchQuery(e.currentTarget.value)}
          class="search-input"
          aria-label="Search documents"
        />
      </div>

      <div class="grid" role="listbox" aria-label="Document gallery">
        <For each={filteredDocs()}>
          {(doc) => (
            <a
              href={`${base}pdfs/${doc.file}`}
              target="_blank"
              rel="noopener noreferrer"
              class="card"
              role="option"
              aria-label={`${doc.name}: ${doc.desc}`}
            >
              <div class="card-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
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
