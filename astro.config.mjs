// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';
import vercel from '@astrojs/vercel';

export default defineConfig({
  site: 'https://nexux.pro',
  trailingSlash: 'never',
  output: 'server',
  adapter: vercel(),
  integrations: [sitemap({
    filter: (page) => !page.includes('/gracias') && !page.includes('/admin') && !page.includes('/acceso-denegado'),
  })],
  vite: {
    plugins: [tailwindcss()],
  },
  server: {
    host: '0.0.0.0',
    port: 4325,
  },
});
