import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      },
      '/model-file': {
        target: 'http://localhost:8080',
        changeOrigin: true
      },
      '/assets': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    },
    fs: {
      strict: false
    }
  }
})
