import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../', import.meta.url));
const three = (file) => fileURLToPath(new URL(`../vendor/three/${file}`, import.meta.url));
const fiber = fileURLToPath(new URL('../vendor/react-three-fiber/packages/fiber/src/index.tsx', import.meta.url));
export default defineConfig({
  plugins: [react()],
  worker: { format: 'es' },
  root,
  base: './',
  publicDir: false,
  resolve: {
    dedupe: ['three', 'lil-gui', 'three-mesh-bvh', 'react', 'react-dom'],
    alias: [
      { find: '@vibegameengine/react-three-fiber', replacement: fiber },
      { find: '@react-three/fiber', replacement: fiber },
      { find: /^three\/webgpu$/, replacement: three('src/Three.WebGPU.js') },
      { find: /^three\/tsl$/, replacement: three('src/Three.TSL.js') },
      { find: /^three\/(?:addons|examples\/jsm)\//, replacement: three('examples/jsm/') },
      { find: /^three$/, replacement: three('src/Three.js') },
    ],
  },
  optimizeDeps: { entries: ['atlas.html'], exclude: ['three'] },
  server: { host: '127.0.0.1', port: 5190, strictPort: true, fs: { allow: [root, fileURLToPath(new URL('../../', import.meta.url))] } },
  build: {
    target: 'esnext',
    outDir: process.env.ATLAS_OUTPUT || '.atlas-dist',
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: { input: fileURLToPath(new URL('../atlas.html', import.meta.url)) },
  },
});
