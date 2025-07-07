import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 6070,
    proxy: {
      '/api': {
        target: 'http://web:8000',
        changeOrigin: true,
      },
      '/scraping': {
        target: 'http://web:8000',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://web:8000',
        changeOrigin: true,
      }
    }
  }
})