import { createSignal, onMount, onCleanup, Show } from 'solid-js';

interface Props {
  url: string;
  title?: string;
}

export default function PdfViewer(props: Props) {
  const [loaded, setLoaded] = createSignal(false);
  const [error, setError] = createSignal(false);
  let containerRef: HTMLDivElement | undefined;

  onMount(() => {
    // PDF.js is loaded from CDN
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.min.mjs';
    script.type = 'module';
    script.onload = () => setLoaded(true);
    script.onerror = () => setError(true);
    document.head.appendChild(script);
  });

  return (
    <div class="pdf-viewer" ref={containerRef}>
      <Show when={!error()} fallback={
        <div class="pdf-fallback">
          <p>PDF viewer unavailable. <a href={props.url} target="_blank" rel="noopener noreferrer">Download PDF</a></p>
        </div>
      }>
        <Show when={loaded()} fallback={
          <div class="pdf-loading">Loading viewer...</div>
        }>
          <iframe
            src={`https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/web/viewer.html?file=${encodeURIComponent(props.url)}`}
            title={props.title || 'PDF Preview'}
            style={{ width: '100%', height: '100%', border: 'none' }}
            loading="lazy"
          />
        </Show>
      </Show>
    </div>
  );
}
