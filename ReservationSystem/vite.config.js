import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import { VitePWA } from 'vite-plugin-pwa';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      manifest: {
        display:'standalone',
        display_override: ['window-controls-overlay'],
        lang: 'en-EN',
        name: 'PWA GIS Reservation System',
        short_name: 'PWA_GIS_RS',
        description: 'GIS course project, for classroom reservation management, for teachers.',
        theme_color: '#19223c',
        background_color: '#d4d4d4',
        icons: 
        [
          {
          src: 'vite.svg',
          sizes: '64x64',
          type: 'image/png',
          purpose: 'any',
        },
      ]
      },
    }),
  ],
})
