
const CATS = [
  {id:'all',label:'All'},
  {id:'featured',label:'Root'},
  {id:'academic',label:'Academic'},
  {id:'professional',label:'Professional'},
  {id:'books',label:'Books & Reference'},
  {id:'features',label:'Themes & Features'},
  {id:'multilingual',label:'Multilingual'},
  {id:'lifestyle',label:'Lifestyle'},
  {id:'templates',label:'Templates'},
];

const DOCS = [
  {id:'thesis',name:'Thesis',desc:'Academic thesis',cat:'academic',file:'pdfs/thesis.pdf'},
  {id:'thesis-spacing',name:'Thesis (Spacing)',desc:'Line spacing variants',cat:'academic',file:'pdfs/thesis-spacing.pdf'},
  {id:'thesis-tuhh',name:'Thesis (TUHH)',desc:'TUHH institution',cat:'academic',file:'pdfs/thesis-tuhh.pdf'},
  {id:'dissertation',name:'Dissertation',desc:'Dissertation',cat:'academic',file:'pdfs/dissertation.pdf'},
  {id:'article',name:'Article',desc:'Standard article',cat:'academic',file:'pdfs/article.pdf'},
  {id:'journal',name:'Journal',desc:'Journal article',cat:'academic',file:'pdfs/journal.pdf'},
  {id:'inline-paper',name:'Inline Paper',desc:'Inline research paper',cat:'academic',file:'pdfs/inline-paper.pdf'},
  {id:'citation-styles',name:'Citation Styles',desc:'Bibliography styles',cat:'academic',file:'pdfs/citation-styles.pdf'},
  {id:'cv',name:'CV',desc:'Curriculum vitae',cat:'professional',file:'pdfs/cv.pdf'},
  {id:'cv-twopage',name:'CV (Two-Page)',desc:'Two-page CV',cat:'professional',file:'pdfs/cv-twopage.pdf'},
  {id:'cover-letter',name:'Cover Letter',desc:'Cover letter',cat:'professional',file:'pdfs/cover-letter.pdf'},
  {id:'cover-letter-formal',name:'Cover Letter (Formal)',desc:'Formal cover letter',cat:'professional',file:'pdfs/cover-letter-formal.pdf'},
  {id:'letter',name:'Letter',desc:'Formal letter',cat:'professional',file:'pdfs/letter.pdf'},
  {id:'presentation',name:'Presentation',desc:'Slide presentation',cat:'professional',file:'pdfs/presentation.pdf'},
  {id:'beamer-academic',name:'Beamer (Academic)',desc:'Academic beamer slides',cat:'professional',file:'pdfs/beamer-academic.pdf'},
  {id:'beamer-corporate',name:'Beamer (Corporate)',desc:'Corporate beamer slides',cat:'professional',file:'pdfs/beamer-corporate.pdf'},
  {id:'beamer-minimal',name:'Beamer (Minimal)',desc:'Minimal beamer slides',cat:'professional',file:'pdfs/beamer-minimal.pdf'},
  {id:'beamer-native',name:'Beamer (Native)',desc:'Native beamer doctype',cat:'professional',file:'pdfs/beamer-native.pdf'},
  {id:'beamer-defense',name:'Beamer (Defense)',desc:'Thesis defense slides',cat:'professional',file:'pdfs/beamer-defense.pdf'},
  {id:'poster',name:'Poster',desc:'Conference poster',cat:'professional',file:'pdfs/poster.pdf'},
  {id:'standard',name:'Standard',desc:'Standards document',cat:'professional',file:'pdfs/standard.pdf'},
  {id:'patent',name:'Patent',desc:'Patent application',cat:'professional',file:'pdfs/patent.pdf'},
  {id:'book',name:'Book',desc:'Book',cat:'books',file:'pdfs/book.pdf'},
  {id:'manual',name:'Manual',desc:'Manual / handbook',cat:'books',file:'pdfs/manual.pdf'},
  {id:'dictionary',name:'Dictionary',desc:'Dictionary / lexicon',cat:'books',file:'pdfs/dictionary.pdf'},
  {id:'technical-report',name:'Technical Report',desc:'Technical report',cat:'books',file:'pdfs/technical-report.pdf'},
  {id:'color-themes',name:'Color Themes',desc:'All color palettes',cat:'features',file:'pdfs/color-themes.pdf'},
  {id:'article-color',name:'Article (Color)',desc:'Color mode article',cat:'features',file:'pdfs/article-color.pdf'},
  {id:'multi-language',name:'Multi-Language',desc:'Multiple languages',cat:'multilingual',file:'pdfs/multi-language.pdf'},
  {id:'cjk-chinese',name:'CJK Chinese',desc:'Chinese document',cat:'multilingual',file:'pdfs/cjk-chinese.pdf'},
  {id:'cjk-japanese',name:'CJK Japanese',desc:'Japanese document',cat:'multilingual',file:'pdfs/cjk-japanese.pdf'},
  {id:'cjk-korean',name:'CJK Korean',desc:'Korean document',cat:'multilingual',file:'pdfs/cjk-korean.pdf'},
  {id:'rtl-arabic',name:'RTL Arabic',desc:'Arabic document',cat:'multilingual',file:'pdfs/rtl-arabic.pdf'},
  {id:'rtl-hebrew',name:'RTL Hebrew',desc:'Hebrew document',cat:'multilingual',file:'pdfs/rtl-hebrew.pdf'},
  {id:'minimal-starter',name:'Minimal Starter',desc:'Bare minimum template',cat:'templates',file:'pdfs/minimal-starter.pdf'},
  {id:'minimal-custom',name:'Minimal Custom',desc:'Customized minimal',cat:'templates',file:'pdfs/minimal-custom.pdf'},
  {id:'accessibility-test',name:'Accessibility',desc:'Accessibility features',cat:'templates',file:'pdfs/accessibility-test.pdf'},
  {id:'lua-showcase',name:'Lua Showcase',desc:'LuaLaTeX integration',cat:'templates',file:'pdfs/lua-showcase.pdf'},
  {id:'exam',name:'Exam',desc:'Examination paper',cat:'academic',file:'pdfs/exam.pdf'},
  {id:'homework',name:'Homework',desc:'Homework assignment',cat:'academic',file:'pdfs/homework.pdf'},
  {id:'research-proposal',name:'Research Proposal',desc:'Research proposal',cat:'academic',file:'pdfs/research-proposal.pdf'},
  {id:'lecture-notes',name:'Lecture Notes',desc:'Academic lecture notes',cat:'academic',file:'pdfs/lecture-notes.pdf'},
  {id:'syllabus',name:'Syllabus',desc:'Course syllabus',cat:'academic',file:'pdfs/syllabus.pdf'},
  {id:'handout',name:'Handout',desc:'Teaching handout',cat:'academic',file:'pdfs/handout.pdf'},
  {id:'memo',name:'Memo',desc:'Internal memorandum',cat:'professional',file:'pdfs/memo.pdf'},
  {id:'white-paper',name:'White Paper',desc:'Position paper',cat:'professional',file:'pdfs/white-paper.pdf'},
  {id:'invoice',name:'Invoice',desc:'Commercial invoice',cat:'professional',file:'pdfs/invoice.pdf'},
  {id:'recipe',name:'Recipe',desc:'Cooking recipe',cat:'lifestyle',file:'pdfs/recipe.pdf'},
];

