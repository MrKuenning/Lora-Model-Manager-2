import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import fs from 'fs'
import path from 'path'

let targetPort = 8080
try {
  let configPath = path.resolve(__dirname, '../backend/config.json')
  if (!fs.existsSync(configPath)) {
    configPath = path.resolve(__dirname, '../config.json')
  }
  if (fs.existsSync(configPath)) {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'))
    if (config.port) {
      targetPort = parseInt(config.port, 10) || 8080
    }
  }
} catch (e) {
  targetPort = 8080
}

const targetUrl = `http://localhost:${targetPort}`

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: targetUrl,
        changeOrigin: true
      },
      '/model-file': {
        target: targetUrl,
        changeOrigin: true
      },
      '/assets': {
        target: targetUrl,
        changeOrigin: true
      }
    },
    fs: {
      strict: false
    }
  }
})
