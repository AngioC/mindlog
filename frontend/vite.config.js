import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa' // <- 1. Importa il plugin

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    // 2. Configura il plugin PWA
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'MindLog - Diario Personale',
        short_name: 'MindLog',
        description: 'Il tuo diario personale con Mood Tracker e Tag',
        theme_color: '#4F46E5', // Colore della barra di stato su mobile
        background_color: '#0f172a', // Colore della splash screen (Dark mode friendly)
        display: 'standalone', // Fa scomparire la barra dell'URL del browser!
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ]
      }
    })
  ],
})