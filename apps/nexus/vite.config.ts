import vue from '@vitejs/plugin-vue';
import vuetify from 'vite-plugin-vuetify';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [
    vue(),
    vuetify({
      autoImport: true,
      styles: { configFile: 'src/styles/settings.scss' },
    }),
  ],
  server: {
    allowedHosts: ['nexus-test.viper.guru'],
  },
});
