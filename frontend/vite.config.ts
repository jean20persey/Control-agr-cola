import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0', // Permite acceso desde otros dispositivos
    proxy: {
      '/api': {
        target: 'https://limicoline-probably-travis.ngrok-free.dev', // URL pública de ngrok
        changeOrigin: true,
        secure: false,
      }
    },
    // Configuración para desarrollo limpio
    middlewareMode: false,
    hmr: {
      overlay: false // Desactivar overlay de errores para evitar mostrar errores de extensiones
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          mui: ['@mui/material', '@mui/icons-material', '@mui/x-data-grid']
        }
      }
    }
  },
  define: {
    // Variables globales
    __DEV__: JSON.stringify(true)
  },
  esbuild: {
    // Mantener console.log en desarrollo, eliminar en producción
    drop: []
  }
})
