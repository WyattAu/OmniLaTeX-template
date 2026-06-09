import { createSignal, onMount, Show, For } from 'solid-js';

const REPO = 'WyattAu/OmniLaTeX-template';
const API_BASE = `https://api.github.com/repos/${REPO}`;

interface CommitInfo {
  sha: string;
  shortSha: string;
  message: string;
  author: string;
  date: string;
  url: string;
  branch: string;
}

interface VerificationResult {
  status: 'match' | 'mismatch' | 'behind' | 'error' | 'loading';
  pdfCommit: string;
  headCommit: CommitInfo | null;
  commitsBehind: number;
  error?: string;
}

async function fetchHeadCommit(): Promise<CommitInfo> {
  const res = await fetch(`${API_BASE}/commits/main`);
  if (!res.ok) throw new Error(`GitHub API error: ${res.status}`);
  const data = await res.json();
  return {
    sha: data.sha,
    shortSha: data.sha.slice(0, 7),
    message: data.commit.message.split('\n')[0],
    author: data.commit.author.name,
    date: new Date(data.commit.author.date).toISOString().split('T')[0],
    url: data.html_url,
    branch: 'main',
  };
}

async function resolveCommit(sha: string): Promise<CommitInfo | null> {
  if (!sha || sha === 'n.a.') return null;
  const fullSha = sha.length < 40 ? null : sha;
  if (fullSha) {
    try {
      const res = await fetch(`${API_BASE}/commits/${fullSha}`);
      if (res.ok) {
        const data = await res.json();
        return {
          sha: data.sha,
          shortSha: data.sha.slice(0, 7),
          message: data.commit.message.split('\n')[0],
          author: data.commit.author.name,
          date: new Date(data.commit.author.date).toISOString().split('T')[0],
          url: data.html_url,
          branch: '',
        };
      }
    } catch { /* not found */ }
  }
  return { sha: sha, shortSha: sha.slice(0, 7), message: '', author: '', date: '', url: '', branch: '' };
}

async function countCommitsBehind(fromSha: string, toSha: string): Promise<number> {
  try {
    const res = await fetch(`${API_BASE}/compare/${fromSha}...${toSha}`);
    if (!res.ok) return -1;
    const data = await res.json();
    return data.ahead_by ?? data.total_commits ?? -1;
  } catch {
    return -1;
  }
}

function StatusIcon(props: { status: string }) {
  switch (props.status) {
    case 'match':
      return <span class="status-icon status-match" aria-label="Verified">&#10003;</span>;
    case 'mismatch':
      return <span class="status-icon status-mismatch" aria-label="Mismatch">&#10007;</span>;
    case 'behind':
      return <span class="status-icon status-behind" aria-label="Outdated">&#9888;</span>;
    case 'error':
      return <span class="status-icon status-error" aria-label="Error">&#33;</span>;
    default:
      return <span class="status-icon status-loading" aria-label="Loading">&#10227;</span>;
  }
}

