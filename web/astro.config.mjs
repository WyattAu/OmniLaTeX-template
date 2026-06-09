import { defineConfig } from 'astro/config';
import solidJs from '@astrojs/solid-js';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// When CLOUDFLARE_DEPLOY=1 (set in cloudflare-pages workflow),
// build without base path for the custom domain root deployment.
const isCloudflare = process.env.CLOUDFLARE_DEPLOY === '1';

export default defineConfig({
  site: isCloudflare
    ? 'https://omnilatex-template.wyattau.com/'
    : 'https://wyattau.github.io/OmniLaTeX-template/',
  base: isCloudflare ? '/' : '/OmniLaTeX-template',
  integrations: [solidJs(), mdx(), isCloudflare ? false : sitemap()],
  output: 'static',
  build: {
    assets: 'assets',
  },
  markdown: {
    shikiConfig: {
      theme: 'github-dark',
    },
  },
});
