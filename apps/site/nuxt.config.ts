export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      titleTemplate: '%s | Aeonic',
      htmlAttrs: { lang: 'en' },
      link: [
        { rel: 'icon', type: 'image/png', href: '/assets/favicon.png' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }
      ],
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'theme-color', content: '#0d0f0c' },
        {
          name: 'description',
          content:
            'Aeonic is the clinical infrastructure for functional, performance, and precision longevity medicine.'
        },
        { property: 'og:image', content: '/assets/og-image.png' }
      ]
    }
  },
  nitro: {
    prerender: {
      crawlLinks: true
    }
  }
})
