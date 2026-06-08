import { createSignal, Show, onMount } from 'solid-js';

const DOCTYPES = [
  'article', 'book', 'thesis', 'dissertation', 'cv', 'cover-letter',
  'letter', 'presentation', 'poster', 'manual', 'technical-report',
  'standard', 'patent', 'research-proposal', 'exam', 'homework',
  'handout', 'lecture-notes', 'syllabus', 'memo', 'white-paper',
  'invoice', 'recipe', 'dictionary', 'journal', 'inlinepaper', 'beamer',
];

const INSTITUTIONS = [
  'none', 'aalto', 'cambridge', 'chalmers', 'cmu', 'columbia', 'epfl',
  'eth', 'harvard', 'imperial', 'kit', 'mit', 'ntnu', 'oxford',
  'princeton', 'stanford', 'tudelft', 'tuhh', 'tum', 'uoft', 'yale',
];

const LANGUAGES = [
  'english', 'german', 'french', 'spanish', 'italian', 'portuguese',
  'russian', 'dutch', 'polish', 'czech', 'greek', 'turkish', 'swedish',
  'finnish', 'danish', 'norwegian', 'chinese', 'japanese', 'korean',
  'arabic', 'persian', 'hebrew', 'vietnamese', 'hindi', 'thai', 'bengali',
];

interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  classLine: string;
}

function validate(doctype: string, institution: string, language: string): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (!DOCTYPES.includes(doctype)) {
    errors.push(`Unknown doctype: "${doctype}". Valid: ${DOCTYPES.join(', ')}`);
  }
  if (!INSTITUTIONS.includes(institution)) {
    errors.push(`Unknown institution: "${institution}". Valid: ${INSTITUTIONS.join(', ')}`);
  }
  if (!LANGUAGES.includes(language)) {
    warnings.push(`Language "${language}" may not be fully supported. Check polyglossia documentation.`);
  }

  // Doctype-specific warnings
  if (['thesis', 'dissertation', 'book', 'dictionary'].includes(doctype) && institution === 'none') {
    warnings.push(`Doctype "${doctype}" typically uses an institution config for branding.`);
  }
  if (['arabic', 'persian', 'hebrew'].includes(language)) {
    warnings.push(`RTL language "${language}" requires LuaLaTeX with proper font support.`);
  }
  if (['chinese', 'japanese', 'korean'].includes(language)) {
    warnings.push(`CJK language "${language}" requires Noto CJK fonts installed.`);
  }

  const classLine = errors.length === 0
    ? `\\documentclass[doctype=${doctype},language=${language},institution=${institution}]{omnilatex}`
    : '';

  return { valid: errors.length === 0, errors, warnings, classLine };
}

export default function Validator() {
  const [doctype, setDoctype] = createSignal('article');
  const [institution, setInstitution] = createSignal('none');
  const [language, setLanguage] = createSignal('english');
  const [result, setResult] = createSignal<ValidationResult | null>(null);
  const [copied, setCopied] = createSignal(false);

  const runValidation = () => {
    setResult(validate(doctype(), institution(), language()));
  };

  const copyToClipboard = async () => {
    const r = result();
    if (r?.classLine) {
      await navigator.clipboard.writeText(r.classLine);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  onMount(runValidation);

  return (
    <div class="validator">
      <div class="form-grid">
        <label>
          <span class="label-text">Document Type</span>
          <select value={doctype()} onChange={(e) => { setDoctype(e.currentTarget.value); runValidation(); }}>
            {DOCTYPES.map(d => <option value={d}>{d}</option>)}
          </select>
        </label>

        <label>
          <span class="label-text">Institution</span>
          <select value={institution()} onChange={(e) => { setInstitution(e.currentTarget.value); runValidation(); }}>
            {INSTITUTIONS.map(i => <option value={i}>{i}</option>)}
          </select>
        </label>

        <label>
          <span class="label-text">Language</span>
          <select value={language()} onChange={(e) => { setLanguage(e.currentTarget.value); runValidation(); }}>
            {LANGUAGES.map(l => <option value={l}>{l}</option>)}
          </select>
        </label>
      </div>

      <Show when={result()}>
        <div class={`result ${result()!.valid ? 'valid' : 'invalid'}`} role="status" aria-live="polite">
          <Show when={result()!.errors.length > 0}>
            <div class="errors">
              <strong>Errors:</strong>
              <ul>
                {result()!.errors.map(e => <li>{e}</li>)}
              </ul>
            </div>
          </Show>

          <Show when={result()!.warnings.length > 0}>
            <div class="warnings">
              <strong>Warnings:</strong>
              <ul>
                {result()!.warnings.map(w => <li>{w}</li>)}
              </ul>
            </div>
          </Show>

          <Show when={result()!.valid}>
            <div class="class-line">
              <code>{result()!.classLine}</code>
              <button onClick={copyToClipboard} class="copy-btn" aria-label="Copy documentclass command to clipboard">
                {copied() ? 'Copied' : 'Copy'}
              </button>
            </div>
          </Show>
        </div>
      </Show>
    </div>
  );
}