export default function GitVerifier() {
  const [inputSha, setInputSha] = createSignal('');
  const [result, setResult] = createSignal<VerificationResult>({
    status: 'loading',
    pdfCommit: '',
    headCommit: null,
    commitsBehind: 0,
  });

  // Read commit from URL query parameter on mount
  onMount(async () => {
    const params = new URLSearchParams(window.location.search);
    const commit = params.get('commit') || '';
    if (commit && commit !== 'n.a.') {
      setInputSha(commit);
      await verify(commit);
    } else {
      setResult(r => ({ ...r, status: 'error', error: 'No commit SHA provided. Enter a SHA or click "Check for updates" in an OmniLaTeX PDF.' }));
    }
  });

  async function verify(sha: string) {
    setResult({ status: 'loading', pdfCommit: sha, headCommit: null, commitsBehind: 0 });

    try {
      const [head, pdfCommit] = await Promise.all([
        fetchHeadCommit(),
        resolveCommit(sha),
      ]);

      if (!pdfCommit) {
        setResult({ status: 'error', pdfCommit: sha, headCommit: head, commitsBehind: 0, error: 'Commit not found in repository.' });
        return;
      }

      if (pdfCommit.sha === head.sha) {
        setResult({ status: 'match', pdfCommit: sha, headCommit: head, commitsBehind: 0 });
      } else {
        const behind = await countCommitsBehind(pdfCommit.sha, head.sha);
        setResult({
          status: behind >= 0 ? 'behind' : 'mismatch',
          pdfCommit: sha,
          headCommit: head,
          commitsBehind: behind >= 0 ? behind : -1,
        });
      }
    } catch (e) {
      setResult({
        status: 'error',
        pdfCommit: sha,
        headCommit: null,
        commitsBehind: 0,
        error: e instanceof Error ? e.message : 'Failed to verify commit.',
      });
    }
  }

  const handleSubmit = (e: Event) => {
    e.preventDefault();
    const sha = inputSha().trim();
    if (sha) {
      // Update URL without reload
      const url = new URL(window.location.href);
      url.searchParams.set('commit', sha);
      history.replaceState(null, '', url.toString());
      verify(sha);
    }
  };

  const r = result();

  return (
    <div class="verifier">
      <form onSubmit={handleSubmit} class="verify-form">
        <label for="sha-input">Git Commit SHA</label>
        <div class="input-row">
          <input
            id="sha-input"
            type="text"
            value={inputSha()}
            onInput={(e) => setInputSha(e.currentTarget.value)}
            placeholder="e.g. a34858e or full 40-char SHA"
            spellcheck={false}
            autocomplete="off"
            class="sha-input"
          />
          <button type="submit" class="verify-btn" disabled={!inputSha().trim()}>
            Verify
          </button>
        </div>
      </form>

      <Show when={r.status !== 'loading'}>
        <div class={`result-panel result-${r.status}`} role="status" aria-live="polite">
          <div class="result-header">
            <StatusIcon status={r.status} />
            <span class="result-title">
              {r.status === 'match' && 'PDF matches HEAD commit'}
              {r.status === 'behind' && `PDF is ${r.commitsBehind} commit${r.commitsBehind !== 1 ? 's' : ''} behind HEAD`}
              {r.status === 'mismatch' && 'Commit not found on main branch'}
              {r.status === 'error' && 'Verification Error'}
            </span>
          </div>

          <Show when={r.error}>
            <p class="error-text">{r.error}</p>
          </Show>

          <Show when={r.pdfCommit}>
            <div class="commit-comparison">
              <div class="commit-card">
                <span class="commit-label">PDF Commit</span>
                <code class="commit-sha">{r.pdfCommit.slice(0, 7)}</code>
                <Show when={r.headCommit && r.status === 'behind'}>
                  <span class="commit-meta">
                    <a href={`${API_BASE.replace('api.', '').replace('/repos/', '/')}/commit/${r.pdfCommit}`} target="_blank" rel="noopener noreferrer">View commit</a>
                  </span>
                </Show>
              </div>

              <div class="commit-card">
                <span class="commit-label">HEAD (main)</span>
                <code class="commit-sha">{r.headCommit?.shortSha ?? '...'}</code>
                <Show when={r.headCommit}>
                  <span class="commit-meta">{r.headCommit.message}</span>
                  <span class="commit-meta">{r.headCommit.author} &middot; {r.headCommit.date}</span>
                </Show>
              </div>
            </div>
          </Show>

          <Show when={r.status === 'match'}>
            <p class="success-text">
              This PDF was built from the latest commit on the <code>main</code> branch.
              The document is up to date.
            </p>
          </Show>

          <Show when={r.status === 'behind'}>
            <p class="warning-text">
              This PDF was built from an older commit. Rebuild with{' '}
              <code>python build.py build-example {'<name>'}</code>{' '}
              to get the latest version.
            </p>
          </Show>
        </div>
      </Show>

      <Show when={r.status === 'loading'}>
        <div class="loading" role="status">
          <div class="spinner"></div>
          <span>Verifying against GitHub...</span>
        </div>
      </Show>

      <section class="how-it-works">
        <h2>How it works</h2>
        <ol>
          <li>
            OmniLaTeX embeds Git metadata into every PDF at build time via{' '}
            <code>lua/git-metadata.lua</code>. The{' '}
            <code>\GitVerificationBox</code> command creates a clickable link to this page.
          </li>
          <li>
            This page reads the embedded commit SHA and compares it against the{' '}
            <code>main</code> branch HEAD via the GitHub API.
          </li>
          <li>
            If the SHAs match, the PDF is verified as current. If they differ,
            the page shows how many commits the PDF is behind.
          </li>
        </ol>
        <p>
          To add verification to your own documents, add this to your preamble:
        </p>
        <pre><code>\GitVerificationBox</code></pre>
      </section>
    </div>
  );
}
