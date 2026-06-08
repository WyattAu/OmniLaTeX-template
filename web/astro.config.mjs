import { defineConfig } from 'astro/config';
import solidJs from '@astrojs/solid-js';
import mdx from '@astrojs/mdx';

export default defineConfig({
  site: 'https://wyattau.github.io/OmniLaTeX-template/',
  base: '/OmniLaTeX-template',
  integrations: [solidJs(), mdx()],
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
