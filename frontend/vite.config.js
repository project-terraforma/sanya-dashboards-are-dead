import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

// `base` lets GitHub Pages serve the app from /<repo-name>/. Set
// VITE_BASE in the workflow; defaults to '/' for local dev.
export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE || '/',
  resolve: {
    alias: {
      '@root': fileURLToPath(new URL('..', import.meta.url)),
    },
  },
  server: {
    fs: {
      allow: ['..'],
    },
  },
})
