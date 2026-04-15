// Import Vite's helper function for defining configuration with type hints and validation
import { defineConfig } from 'vite'

// Import the official Vite plugin that adds React support (JSX transpilation, Fast Refresh, etc.)
import react from '@vitejs/plugin-react'

// Export the Vite configuration object — Vite reads this file automatically at build/dev time
export default defineConfig({
  // Plugins extend Vite's capabilities; here we enable React support
  plugins: [react()],

  // Settings for the local development server (used when you run `npm run dev`)
  server: {
    // The port the dev server listens on — open http://localhost:5173 in your browser
    port: 5173,

    // Proxy rules redirect certain requests from the frontend to the backend,
    // avoiding CORS issues during local development
    proxy: {
      // Any request whose path starts with /api will be forwarded to the backend
      '/api': {
        // The backend server address — change this if your backend runs on a different port
        target: 'http://localhost:8000',

        // Rewrites the Host header to match the target, required by most backend frameworks
        changeOrigin: true
      }
    }
  }
})

