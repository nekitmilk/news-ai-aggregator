import path from 'node:path';
import react from '@vitejs/plugin-react-swc';
import { defineConfig } from 'vite';

// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    allowedHosts: [
      'https://79be9acd1293e8baf0ccf75a67e420dc.serveo.net/',
      '.serveo.net', // разрешаем все субдомены loca.lt
    ],
    proxy: {
      '/api': {
        target: 'http://localhost:8000/api/v1',
        changeOrigin: true,
      },
    },
  },
  build: {
    assetsInlineLimit: 0,
  },
  plugins: [react()],
});
