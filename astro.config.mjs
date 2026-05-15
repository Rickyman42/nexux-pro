// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://nexux.pro',
  integrations: [sitemap()],
  vite: {
    plugins: [tailwindcss()],
  },
  server: {
    host: '0.0.0.0',
    port: 4325,
  },
});
