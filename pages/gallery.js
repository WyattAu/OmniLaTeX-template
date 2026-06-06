
const PROFILES = [
  {id:'thesis',        name:'Thesis',           desc:'Academic thesis',               cls:'scrbook',  icon:'Doc'},
  {id:'dissertation',  name:'Dissertation',      desc:'Dissertation',                  cls:'scrbook',  icon:'Dis'},
  {id:'article',       name:'Article',           desc:'Standard article',              cls:'scrartcl', icon:'Art'},
  {id:'journal',       name:'Journal',           desc:'Journal article',               cls:'scrartcl', icon:'Jnl'},
  {id:'cv',            name:'CV',                desc:'Curriculum vitae',              cls:'scrartcl', icon:'CV'},
  {id:'presentation',  name:'Presentation',      desc:'Presentation slides',           cls:'scrartcl', icon:'Pres'},
  {id:'poster',        name:'Poster',            desc:'Conference poster',             cls:'scrartcl', icon:'Pos'},
  {id:'letter',        name:'Letter',            desc:'Formal letter',                 cls:'scrartcl', icon:'Let'},
  {id:'book',          name:'Book',              desc:'Book',                          cls:'scrbook',  icon:'Bk'},
  {id:'manual',        name:'Manual',            desc:'Manual / handbook',             cls:'scrreprt', icon:'Man'},
  {id:'technicalreport',name:'Technical Report', desc:'Technical report',              cls:'scrreprt', icon:'TR'},
  {id:'standard',      name:'Standard',          desc:'Standards document',            cls:'scrreprt', icon:'Std'},
  {id:'patent',        name:'Patent',            desc:'Patent application',            cls:'scrreprt', icon:'Pat'},
  {id:'cover-letter',  name:'Cover Letter',      desc:'Cover letter',                  cls:'scrartcl', icon:'CL'},
  {id:'dictionary',    name:'Dictionary',        desc:'Dictionary / lexicon',          cls:'scrbook',  icon:'Dic'},
  {id:'inlinepaper',   name:'Inline Paper',      desc:'Inline research paper',         cls:'scrartcl', icon:'IP'},
];

const INST_MAP = {
  none:'', tuhh:'tuhh', tum:'tum', eth:'eth',
  mit:'mit', stanford:'stanford', cambridge:'cambridge', tudelft:'tudelft',
};

const LANG_LABELS = {
  english:'English', german:'German', french:'French', spanish:'Spanish',
  portuguese:'Portuguese', italian:'Italian', dutch:'Dutch', russian:'Russian',
  chinese:'Chinese', japanese:'Japanese', korean:'Korean', arabic:'Arabic',
};

const INST_LABELS = {
  none:'None', tuhh:'TUHH', tum:'TUM', eth:'ETH Zürich',
  mit:'MIT', stanford:'Stanford', cambridge:'Cambridge', tudelft:'TU Delft',
};

let selected = 'thesis';

const grid = document.getElementById('profile-grid');
const langSel = document.getElementById('lang');
const instSel = document.getElementById('inst');
const codeOut = document.getElementById('code-output');

function renderCards() {
  grid.innerHTML = PROFILES.map(p => `
    <div class="card${p.id===selected?' selected':''}" data-id="${p.id}" role="button" tabindex="0">
      <div class="card-icon">${p.icon}</div>
      <div class="card-name">${p.name}</div>
      <div class="card-desc">${p.desc}</div>
      <span class="card-class">${p.cls}</span>
    </div>
  `).join('');
}

function getDocClass() {
  const lang = langSel.value;
  const inst = instSel.value;
  const profile = PROFILES.find(p => p.id === selected);
  let opts = `doctype=${profile.id},language=${lang}`;
  if (inst !== 'none') opts += `,institution=${inst}`;
  return `\\documentclass[${opts}]{omnilatex}`;
}

function updatePreview() {
  const lang = langSel.value;
  const inst = instSel.value;
  const profile = PROFILES.find(p => p.id === selected);
  let optsParts = [`doctype=<span class="val">${profile.id}</span>`, `language=<span class="val">${lang}</span>`];
  if (inst !== 'none') optsParts.push(`institution=<span class="val">${inst}</span>`);
  const optsStr = optsParts.join(',<span class="opt"> </span>');
  codeOut.innerHTML =
    `<span class="cm">% OmniLaTeX — ${profile.name} Template</span>\n` +
    `<span class="kw">\\documentclass</span>[${optsStr}]<span class="opt">{</span><span class="val">omnilatex</span><span class="opt">}</span>\n\n` +
    `<span class="kw">\\begin</span><span class="opt">{</span><span class="val">document</span><span class="opt">}</span>\n` +
    `  <span class="cm">% Your content here</span>\n` +
    `<span class="kw">\\end</span><span class="opt">{</span><span class="val">document</span><span class="opt">}</span>`;
}

function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

grid.addEventListener('keydown', e => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    const card = e.target.closest('.card');
    if (!card) return;
    card.click();
  }
});

grid.addEventListener('click', e => {
  const card = e.target.closest('.card');
  if (!card) return;
  selected = card.dataset.id;
  grid.querySelectorAll('.card').forEach(c => c.classList.toggle('selected', c.dataset.id === selected));
  updatePreview();
});

langSel.addEventListener('change', updatePreview);
instSel.addEventListener('change', updatePreview);

document.getElementById('btn-download').addEventListener('click', () => {
  window.open('https://github.com/WyattAu/OmniLaTeX-template/archive/refs/heads/main.zip', '_blank');
  showToast('Download started! Customize your document by editing main.tex');
});

document.getElementById('btn-copy').addEventListener('click', () => {
  const text = getDocClass();
  navigator.clipboard.writeText(text).then(() => {
    showToast('Copied to clipboard!');
  }).catch(() => {
    const ta = document.createElement('textarea');
    ta.value = text; document.body.appendChild(ta);
    ta.select(); document.execCommand('copy');
    document.body.removeChild(ta);
    showToast('Copied to clipboard!');
  });
});

document.querySelectorAll('nav a[href^="#"]').forEach(a => {
  a.addEventListener('click', () => {
    document.querySelectorAll('nav a').forEach(x => x.classList.remove('active'));
    a.classList.add('active');
  });
});

renderCards();
updatePreview();