const catTabs = document.getElementById('cat-tabs');
const docGrid = document.getElementById('doc-grid');
const lightbox = document.getElementById('lightbox');
const lbTitle = document.getElementById('lb-title');
const lbIframe = document.getElementById('lb-iframe');
const lbClose = document.getElementById('lb-close');
const loadedCards = new Set();

let activeCat = 'all';

function renderTabs() {
  catTabs.innerHTML = CATS.map(c =>
    `<button class="cat-tab${c.id===activeCat?' active':''}" data-cat="${c.id}" role="tab" aria-selected="${c.id===activeCat}" aria-controls="doc-grid" id="tab-${c.id}">${c.label}</button>`
  ).join('');
}

function filteredDocs() {
  if (activeCat === 'all') return DOCS;
  return DOCS.filter(d => d.cat === activeCat);
}

function placeholderSVG() {
  return `<div class="card-placeholder">
    <svg width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
      <polyline points="10 9 9 9 8 9"/>
    </svg>
    <span>Scroll to load preview</span>
  </div>`;
}

function renderGrid() {
  const docs = filteredDocs();
  if (!docs.length) {
    docGrid.innerHTML = `<div class="empty-state">
      <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <p>No documents in this category.</p>
    </div>`;
    return;
  }
  docGrid.innerHTML = docs.map(d => {
    const isFeatured = d.cat === 'featured';
    const isLoaded = loadedCards.has(d.id);
    return `<div class="card card-loading${isFeatured?' featured':''}" data-id="${d.id}" data-file="${d.file}" role="button" tabindex="0">
      <div class="card-preview">${isLoaded ? '' : placeholderSVG()}</div>
      <div class="card-info">
        <div class="card-name">${d.name}</div>
        <div class="card-desc">${d.desc}</div>
        <span class="card-cat">${d.cat}</span>
      </div>
    </div>`;
  }).join('');
  observeCards();
}

