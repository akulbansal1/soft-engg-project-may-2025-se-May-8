import path from "path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(), 
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Swaasthy App',
        short_name: 'Swaasthy',
        start_url: '/',
        display: 'standalone',
        description: 'Senior Wellness and Health Application',
        background_color: '#0f172a',
        theme_color: '#0f172a',
        icons: [
          { src: '/meditation_logo_192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
          { src: '/meditation_logo_512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' }
        ],
      },
    }),
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
