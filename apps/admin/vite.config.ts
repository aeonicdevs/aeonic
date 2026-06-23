import vue from '@vitejs/plugin-vue';
import vuetify from 'vite-plugin-vuetify';
import { defineConfig } from 'vite';

const allowedHosts = (process.env.VITE_ALLOWED_HOSTS ?? 'localhost,127.0.0.1')
  .split(',')
  .map((host) => host.trim())
  .filter(Boolean);

export default defineConfig({
  plugins: [
    vue(),
    vuetify({
      autoImport: true,
      styles: { configFile: 'src/styles/settings.scss' },
    }),
  ],
  server: {
    allowedHosts,
  },
});
