import { defineConfig } from 'astro/config';
import solidJs from '@astrojs/solid-js';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://wyattau.github.io/OmniLaTeX-template/',
  base: '/OmniLaTeX-template',
  integrations: [solidJs(), mdx(), sitemap()],
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
