import { createVuetify } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

export const vuetify = createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi },
  },
  theme: {
    defaultTheme: 'aeonicLight',
    themes: {
      aeonicLight: {
        dark: false,
        colors: {
          background: '#f5f3ec',
          surface: '#ffffff',
          primary: '#0f9d8e',
          secondary: '#1d1b17',
          accent: '#b9743a',
          error: '#b3503a',
          info: '#3a5a86',
          success: '#2f8f6b',
          warning: '#b9743a',
        },
      },
    },
  },
  defaults: {
    VBtn: {
      rounded: 'lg',
      elevation: 0,
    },
    VCard: {
      rounded: 'xl',
      elevation: 0,
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
    },
  },
});
