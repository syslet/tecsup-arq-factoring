// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import react from '@astrojs/react';

// https://astro.build/config
export default defineConfig({
  vite: {
    // @ts-expect-error - Vite version compatibility between Astro and Tailwind
    plugins: [tailwindcss()]
  },

  integrations: [react()]
});