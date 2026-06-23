import { createVuetify } from 'vuetify';
import { aliases, mdi } from 'vuetify/iconsets/mdi';

export const vuetify = createVuetify({
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: { mdi },
  },
  theme: {
    defaultTheme: 'aeonicAdmin',
    themes: {
      aeonicAdmin: {
        dark: false,
        colors: {
          background: '#f7f5ef',
          surface: '#ffffff',
          primary: '#0f8f83',
          secondary: '#1f2421',
          accent: '#9f6537',
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
      rounded: 'lg',
      elevation: 0,
    },
    VTextField: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
    },
    VSelect: {
      variant: 'outlined',
      density: 'comfortable',
      color: 'primary',
    },
  },
});
