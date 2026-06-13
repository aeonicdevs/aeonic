export default defineNuxtConfig({
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  runtimeConfig: {
    public: {
      partnerAppUrl: process.env.NUXT_PUBLIC_PARTNER_APP_URL || 'http://127.0.0.1:5174'
    }
  },
  app: {
    head: {
      titleTemplate: '%s | Aeonic',
      htmlAttrs: { lang: 'en' },
      link: [
        { rel: 'icon', type: 'image/png', href: '/mock/assets/aeonic-mark.png' },
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
        { property: 'og:image', content: '/mock/assets/hero-systems.avif' }
      ]
    }
  },
  nitro: {
    prerender: {
      crawlLinks: false,
      routes: [
        '/',
        '/programs',
        '/treatments',
        '/catalog',
        '/member-login',
        '/nexus',
        '/partner-login',
        '/partner-signup',
        '/our-story',
        '/mission',
        '/dr-lacey',
        '/partners',
        '/press',
        '/announcements',
        '/contact',
        '/connect-inquiry',
        '/ways',
        '/privacy',
        '/terms',
        '/science',
        '/faq',
        '/whats-included',
        '/the-science',
        '/technology',
        '/labs-biomarkers',
        '/health-start',
        '/aeva',
        '/aura',
        '/aura-intelligence',
        '/connect-academy',
        '/connect-aura',
        '/connect-economics',
        '/connect-growth',
        '/connect-integrations',
        '/connect-licensing',
        '/connect-model',
        '/connect-platform-stack',
        '/connect-portal',
        '/connect-pricing',
        '/connect-protocol-engine',
        '/connect-provider-flexibility',
        '/connect-scale',
        '/connect-technology',
        '/treatment-weight',
        '/treatment-hormones',
        '/treatment-peptides',
        '/treatment-longevity',
        '/treatment-cognitive',
        '/treatment-gut',
        '/treatment-immune',
        '/treatment-sexual',
        '/treatment-skin',
        '/treatment-sleep'
      ]
    }
  }
})