function loadCardPreview(card) {
  const id = card.dataset.id;
  const file = card.dataset.file;
  if (loadedCards.has(id)) return;
  loadedCards.add(id);
  const preview = card.querySelector('.card-preview');
  preview.innerHTML = '';
  const iframe = document.createElement('iframe');
  iframe.src = file;
  iframe.loading = 'lazy';
  iframe.setAttribute('aria-hidden', 'true');
  preview.appendChild(iframe);
  card.classList.remove('card-loading');
}

function observeCards() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        loadCardPreview(e.target);
        observer.unobserve(e.target);
      }
    });
  }, { rootMargin: '200px' });
  docGrid.querySelectorAll('.card').forEach(c => observer.observe(c));
}

catTabs.addEventListener('click', e => {
  const tab = e.target.closest('.cat-tab');
  if (!tab) return;
  activeCat = tab.dataset.cat;
  catTabs.querySelectorAll('.cat-tab').forEach(t => t.classList.toggle('active', t.dataset.cat === activeCat));
  renderGrid();
});

docGrid.addEventListener('keydown', e => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    const card = e.target.closest('.card');
    if (!card) return;
    card.click();
  }
});

let lastFocusedElement = null;

docGrid.addEventListener('click', e => {
  const card = e.target.closest('.card');
  if (!card) return;
  const doc = DOCS.find(d => d.id === card.dataset.id);
  if (!doc) return;
  lastFocusedElement = card;
  lbTitle.textContent = doc.name + ' \u2014 ' + doc.desc;
  lbIframe.src = doc.file;
  lightbox.classList.add('open');
  lightbox.removeAttribute('hidden');
  document.body.style.overflow = 'hidden';
  lbClose.focus();
});

function closeLightbox() {
  lightbox.classList.remove('open');
  lightbox.setAttribute('hidden', '');
  document.body.style.overflow = '';
  setTimeout(() => { lbIframe.src = ''; }, 200);
  if (lastFocusedElement) {
    lastFocusedElement.focus();
    lastFocusedElement = null;
  }
}

lbClose.addEventListener('click', closeLightbox);
lightbox.addEventListener('click', e => {
  if (e.target === lightbox || e.target.classList.contains('lightbox-body')) closeLightbox();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && lightbox.classList.contains('open')) {
    closeLightbox();
    return;
  }
  // Focus trap: keep Tab within the lightbox when open
  if (e.key === 'Tab' && lightbox.classList.contains('open')) {
    const focusable = lightbox.querySelectorAll('button, [href], [tabindex]:not([tabindex="-1"])');
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
});

renderTabs();
renderGrid();
