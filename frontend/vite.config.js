import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 6070,
    allowedHosts: ['xcraper.chequeabot.com'], 
    protocol: 'wss',
    proxy: {
      '/api': {
        target: 'http://web:6060',
        changeOrigin: true,
      },
      '/scraping': {
        target: 'http://web6060',
        changeOrigin: true,
      },
      '/admin': {
        target: 'http://web:6060',
        changeOrigin: true,
      }
    }
  }
})